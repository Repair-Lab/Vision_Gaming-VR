#!/usr/bin/env python3
"""
VR Gaming Server - Windows Screen Capture
Windows-spezifische Bildschirm-Aufnahme mit DirectX
"""

import logging
from typing import Optional, Tuple
import ctypes
from ctypes import wintypes
from PIL import Image
import time

# Windows API Konstanten
SRCCOPY = 0x00CC0020
DIB_RGB_COLORS = 0

# BITMAPINFO Struktur definieren
class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", ctypes.c_uint32),
        ("biWidth", ctypes.c_int32),
        ("biHeight", ctypes.c_int32),
        ("biPlanes", ctypes.c_uint16),
        ("biBitCount", ctypes.c_uint16),
        ("biCompression", ctypes.c_uint32),
        ("biSizeImage", ctypes.c_uint32),
        ("biXPelsPerMeter", ctypes.c_int32),
        ("biYPelsPerMeter", ctypes.c_int32),
        ("biClrUsed", ctypes.c_uint32),
        ("biClrImportant", ctypes.c_uint32)
    ]

class BITMAPINFO(ctypes.Structure):
    _fields_ = [
        ("bmiHeader", BITMAPINFOHEADER),
        ("bmiColors", ctypes.c_uint32 * 3)
    ]

class WindowsScreenCapture:
    """Windows Screen Capture mit GDI"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_initialized = False
        self.display_width = 0
        self.display_height = 0

        # Windows API Setup
        self._setup_windows_api()

    def _setup_windows_api(self):
        """Windows API Funktionen laden"""
        try:
            self.user32 = ctypes.windll.user32
            self.gdi32 = ctypes.windll.gdi32
            self.kernel32 = ctypes.windll.kernel32

            # API Funktionen definieren
            self.get_system_metrics = self.user32.GetSystemMetrics
            self.get_system_metrics.argtypes = [ctypes.c_int]
            self.get_system_metrics.restype = ctypes.c_int

            self.get_window_dc = self.user32.GetWindowDC
            self.get_window_dc.argtypes = [wintypes.HWND]
            self.get_window_dc.restype = wintypes.HDC

            self.create_compatible_dc = self.gdi32.CreateCompatibleDC
            self.create_compatible_dc.argtypes = [wintypes.HDC]
            self.create_compatible_dc.restype = wintypes.HDC

            self.create_compatible_bitmap = self.gdi32.CreateCompatibleBitmap
            self.create_compatible_bitmap.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int]
            self.create_compatible_bitmap.restype = wintypes.HBITMAP

            self.select_object = self.gdi32.SelectObject
            self.select_object.argtypes = [wintypes.HDC, wintypes.HGDIOBJ]
            self.select_object.restype = wintypes.HGDIOBJ

            self.bit_blt = self.gdi32.BitBlt
            self.bit_blt.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                   wintypes.HDC, ctypes.c_int, ctypes.c_int, ctypes.c_uint]
            self.bit_blt.restype = wintypes.BOOL

            self.get_di_bits = self.gdi32.GetDIBits
            self.get_di_bits.argtypes = [wintypes.HDC, wintypes.HBITMAP, ctypes.c_uint, ctypes.c_uint,
                                      ctypes.c_void_p, ctypes.POINTER(BITMAPINFO), ctypes.c_uint]
            self.get_di_bits.restype = ctypes.c_int

            self.delete_dc = self.gdi32.DeleteDC
            self.delete_dc.argtypes = [wintypes.HDC]
            self.delete_dc.restype = wintypes.BOOL

            self.release_dc = self.user32.ReleaseDC
            self.release_dc.argtypes = [wintypes.HWND, wintypes.HDC]
            self.release_dc.restype = ctypes.c_int

            self.delete_object = self.gdi32.DeleteObject
            self.delete_object.argtypes = [wintypes.HGDIOBJ]
            self.delete_object.restype = wintypes.BOOL

            self.is_initialized = True
            self.logger.info("Windows API erfolgreich initialisiert")

        except Exception as e:
            self.logger.error(f"Fehler bei Windows API Setup: {e}")
            self.is_initialized = False

    def initialize(self) -> bool:
        """Capture-System initialisieren"""
        if not self.is_initialized:
            self._setup_windows_api()

        if not self.is_initialized:
            return False

        try:
            # Display-Größe ermitteln
            self.display_width = self.GetSystemMetrics(0)  # SM_CXSCREEN
            self.display_height = self.GetSystemMetrics(1)  # SM_CYSCREEN

            self.logger.info(f"Display-Größe: {self.display_width}x{self.display_height}")
            return True

        except Exception as e:
            self.logger.error(f"Fehler bei Display-Initialisierung: {e}")
            return False

    def capture_frame(self) -> Optional[bytes]:
        """Einzelnes Frame aufnehmen"""
        if not self.is_initialized:
            return None

        try:
            # Desktop Window Handle
            hwnd = self.user32.GetDesktopWindow()

            # Device Contexts erstellen
            hdc_screen = self.GetWindowDC(hwnd)
            hdc_mem = self.CreateCompatibleDC(hdc_screen)

            # Bitmap erstellen
            hbitmap = self.CreateCompatibleBitmap(hdc_screen, self.display_width, self.display_height)
            self.SelectObject(hdc_mem, hbitmap)

            # Screen in Bitmap kopieren
            self.BitBlt(hdc_mem, 0, 0, self.display_width, self.display_height,
                       hdc_screen, 0, 0, SRCCOPY)

            # Bitmap-Daten abrufen
            bitmap_data = self._get_bitmap_data(hbitmap, hdc_mem)

            # Ressourcen freigeben
            self.DeleteObject(hbitmap)
            self.DeleteDC(hdc_mem)
            self.ReleaseDC(hwnd, hdc_screen)

            return bitmap_data

        except Exception as e:
            self.logger.error(f"Fehler bei Frame-Capture: {e}")
            return None

    def _get_bitmap_data(self, hbitmap, hdc_mem) -> Optional[bytes]:
        """Bitmap-Daten als Bytes abrufen"""
        try:
            # BITMAPINFO Struktur
            class BITMAPINFOHEADER(ctypes.Structure):
                _fields_ = [
                    ("biSize", ctypes.c_uint32),
                    ("biWidth", ctypes.c_int32),
                    ("biHeight", ctypes.c_int32),
                    ("biPlanes", ctypes.c_uint16),
                    ("biBitCount", ctypes.c_uint16),
                    ("biCompression", ctypes.c_uint32),
                    ("biSizeImage", ctypes.c_uint32),
                    ("biXPelsPerMeter", ctypes.c_int32),
                    ("biYPelsPerMeter", ctypes.c_int32),
                    ("biClrUsed", ctypes.c_uint32),
                    ("biClrImportant", ctypes.c_uint32)
                ]

            class BITMAPINFO(ctypes.Structure):
                _fields_ = [
                    ("bmiHeader", BITMAPINFOHEADER),
                    ("bmiColors", ctypes.c_uint32 * 3)
                ]

            # Bitmap-Info erstellen
            bmi = BITMAPINFO()
            bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
            bmi.bmiHeader.biWidth = self.display_width
            bmi.bmiHeader.biHeight = -self.display_height  # Negative Höhe für top-down
            bmi.bmiHeader.biPlanes = 1
            bmi.bmiHeader.biBitCount = 32
            bmi.bmiHeader.biCompression = 0  # BI_RGB

            # Buffer für Pixel-Daten
            buffer_size = self.display_width * self.display_height * 4
            buffer = (ctypes.c_uint8 * buffer_size)()

            # Bitmap-Daten abrufen
            result = self.GetDIBits(hdc_mem, hbitmap, 0, self.display_height,
                                   ctypes.byref(buffer), ctypes.byref(bmi), DIB_RGB_COLORS)

            if result == 0:
                self.logger.error("GetDIBits fehlgeschlagen")
                return None

            # BGRA zu RGB konvertieren
            rgb_data = self._bgra_to_rgb(bytes(buffer))

            # Als JPEG komprimieren
            return self._compress_to_jpeg(rgb_data)

        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen der Bitmap-Daten: {e}")
            return None

    def _bgra_to_rgb(self, bgra_data: bytes) -> bytes:
        """BGRA zu RGB konvertieren"""
        rgb_data = bytearray()
        for i in range(0, len(bgra_data), 4):
            # BGRA zu RGB (Alpha ignorieren)
            b, g, r, _ = bgra_data[i:i+4]
            rgb_data.extend([r, g, b])
        return bytes(rgb_data)

    def _compress_to_jpeg(self, rgb_data: bytes) -> bytes:
        """RGB-Daten zu JPEG komprimieren"""
        try:
            # PIL Image erstellen
            img = Image.frombytes('RGB', (self.display_width, self.display_height), rgb_data)

            # JPEG komprimieren
            from io import BytesIO
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=85, optimize=True)
            return buffer.getvalue()

        except Exception as e:
            self.logger.error(f"Fehler bei JPEG-Komprimierung: {e}")
            return rgb_data

    def get_display_info(self) -> dict:
        """Display-Informationen abrufen"""
        return {
            "width": self.display_width,
            "height": self.display_height,
            "refresh_rate": 60,  # Standardwert
            "color_depth": 32,
            "platform": "windows"
        }
