#!/usr/bin/env python3
"""
VR Gaming Server - Universal Screen Capture
Plattform-unabhängige Bildschirm-Aufnahme
"""

import sys
import platform
import logging
from typing import Optional, Tuple, Callable
from abc import ABC, abstractmethod
import asyncio
import threading
import time
from queue import Queue, Full, Empty

class ScreenCapture(ABC):
    """Abstrakte Basisklasse für Screen Capture"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_capturing = False
        self.capture_thread: Optional[threading.Thread] = None
        self.frame_callbacks: list[Callable] = []
        self.frame_queue: Queue = Queue(maxsize=10)
        self.frames_captured = 0
        self.last_fps_update = time.time()
        self.fps = 0
        self.target_fps = 60

    @abstractmethod
    def initialize(self) -> bool:
        """Capture-System initialisieren"""
        pass

    @abstractmethod
    def capture_frame(self) -> Optional[bytes]:
        """Einzelnes Frame aufnehmen"""
        pass

    @abstractmethod
    def get_display_info(self) -> dict:
        """Display-Informationen abrufen"""
        pass

    def start_capture(self, callback: Optional[Callable] = None) -> bool:
        """Capture-Thread starten"""
        if self.is_capturing:
            self.logger.warning("Capture bereits aktiv")
            return True

        if callback:
            self.frame_callbacks.append(callback)

        try:
            self.is_capturing = True
            self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.capture_thread.start()
            self.logger.info("Screen Capture gestartet")
            return True
        except Exception as e:
            self.logger.error(f"Fehler beim Starten des Capture: {e}")
            self.is_capturing = False
            return False

    def stop_capture(self):
        """Capture stoppen"""
        if not self.is_capturing:
            return

        self.is_capturing = False
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=2.0)

        self.logger.info("Screen Capture gestoppt")

    def _capture_loop(self):
        """Haupt-Capture-Loop"""
        frame_interval = 1.0 / self.target_fps

        while self.is_capturing:
            start_time = time.time()

            try:
                # Frame aufnehmen und verarbeiten
                self._process_frame()
            except Exception as e:
                self.logger.error(f"Fehler bei Frame-Capture: {e}")

            # Frame-Rate begrenzen
            self._limit_frame_rate(start_time, frame_interval)

    def _process_frame(self):
        """Frame aufnehmen und verarbeiten"""
        frame = self.capture_frame()
        if frame:
            self._handle_frame(frame)
            self.frames_captured += 1
            self._update_fps_stats()

    def _handle_frame(self, frame: bytes):
        """Frame in Queue legen und Callbacks aufrufen"""
        try:
            self.frame_queue.put_nowait(frame)
        except Full:
            # Ältesten Frame verwerfen
            try:
                self.frame_queue.get_nowait()
                self.frame_queue.put_nowait(frame)
            except Empty:
                pass

        # Callbacks aufrufen
        for callback in self.frame_callbacks:
            try:
                callback(frame)
            except Exception as e:
                self.logger.error(f"Frame-Callback-Fehler: {e}")

    def _limit_frame_rate(self, start_time: float, frame_interval: float):
        """Frame-Rate begrenzen"""
        elapsed = time.time() - start_time
        if elapsed < frame_interval:
            time.sleep(frame_interval - elapsed)

    def _update_fps_stats(self):
        """FPS-Statistiken aktualisieren"""
        current_time = time.time()
        if current_time - self.last_fps_update >= 1.0:
            self.fps = self.frames_captured / (current_time - self.last_fps_update)
            self.frames_captured = 0
            self.last_fps_update = current_time

    def get_frame(self, timeout: float = 1.0) -> Optional[bytes]:
        """Frame aus Queue holen"""
        try:
            return self.frame_queue.get(timeout=timeout)
        except Empty:
            return None

    def get_stats(self) -> dict:
        """Capture-Statistiken abrufen"""
        return {
            "is_capturing": self.is_capturing,
            "fps": round(self.fps, 2),
            "target_fps": self.target_fps,
            "queue_size": self.frame_queue.qsize(),
            "frames_captured": self.frames_captured
        }

    def set_target_fps(self, fps: int):
        """Ziel-FPS setzen"""
        self.target_fps = max(1, min(120, fps))
        self.logger.info(f"Ziel-FPS auf {self.target_fps} gesetzt")


def create_capture_system() -> ScreenCapture:
    """Plattform-spezifisches Capture-System erstellen"""
    system = platform.system().lower()

    if system == "windows":
        from .windows_capture import WindowsScreenCapture
        return WindowsScreenCapture()
    elif system == "darwin":
        from .macos_capture import MacOSScreenCapture
        return MacOSScreenCapture()
    elif system == "linux":
        from .linux_capture import LinuxScreenCapture
        return LinuxScreenCapture()
    else:
        raise NotImplementedError(f"Unsupported platform: {system}")


# Factory-Funktion für einfache Verwendung
def get_screen_capture() -> ScreenCapture:
    """Screen Capture Instanz erstellen"""
    return create_capture_system()
