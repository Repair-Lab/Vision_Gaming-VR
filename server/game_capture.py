#!/usr/bin/env python3
"""
Game Capture - Cross-platform screen/game capture
Supports Windows DirectShow, macOS AVFoundation, Linux X11
"""

import asyncio
import logging
import platform
import time
from typing import Optional, Callable, Tuple
import threading
import queue

import cv2
import mss
import numpy as np

# Platform-spezifische Imports
system = platform.system()
if system == "Windows":
    try:
        import win32gui
        import win32process
        import psutil
        WINDOWS_API_AVAILABLE = True
    except ImportError:
        WINDOWS_API_AVAILABLE = False
elif system == "Darwin":
    try:
        import Quartz
        MAC_API_AVAILABLE = True
    except ImportError:
        MAC_API_AVAILABLE = False
else:
    MAC_API_AVAILABLE = False
    WINDOWS_API_AVAILABLE = False


class GameCapture:
    """Cross-platform game/screen capture mit optimierter Performance"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_capturing = False
        self.capture_thread = None
        self.frame_queue = queue.Queue(maxsize=5)
        
        # Capture-Einstellungen
        self.target_fps = 60
        self.capture_width = 1920
        self.capture_height = 1080
        self.monitor_index = 0
        self.target_window = None
        
        # Performance-Tracking
        self.frames_captured = 0
        self.capture_start_time = 0
        self.last_fps_update = 0
        self.current_fps = 0
        
        # Callbacks
        self.frame_callbacks = []
        
        # Platform-spezifische Initialisierung
        self.screen_capture = mss.mss()
        self.capture_method = self._detect_best_capture_method()
        
        self.logger.info(f"GameCapture initialisiert mit Methode: {self.capture_method}")
    
    def _detect_best_capture_method(self) -> str:
        """Beste verfügbare Capture-Methode erkennen"""
        if system == "Windows" and WINDOWS_API_AVAILABLE:
            return "windows_optimized"
        elif system == "Darwin" and MAC_API_AVAILABLE:
            return "macos_optimized"
        else:
            return "mss_universal"
    
    def add_frame_callback(self, callback: Callable[[np.ndarray], None]):
        """Frame-Callback hinzufügen"""
        self.frame_callbacks.append(callback)
    
    def remove_frame_callback(self, callback: Callable[[np.ndarray], None]):
        """Frame-Callback entfernen"""
        if callback in self.frame_callbacks:
            self.frame_callbacks.remove(callback)
    
    def set_capture_settings(self, width: int, height: int, fps: int, monitor: int = 0):
        """Capture-Einstellungen setzen"""
        self.capture_width = width
        self.capture_height = height
        self.target_fps = fps
        self.monitor_index = monitor
        
        self.logger.info(f"Capture-Einstellungen: {width}x{height}@{fps}fps, Monitor {monitor}")
    
    def set_target_window(self, window_title: Optional[str] = None, process_name: Optional[str] = None):
        """Spezifisches Fenster als Capture-Ziel setzen"""
        if system == "Windows" and WINDOWS_API_AVAILABLE:
            self.target_window = self._find_window_windows(window_title, process_name)
        else:
            self.logger.warning("Window-spezifisches Capture nur auf Windows unterstützt")
            self.target_window = None
        
        if self.target_window:
            self.logger.info(f"Capture-Ziel gesetzt: {window_title or process_name}")
        else:
            self.logger.info("Capture-Ziel zurückgesetzt auf Monitor")
    
    def _find_window_windows(self, window_title: Optional[str], process_name: Optional[str]) -> Optional[int]:
        """Windows-Fenster finden"""
        if not WINDOWS_API_AVAILABLE:
            return None
        
        try:
            target_hwnd = None
            
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    
                    # Nach Fenster-Titel suchen
                    if window_title and window_title.lower() in title.lower():
                        windows.append(hwnd)
                    
                    # Nach Prozess-Name suchen
                    if process_name:
                        try:
                            _, pid = win32process.GetWindowThreadProcessId(hwnd)
                            process = psutil.Process(pid)
                            if process_name.lower() in process.name().lower():
                                windows.append(hwnd)
                        except:
                            pass
                
                return True
            
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            return windows[0] if windows else None
            
        except Exception as e:
            self.logger.error(f"Fehler bei Windows-Fenster-Suche: {e}")
            return None
    
    async def start(self) -> bool:
        """Capture starten"""
        if self.is_capturing:
            self.logger.warning("Capture bereits aktiv")
            return True
        
        try:
            self.is_capturing = True
            self.capture_start_time = time.time()
            self.frames_captured = 0
            
            # Capture-Thread starten
            self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.capture_thread.start()
            
            self.logger.info("Game Capture gestartet")
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler beim Capture-Start: {e}")
            self.is_capturing = False
            return False
    
    async def stop(self):
        """Capture stoppen"""
        if not self.is_capturing:
            return
        
        self.is_capturing = False
        
        # Warte auf Thread-Ende
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=2)
        
        # Queue leeren
        while not self.frame_queue.empty():
            try:
                self.frame_queue.get_nowait()
            except queue.Empty:
                break
        
        self.logger.info("Game Capture gestoppt")
    
    def _capture_loop(self):
        """Hauptschleife für Capture"""
        frame_interval = 1.0 / self.target_fps
        next_frame_time = time.time()
        
        self.logger.info(f"Capture-Loop gestartet - {self.target_fps} FPS")
        
        while self.is_capturing:
            try:
                current_time = time.time()
                
                # Warte bis nächster Frame-Zeit
                if current_time < next_frame_time:
                    time.sleep(next_frame_time - current_time)
                
                # Frame capturen
                frame = self._capture_frame()
                if frame is not None:
                    # Frame in Queue einreihen (non-blocking)
                    try:
                        self.frame_queue.put_nowait(frame)
                    except queue.Full:
                        # Ältesten Frame verwerfen
                        try:
                            self.frame_queue.get_nowait()
                            self.frame_queue.put_nowait(frame)
                        except queue.Empty:
                            pass
                    
                    # Callbacks aufrufen
                    for callback in self.frame_callbacks:
                        try:
                            callback(frame)
                        except Exception as e:
                            self.logger.error(f"Frame-Callback-Fehler: {e}")
                    
                    # Performance-Tracking
                    self.frames_captured += 1
                    self._update_fps_stats()
                
                # Nächste Frame-Zeit berechnen
                next_frame_time += frame_interval
                
                # Drift-Korrektur
                if time.time() > next_frame_time + frame_interval:
                    next_frame_time = time.time()
                
            except Exception as e:
                self.logger.error(f"Capture-Loop-Fehler: {e}")
                time.sleep(0.1)
        
        self.logger.info("Capture-Loop beendet")
    
    def _capture_frame(self) -> Optional[np.ndarray]:
        """Einzelnen Frame capturen"""
        try:
            if self.capture_method == "windows_optimized":
                return self._capture_frame_windows()
            elif self.capture_method == "macos_optimized":
                return self._capture_frame_macos()
            else:
                return self._capture_frame_mss()
                
        except Exception as e:
            self.logger.error(f"Frame-Capture-Fehler: {e}")
            return None
    
    def _capture_frame_windows(self) -> Optional[np.ndarray]:
        """Windows-optimiertes Capture"""
        try:
            if self.target_window:
                # Fenster-spezifisches Capture
                bbox = win32gui.GetWindowRect(self.target_window)
                monitor = {
                    "top": bbox[1],
                    "left": bbox[0], 
                    "width": bbox[2] - bbox[0],
                    "height": bbox[3] - bbox[1]
                }
            else:
                # Monitor-Capture
                monitor = self.screen_capture.monitors[self.monitor_index + 1]
            
            screenshot = self.screen_capture.grab(monitor)
            frame = np.array(screenshot)
            
            # BGR Konvertierung (OpenCV Standard)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            
            # Skalierung falls nötig
            current_height, current_width = frame.shape[:2]
            if current_width != self.capture_width or current_height != self.capture_height:
                frame = cv2.resize(frame, (self.capture_width, self.capture_height), 
                                 interpolation=cv2.INTER_LINEAR)
            
            return frame
            
        except Exception as e:
            self.logger.error(f"Windows-Capture-Fehler: {e}")
            return None
    
    def _capture_frame_macos(self) -> Optional[np.ndarray]:
        """macOS-optimiertes Capture"""
        try:
            # Fallback auf MSS für macOS
            return self._capture_frame_mss()
            
        except Exception as e:
            self.logger.error(f"macOS-Capture-Fehler: {e}")
            return None
    
    def _capture_frame_mss(self) -> Optional[np.ndarray]:
        """Universal MSS Capture"""
        try:
            monitor = self.screen_capture.monitors[self.monitor_index + 1]
            screenshot = self.screen_capture.grab(monitor)
            frame = np.array(screenshot)
            
            # BGRA zu BGR
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            
            # Skalierung
            current_height, current_width = frame.shape[:2]
            if current_width != self.capture_width or current_height != self.capture_height:
                frame = cv2.resize(frame, (self.capture_width, self.capture_height))
            
            return frame
            
        except Exception as e:
            self.logger.error(f"MSS-Capture-Fehler: {e}")
            return None
    
    def _update_fps_stats(self):
        """FPS-Statistiken aktualisieren"""
        current_time = time.time()
        
        if current_time - self.last_fps_update >= 1.0:
            elapsed_time = current_time - self.capture_start_time
            if elapsed_time > 0:
                self.current_fps = self.frames_captured / elapsed_time
            
            self.last_fps_update = current_time
    
    def get_latest_frame(self) -> Optional[np.ndarray]:
        """Neuesten Frame aus Queue holen"""
        try:
            return self.frame_queue.get_nowait()
        except queue.Empty:
            return None
    
    def get_fps(self) -> float:
        """Aktuelle FPS zurückgeben"""
        return self.current_fps
    
    def get_stats(self) -> dict:
        """Capture-Statistiken"""
        return {
            "is_capturing": self.is_capturing,
            "fps": self.current_fps,
            "frames_captured": self.frames_captured,
            "capture_method": self.capture_method,
            "resolution": f"{self.capture_width}x{self.capture_height}",
            "target_fps": self.target_fps,
            "queue_size": self.frame_queue.qsize()
        }


# Test-Funktion
if __name__ == "__main__":
    import asyncio
    
    async def test_capture():
        logging.basicConfig(level=logging.INFO)
        
        capture = GameCapture()
        
        def frame_callback(frame):
            print(f"Frame erhalten: {frame.shape}")
        
        capture.add_frame_callback(frame_callback)
        capture.set_capture_settings(1280, 720, 30)
        
        print("Starte Capture-Test...")
        await capture.start()
        
        await asyncio.sleep(5)
        
        print("Stoppe Capture-Test...")
        await capture.stop()
        
        print("Test abgeschlossen!")
    
    asyncio.run(test_capture())