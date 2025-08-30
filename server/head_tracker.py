#!/usr/bin/env python3
"""
Head Tracker - Verarbeitung von WebXR Head-Tracking-Daten
Konvertiert Quaternion-basierte Kopfbewegungen zu Mouse-Input
"""

import logging
import math
import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import numpy as np

@dataclass
class HeadPose:
    """Head-Pose-Datenstruktur"""
    quaternion: Tuple[float, float, float, float]  # x, y, z, w
    position: Tuple[float, float, float]           # x, y, z
    timestamp: float
    confidence: float = 1.0

@dataclass  
class ProcessedInput:
    """Verarbeitete Input-Daten für Injection"""
    mouse_delta_x: float
    mouse_delta_y: float
    timestamp: float
    source: str = "head_tracking"

class HeadTracker:
    """Head-Tracking-Verarbeitung mit Smoothing und Deadzone"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Konfiguration
        self.sensitivity_x = 1.0
        self.sensitivity_y = 1.0
        self.deadzone_degrees = 0.8
        self.smoothing_factor = 0.15
        self.max_speed_deg_per_sec = 180.0
        self.invert_y = False
        self.invert_x = False
        
        # Tracking-Status
        self.is_active = False
        self.last_pose: Optional[HeadPose] = None
        self.last_yaw = 0.0
        self.last_pitch = 0.0
        self.last_roll = 0.0
        self.smoothed_yaw = 0.0
        self.smoothed_pitch = 0.0
        
        # Performance-Tracking
        self.frames_processed = 0
        self.start_time = time.time()
        
        # Kalibration
        self.calibration_offset_yaw = 0.0
        self.calibration_offset_pitch = 0.0
        self.is_calibrated = False
        
        self.logger.info("HeadTracker initialisiert")
    
    def configure(self, config: Dict):
        """Head-Tracker mit Profil-Konfiguration konfigurieren"""
        head_tracking_config = config.get("head_tracking", {})
        
        self.sensitivity_x = head_tracking_config.get("sensitivity_x", 1.0)
        self.sensitivity_y = head_tracking_config.get("sensitivity_y", 1.0)
        self.deadzone_degrees = head_tracking_config.get("deadzone", 0.8)
        self.smoothing_factor = head_tracking_config.get("smoothing", 0.15)
        self.max_speed_deg_per_sec = head_tracking_config.get("max_speed", 180.0)
        self.invert_y = head_tracking_config.get("invert_y", False)
        self.invert_x = head_tracking_config.get("invert_x", False)
        
        self.logger.info(f"HeadTracker konfiguriert: Sens({self.sensitivity_x}, {self.sensitivity_y}), "
                        f"Deadzone({self.deadzone_degrees}°), Smoothing({self.smoothing_factor})")
    
    def start_tracking(self):
        """Head-Tracking aktivieren"""
        self.is_active = True
        self.frames_processed = 0
        self.start_time = time.time()
        self.logger.info("Head-Tracking gestartet")
    
    def stop_tracking(self):
        """Head-Tracking deaktivieren"""
        self.is_active = False
        self.logger.info("Head-Tracking gestoppt")
    
    def calibrate(self):
        """Aktuelle Kopfposition als Neutral-Position kalibrieren"""
        if self.last_pose:
            # Aktuelle Rotation als Offset speichern
            yaw, pitch, roll = self._quaternion_to_euler(self.last_pose.quaternion)
            self.calibration_offset_yaw = yaw
            self.calibration_offset_pitch = pitch
            self.is_calibrated = True
            
            # Smoothed-Werte zurücksetzen
            self.smoothed_yaw = 0.0
            self.smoothed_pitch = 0.0
            
            self.logger.info(f"Kalibrierung abgeschlossen: Yaw={math.degrees(yaw):.1f}°, "
                           f"Pitch={math.degrees(pitch):.1f}°")
        else:
            self.logger.warning("Keine Head-Pose für Kalibrierung verfügbar")
    
    def process_pose(self, quaternion: List[float], position: List[float], 
                    timestamp: float) -> Optional[ProcessedInput]:
        """Head-Pose verarbeiten und Input generieren"""
        if not self.is_active:
            return None
        
        try:
            # HeadPose erstellen
            pose = HeadPose(
                quaternion=tuple(quaternion),
                position=tuple(position),
                timestamp=timestamp
            )
            
            # Euler-Winkel berechnen
            yaw, pitch, roll = self._quaternion_to_euler(pose.quaternion)
            
            # Kalibrierung anwenden
            if self.is_calibrated:
                yaw -= self.calibration_offset_yaw
                pitch -= self.calibration_offset_pitch
            
            # In Grad umwandeln
            yaw_deg = math.degrees(yaw)
            pitch_deg = math.degrees(pitch)
            
            # Deadzone anwenden
            if abs(yaw_deg) < self.deadzone_degrees and abs(pitch_deg) < self.deadzone_degrees:
                return None
            
            # Smoothing anwenden
            self.smoothed_yaw = self._apply_smoothing(self.smoothed_yaw, yaw_deg)
            self.smoothed_pitch = self._apply_smoothing(self.smoothed_pitch, pitch_deg)
            
            # Delta berechnen (seit letztem Frame)
            if self.last_pose:
                dt = timestamp - self.last_pose.timestamp
                if dt > 0:
                    delta_yaw = self.smoothed_yaw - self.last_yaw
                    delta_pitch = self.smoothed_pitch - self.last_pitch
                    
                    # Geschwindigkeitsbegrenzung
                    max_delta = self.max_speed_deg_per_sec * dt
                    delta_yaw = np.clip(delta_yaw, -max_delta, max_delta)
                    delta_pitch = np.clip(delta_pitch, -max_delta, max_delta)
                    
                    # Sensitivität anwenden
                    mouse_delta_x = delta_yaw * self.sensitivity_x
                    mouse_delta_y = delta_pitch * self.sensitivity_y
                    
                    # Invertierung
                    if self.invert_x:
                        mouse_delta_x = -mouse_delta_x
                    if self.invert_y:
                        mouse_delta_y = -mouse_delta_y
                    
                    # Werte speichern
                    self.last_yaw = self.smoothed_yaw
                    self.last_pitch = self.smoothed_pitch
                    self.last_pose = pose
                    self.frames_processed += 1
                    
                    # ProcessedInput erstellen
                    if abs(mouse_delta_x) > 0.1 or abs(mouse_delta_y) > 0.1:
                        return ProcessedInput(
                            mouse_delta_x=mouse_delta_x,
                            mouse_delta_y=mouse_delta_y,
                            timestamp=timestamp
                        )
            else:
                # Erstes Frame - nur speichern
                self.last_yaw = self.smoothed_yaw
                self.last_pitch = self.smoothed_pitch
                self.last_pose = pose
                self.frames_processed += 1
            
            return None
            
        except Exception as e:
            self.logger.error(f"Fehler bei Pose-Verarbeitung: {e}")
            return None
    
    def _quaternion_to_euler(self, quaternion: Tuple[float, float, float, float]) -> Tuple[float, float, float]:
        """Quaternion zu Euler-Winkeln konvertieren"""
        x, y, z, w = quaternion
        
        # Roll (x-axis rotation)
        sinr_cosp = 2 * (w * x + y * z)
        cosr_cosp = 1 - 2 * (x * x + y * y)
        roll = math.atan2(sinr_cosp, cosr_cosp)
        
        # Pitch (y-axis rotation)
        sinp = 2 * (w * y - z * x)
        if abs(sinp) >= 1:
            pitch = math.copysign(math.pi / 2, sinp)  # Use 90 degrees if out of range
        else:
            pitch = math.asin(sinp)
        
        # Yaw (z-axis rotation)
        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)
        yaw = math.atan2(siny_cosp, cosy_cosp)
        
        return yaw, pitch, roll
    
    def _apply_smoothing(self, current_value: float, target_value: float) -> float:
        """Exponential Smoothing anwenden"""
        alpha = self.smoothing_factor
        return current_value * (1 - alpha) + target_value * alpha
    
    def reset_tracking(self):
        """Tracking-Status zurücksetzen"""
        self.last_pose = None
        self.last_yaw = 0.0
        self.last_pitch = 0.0
        self.last_roll = 0.0
        self.smoothed_yaw = 0.0
        self.smoothed_pitch = 0.0
        self.logger.info("Tracking-Status zurückgesetzt")
    
    def get_stats(self) -> Dict:
        """Head-Tracking-Statistiken"""
        uptime = time.time() - self.start_time
        fps = self.frames_processed / uptime if uptime > 0 else 0
        
        return {
            "is_active": self.is_active,
            "is_calibrated": self.is_calibrated,
            "frames_processed": self.frames_processed,
            "fps": fps,
            "uptime": uptime,
            "current_pose": {
                "yaw": self.smoothed_yaw,
                "pitch": self.smoothed_pitch,
                "smoothed": True
            } if self.is_active else None,
            "configuration": {
                "sensitivity_x": self.sensitivity_x,
                "sensitivity_y": self.sensitivity_y,
                "deadzone_degrees": self.deadzone_degrees,
                "smoothing_factor": self.smoothing_factor,
                "max_speed": self.max_speed_deg_per_sec,
                "invert_x": self.invert_x,
                "invert_y": self.invert_y
            }
        }


# Test-Funktion
if __name__ == "__main__":
    import asyncio
    
    def test_head_tracker():
        logging.basicConfig(level=logging.INFO)
        
        tracker = HeadTracker()
        
        # Test-Konfiguration
        config = {
            "head_tracking": {
                "sensitivity_x": 1.5,
                "sensitivity_y": 1.2,
                "deadzone": 1.0,
                "smoothing": 0.2
            }
        }
        
        tracker.configure(config)
        tracker.start_tracking()
        
        # Simulate head movement
        import random
        for i in range(10):
            # Random quaternion (simplified)
            quat = [
                random.uniform(-0.1, 0.1),  # x
                random.uniform(-0.1, 0.1),  # y
                random.uniform(-0.1, 0.1),  # z
                0.9 + random.uniform(-0.1, 0.1)  # w
            ]
            pos = [0, 0, 0]
            timestamp = time.time()
            
            result = tracker.process_pose(quat, pos, timestamp)
            if result:
                print(f"Mouse delta: X={result.mouse_delta_x:.2f}, Y={result.mouse_delta_y:.2f}")
            
            time.sleep(0.1)
        
        stats = tracker.get_stats()
        print(f"Stats: {stats}")
        
        tracker.stop_tracking()
    
    test_head_tracker()