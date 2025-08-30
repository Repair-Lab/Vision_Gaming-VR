#!/usr/bin/env python3
"""
VR Gaming Server - Head Pose Processor
Verarbeitung von Kopfbewegungsdaten für VR-Input
"""

import logging
from typing import Dict, List, Tuple, Optional
import math
import time
from dataclasses import dataclass

@dataclass
class PoseData:
    """Kopfbewegungsdaten"""
    quaternion: Tuple[float, float, float, float]  # x, y, z, w
    position: Tuple[float, float, float]  # x, y, z
    timestamp: float
    confidence: float = 1.0

@dataclass
class ProcessedInput:
    """Verarbeitete Input-Daten"""
    mouse_x: float = 0.0
    mouse_y: float = 0.0
    mouse_click: bool = False
    keyboard_keys: Optional[List[str]] = None
    scroll_direction: str = ""
    timestamp: float = 0.0

    def __post_init__(self):
        if self.keyboard_keys is None:
            self.keyboard_keys = []

class HeadPoseProcessor:
    """Verarbeitet Kopfbewegungsdaten zu Input-Befehlen"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_initialized = False

        # Konfiguration
        self.sensitivity = 1.0
        self.deadzone = 0.05
        self.screen_width = 1920
        self.screen_height = 1080

        # Kalibrierungsdaten
        self.center_pose: Optional[PoseData] = None
        self.calibration_frames = 0
        self.max_calibration_frames = 30

        # Bewegungsgeschichte für Glättung
        self.pose_history: List[PoseData] = []
        self.history_size = 5

        # Gesten-Erkennung
        self.gesture_detector = GestureDetector()

    def initialize(self) -> bool:
        """Prozessor initialisieren"""
        try:
            self.logger.info("Head Pose Processor initialisiert")
            self.is_initialized = True
            return True
        except Exception as e:
            self.logger.error(f"Fehler bei Initialisierung: {e}")
            return False

    def calibrate(self, pose_data: PoseData) -> bool:
        """Kalibrierung mit zentrierter Pose"""
        if self.calibration_frames < self.max_calibration_frames:
            # Sammle Kalibrierungsdaten
            self.pose_history.append(pose_data)
            if len(self.pose_history) > self.history_size:
                self.pose_history.pop(0)

            self.calibration_frames += 1
            return False  # Noch nicht fertig

        # Berechne Durchschnitt für Center-Pose
        if not self.center_pose:
            avg_quaternion = self._average_quaternions([p.quaternion for p in self.pose_history])
            avg_position = self._average_positions([p.position for p in self.pose_history])

            self.center_pose = PoseData(
                quaternion=avg_quaternion,
                position=avg_position,
                timestamp=time.time()
            )

            self.logger.info("Kalibrierung abgeschlossen")
            return True

        return True

    def process_pose(self, pose_data: PoseData) -> Optional[ProcessedInput]:
        """Pose-Daten verarbeiten und Input generieren"""
        if not self.is_initialized or not self.center_pose:
            return None

        try:
            # Pose zur Historie hinzufügen
            self.pose_history.append(pose_data)
            if len(self.pose_history) > self.history_size:
                self.pose_history.pop(0)

            # Glättung anwenden
            smoothed_pose = self._smooth_pose()

            # Relative Bewegung berechnen
            relative_movement = self._calculate_relative_movement(smoothed_pose)

            # In Mauskoordinaten konvertieren
            mouse_input = self._pose_to_mouse(relative_movement)

            # Gesten erkennen
            gestures = self.gesture_detector.detect_gestures(self.pose_history)

            # Input-Befehle generieren
            processed_input = ProcessedInput(
                mouse_x=mouse_input[0],
                mouse_y=mouse_input[1],
                mouse_click=gestures.get("click", False),
                keyboard_keys=gestures.get("keys", []),
                scroll_direction=gestures.get("scroll", ""),
                timestamp=time.time()
            )

            return processed_input

        except Exception as e:
            self.logger.error(f"Fehler bei Pose-Verarbeitung: {e}")
            return None

    def _smooth_pose(self) -> PoseData:
        """Pose-Daten glätten"""
        if len(self.pose_history) < 2:
            return self.pose_history[-1]

        # Gewichteter Durchschnitt der letzten Posen
        weights = [0.5, 0.3, 0.2]  # Neueste Pose hat höchstes Gewicht
        recent_poses = self.pose_history[-len(weights):]

        avg_quaternion = self._weighted_average_quaternions(
            [p.quaternion for p in recent_poses], weights[:len(recent_poses)]
        )

        avg_position = self._weighted_average_positions(
            [p.position for p in recent_poses], weights[:len(recent_poses)]
        )

        return PoseData(
            quaternion=avg_quaternion,
            position=avg_position,
            timestamp=time.time()
        )

    def _calculate_relative_movement(self, current_pose: PoseData) -> Tuple[float, float, float]:
        """Relative Bewegung zum Center-Pose berechnen"""
        # Quaternion-Differenz berechnen
        q_diff = self._quaternion_difference(self.center_pose.quaternion, current_pose.quaternion)

        # Zu Euler-Winkeln konvertieren
        euler = self._quaternion_to_euler(q_diff)

        # Position-Differenz
        pos_diff = (
            current_pose.position[0] - self.center_pose.position[0],
            current_pose.position[1] - self.center_pose.position[1],
            current_pose.position[2] - self.center_pose.position[2]
        )

        return euler[0], euler[1], pos_diff[2]  # yaw, pitch, z-movement

    def _pose_to_mouse(self, movement: Tuple[float, float, float]) -> Tuple[float, float]:
        """Bewegung in Mauskoordinaten konvertieren"""
        yaw, pitch, _ = movement

        # Deadzone anwenden
        if abs(yaw) < self.deadzone:
            yaw = 0
        if abs(pitch) < self.deadzone:
            pitch = 0

        # Sensitivität anwenden
        mouse_x = yaw * self.sensitivity
        mouse_y = pitch * self.sensitivity

        # Normalisieren auf 0-1
        mouse_x = max(-1.0, min(1.0, mouse_x))
        mouse_y = max(-1.0, min(1.0, mouse_y))

        return mouse_x, mouse_y

    def _quaternion_difference(self, q1: Tuple[float, float, float, float],
                              q2: Tuple[float, float, float, float]) -> Tuple[float, float, float, float]:
        """Quaternion-Differenz berechnen"""
        # q1^-1 * q2
        w1, x1, y1, z1 = q1
        w2, x2, y2, z2 = q2

        w = w1 * w2 + x1 * x2 + y1 * y2 + z1 * z2
        x = w1 * x2 - x1 * w2 - y1 * z2 + z1 * y2
        y = w1 * y2 + x1 * z2 - y1 * w2 - z1 * x2
        z = w1 * z2 - x1 * y2 + y1 * x2 - z1 * w2

        return w, x, y, z

    def _quaternion_to_euler(self, q: Tuple[float, float, float, float]) -> Tuple[float, float, float]:
        """Quaternion zu Euler-Winkeln konvertieren"""
        w, x, y, z = q

        # Yaw (Z-Rotation)
        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)
        yaw = math.atan2(siny_cosp, cosy_cosp)

        # Pitch (Y-Rotation)
        sinp = 2 * (w * y - z * x)
        if abs(sinp) >= 1:
            pitch = math.copysign(math.pi / 2, sinp)
        else:
            pitch = math.asin(sinp)

        # Roll (X-Rotation)
        sinr_cosp = 2 * (w * x + y * z)
        cosr_cosp = 1 - 2 * (x * x + y * y)
        roll = math.atan2(sinr_cosp, cosr_cosp)

        return yaw, pitch, roll

    def _average_quaternions(self, quaternions: List[Tuple[float, float, float, float]]) -> Tuple[float, float, float, float]:
        """Durchschnitt mehrerer Quaternions"""
        if not quaternions:
            return (1, 0, 0, 0)

        avg_w = sum(q[0] for q in quaternions) / len(quaternions)
        avg_x = sum(q[1] for q in quaternions) / len(quaternions)
        avg_y = sum(q[2] for q in quaternions) / len(quaternions)
        avg_z = sum(q[3] for q in quaternions) / len(quaternions)

        # Normalisieren
        length = math.sqrt(avg_w**2 + avg_x**2 + avg_y**2 + avg_z**2)
        if length > 0:
            return avg_w/length, avg_x/length, avg_y/length, avg_z/length
        return (1, 0, 0, 0)

    def _average_positions(self, positions: List[Tuple[float, float, float]]) -> Tuple[float, float, float]:
        """Durchschnitt mehrerer Positionen"""
        if not positions:
            return (0, 0, 0)

        avg_x = sum(p[0] for p in positions) / len(positions)
        avg_y = sum(p[1] for p in positions) / len(positions)
        avg_z = sum(p[2] for p in positions) / len(positions)

        return avg_x, avg_y, avg_z

    def _weighted_average_quaternions(self, quaternions: List[Tuple[float, float, float, float]],
                                     weights: List[float]) -> Tuple[float, float, float, float]:
        """Gewichteter Durchschnitt von Quaternions"""
        if not quaternions or not weights:
            return (1, 0, 0, 0)

        total_weight = sum(weights)
        avg_w = sum(q[0] * w for q, w in zip(quaternions, weights)) / total_weight
        avg_x = sum(q[1] * w for q, w in zip(quaternions, weights)) / total_weight
        avg_y = sum(q[2] * w for q, w in zip(quaternions, weights)) / total_weight
        avg_z = sum(q[3] * w for q, w in zip(quaternions, weights)) / total_weight

        # Normalisieren
        length = math.sqrt(avg_w**2 + avg_x**2 + avg_y**2 + avg_z**2)
        if length > 0:
            return avg_w/length, avg_x/length, avg_y/length, avg_z/length
        return (1, 0, 0, 0)

    def _weighted_average_positions(self, positions: List[Tuple[float, float, float]],
                                   weights: List[float]) -> Tuple[float, float, float]:
        """Gewichteter Durchschnitt von Positionen"""
        if not positions or not weights:
            return (0, 0, 0)

        total_weight = sum(weights)
        avg_x = sum(p[0] * w for p, w in zip(positions, weights)) / total_weight
        avg_y = sum(p[1] * w for p, w in zip(positions, weights)) / total_weight
        avg_z = sum(p[2] * w for p, w in zip(positions, weights)) / total_weight

        return avg_x, avg_y, avg_z

    def set_sensitivity(self, sensitivity: float):
        """Sensitivität setzen"""
        self.sensitivity = max(0.1, min(3.0, sensitivity))

    def set_screen_size(self, width: int, height: int):
        """Bildschirm-Größe setzen"""
        self.screen_width = width
        self.screen_height = height

    def get_stats(self) -> dict:
        """Prozessor-Statistiken"""
        return {
            "initialized": self.is_initialized,
            "calibrated": self.center_pose is not None,
            "sensitivity": self.sensitivity,
            "history_size": len(self.pose_history),
            "screen_size": f"{self.screen_width}x{self.screen_height}"
        }


class GestureDetector:
    """Erkennt Gesten aus Kopfbewegungsdaten"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.nod_threshold = 0.3
        self.shake_threshold = 0.4
        self.gesture_cooldown = 1.0  # Sekunden
        self.last_gesture_time = 0

    def detect_gestures(self, pose_history: List[PoseData]) -> Dict:
        """Gesten aus Pose-Historie erkennen"""
        if len(pose_history) < 5:
            return {}

        current_time = time.time()
        if current_time - self.last_gesture_time < self.gesture_cooldown:
            return {}

        gestures = {}

        # Nick-Geste (Auf/Ab)
        if self._detect_nod(pose_history):
            gestures["click"] = True
            self.last_gesture_time = current_time

        # Schüttel-Geste (Links/Rechts)
        elif self._detect_shake(pose_history):
            gestures["scroll"] = "down"
            self.last_gesture_time = current_time

        return gestures

    def _detect_nod(self, pose_history: List[PoseData]) -> bool:
        """Nick-Geste erkennen"""
        if len(pose_history) < 3:
            return False

        # Pitch-Werte extrahieren
        pitches = []
        for pose in pose_history[-3:]:
            euler = self._quaternion_to_euler_simple(pose.quaternion)
            pitches.append(euler[1])

        # Schnelle Auf/Ab Bewegung
        pitch_change = pitches[-1] - pitches[0]
        return abs(pitch_change) > self.nod_threshold

    def _detect_shake(self, pose_history: List[PoseData]) -> bool:
        """Schüttel-Geste erkennen"""
        if len(pose_history) < 3:
            return False

        # Yaw-Werte extrahieren
        yaws = []
        for pose in pose_history[-3:]:
            euler = self._quaternion_to_euler_simple(pose.quaternion)
            yaws.append(euler[0])

        # Schnelle Links/Rechts Bewegung
        yaw_change = yaws[-1] - yaws[0]
        return abs(yaw_change) > self.shake_threshold

    def _quaternion_to_euler_simple(self, q: Tuple[float, float, float, float]) -> Tuple[float, float, float]:
        """Vereinfachte Quaternion zu Euler Konvertierung"""
        w, x, y, z = q

        # Yaw
        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)
        yaw = math.atan2(siny_cosp, cosy_cosp)

        # Pitch
        sinp = 2 * (w * y - z * x)
        if abs(sinp) >= 1:
            pitch = math.copysign(math.pi / 2, sinp)
        else:
            pitch = math.asin(sinp)

        return yaw, pitch, 0
