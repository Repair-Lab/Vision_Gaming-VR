#!/usr/bin/env python3
"""
VR Gaming Server - macOS Screen Capture
macOS-spezifische Bildschirm-Aufnahme mit AVFoundation
"""

import logging
from typing import Optional, Tuple
import subprocess
import time
from PIL import Image
import io

class MacOSScreenCapture:
    """macOS Screen Capture mit Screenshot-Tools"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_initialized = False
        self.display_width = 0
        self.display_height = 0
        self.temp_file = '/tmp/vr_capture.jpg'

    def initialize(self) -> bool:
        """Capture-System initialisieren"""
        try:
            # Display-Größe mit system_profiler ermitteln
            result = subprocess.run(
                ['system_profiler', 'SPDisplaysDataType'],
                capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                # Parse Resolution aus Output
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'Resolution:' in line:
                        parts = line.split(':')[1].strip().split(' ')
                        if len(parts) >= 2:
                            resolution = parts[0]
                            width, height = map(int, resolution.split('x'))
                            self.display_width = width
                            self.display_height = height
                            break

            if self.display_width == 0:
                # Fallback: Standard-Auflösung
                self.display_width = 1920
                self.display_height = 1080

            self.is_initialized = True
            self.logger.info(f"macOS Display-Größe: {self.display_width}x{self.display_height}")
            return True

        except Exception as e:
            self.logger.error(f"Fehler bei macOS Display-Initialisierung: {e}")
            return False

    def capture_frame(self) -> Optional[bytes]:
        """Einzelnes Frame aufnehmen mit screencapture"""
        if not self.is_initialized:
            return None

        try:
            # Screenshot mit screencapture erstellen
            result = subprocess.run(
                ['screencapture', '-x', '-t', 'jpg', self.temp_file],
                capture_output=True, timeout=2
            )

            if result.returncode != 0:
                self.logger.error(f"screencapture fehlgeschlagen: {result.stderr.decode()}")
                return None

            # Bild laden und als Bytes zurückgeben
            with open(self.temp_file, 'rb') as f:
                image_data = f.read()

            # Aufräumen
            subprocess.run(['rm', self.temp_file], capture_output=True)

            return image_data

        except subprocess.TimeoutExpired:
            self.logger.error("screencapture Timeout")
            return None
        except Exception as e:
            self.logger.error(f"Fehler bei Frame-Capture: {e}")
            return None

    def get_display_info(self) -> dict:
        """Display-Informationen abrufen"""
        return {
            "width": self.display_width,
            "height": self.display_height,
            "refresh_rate": 60,  # Standardwert für macOS
            "color_depth": 24,
            "platform": "macos"
        }
