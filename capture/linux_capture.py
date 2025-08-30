#!/usr/bin/env python3
"""
VR Gaming Server - Linux Screen Capture
Linux-spezifische Bildschirm-Aufnahme mit X11
"""

import logging
from typing import Optional, Tuple
import subprocess
import time
from PIL import Image
import io

class LinuxScreenCapture:
    """Linux Screen Capture mit X11-Tools"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_initialized = False
        self.display_width = 0
        self.display_height = 0
        self.temp_file = '/tmp/vr_capture.png'

    def initialize(self) -> bool:
        """Capture-System initialisieren"""
        try:
            # Display-Größe ermitteln
            if not self._get_display_size():
                return False

            # Capture-Methode bestimmen
            if not self._setup_capture_method():
                return False

            self.is_initialized = True
            self.logger.info(f"Linux Display-Größe: {self.display_width}x{self.display_height}")
            return True

        except Exception as e:
            self.logger.error(f"Fehler bei Linux Display-Initialisierung: {e}")
            return False

    def _get_display_size(self) -> bool:
        """Display-Größe mit xrandr ermitteln"""
        try:
            result = subprocess.run(
                ['xrandr', '--current'],
                capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                return self._parse_xrandr_output(result.stdout)

            # Fallback: Standard-Auflösung
            self.display_width = 1920
            self.display_height = 1080
            return True

        except Exception as e:
            self.logger.error(f"Fehler bei xrandr: {e}")
            return False

    def _parse_xrandr_output(self, output: str) -> bool:
        """Parse xrandr Output für Resolution"""
        lines = output.split('\n')
        for line in lines:
            if '*' in line and 'x' in line:
                parts = line.strip().split()[0].split('x')
                if len(parts) == 2:
                    try:
                        self.display_width = int(parts[0])
                        self.display_height = int(parts[1])
                        return True
                    except ValueError:
                        continue
        return False

    def _setup_capture_method(self) -> bool:
        """Capture-Methode bestimmen und einrichten"""
        # Prüfen ob scrot verfügbar ist
        result = subprocess.run(['which', 'scrot'], capture_output=True)
        if result.returncode == 0:
            self.use_pil = False
            return True

        # Fallback zu PIL ImageGrab
        try:
            from PIL import ImageGrab
            self.use_pil = True
            return True
        except ImportError:
            self.logger.error("Weder scrot noch PIL ImageGrab verfügbar")
            return False

    def capture_frame(self) -> Optional[bytes]:
        """Einzelnes Frame aufnehmen"""
        if not self.is_initialized:
            return None

        try:
            if self.use_pil:
                # PIL ImageGrab verwenden
                from PIL import ImageGrab
                screenshot = ImageGrab.grab()
                # In Bytes konvertieren
                buffer = io.BytesIO()
                screenshot.save(buffer, format='PNG', optimize=True)
                return buffer.getvalue()
            else:
                # scrot verwenden
                result = subprocess.run(
                    ['scrot', '-z', self.temp_file],
                    capture_output=True, timeout=2
                )

                if result.returncode != 0:
                    self.logger.error(f"scrot fehlgeschlagen: {result.stderr.decode()}")
                    return None

                # Bild laden und als Bytes zurückgeben
                with open(self.temp_file, 'rb') as f:
                    image_data = f.read()

                # Aufräumen
                subprocess.run(['rm', self.temp_file], capture_output=True)

                return image_data

        except subprocess.TimeoutExpired:
            self.logger.error("Screenshot Timeout")
            return None
        except Exception as e:
            self.logger.error(f"Fehler bei Frame-Capture: {e}")
            return None

    def get_display_info(self) -> dict:
        """Display-Informationen abrufen"""
        return {
            "width": self.display_width,
            "height": self.display_height,
            "refresh_rate": 60,  # Standardwert für Linux
            "color_depth": 24,
            "platform": "linux",
            "capture_method": "pil" if self.use_pil else "scrot"
        }
