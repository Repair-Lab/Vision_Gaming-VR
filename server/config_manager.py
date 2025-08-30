#!/usr/bin/env python3
"""
Config Manager - Konfigurationsverwaltung für VR Gaming Server
Lädt und verwaltet Spiel-Profile und Server-Einstellungen
"""

import json
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

class ConfigManager:
    """Konfigurationsmanager für Server und Spiel-Profile"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Pfade
        self.config_dir = Path("config")
        self.profiles_dir = Path("profiles")
        
        # Konfigurationsdaten
        self.server_config = {}
        self.game_profiles = {}
        self.active_profile_name = "default"
        
        # Verzeichnisse erstellen
        self.config_dir.mkdir(exist_ok=True)
        self.profiles_dir.mkdir(exist_ok=True)
        
        self.logger.info("ConfigManager initialisiert")
    
    def load_config(self):
        """Alle Konfigurationen laden"""
        self._load_server_config()
        self._load_game_profiles()
        self.logger.info("Konfigurationen geladen")
    
    def _load_server_config(self):
        """Server-Konfiguration laden"""
        config_file = self.config_dir / "server_config.yaml"
        
        if not config_file.exists():
            self._create_default_server_config()
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                self.server_config = yaml.safe_load(f) or {}
                self.logger.info("Server-Konfiguration geladen")
        except Exception as e:
            self.logger.error(f"Fehler beim Laden der Server-Konfiguration: {e}")
            self.server_config = self._get_default_server_config()
    
    def _create_default_server_config(self):
        """Standard-Server-Konfiguration erstellen"""
        default_config = self._get_default_server_config()
        config_file = self.config_dir / "server_config.yaml"
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(default_config, f, default_flow_style=False, indent=2)
            self.logger.info("Standard-Server-Konfiguration erstellt")
        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen der Standard-Konfiguration: {e}")
    
    def _get_default_server_config(self) -> Dict:
        """Standard-Server-Konfiguration"""
        return {
            "server": {
                "host": "0.0.0.0",
                "port": 8080,
                "debug": False
            },
            "video": {
                "width": 1920,
                "height": 1080,
                "fps": 60,
                "quality": 85
            },
            "capture": {
                "method": "auto",
                "monitor": 0,
                "target_window": None
            },
            "input": {
                "mouse_sensitivity": 1.0,
                "acceleration_curve": 1.0,
                "min_mouse_delta": 0.5
            },
            "head_tracking": {
                "sensitivity_x": 1.0,
                "sensitivity_y": 1.0,
                "deadzone": 0.8,
                "smoothing": 0.15,
                "max_speed": 180.0,
                "invert_x": False,
                "invert_y": False
            },
            "streaming": {
                "enable_webrtc": False,
                "mjpeg_quality": 85,
                "adaptive_quality": True
            },
            "logging": {
                "level": "INFO",
                "file": "logs/server.log"
            }
        }
    
    def _load_game_profiles(self):
        """Alle Spiel-Profile laden"""
        # Zuerst Standard-Profile erstellen
        self._create_default_profiles()
        
        # Dann alle Profile laden
        for profile_file in self.profiles_dir.glob("*.json"):
            try:
                with open(profile_file, 'r', encoding='utf-8') as f:
                    profile_data = json.load(f)
                    profile_name = profile_data.get("name", profile_file.stem)
                    self.game_profiles[profile_name] = profile_data
                    
            except Exception as e:
                self.logger.error(f"Fehler beim Laden von Profil {profile_file}: {e}")
        
        self.logger.info(f"{len(self.game_profiles)} Spiel-Profile geladen")
    
    def _create_default_profiles(self):
        """Standard-Spiel-Profile erstellen"""
        profiles = {
            "default": {
                "name": "Default",
                "description": "Standard-Profil für alle Spiele",
                "process_patterns": ["*"],
                "head_tracking": {
                    "sensitivity_x": 1.0,
                    "sensitivity_y": 1.0,
                    "deadzone": 0.8,
                    "smoothing": 0.15,
                    "max_speed": 180.0,
                    "invert_x": False,
                    "invert_y": False
                },
                "input": {
                    "mouse_sensitivity": 1.0,
                    "acceleration_curve": 1.0,
                    "min_mouse_delta": 0.5
                },
                "gestures": {}
            },
            "cyberpunk2077": {
                "name": "Cyberpunk 2077",
                "description": "Optimiert für Cyberpunk 2077",
                "process_patterns": ["Cyberpunk2077.exe"],
                "head_tracking": {
                    "sensitivity_x": 1.2,
                    "sensitivity_y": 1.0,
                    "deadzone": 0.8,
                    "smoothing": 0.15,
                    "max_speed": 200.0,
                    "invert_x": False,
                    "invert_y": False
                },
                "input": {
                    "mouse_sensitivity": 1.2,
                    "acceleration_curve": 1.3,
                    "min_mouse_delta": 0.3
                },
                "gestures": {
                    "left_grab": "F",
                    "right_pinch": "LMB",
                    "right_fist": "R",
                    "left_open": "TAB"
                }
            },
            "minecraft": {
                "name": "Minecraft",
                "description": "Optimiert für Minecraft",
                "process_patterns": ["javaw.exe", "minecraft.exe"],
                "head_tracking": {
                    "sensitivity_x": 0.8,
                    "sensitivity_y": 0.8,
                    "deadzone": 1.0,
                    "smoothing": 0.2,
                    "max_speed": 120.0,
                    "invert_x": False,
                    "invert_y": False
                },
                "input": {
                    "mouse_sensitivity": 0.8,
                    "acceleration_curve": 1.0,
                    "min_mouse_delta": 0.4
                },
                "gestures": {
                    "left_grab": "LMB",
                    "right_pinch": "RMB",
                    "left_fist": "Q",
                    "right_open": "E"
                }
            },
            "forza": {
                "name": "Forza Horizon",
                "description": "Racing-optimiert für Forza",
                "process_patterns": ["ForzaHorizon5.exe", "ForzaHorizon4.exe"],
                "head_tracking": {
                    "sensitivity_x": 0.6,
                    "sensitivity_y": 0.4,
                    "deadzone": 1.5,
                    "smoothing": 0.3,
                    "max_speed": 90.0,
                    "invert_x": False,
                    "invert_y": False
                },
                "input": {
                    "mouse_sensitivity": 0.6,
                    "acceleration_curve": 0.8,
                    "min_mouse_delta": 0.8
                },
                "gestures": {}
            },
            "msfs": {
                "name": "Flight Simulator",
                "description": "Flight Sim optimiert",
                "process_patterns": ["FlightSimulator.exe"],
                "head_tracking": {
                    "sensitivity_x": 0.5,
                    "sensitivity_y": 0.5,
                    "deadzone": 0.5,
                    "smoothing": 0.1,
                    "max_speed": 60.0,
                    "invert_x": False,
                    "invert_y": False
                },
                "input": {
                    "mouse_sensitivity": 0.5,
                    "acceleration_curve": 0.9,
                    "min_mouse_delta": 0.2
                },
                "gestures": {}
            }
        }
        
        for profile_name, profile_data in profiles.items():
            profile_file = self.profiles_dir / f"{profile_name}.json"
            
            if not profile_file.exists():
                try:
                    with open(profile_file, 'w', encoding='utf-8') as f:
                        json.dump(profile_data, f, indent=2, ensure_ascii=False)
                    self.logger.info(f"Standard-Profil erstellt: {profile_name}")
                except Exception as e:
                    self.logger.error(f"Fehler beim Erstellen von Profil {profile_name}: {e}")
    
    def get_server_config(self) -> Dict:
        """Server-Konfiguration abrufen"""
        return self.server_config.copy()
    
    def update_server_config(self, updates: Dict):
        """Server-Konfiguration aktualisieren"""
        def deep_update(target, source):
            for key, value in source.items():
                if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                    deep_update(target[key], value)
                else:
                    target[key] = value
        
        deep_update(self.server_config, updates)
        
        # Speichern
        config_file = self.config_dir / "server_config.yaml"
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.server_config, f, default_flow_style=False, indent=2)
            self.logger.info("Server-Konfiguration aktualisiert")
        except Exception as e:
            self.logger.error(f"Fehler beim Speichern der Server-Konfiguration: {e}")
    
    def get_game_profiles(self) -> Dict[str, Dict]:
        """Alle Spiel-Profile abrufen"""
        return self.game_profiles.copy()
    
    def get_profile(self, profile_name: str) -> Optional[Dict]:
        """Spezifisches Spiel-Profil abrufen"""
        return self.game_profiles.get(profile_name)
    
    def get_active_profile(self) -> Dict:
        """Aktives Spiel-Profil abrufen"""
        return self.game_profiles.get(self.active_profile_name, self.game_profiles.get("default", {}))
    
    def get_active_profile_name(self) -> str:
        """Name des aktiven Profils abrufen"""
        return self.active_profile_name
    
    def set_active_profile(self, profile_name: str) -> bool:
        """Aktives Spiel-Profil setzen"""
        if profile_name in self.game_profiles:
            self.active_profile_name = profile_name
            self.logger.info(f"Aktives Profil geändert zu: {profile_name}")
            return True
        else:
            self.logger.warning(f"Profil nicht gefunden: {profile_name}")
            return False
    
    def find_profile_for_game(self, game_name: str) -> Optional[str]:
        """Profil für Spiel finden basierend auf Prozess-Pattern"""
        game_name_lower = game_name.lower()
        
        for profile_name, profile_data in self.game_profiles.items():
            if profile_name == "default":
                continue
                
            patterns = profile_data.get("process_patterns", [])
            for pattern in patterns:
                if pattern.lower() in game_name_lower or game_name_lower in pattern.lower():
                    return profile_name
        
        return None
    
    def create_profile(self, profile_name: str, profile_data: Dict) -> bool:
        """Neues Spiel-Profil erstellen"""
        profile_file = self.profiles_dir / f"{profile_name}.json"
        
        try:
            with open(profile_file, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=2, ensure_ascii=False)
            
            self.game_profiles[profile_name] = profile_data
            self.logger.info(f"Neues Profil erstellt: {profile_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen von Profil {profile_name}: {e}")
            return False
    
    def update_profile(self, profile_name: str, profile_data: Dict) -> bool:
        """Bestehendes Spiel-Profil aktualisieren"""
        if profile_name not in self.game_profiles:
            return False
        
        profile_file = self.profiles_dir / f"{profile_name}.json"
        
        try:
            with open(profile_file, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=2, ensure_ascii=False)
            
            self.game_profiles[profile_name] = profile_data
            self.logger.info(f"Profil aktualisiert: {profile_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler beim Aktualisieren von Profil {profile_name}: {e}")
            return False
    
    def delete_profile(self, profile_name: str) -> bool:
        """Spiel-Profil löschen"""
        if profile_name == "default":
            self.logger.warning("Standard-Profil kann nicht gelöscht werden")
            return False
        
        if profile_name not in self.game_profiles:
            return False
        
        profile_file = self.profiles_dir / f"{profile_name}.json"
        
        try:
            if profile_file.exists():
                profile_file.unlink()
            
            del self.game_profiles[profile_name]
            
            if self.active_profile_name == profile_name:
                self.active_profile_name = "default"
            
            self.logger.info(f"Profil gelöscht: {profile_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler beim Löschen von Profil {profile_name}: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Konfigurationsstatistiken"""
        return {
            "server_config_loaded": bool(self.server_config),
            "game_profiles_count": len(self.game_profiles),
            "active_profile": self.active_profile_name,
            "available_profiles": list(self.game_profiles.keys())
        }


# Test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    config_mgr = ConfigManager()
    config_mgr.load_config()
    
    print("Server Config:", config_mgr.get_server_config())
    print("Game Profiles:", list(config_mgr.get_game_profiles().keys()))
    print("Active Profile:", config_mgr.get_active_profile_name())
    
    stats = config_mgr.get_stats()
    print("Stats:", stats)