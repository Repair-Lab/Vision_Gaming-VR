#!/usr/bin/env python3
"""
Input Injector - Cross-platform Input-Injection
Konvertiert VR-Input zu Maus/Tastatur-Eingaben
"""

import logging
import platform
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Cross-platform Input-Libraries
try:
    import pynput
    from pynput.mouse import Button, Listener as MouseListener
    from pynput.keyboard import Key, KeyCode, Listener as KeyboardListener
    from pynput import mouse, keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False

# Windows-spezifische APIs
if platform.system() == "Windows":
    try:
        import win32api
        import win32con
        import ctypes
        from ctypes import wintypes
        WIN32_AVAILABLE = True
    except ImportError:
        WIN32_AVAILABLE = False
else:
    WIN32_AVAILABLE = False

@dataclass
class InputAction:
    """Input-Aktion-Definition"""
    action_type: str  # "mouse_move", "mouse_click", "key_press", "key_release"
    data: Dict[str, Any]
    timestamp: float = 0.0

class InputInjector:
    """Cross-platform Input-Injection mit Windows-Optimierungen"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_active = False
        
        # Input-Controller initialisieren
        self.mouse_controller = None
        self.keyboard_controller = None
        self.input_method = self._detect_input_method()
        
        # Konfiguration
        self.mouse_sensitivity = 1.0
        self.acceleration_curve = 1.0
        self.min_mouse_delta = 0.5
        
        # Statistiken
        self.actions_processed = 0
        self.start_time = time.time()
        
        self._initialize_controllers()
        
        self.logger.info(f"InputInjector initialisiert mit Methode: {self.input_method}")
    
    def _detect_input_method(self) -> str:
        """Beste verfügbare Input-Methode erkennen"""
        if WIN32_AVAILABLE:
            return "win32_native"
        elif PYNPUT_AVAILABLE:
            return "pynput_cross_platform"
        else:
            return "none"
    
    def _initialize_controllers(self):
        """Input-Controller initialisieren"""
        if self.input_method == "pynput_cross_platform" and PYNPUT_AVAILABLE:
            try:
                self.mouse_controller = mouse.Controller()
                self.keyboard_controller = keyboard.Controller()
                self.logger.info("Pynput-Controller initialisiert")
            except Exception as e:
                self.logger.error(f"Pynput-Initialisierung fehlgeschlagen: {e}")
                self.input_method = "none"
        
        elif self.input_method == "win32_native":
            self.logger.info("Win32-Native-Input verfügbar")
    
    def configure(self, config: Dict):
        """Input-Injector mit Profil konfigurieren"""
        input_config = config.get("input", {})
        
        self.mouse_sensitivity = input_config.get("mouse_sensitivity", 1.0)
        self.acceleration_curve = input_config.get("acceleration_curve", 1.0)
        self.min_mouse_delta = input_config.get("min_mouse_delta", 0.5)
        
        self.logger.info(f"InputInjector konfiguriert: Sensitivity={self.mouse_sensitivity}, "
                        f"Acceleration={self.acceleration_curve}")
    
    def start(self):
        """Input-Injection aktivieren"""
        if self.input_method == "none":
            self.logger.error("Keine Input-Methode verfügbar")
            return False
        
        self.is_active = True
        self.actions_processed = 0
        self.start_time = time.time()
        
        self.logger.info("Input-Injection gestartet")
        return True
    
    def stop(self):
        """Input-Injection deaktivieren"""
        self.is_active = False
        self.logger.info("Input-Injection gestoppt")
    
    async def inject_input(self, processed_input) -> bool:
        """Verarbeiteten Input injizieren"""
        if not self.is_active or self.input_method == "none":
            return False
        
        try:
            # Mouse Movement
            if hasattr(processed_input, 'mouse_delta_x') and hasattr(processed_input, 'mouse_delta_y'):
                success = await self._inject_mouse_movement(
                    processed_input.mouse_delta_x, 
                    processed_input.mouse_delta_y
                )
                if success:
                    self.actions_processed += 1
                return success
            
            return False
            
        except Exception as e:
            self.logger.error(f"Input-Injection-Fehler: {e}")
            return False
    
    async def _inject_mouse_movement(self, delta_x: float, delta_y: float) -> bool:
        """Mausbewegung injizieren"""
        # Sensitivität und Acceleration anwenden
        adjusted_x = delta_x * self.mouse_sensitivity
        adjusted_y = delta_y * self.mouse_sensitivity
        
        # Acceleration-Curve anwenden
        if self.acceleration_curve != 1.0:
            magnitude = (adjusted_x ** 2 + adjusted_y ** 2) ** 0.5
            if magnitude > 0:
                acceleration_factor = magnitude ** (self.acceleration_curve - 1.0)
                adjusted_x *= acceleration_factor
                adjusted_y *= acceleration_factor
        
        # Minimum-Delta prüfen
        if abs(adjusted_x) < self.min_mouse_delta and abs(adjusted_y) < self.min_mouse_delta:
            return False
        
        # Integer-Konvertierung
        move_x = int(round(adjusted_x))
        move_y = int(round(adjusted_y))
        
        if move_x == 0 and move_y == 0:
            return False
        
        # Platform-spezifische Injection
        if self.input_method == "win32_native":
            return self._inject_mouse_win32(move_x, move_y)
        elif self.input_method == "pynput_cross_platform":
            return self._inject_mouse_pynput(move_x, move_y)
        
        return False
    
    def _inject_mouse_win32(self, delta_x: int, delta_y: int) -> bool:
        """Windows Win32 API Mouse-Injection"""
        try:
            # GetCursorPos für aktuelle Position
            cursor_pos = wintypes.POINT()
            ctypes.windll.user32.GetCursorPos(ctypes.byref(cursor_pos))
            
            # Neue Position berechnen
            new_x = cursor_pos.x + delta_x
            new_y = cursor_pos.y + delta_y
            
            # SetCursorPos für absolute Positionierung
            result = ctypes.windll.user32.SetCursorPos(new_x, new_y)
            return result != 0
            
        except Exception as e:
            self.logger.error(f"Win32-Mouse-Injection-Fehler: {e}")
            return False
    
    def _inject_mouse_pynput(self, delta_x: int, delta_y: int) -> bool:
        """Pynput Mouse-Injection"""
        try:
            if self.mouse_controller:
                self.mouse_controller.move(delta_x, delta_y)
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Pynput-Mouse-Injection-Fehler: {e}")
            return False
    
    async def inject_key_press(self, key: str) -> bool:
        """Tastendruck injizieren"""
        if not self.is_active or self.input_method == "none":
            return False
        
        try:
            if self.input_method == "win32_native":
                return self._inject_key_win32(key, press=True)
            elif self.input_method == "pynput_cross_platform":
                return self._inject_key_pynput(key, press=True)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Key-Press-Injection-Fehler: {e}")
            return False
    
    async def inject_key_release(self, key: str) -> bool:
        """Tasten-Release injizieren"""
        if not self.is_active or self.input_method == "none":
            return False
        
        try:
            if self.input_method == "win32_native":
                return self._inject_key_win32(key, press=False)
            elif self.input_method == "pynput_cross_platform":
                return self._inject_key_pynput(key, press=False)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Key-Release-Injection-Fehler: {e}")
            return False
    
    def _inject_key_win32(self, key: str, press: bool) -> bool:
        """Windows Win32 Key-Injection"""
        try:
            # Key-Code-Mapping
            key_codes = {
                'SPACE': 0x20,
                'ENTER': 0x0D,
                'ESC': 0x1B,
                'TAB': 0x09,
                'SHIFT': 0x10,
                'CTRL': 0x11,
                'ALT': 0x12,
                'F1': 0x70, 'F2': 0x71, 'F3': 0x72, 'F4': 0x73,
                'F5': 0x74, 'F6': 0x75, 'F7': 0x76, 'F8': 0x77,
                'F9': 0x78, 'F10': 0x79, 'F11': 0x7A, 'F12': 0x7B,
                'A': 0x41, 'B': 0x42, 'C': 0x43, 'D': 0x44,
                'E': 0x45, 'F': 0x46, 'G': 0x47, 'H': 0x48,
                'I': 0x49, 'J': 0x4A, 'K': 0x4B, 'L': 0x4C,
                'M': 0x4D, 'N': 0x4E, 'O': 0x4F, 'P': 0x50,
                'Q': 0x51, 'R': 0x52, 'S': 0x53, 'T': 0x54,
                'U': 0x55, 'V': 0x56, 'W': 0x57, 'X': 0x58,
                'Y': 0x59, 'Z': 0x5A,
                'LMB': 0x01, 'RMB': 0x02, 'MMB': 0x04
            }
            
            key_upper = key.upper()
            if key_upper not in key_codes:
                self.logger.warning(f"Unbekannter Key: {key}")
                return False
            
            vk_code = key_codes[key_upper]
            
            if key_upper in ['LMB', 'RMB', 'MMB']:
                # Maus-Button
                if key_upper == 'LMB':
                    event = win32con.MOUSEEVENTF_LEFTDOWN if press else win32con.MOUSEEVENTF_LEFTUP
                elif key_upper == 'RMB':
                    event = win32con.MOUSEEVENTF_RIGHTDOWN if press else win32con.MOUSEEVENTF_RIGHTUP
                else:  # MMB
                    event = win32con.MOUSEEVENTF_MIDDLEDOWN if press else win32con.MOUSEEVENTF_MIDDLEUP
                
                win32api.mouse_event(event, 0, 0, 0, 0)
            else:
                # Tastatur-Key
                flags = 0 if press else win32con.KEYEVENTF_KEYUP
                win32api.keybd_event(vk_code, 0, flags, 0)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Win32-Key-Injection-Fehler: {e}")
            return False
    
    def _inject_key_pynput(self, key: str, press: bool) -> bool:
        """Pynput Key-Injection"""
        try:
            if not self.keyboard_controller:
                return False
            
            # Key-Mapping für pynput
            key_mapping = {
                'SPACE': Key.space,
                'ENTER': Key.enter,
                'ESC': Key.esc,
                'TAB': Key.tab,
                'SHIFT': Key.shift,
                'CTRL': Key.ctrl,
                'ALT': Key.alt,
                'F1': Key.f1, 'F2': Key.f2, 'F3': Key.f3, 'F4': Key.f4,
                'F5': Key.f5, 'F6': Key.f6, 'F7': Key.f7, 'F8': Key.f8,
                'F9': Key.f9, 'F10': Key.f10, 'F11': Key.f11, 'F12': Key.f12
            }
            
            key_upper = key.upper()
            
            # Mouse-Button-Handling
            if key_upper in ['LMB', 'RMB', 'MMB']:
                if not self.mouse_controller:
                    return False
                
                button_mapping = {
                    'LMB': Button.left,
                    'RMB': Button.right,
                    'MMB': Button.middle
                }
                
                button = button_mapping[key_upper]
                if press:
                    self.mouse_controller.press(button)
                else:
                    self.mouse_controller.release(button)
                
                return True
            
            # Keyboard-Key-Handling
            if key_upper in key_mapping:
                pynput_key = key_mapping[key_upper]
            elif len(key) == 1:
                pynput_key = KeyCode.from_char(key.lower())
            else:
                self.logger.warning(f"Unbekannter Key für pynput: {key}")
                return False
            
            if press:
                self.keyboard_controller.press(pynput_key)
            else:
                self.keyboard_controller.release(pynput_key)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Pynput-Key-Injection-Fehler: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Input-Injection-Statistiken"""
        uptime = time.time() - self.start_time
        actions_per_second = self.actions_processed / uptime if uptime > 0 else 0
        
        return {
            "is_active": self.is_active,
            "input_method": self.input_method,
            "actions_processed": self.actions_processed,
            "actions_per_second": actions_per_second,
            "uptime": uptime,
            "configuration": {
                "mouse_sensitivity": self.mouse_sensitivity,
                "acceleration_curve": self.acceleration_curve,
                "min_mouse_delta": self.min_mouse_delta
            }
        }


# Test-Funktion
if __name__ == "__main__":
    import asyncio
    
    async def test_input_injector():
        logging.basicConfig(level=logging.INFO)
        
        injector = InputInjector()
        
        if injector.start():
            print("Teste Mausbewegung...")
            
            # Simuliere ProcessedInput
            class MockInput:
                def __init__(self, x, y):
                    self.mouse_delta_x = x
                    self.mouse_delta_y = y
            
            # Test verschiedene Bewegungen
            movements = [
                (10, 0),   # Rechts
                (0, 10),   # Runter
                (-10, 0),  # Links
                (0, -10),  # Rauf
                (5, 5),    # Diagonal
            ]
            
            for dx, dy in movements:
                mock_input = MockInput(dx, dy)
                success = await injector.inject_input(mock_input)
                print(f"Movement ({dx}, {dy}): {'Success' if success else 'Failed'}")
                await asyncio.sleep(0.5)
            
            print("Teste Tastendruck...")
            await injector.inject_key_press("A")
            await asyncio.sleep(0.1)
            await injector.inject_key_release("A")
            
            stats = injector.get_stats()
            print(f"Statistiken: {stats}")
            
            injector.stop()
        else:
            print("Input-Injector konnte nicht gestartet werden")
    
    asyncio.run(test_input_injector())