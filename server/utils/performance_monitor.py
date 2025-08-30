#!/usr/bin/env python3
"""
Performance Monitor - Leistungsüberwachung für VR Gaming Server
"""
import time
import psutil
import logging
from typing import Dict

class PerformanceMonitor:
    """Überwacht System-Performance und Server-Statistiken"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.start_time = time.time()
        self.frame_count = 0
        self.head_tracking_frames = 0
        self.capture_frames = 0
        self.streaming_frames = 0
        
    def start(self):
        """Monitoring starten"""
        self.start_time = time.time()
        self.logger.info("Performance-Monitoring gestartet")
    
    def stop(self):
        """Monitoring stoppen"""
        self.logger.info("Performance-Monitoring gestoppt")
    
    def record_head_tracking_frame(self):
        """Head-Tracking-Frame aufzeichnen"""
        self.head_tracking_frames += 1
    
    def record_capture_frame(self):
        """Capture-Frame aufzeichnen"""
        self.capture_frames += 1
    
    def record_streaming_frame(self):
        """Streaming-Frame aufzeichnen"""
        self.streaming_frames += 1
    
    def get_stats(self) -> Dict:
        """Aktuelle Performance-Statistiken"""
        uptime = time.time() - self.start_time
        
        return {
            "uptime": uptime,
            "total_frames": self.frame_count,
            "head_tracking_fps": self.head_tracking_frames / uptime if uptime > 0 else 0,
            "capture_fps": self.capture_frames / uptime if uptime > 0 else 0,
            "streaming_fps": self.streaming_frames / uptime if uptime > 0 else 0,
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "network_connections": len(psutil.net_connections())
        }
