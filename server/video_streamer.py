#!/usr/bin/env python3
"""
Video Streamer - WebRTC/MJPEG Video-Streaming für VR
Niedrige Latenz Video-Übertragung an WebXR-Clients
"""

import asyncio
import logging
import threading
import time
import queue
from typing import Optional, Dict, Any
import json
import base64

import cv2
import numpy as np
from fastapi import WebSocket

# WebRTC Support (falls verfügbar)
try:
    from aiortc import VideoStreamTrack, RTCPeerConnection, RTCSessionDescription
    from aiortc.contrib.media import MediaPlayer
    WEBRTC_AVAILABLE = True
except ImportError:
    WEBRTC_AVAILABLE = False

class CustomVideoStreamTrack(VideoStreamTrack):
    """Custom WebRTC Video Stream Track"""
    
    def __init__(self, capture_source):
        super().__init__()
        self.capture_source = capture_source
        self.logger = logging.getLogger(__name__)
    
    async def recv(self):
        """Frame für WebRTC bereitstellen"""
        try:
            frame = self.capture_source.get_latest_frame()
            if frame is not None:
                # Convert BGR to RGB for WebRTC
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Create VideoFrame
                from aiortc import VideoFrame
                av_frame = VideoFrame.from_ndarray(rgb_frame, format="rgb24")
                av_frame.pts = self.time_base * int(time.time() * self.time_base.denominator)
                av_frame.time_base = self.time_base
                
                return av_frame
            else:
                # Dummy frame if no capture available
                dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                from aiortc import VideoFrame
                av_frame = VideoFrame.from_ndarray(dummy_frame, format="rgb24")
                av_frame.pts = self.time_base * int(time.time() * self.time_base.denominator)
                av_frame.time_base = self.time_base
                
                return av_frame
                
        except Exception as e:
            self.logger.error(f"WebRTC frame error: {e}")
            raise


class VideoStreamer:
    """Video-Streaming-Manager mit WebRTC und MJPEG-Fallback"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_streaming = False
        self.capture_source = None
        
        # WebRTC Support
        self.webrtc_enabled = WEBRTC_AVAILABLE
        self.peer_connections: Dict[str, RTCPeerConnection] = {}
        
        # MJPEG Streaming
        self.mjpeg_enabled = True
        self.mjpeg_clients: Dict[str, WebSocket] = {}
        self.mjpeg_thread = None
        
        # Video-Einstellungen
        self.video_width = 1920
        self.video_height = 1080
        self.video_fps = 60
        self.video_quality = 85
        self.video_bitrate = 5000000  # 5 Mbps
        
        # Streaming-Statistiken
        self.frames_sent = 0
        self.bytes_sent = 0
        self.start_time = 0
        
        self.logger.info(f"VideoStreamer initialisiert - WebRTC: {self.webrtc_enabled}")
    
    def configure(self, width: int, height: int, fps: int, quality: int = 85, bitrate: int = 5000000):
        """Video-Einstellungen konfigurieren"""
        self.video_width = width
        self.video_height = height
        self.video_fps = fps
        self.video_quality = quality
        self.video_bitrate = bitrate
        
        self.logger.info(f"Video konfiguriert: {width}x{height}@{fps}fps, Q={quality}, BR={bitrate}")
    
    async def start(self, capture_source) -> bool:
        """Video-Streaming starten"""
        if self.is_streaming:
            self.logger.warning("Streaming bereits aktiv")
            return True
        
        try:
            self.capture_source = capture_source
            self.is_streaming = True
            self.start_time = time.time()
            self.frames_sent = 0
            self.bytes_sent = 0
            
            # MJPEG-Streaming starten
            if self.mjpeg_enabled:
                self.mjpeg_thread = threading.Thread(target=self._mjpeg_streaming_loop, daemon=True)
                self.mjpeg_thread.start()
            
            self.logger.info("Video-Streaming gestartet")
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler beim Streaming-Start: {e}")
            self.is_streaming = False
            return False
    
    async def stop(self):
        """Video-Streaming stoppen"""
        if not self.is_streaming:
            return
        
        self.is_streaming = False
        
        # WebRTC-Verbindungen schließen
        for peer_id, pc in list(self.peer_connections.items()):
            try:
                await pc.close()
            except:
                pass
        self.peer_connections.clear()
        
        # MJPEG-Clients trennen
        for client_id, websocket in list(self.mjpeg_clients.items()):
            try:
                await websocket.close()
            except:
                pass
        self.mjpeg_clients.clear()
        
        self.logger.info("Video-Streaming gestoppt")
    
    def get_stream_url(self) -> str:
        """Stream-URL für Clients"""
        return "/ws/video-stream"
    
    async def handle_webrtc_offer(self, client_id: str, offer_sdp: str) -> Optional[str]:
        """WebRTC-Offer verarbeiten und Answer zurückgeben"""
        if not self.webrtc_enabled:
            self.logger.error("WebRTC nicht verfügbar")
            return None
        
        try:
            # Neue PeerConnection erstellen
            pc = RTCPeerConnection()
            self.peer_connections[client_id] = pc
            
            # Video-Track hinzufügen
            video_track = CustomVideoStreamTrack(self.capture_source)
            pc.addTrack(video_track)
            
            # Offer setzen
            await pc.setRemoteDescription(RTCSessionDescription(sdp=offer_sdp, type="offer"))
            
            # Answer erstellen
            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)
            
            self.logger.info(f"WebRTC-Session für {client_id} erstellt")
            return answer.sdp
            
        except Exception as e:
            self.logger.error(f"WebRTC-Offer-Fehler für {client_id}: {e}")
            if client_id in self.peer_connections:
                del self.peer_connections[client_id]
            return None
    
    async def add_mjpeg_client(self, client_id: str, websocket: WebSocket):
        """MJPEG-Client hinzufügen"""
        self.mjpeg_clients[client_id] = websocket
        self.logger.info(f"MJPEG-Client {client_id} hinzugefügt")
    
    async def remove_mjpeg_client(self, client_id: str):
        """MJPEG-Client entfernen"""
        if client_id in self.mjpeg_clients:
            del self.mjpeg_clients[client_id]
            self.logger.info(f"MJPEG-Client {client_id} entfernt")
    
    def _mjpeg_streaming_loop(self):
        """MJPEG-Streaming-Loop für WebSocket-Clients"""
        frame_interval = 1.0 / self.video_fps
        next_frame_time = time.time()
        
        self.logger.info("MJPEG-Streaming-Loop gestartet")
        
        while self.is_streaming:
            try:
                current_time = time.time()
                
                if current_time < next_frame_time:
                    time.sleep(next_frame_time - current_time)
                
                if not self.mjpeg_clients:
                    time.sleep(0.1)
                    continue
                
                # Frame von Capture-Source holen
                frame = self.capture_source.get_latest_frame() if self.capture_source else None
                
                if frame is not None:
                    # Frame skalieren falls nötig
                    if frame.shape[:2] != (self.video_height, self.video_width):
                        frame = cv2.resize(frame, (self.video_width, self.video_height))
                    
                    # JPEG-Encoding
                    encode_params = [cv2.IMWRITE_JPEG_QUALITY, self.video_quality]
                    success, buffer = cv2.imencode('.jpg', frame, encode_params)
                    
                    if success:
                        # Base64-Encoding für WebSocket
                        jpg_data = base64.b64encode(buffer).decode('utf-8')
                        
                        # An alle MJPEG-Clients senden
                        message = {
                            "type": "video_frame",
                            "data": jpg_data,
                            "timestamp": current_time,
                            "format": "jpeg",
                            "width": self.video_width,
                            "height": self.video_height
                        }
                        
                        # Asynchron an alle Clients senden
                        asyncio.create_task(self._send_to_all_mjpeg_clients(message))
                        
                        # Statistiken aktualisieren
                        self.frames_sent += 1
                        self.bytes_sent += len(buffer)
                
                next_frame_time += frame_interval
                
                # Drift-Korrektur
                if time.time() > next_frame_time + frame_interval:
                    next_frame_time = time.time()
                
            except Exception as e:
                self.logger.error(f"MJPEG-Streaming-Fehler: {e}")
                time.sleep(0.1)
        
        self.logger.info("MJPEG-Streaming-Loop beendet")
    
    async def _send_to_all_mjpeg_clients(self, message: dict):
        """Nachricht an alle MJPEG-Clients senden"""
        if not self.mjpeg_clients:
            return
        
        json_message = json.dumps(message)
        disconnected_clients = []
        
        for client_id, websocket in self.mjpeg_clients.items():
            try:
                await websocket.send_text(json_message)
            except Exception as e:
                self.logger.warning(f"Fehler beim Senden an {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Getrennte Clients entfernen
        for client_id in disconnected_clients:
            await self.remove_mjpeg_client(client_id)
    
    def get_stats(self) -> dict:
        """Streaming-Statistiken"""
        uptime = time.time() - self.start_time if self.start_time > 0 else 0
        avg_fps = self.frames_sent / uptime if uptime > 0 else 0
        avg_bitrate = (self.bytes_sent * 8) / uptime if uptime > 0 else 0
        
        return {
            "is_streaming": self.is_streaming,
            "webrtc_enabled": self.webrtc_enabled,
            "webrtc_clients": len(self.peer_connections),
            "mjpeg_clients": len(self.mjpeg_clients),
            "frames_sent": self.frames_sent,
            "bytes_sent": self.bytes_sent,
            "avg_fps": avg_fps,
            "avg_bitrate_bps": avg_bitrate,
            "uptime": uptime,
            "video_config": {
                "width": self.video_width,
                "height": self.video_height,
                "fps": self.video_fps,
                "quality": self.video_quality,
                "bitrate": self.video_bitrate
            }
        }


# WebSocket-Handler für Video-Streaming
class VideoStreamWebSocketHandler:
    """WebSocket-Handler für Video-Streaming"""
    
    def __init__(self, video_streamer: VideoStreamer):
        self.video_streamer = video_streamer
        self.logger = logging.getLogger(__name__)
    
    async def handle_connection(self, websocket: WebSocket, client_id: str):
        """WebSocket-Verbindung für Video-Streaming verwalten"""
        await websocket.accept()
        self.logger.info(f"Video-WebSocket-Client {client_id} verbunden")
        
        try:
            # Client zu MJPEG-Streaming hinzufügen
            await self.video_streamer.add_mjpeg_client(client_id, websocket)
            
            while True:
                # Auf Client-Nachrichten warten
                data = await websocket.receive_text()
                message = json.loads(data)
                
                await self.handle_client_message(client_id, message, websocket)
                
        except Exception as e:
            self.logger.info(f"Video-WebSocket-Client {client_id} getrennt: {e}")
        finally:
            await self.video_streamer.remove_mjpeg_client(client_id)
    
    async def handle_client_message(self, client_id: str, message: dict, websocket: WebSocket):
        """Client-Nachricht verarbeiten"""
        message_type = message.get("type")
        
        if message_type == "webrtc_offer":
            # WebRTC-Offer verarbeiten
            offer_sdp = message.get("sdp")
            if offer_sdp:
                answer_sdp = await self.video_streamer.handle_webrtc_offer(client_id, offer_sdp)
                if answer_sdp:
                    response = {
                        "type": "webrtc_answer",
                        "sdp": answer_sdp
                    }
                    await websocket.send_text(json.dumps(response))
        
        elif message_type == "quality_change":
            # Video-Qualität ändern
            quality = message.get("quality", 85)
            self.video_streamer.video_quality = max(10, min(100, quality))
            
        elif message_type == "resolution_change":
            # Auflösung ändern
            width = message.get("width", 1920)
            height = message.get("height", 1080)
            self.video_streamer.configure(width, height, self.video_streamer.video_fps)
        
        elif message_type == "ping":
            # Ping-Pong für Latenz-Messung
            response = {
                "type": "pong",
                "timestamp": message.get("timestamp"),
                "server_timestamp": time.time()
            }
            await websocket.send_text(json.dumps(response))


# Test-Funktion
if __name__ == "__main__":
    import asyncio
    from game_capture import GameCapture
    
    async def test_streaming():
        logging.basicConfig(level=logging.INFO)
        
        # Mock Capture Source
        class MockCapture:
            def get_latest_frame(self):
                # Dummy-Frame für Test
                return np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8)
        
        streamer = VideoStreamer()
        mock_capture = MockCapture()
        
        print("Starte Streaming-Test...")
        await streamer.start(mock_capture)
        
        await asyncio.sleep(5)
        
        print("Stoppe Streaming-Test...")
        await streamer.stop()
        
        stats = streamer.get_stats()
        print(f"Statistiken: {stats}")
        
        print("Test abgeschlossen!")
    
    asyncio.run(test_streaming())