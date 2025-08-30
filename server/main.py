#!/usr/bin/env python3
"""
VR Gaming Server - Main FastAPI Server
Ultra-low latency VR game streaming with head tracking
"""

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Lokale Imports
from game_capture import GameCapture
from video_streamer import VideoStreamer  
from head_tracker import HeadTracker
from input_injector import InputInjector
from config_manager import ConfigManager
from game_detector import GameDetector
from utils.performance_monitor import PerformanceMonitor
from utils.logger import setup_logging

class VRGameServer:
    """Haupt VR Gaming Server"""
    
    def __init__(self):
        # Server Setup
        self.app = FastAPI(
            title="VR Gaming Server",
            description="Ultra-low latency VR game streaming",
            version="1.0.0"
        )
        
        # Setup CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # In Produktion einschränken
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Komponenten
        self.config = ConfigManager()
        self.game_capture = GameCapture()
        self.video_streamer = VideoStreamer()
        self.head_tracker = HeadTracker()
        self.input_injector = InputInjector()
        self.game_detector = GameDetector()
        self.performance_monitor = PerformanceMonitor()
        
        # Status
        self.is_running = False
        self.is_streaming = False
        self.connected_clients: Dict[str, WebSocket] = {}
        self.current_game = None
        
        # Setup Templates und Static Files
        self.templates = Jinja2Templates(directory="web/templates")
        
        # Routes registrieren
        self.setup_routes()
        
        # Logging
        setup_logging()
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("VR Gaming Server initialisiert")
    
    def setup_routes(self):
        """Setup FastAPI Routes"""
        
        # Static Files
        self.app.mount("/static", StaticFiles(directory="web/static"), name="static")
        
        # Haupt-Routen
        @self.app.get("/", response_class=HTMLResponse)
        async def index(request: Request):
            """Startseite"""
            return self.templates.TemplateResponse("index.html", {
                "request": request,
                "server_status": self.get_server_status()
            })
        
        @self.app.get("/sensor-check", response_class=HTMLResponse)
        async def sensor_check(request: Request):
            """Sensor-Test-Seite"""
            return self.templates.TemplateResponse("sensor-check.html", {
                "request": request
            })
        
        @self.app.get("/server-control", response_class=HTMLResponse)
        async def server_control(request: Request):
            """Server-Steuerung"""
            return self.templates.TemplateResponse("server-control.html", {
                "request": request,
                "server_status": self.get_server_status(),
                "performance_stats": self.performance_monitor.get_stats()
            })
        
        @self.app.get("/game-setup", response_class=HTMLResponse)
        async def game_setup(request: Request):
            """Spiel-Setup-Seite"""
            return self.templates.TemplateResponse("game-setup.html", {
                "request": request,
                "detected_games": self.game_detector.get_running_games(),
                "profiles": self.config.get_game_profiles()
            })
        
        @self.app.get("/settings", response_class=HTMLResponse)
        async def settings(request: Request):
            """Einstellungen-Seite"""
            return self.templates.TemplateResponse("settings.html", {
                "request": request,
                "current_config": self.config.get_server_config()
            })
        
        # API Endpoints
        @self.app.get("/api/status")
        async def get_status():
            """Server-Status abfragen"""
            return JSONResponse(self.get_server_status())
        
        @self.app.post("/api/start-streaming")
        async def start_streaming():
            """Video-Streaming starten"""
            try:
                success = await self.start_video_streaming()
                return JSONResponse({
                    "success": success,
                    "message": "Streaming gestartet" if success else "Streaming-Start fehlgeschlagen"
                })
            except Exception as e:
                self.logger.error(f"Fehler beim Streaming-Start: {e}")
                return JSONResponse({
                    "success": False,
                    "message": f"Fehler: {str(e)}"
                }, status_code=500)
        
        @self.app.post("/api/stop-streaming")
        async def stop_streaming():
            """Video-Streaming stoppen"""
            try:
                await self.stop_video_streaming()
                return JSONResponse({
                    "success": True,
                    "message": "Streaming gestoppt"
                })
            except Exception as e:
                self.logger.error(f"Fehler beim Streaming-Stopp: {e}")
                return JSONResponse({
                    "success": False,
                    "message": f"Fehler: {str(e)}"
                }, status_code=500)
        
        @self.app.get("/api/games")
        async def get_detected_games():
            """Erkannte Spiele auflisten"""
            games = self.game_detector.get_running_games()
            return JSONResponse(games)
        
        @self.app.get("/api/profiles")
        async def get_game_profiles():
            """Verfügbare Game-Profile"""
            profiles = self.config.get_game_profiles()
            return JSONResponse(profiles)
        
        @self.app.post("/api/profile/{profile_name}")
        async def set_game_profile(profile_name: str):
            """Game-Profil setzen"""
            try:
                success = self.config.set_active_profile(profile_name)
                if success:
                    # Input-Mapping neu konfigurieren
                    profile_config = self.config.get_active_profile()
                    self.input_injector.configure(profile_config)
                    
                return JSONResponse({
                    "success": success,
                    "message": f"Profil '{profile_name}' aktiviert" if success else "Profil nicht gefunden"
                })
            except Exception as e:
                return JSONResponse({
                    "success": False,
                    "message": f"Fehler: {str(e)}"
                }, status_code=500)
        
        @self.app.get("/api/performance")
        async def get_performance_stats():
            """Performance-Statistiken"""
            return JSONResponse(self.performance_monitor.get_stats())
        
        # WebSocket für Real-time Kommunikation
        @self.app.websocket("/ws/{client_id}")
        async def websocket_endpoint(websocket: WebSocket, client_id: str):
            await self.handle_websocket_connection(websocket, client_id)
        
        # WebSocket für Head-Tracking
        @self.app.websocket("/ws/head-tracking/{client_id}")
        async def head_tracking_websocket(websocket: WebSocket, client_id: str):
            await self.handle_head_tracking_websocket(websocket, client_id)
    
    async def handle_websocket_connection(self, websocket: WebSocket, client_id: str):
        """WebSocket-Verbindung verwalten"""
        await websocket.accept()
        self.connected_clients[client_id] = websocket
        
        self.logger.info(f"Client {client_id} verbunden")
        
        try:
            while True:
                # Warte auf Nachrichten vom Client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Verarbeite verschiedene Message-Types
                await self.handle_client_message(client_id, message)
                
        except WebSocketDisconnect:
            self.logger.info(f"Client {client_id} getrennt")
        except Exception as e:
            self.logger.error(f"WebSocket-Fehler für {client_id}: {e}")
        finally:
            if client_id in self.connected_clients:
                del self.connected_clients[client_id]
    
    async def handle_head_tracking_websocket(self, websocket: WebSocket, client_id: str):
        """Head-Tracking WebSocket verwalten"""
        await websocket.accept()
        
        self.logger.info(f"Head-Tracking für {client_id} verbunden")
        
        try:
            while True:
                # Empfange Head-Tracking-Daten
                data = await websocket.receive_text()
                tracking_data = json.loads(data)
                
                # Verarbeite Kopfbewegungsdaten
                await self.process_head_tracking_data(client_id, tracking_data)
                
        except WebSocketDisconnect:
            self.logger.info(f"Head-Tracking für {client_id} getrennt")
        except Exception as e:
            self.logger.error(f"Head-Tracking-Fehler für {client_id}: {e}")
    
    async def handle_client_message(self, client_id: str, message: dict):
        """Client-Nachrichten verarbeiten"""
        message_type = message.get("type")
        
        if message_type == "ping":
            # Pong zurücksenden für Latenz-Messung
            await self.send_to_client(client_id, {
                "type": "pong",
                "timestamp": message.get("timestamp"),
                "server_timestamp": time.time()
            })
        
        elif message_type == "request_stream":
            # Video-Stream anfordern
            await self.start_video_streaming()
        
        elif message_type == "stop_stream":
            # Video-Stream stoppen
            await self.stop_video_streaming()
        
        elif message_type == "configure":
            # Konfiguration ändern
            config_data = message.get("config", {})
            self.config.update_config(config_data)
    
    async def process_head_tracking_data(self, client_id: str, tracking_data: dict):
        """Kopfbewegungsdaten verarbeiten"""
        try:
            # Extrahiere Pose-Daten
            pose = tracking_data.get("pose", {})
            quaternion = pose.get("quaternion", [0, 0, 0, 1])  # x, y, z, w
            position = pose.get("position", [0, 0, 0])  # x, y, z
            timestamp = tracking_data.get("timestamp", time.time())
            
            # An Head-Tracker weiterleiten
            processed_input = self.head_tracker.process_pose(
                quaternion=quaternion,
                position=position,
                timestamp=timestamp
            )
            
            # Input-Injection wenn verarbeitet
            if processed_input:
                await self.input_injector.inject_input(processed_input)
            
            # Performance-Monitoring
            self.performance_monitor.record_head_tracking_frame()
            
        except Exception as e:
            self.logger.error(f"Fehler bei Head-Tracking-Verarbeitung: {e}")
    
    async def send_to_client(self, client_id: str, message: dict):
        """Nachricht an Client senden"""
        if client_id in self.connected_clients:
            try:
                await self.connected_clients[client_id].send_text(json.dumps(message))
            except Exception as e:
                self.logger.error(f"Fehler beim Senden an {client_id}: {e}")
    
    async def broadcast_to_all_clients(self, message: dict):
        """Nachricht an alle verbundenen Clients senden"""
        for client_id in list(self.connected_clients.keys()):
            await self.send_to_client(client_id, message)
    
    async def start_video_streaming(self) -> bool:
        """Video-Streaming starten"""
        if self.is_streaming:
            self.logger.warning("Streaming bereits aktiv")
            return True
        
        try:
            # Game Capture starten
            capture_success = await self.game_capture.start()
            if not capture_success:
                self.logger.error("Game Capture konnte nicht gestartet werden")
                return False
            
            # Video Streamer starten
            stream_success = await self.video_streamer.start(self.game_capture)
            if not stream_success:
                self.logger.error("Video Streamer konnte nicht gestartet werden")
                await self.game_capture.stop()
                return False
            
            self.is_streaming = True
            self.logger.info("Video-Streaming gestartet")
            
            # Benachrichtige alle Clients
            await self.broadcast_to_all_clients({
                "type": "streaming_started",
                "stream_url": self.video_streamer.get_stream_url()
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler beim Streaming-Start: {e}")
            return False
    
    async def stop_video_streaming(self):
        """Video-Streaming stoppen"""
        if not self.is_streaming:
            return
        
        try:
            await self.video_streamer.stop()
            await self.game_capture.stop()
            
            self.is_streaming = False
            self.logger.info("Video-Streaming gestoppt")
            
            # Benachrichtige alle Clients
            await self.broadcast_to_all_clients({
                "type": "streaming_stopped"
            })
            
        except Exception as e:
            self.logger.error(f"Fehler beim Streaming-Stopp: {e}")
    
    def get_server_status(self) -> dict:
        """Aktueller Server-Status"""
        return {
            "is_running": self.is_running,
            "is_streaming": self.is_streaming,
            "connected_clients": len(self.connected_clients),
            "current_game": self.current_game,
            "performance": self.performance_monitor.get_stats(),
            "detected_games": self.game_detector.get_running_games(),
            "active_profile": self.config.get_active_profile_name()
        }
    
    async def start_background_tasks(self):
        """Hintergrund-Tasks starten"""
        # Game Detection Task
        asyncio.create_task(self.game_detection_loop())
        
        # Performance Monitoring Task
        asyncio.create_task(self.performance_monitoring_loop())
        
        self.logger.info("Hintergrund-Tasks gestartet")
    
    async def game_detection_loop(self):
        """Kontinuierliche Spiel-Erkennung"""
        while self.is_running:
            try:
                detected_games = self.game_detector.get_running_games()
                
                # Auto-Switch zu erkanntem Spiel-Profil
                for game in detected_games:
                    profile_name = self.config.find_profile_for_game(game["name"])
                    if profile_name and profile_name != self.config.get_active_profile_name():
                        self.config.set_active_profile(profile_name)
                        profile_config = self.config.get_active_profile()
                        self.input_injector.configure(profile_config)
                        
                        self.current_game = game["name"]
                        self.logger.info(f"Auto-switched zu Profil: {profile_name}")
                        
                        # Benachrichtige Clients
                        await self.broadcast_to_all_clients({
                            "type": "game_detected",
                            "game": game,
                            "profile": profile_name
                        })
                        break
                
                await asyncio.sleep(5)  # Alle 5 Sekunden prüfen
                
            except Exception as e:
                self.logger.error(f"Fehler bei Game Detection: {e}")
                await asyncio.sleep(10)
    
    async def performance_monitoring_loop(self):
        """Performance-Monitoring Loop"""
        while self.is_running:
            try:
                # Performance-Stats aktualisieren
                stats = self.performance_monitor.get_stats()
                
                # An Clients senden
                await self.broadcast_to_all_clients({
                    "type": "performance_update",
                    "stats": stats
                })
                
                await asyncio.sleep(1)  # Jede Sekunde
                
            except Exception as e:
                self.logger.error(f"Fehler bei Performance-Monitoring: {e}")
                await asyncio.sleep(5)
    
    async def start_server(self):
        """Server starten"""
        self.is_running = True
        self.logger.info("VR Gaming Server wird gestartet...")
        
        # Initialisierung der Komponenten
        await self.initialize_components()
        
        # Hintergrund-Tasks starten
        await self.start_background_tasks()
        
        self.logger.info("VR Gaming Server erfolgreich gestartet!")
    
    async def initialize_components(self):
        """Alle Komponenten initialisieren"""
        try:
            # Config laden
            self.config.load_config()
            
            # Game Detector initialisieren
            self.game_detector.initialize()
            
            # Head Tracker konfigurieren
            profile_config = self.config.get_active_profile()
            self.head_tracker.configure(profile_config)
            self.input_injector.configure(profile_config)
            
            # Performance Monitor starten
            self.performance_monitor.start()
            
            self.logger.info("Alle Komponenten erfolgreich initialisiert")
            
        except Exception as e:
            self.logger.error(f"Fehler bei Komponenten-Initialisierung: {e}")
            raise
    
    async def shutdown(self):
        """Server herunterfahren"""
        self.is_running = False
        self.logger.info("VR Gaming Server wird heruntergefahren...")
        
        try:
            # Streaming stoppen
            if self.is_streaming:
                await self.stop_video_streaming()
            
            # Alle WebSocket-Verbindungen schließen
            for client_id, websocket in self.connected_clients.items():
                try:
                    await websocket.close()
                except:
                    pass
            
            # Komponenten herunterfahren
            self.performance_monitor.stop()
            
            self.logger.info("VR Gaming Server heruntergefahren")
            
        except Exception as e:
            self.logger.error(f"Fehler beim Herunterfahren: {e}")


# Server-Instanz
vr_server = VRGameServer()

# FastAPI-App für uvicorn
app = vr_server.app

# Startup Event
@app.on_event("startup")
async def startup_event():
    await vr_server.start_server()

# Shutdown Event
@app.on_event("shutdown") 
async def shutdown_event():
    await vr_server.shutdown()


if __name__ == "__main__":
    # Development Server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )