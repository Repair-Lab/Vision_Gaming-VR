#!/usr/bin/env python3
"""
VR Gaming Server - Mouse Controller
Maus-Steuerung für VR-Input-Injection
"""

import logging
from typing import Tuple, Optional
import time
import platform
from abc import ABC, abstractmethod

class MouseController(ABC):
    """Abstrakte Basisklasse für Maus-Steuerung"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_initialized = False
        self.screen_width = 1920
        self.screen_height = 1080
        self.sensitivity = 1.0

    @abstractmethod
    def initialize(self) -> bool:
        """Maus-System initialisieren"""
        pass

    @abstractmethod
    def move_to(self, x: int, y: int) -> bool:
        """Maus zu Position bewegen"""
        pass

    @abstractmethod
    def click(self, button: str = "left", double: bool = False) -> bool:
        """Mausklick ausführen"""
        pass

    @abstractmethod
    def scroll(self, direction: str, clicks: int = 1) -> bool:
        """Mausrad scrollen"""
        pass

    def set_screen_size(self, width: int, height: int):
        """Bildschirm-Größe setzen"""
        self.screen_width = width
        self.screen_height = height

    def set_sensitivity(self, sensitivity: float):
        """Maus-Empfindlichkeit setzen"""
        self.sensitivity = max(0.1, min(5.0, sensitivity))

    def normalize_coordinates(self, x: float, y: float) -> Tuple[int, int]:
        """Koordinaten normalisieren (0-1 zu Pixel)"""
        pixel_x = int(x * self.screen_width * self.sensitivity)
        pixel_y = int(y * self.screen_height * self.sensitivity)

        # Begrenzung auf Bildschirm
        pixel_x = max(0, min(pixel_x, self.screen_width - 1))
        pixel_y = max(0, min(pixel_y, self.screen_height - 1))

        return pixel_x, pixel_y

    def get_position(self) -> Tuple[int, int]:
        """Aktuelle Maus-Position abrufen"""
        return (0, 0)  # Default-Implementierung

    def get_stats(self) -> dict:
        """Controller-Statistiken"""
        return {
            "initialized": self.is_initialized,
            "screen_size": f"{self.screen_width}x{self.screen_height}",
            "sensitivity": self.sensitivity,
            "platform": platform.system().lower()
        }


def create_mouse_controller() -> MouseController:
    """Plattform-spezifischen Mouse Controller erstellen"""
    system = platform.system().lower()

    if system == "windows":
        from .windows_mouse import WindowsMouseController
        return WindowsMouseController()
    elif system == "darwin":
        from .macos_mouse import MacOSMouseController
        return MacOSMouseController()
    elif system == "linux":
        from .linux_mouse import LinuxMouseController
        return LinuxMouseController()
    else:
        raise NotImplementedError(f"Unsupported platform: {system}")


# Factory-Funktion für einfache Verwendung
def get_mouse_controller() -> MouseController:
    """Mouse Controller Instanz erstellen"""
    return create_mouse_controller()
