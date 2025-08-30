#!/usr/bin/env python3
"""
VR Gaming Server - Keyboard Controller
Tastatur-Steuerung für VR-Input-Injection
"""

import logging
from typing import List, Optional, Dict
import time
import platform
from abc import ABC, abstractmethod

class KeyboardController(ABC):
    """Abstrakte Basisklasse für Tastatur-Steuerung"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_initialized = False
        self.layout = "de"  # Standard-Layout
        self.key_mappings = self._get_default_mappings()

    @abstractmethod
    def initialize(self) -> bool:
        """Tastatur-System initialisieren"""
        pass

    @abstractmethod
    def press_key(self, key: str) -> bool:
        """Taste drücken"""
        pass

    @abstractmethod
    def release_key(self, key: str) -> bool:
        """Taste loslassen"""
        pass

    @abstractmethod
    def type_text(self, text: str) -> bool:
        """Text eingeben"""
        pass

    def press_and_release(self, key: str, duration: float = 0.1) -> bool:
        """Taste drücken und wieder loslassen"""
        try:
            if self.press_key(key):
                time.sleep(duration)
                return self.release_key(key)
            return False
        except Exception as e:
            self.logger.error(f"Fehler bei press_and_release: {e}")
            return False

    def set_layout(self, layout: str):
        """Tastatur-Layout setzen"""
        supported_layouts = ["de", "en", "fr", "es"]
        if layout.lower() in supported_layouts:
            self.layout = layout.lower()
            self.key_mappings = self._get_layout_mappings(layout.lower())
        else:
            self.logger.warning(f"Nicht unterstütztes Layout: {layout}")

    def get_key_code(self, key: str) -> Optional[str]:
        """Key-Code für Taste abrufen"""
        return self.key_mappings.get(key.lower())

    def _get_default_mappings(self) -> Dict[str, str]:
        """Standard-Key-Mappings"""
        return {
            "a": "a", "b": "b", "c": "c", "d": "d", "e": "e",
            "f": "f", "g": "g", "h": "h", "i": "i", "j": "j",
            "k": "k", "l": "l", "m": "m", "n": "n", "o": "o",
            "p": "p", "q": "q", "r": "r", "s": "s", "t": "t",
            "u": "u", "v": "v", "w": "w", "x": "x", "y": "y", "z": "z",
            "space": "space", "enter": "enter", "tab": "tab",
            "shift": "shift", "ctrl": "ctrl", "alt": "alt",
            "esc": "esc", "f1": "f1", "f2": "f2", "f3": "f3", "f4": "f4",
            "f5": "f5", "f6": "f6", "f7": "f7", "f8": "f8", "f9": "f9",
            "f10": "f10", "f11": "f11", "f12": "f12"
        }

    def _get_layout_mappings(self, layout: str) -> Dict[str, str]:
        """Layout-spezifische Key-Mappings"""
        if layout == "de":
            return {
                **self._get_default_mappings(),
                "ä": "adiaeresis", "ö": "odiaeresis", "ü": "udiaeresis",
                "ß": "ssharp", "y": "z", "z": "y"  # QWERTZ Layout
            }
        elif layout == "fr":
            return {
                **self._get_default_mappings(),
                "a": "q", "q": "a", "z": "w", "w": "z",  # AZERTY Layout
                "m": "semicolon", ";": "m"
            }
        elif layout == "es":
            return {
                **self._get_default_mappings(),
                "ñ": "ntilde"
            }
        else:
            return self._get_default_mappings()

    def get_stats(self) -> dict:
        """Controller-Statistiken"""
        return {
            "initialized": self.is_initialized,
            "layout": self.layout,
            "platform": platform.system().lower(),
            "mappings_count": len(self.key_mappings)
        }


def create_keyboard_controller() -> KeyboardController:
    """Plattform-spezifischen Keyboard Controller erstellen"""
    system = platform.system().lower()

    if system == "windows":
        from .windows_keyboard import WindowsKeyboardController
        return WindowsKeyboardController()
    elif system == "darwin":
        from .macos_keyboard import MacOSKeyboardController
        return MacOSKeyboardController()
    elif system == "linux":
        from .linux_keyboard import LinuxKeyboardController
        return LinuxKeyboardController()
    else:
        raise NotImplementedError(f"Unsupported platform: {system}")


# Factory-Funktion für einfache Verwendung
def get_keyboard_controller() -> KeyboardController:
    """Keyboard Controller Instanz erstellen"""
    return create_keyboard_controller()
