#!/usr/bin/env python3
"""
Game Detector - Automatische Spiel-Erkennung
"""
import psutil
import logging
from typing import List, Dict

class GameDetector:
    """Erkennt laufende Spiele und deren Prozesse"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.game_processes = []
        
    def initialize(self):
        """Game-Detector initialisieren"""
        self.logger.info("Game-Detector initialisiert")
    
    def get_running_games(self) -> List[Dict]:
        """Liste der laufenden Spiele zurückgeben"""
        games = []
        
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                if self._is_game_process(proc.info):
                    games.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'exe': proc.info['exe']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return games
    
    def _is_game_process(self, proc_info: Dict) -> bool:
        """Prüfen, ob es sich um einen Spiel-Prozess handelt"""
        game_keywords = [
            'game', 'steam', 'epic', 'origin', 'uplay', 'battlenet',
            'minecraft', 'fortnite', 'valorant', 'league', 'wow',
            'cyberpunk', 'forza', 'flight', 'simulator'
        ]
        
        name = proc_info.get('name', '').lower()
        exe = proc_info.get('exe', '').lower() if proc_info.get('exe') else ''
        
        for keyword in game_keywords:
            if keyword in name or keyword in exe:
                return True
        
        return False
    
    def get_game_window_info(self, game_name: str) -> Dict:
        """Fenster-Informationen für ein bestimmtes Spiel"""
        import platform
        
        if platform.system() == "Windows":
            try:
                import win32gui
                import win32process
                
                def enum_windows_callback(hwnd, windows):
                    if win32gui.IsWindowVisible(hwnd):
                        title = win32gui.GetWindowText(hwnd)
                        if game_name.lower() in title.lower():
                            try:
                                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                                process = psutil.Process(pid)
                                if self._is_game_process({'name': process.name(), 'exe': process.exe()}):
                                    windows.append({
                                        'hwnd': hwnd,
                                        'title': title,
                                        'pid': pid,
                                        'rect': win32gui.GetWindowRect(hwnd)
                                    })
                            except:
                                pass
                    return True
                
                windows = []
                win32gui.EnumWindows(enum_windows_callback, windows)
                
                if windows:
                    window = windows[0]
                    rect = window['rect']
                    return {
                        'title': window['title'],
                        'handle': window['hwnd'],
                        'pid': window['pid'],
                        'position': (rect[0], rect[1]),
                        'size': (rect[2] - rect[0], rect[3] - rect[1])
                    }
            except ImportError:
                self.logger.warning("Win32-API nicht verfügbar für Window-Info")
        
        # Fallback für andere Plattformen oder wenn Win32 nicht verfügbar
        return {
            'title': game_name,
            'handle': None,
            'pid': None,
            'position': (0, 0),
            'size': (1920, 1080)
        }
