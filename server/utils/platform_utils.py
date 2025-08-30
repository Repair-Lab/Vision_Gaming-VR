#!/usr/bin/env python3
"""
Platform Utils - Cross-platform Hilfsfunktionen
"""
import platform
import os
import subprocess
import logging
from typing import Dict, List, Optional, Tuple

class PlatformUtils:
    """Cross-platform Hilfsfunktionen für System-Operationen"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.system = platform.system().lower()
        self.is_windows = self.system == "windows"
        self.is_macos = self.system == "darwin"
        self.is_linux = self.system == "linux"
        
    def get_system_info(self) -> Dict:
        """System-Informationen abrufen"""
        return {
            "system": self.system,
            "platform": platform.platform(),
            "architecture": platform.architecture(),
            "python_version": platform.python_version(),
            "cpu_count": os.cpu_count()
        }
    
    def get_display_info(self) -> List[Dict]:
        """Display-Informationen abrufen"""
        displays = []
        
        if self.is_windows:
            displays = self._get_windows_displays()
        elif self.is_macos:
            displays = self._get_macos_displays()
        elif self.is_linux:
            displays = self._get_linux_displays()
        
        return displays
    
    def _get_windows_displays(self) -> List[Dict]:
        """Windows Display-Informationen"""
        try:
            import win32api
            import win32con
            
            displays = []
            i = 0
            while True:
                try:
                    device = win32api.EnumDisplayDevices(None, i, 0)
                    if not device.DeviceName:
                        break
                    
                    # Get display settings
                    settings = win32api.EnumDisplaySettings(device.DeviceName, win32con.ENUM_CURRENT_SETTINGS)
                    
                    displays.append({
                        "name": device.DeviceName,
                        "width": settings.PelsWidth,
                        "height": settings.PelsHeight,
                        "frequency": settings.DisplayFrequency,
                        "bits_per_pixel": settings.BitsPerPel
                    })
                    
                    i += 1
                except:
                    break
            
            return displays
        except ImportError:
            self.logger.warning("Win32-API nicht verfügbar für Display-Info")
            return []
    
    def _get_macos_displays(self) -> List[Dict]:
        """macOS Display-Informationen"""
        try:
            result = subprocess.run(['system_profiler', 'SPDisplaysDataType'], 
                                  capture_output=True, text=True, timeout=10)
            
            displays = []
            lines = result.stdout.split('\n')
            current_display = None
            
            for line in lines:
                line = line.strip()
                if 'Display Type:' in line or 'Resolution:' in line:
                    if current_display:
                        displays.append(current_display)
                    current_display = {}
                
                if 'Resolution:' in line:
                    # Parse resolution like "1920 x 1080 (16:9)"
                    res_part = line.split(':')[1].strip()
                    if 'x' in res_part:
                        width, height = res_part.split('x')[0].strip().split()
                        current_display.update({
                            "width": int(width),
                            "height": int(height)
                        })
            
            if current_display:
                displays.append(current_display)
            
            return displays
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen macOS Display-Info: {e}")
            return []
    
    def _get_linux_displays(self) -> List[Dict]:
        """Linux Display-Informationen"""
        try:
            result = subprocess.run(['xrandr'], capture_output=True, text=True, timeout=10)
            
            displays = []
            lines = result.stdout.split('\n')
            
            for line in lines:
                if ' connected ' in line and not line.startswith(' '):
                    parts = line.split()
                    if len(parts) >= 3:
                        name = parts[0]
                        resolution = parts[2] if len(parts) > 2 else ""
                        
                        if 'x' in resolution:
                            width, height = resolution.split('x')[0].split('+')[0].split()
                            displays.append({
                                "name": name,
                                "width": int(width),
                                "height": int(height)
                            })
            
            return displays
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen Linux Display-Info: {e}")
            return []
    
    def get_process_list(self) -> List[Dict]:
        """Liste aller laufenden Prozesse"""
        try:
            import psutil
            
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "exe": proc.info['exe'],
                        "cpu_percent": proc.info['cpu_percent'] or 0,
                        "memory_percent": proc.info['memory_percent'] or 0
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return processes
        except ImportError:
            self.logger.warning("psutil nicht verfügbar für Process-Info")
            return []
    
    def get_system_resources(self) -> Dict:
        """System-Ressourcen-Informationen"""
        try:
            import psutil
            
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory": {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "percent": psutil.virtual_memory().percent
                },
                "disk": {
                    "total": psutil.disk_usage('/').total,
                    "free": psutil.disk_usage('/').free,
                    "percent": psutil.disk_usage('/').percent
                },
                "network": {
                    "bytes_sent": psutil.net_io_counters().bytes_sent,
                    "bytes_recv": psutil.net_io_counters().bytes_recv
                }
            }
        except ImportError:
            self.logger.warning("psutil nicht verfügbar für System-Ressourcen")
            return {}
    
    def is_process_running(self, process_name: str) -> bool:
        """Prüfen ob ein Prozess läuft"""
        try:
            import psutil
            
            for proc in psutil.process_iter(['name']):
                try:
                    if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return False
        except ImportError:
            return False
    
    def get_network_interfaces(self) -> List[Dict]:
        """Netzwerk-Interface-Informationen"""
        try:
            import psutil
            
            interfaces = []
            for name, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family.name == 'AF_INET':  # IPv4
                        interfaces.append({
                            "name": name,
                            "address": addr.address,
                            "netmask": addr.netmask,
                            "broadcast": addr.broadcast
                        })
                        break
            
            return interfaces
        except ImportError:
            self.logger.warning("psutil nicht verfügbar für Network-Info")
            return []


# Test-Funktion
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    utils = PlatformUtils()
    
    print("System Info:", utils.get_system_info())
    print("Displays:", utils.get_display_info())
    print("System Resources:", utils.get_system_resources())
    print("Network Interfaces:", utils.get_network_interfaces())
