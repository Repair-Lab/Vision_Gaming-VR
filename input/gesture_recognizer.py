#!/usr/bin/env python3
"""
VR Gaming Server - Gesture Recognizer
Erkennung von Gesten für VR-Input
"""

import logging
from typing import Dict, List, Tuple, Optional, Callable
import time
import math
from dataclasses import dataclass
from enum import Enum

class GestureType(Enum):
    """Unterstützte Geste-Typen"""
    NOD = "nod"
    SHAKE = "shake"
    TILT_LEFT = "tilt_left"
    TILT_RIGHT = "tilt_right"
    FORWARD = "forward"
    BACKWARD = "backward"
    CIRCLE_CLOCKWISE = "circle_clockwise"
    CIRCLE_COUNTERCLOCKWISE = "circle_counterclockwise"

@dataclass
class GestureEvent:
    """Geste-Ereignis"""
    gesture_type: GestureType
    confidence: float
    timestamp: float
    duration: float = 0.0
    metadata: Optional[Dict] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class GestureRecognizer:
    """Erkennt Gesten aus Bewegungsdaten"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_initialized = False

        # Konfiguration
        self.sensitivity = 1.0
        self.min_confidence = 0.7
        self.cooldown_time = 0.5  # Sekunden zwischen Gesten

        # Bewegungshistorie
        self.pose_history: List[Dict] = []
        self.max_history_size = 30  # ~1 Sekunde bei 30 FPS

        # Geste-Callbacks
        self.gesture_callbacks: Dict[GestureType, List[Callable]] = {}
        for gesture in GestureType:
            self.gesture_callbacks[gesture] = []

        # Cooldown-Tracking
        self.last_gesture_time = 0
        self.last_gesture_type: Optional[GestureType] = None

        # Geste-Detektoren
        self.detectors = {
            GestureType.NOD: self._detect_nod,
            GestureType.SHAKE: self._detect_shake,
            GestureType.TILT_LEFT: self._detect_tilt_left,
            GestureType.TILT_RIGHT: self._detect_tilt_right,
            GestureType.FORWARD: self._detect_forward,
            GestureType.BACKWARD: self._detect_backward,
            GestureType.CIRCLE_CLOCKWISE: self._detect_circle_clockwise,
            GestureType.CIRCLE_COUNTERCLOCKWISE: self._detect_circle_counterclockwise
        }

    def initialize(self) -> bool:
        """Gesture Recognizer initialisieren"""
        try:
            self.logger.info("Gesture Recognizer initialisiert")
            self.is_initialized = True
            return True
        except Exception as e:
            self.logger.error(f"Fehler bei Initialisierung: {e}")
            return False

    def add_pose_data(self, pose_data: Dict):
        """Pose-Daten zur Historie hinzufügen"""
        if not self.is_initialized:
            return

        # Timestamp hinzufügen falls nicht vorhanden
        if 'timestamp' not in pose_data:
            pose_data['timestamp'] = time.time()

        # Zur Historie hinzufügen
        self.pose_history.append(pose_data)

        # Alte Daten entfernen
        if len(self.pose_history) > self.max_history_size:
            self.pose_history.pop(0)

        # Gesten erkennen
        self._detect_gestures()

    def register_callback(self, gesture_type: GestureType, callback: Callable):
        """Callback für Geste registrieren"""
        if gesture_type in self.gesture_callbacks:
            self.gesture_callbacks[gesture_type].append(callback)

    def unregister_callback(self, gesture_type: GestureType, callback: Callable):
        """Callback für Geste entfernen"""
        if gesture_type in self.gesture_callbacks:
            try:
                self.gesture_callbacks[gesture_type].remove(callback)
            except ValueError:
                pass

    def _detect_gestures(self):
        """Alle Gesten erkennen"""
        if len(self.pose_history) < 5:  # Mindestens 5 Frames für Erkennung
            return

        current_time = time.time()

        # Cooldown prüfen
        if current_time - self.last_gesture_time < self.cooldown_time:
            return

        # Jede Geste prüfen
        for gesture_type, detector in self.detectors.items():
            try:
                confidence = detector()
                if confidence >= self.min_confidence:
                    self._trigger_gesture(gesture_type, confidence, current_time)
                    break  # Nur eine Geste pro Frame
            except Exception as e:
                self.logger.error(f"Fehler bei {gesture_type.value} Erkennung: {e}")

    def _trigger_gesture(self, gesture_type: GestureType, confidence: float, timestamp: float):
        """Geste auslösen"""
        gesture_event = GestureEvent(
            gesture_type=gesture_type,
            confidence=confidence,
            timestamp=timestamp
        )

        # Callbacks aufrufen
        for callback in self.gesture_callbacks[gesture_type]:
            try:
                callback(gesture_event)
            except Exception as e:
                self.logger.error(f"Fehler bei Geste-Callback: {e}")

        # Logging
        self.logger.info(f"Geste erkannt: {gesture_type.value} (Konfidenz: {confidence:.2f})")

        # Cooldown setzen
        self.last_gesture_time = timestamp
        self.last_gesture_type = gesture_type

    def _detect_nod(self) -> float:
        """Nick-Geste erkennen (Auf/Ab Bewegung)"""
        if len(self.pose_history) < 8:
            return 0.0

        # Pitch-Werte der letzten 8 Frames
        pitches = []
        for pose in self.pose_history[-8:]:
            if 'euler' in pose:
                pitches.append(pose['euler'][1])  # Pitch
            else:
                # Aus Quaternion berechnen
                pitches.append(self._quaternion_to_pitch(pose.get('quaternion', (1,0,0,0))))

        if len(pitches) < 8:
            return 0.0

        # Bewegungsmuster analysieren
        # Sollte: runter -> hoch -> runter gehen
        pattern_score = self._analyze_movement_pattern(pitches, [1, -1, 1])

        return min(1.0, pattern_score * 1.5)

    def _detect_shake(self) -> float:
        """Schüttel-Geste erkennen (Links/Rechts Bewegung)"""
        if len(self.pose_history) < 8:
            return 0.0

        # Yaw-Werte der letzten 8 Frames
        yaws = []
        for pose in self.pose_history[-8:]:
            if 'euler' in pose:
                yaws.append(pose['euler'][0])  # Yaw
            else:
                # Aus Quaternion berechnen
                yaws.append(self._quaternion_to_yaw(pose.get('quaternion', (1,0,0,0))))

        if len(yaws) < 8:
            return 0.0

        # Bewegungsmuster analysieren
        # Sollte: links -> rechts -> links gehen
        pattern_score = self._analyze_movement_pattern(yaws, [-1, 1, -1])

        return min(1.0, pattern_score * 1.5)

    def _detect_tilt_left(self) -> float:
        """Links-Neige-Geste erkennen"""
        if len(self.pose_history) < 5:
            return 0.0

        # Roll-Werte der letzten 5 Frames
        rolls = []
        for pose in self.pose_history[-5:]:
            if 'euler' in pose:
                rolls.append(pose['euler'][2])  # Roll
            else:
                # Aus Quaternion berechnen
                rolls.append(self._quaternion_to_roll(pose.get('quaternion', (1,0,0,0))))

        if len(rolls) < 5:
            return 0.0

        # Kontinuierliche Links-Neigung
        avg_roll = sum(rolls) / len(rolls)
        tilt_score = max(0, -avg_roll)  # Positive Werte für Links-Neigung

        return min(1.0, tilt_score * 2.0)

    def _detect_tilt_right(self) -> float:
        """Rechts-Neige-Geste erkennen"""
        if len(self.pose_history) < 5:
            return 0.0

        # Roll-Werte der letzten 5 Frames
        rolls = []
        for pose in self.pose_history[-5:]:
            if 'euler' in pose:
                rolls.append(pose['euler'][2])  # Roll
            else:
                # Aus Quaternion berechnen
                rolls.append(self._quaternion_to_roll(pose.get('quaternion', (1,0,0,0))))

        if len(rolls) < 5:
            return 0.0

        # Kontinuierliche Rechts-Neigung
        avg_roll = sum(rolls) / len(rolls)
        tilt_score = max(0, avg_roll)  # Positive Werte für Rechts-Neigung

        return min(1.0, tilt_score * 2.0)

    def _detect_forward(self) -> float:
        """Vorwärts-Geste erkennen"""
        if len(self.pose_history) < 5:
            return 0.0

        # Z-Position der letzten 5 Frames
        z_positions = [pose.get('position', [0,0,0])[2] for pose in self.pose_history[-5:]]

        if len(z_positions) < 5:
            return 0.0

        # Kontinuierliche Vorwärtsbewegung
        z_change = z_positions[-1] - z_positions[0]
        forward_score = max(0, z_change)  # Positive Werte für Vorwärts

        return min(1.0, forward_score * 3.0)

    def _detect_backward(self) -> float:
        """Rückwärts-Geste erkennen"""
        if len(self.pose_history) < 5:
            return 0.0

        # Z-Position der letzten 5 Frames
        z_positions = [pose.get('position', [0,0,0])[2] for pose in self.pose_history[-5:]]

        if len(z_positions) < 5:
            return 0.0

        # Kontinuierliche Rückwärtsbewegung
        z_change = z_positions[-1] - z_positions[0]
        backward_score = max(0, -z_change)  # Negative Werte für Rückwärts

        return min(1.0, backward_score * 3.0)

    def _detect_circle_clockwise(self) -> float:
        """Im Uhrzeigersinn Kreis-Geste erkennen"""
        return self._detect_circular_motion(clockwise=True)

    def _detect_circle_counterclockwise(self) -> float:
        """Gegen Uhrzeigersinn Kreis-Geste erkennen"""
        return self._detect_circular_motion(clockwise=False)

    def _detect_circular_motion(self, clockwise: bool) -> float:
        """Kreisförmige Bewegung erkennen"""
        if len(self.pose_history) < 15:  # Braucht mehr Frames für Kreis
            return 0.0

        # Yaw und Pitch der letzten 15 Frames
        movements = []
        for pose in self.pose_history[-15:]:
            if 'euler' in pose:
                yaw, pitch = pose['euler'][0], pose['euler'][1]
            else:
                quaternion = pose.get('quaternion', (1,0,0,0))
                yaw = self._quaternion_to_yaw(quaternion)
                pitch = self._quaternion_to_pitch(quaternion)
            movements.append((yaw, pitch))

        if len(movements) < 15:
            return 0.0

        # Kreismuster analysieren
        circle_score = self._analyze_circle_pattern(movements, clockwise)
        return min(1.0, circle_score)

    def _analyze_movement_pattern(self, values: List[float], expected_pattern: List[int]) -> float:
        """Bewegungsmuster analysieren"""
        if len(values) < len(expected_pattern):
            return 0.0

        # Ableitung berechnen (Bewegungsrichtung)
        derivatives = []
        for i in range(1, len(values)):
            derivatives.append(values[i] - values[i-1])

        if len(derivatives) < len(expected_pattern):
            return 0.0

        # Muster-Matching
        pattern_matches = 0
        for i, expected in enumerate(expected_pattern):
            if i < len(derivatives):
                actual = 1 if derivatives[i] > 0 else -1
                if actual == expected:
                    pattern_matches += 1

        return pattern_matches / len(expected_pattern)

    def _analyze_circle_pattern(self, movements: List[Tuple[float, float]], clockwise: bool) -> float:
        """Kreismuster analysieren"""
        if len(movements) < 10:
            return 0.0

        # Mittelpunkt berechnen
        center_x = sum(x for x, y in movements) / len(movements)
        center_y = sum(y for x, y in movements) / len(movements)

        # Abstände zum Mittelpunkt
        distances = []
        for x, y in movements:
            distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
            distances.append(distance)

        # Varianz der Abstände (sollte niedrig sein für Kreis)
        avg_distance = sum(distances) / len(distances)
        variance = sum((d - avg_distance)**2 for d in distances) / len(distances)
        circularity = 1.0 / (1.0 + variance)  # 0-1 Score

        # Richtung prüfen
        direction_score = self._analyze_rotation_direction(movements, center_x, center_y, clockwise)

        return (circularity + direction_score) / 2.0

    def _analyze_rotation_direction(self, movements: List[Tuple[float, float]],
                                   center_x: float, center_y: float, clockwise: bool) -> float:
        """Rotationsrichtung analysieren"""
        if len(movements) < 5:
            return 0.0

        # Winkel zum Mittelpunkt berechnen
        angles = []
        for x, y in movements:
            angle = math.atan2(y - center_y, x - center_x)
            angles.append(angle)

        # Richtung der Winkeländerung analysieren
        return self._calculate_direction_score(angles, clockwise)

    def _calculate_direction_score(self, angles: List[float], clockwise: bool) -> float:
        """Richtungsscore berechnen"""
        direction_changes = 0
        correct_direction = 0

        for i in range(1, len(angles)):
            angle_diff = self._normalize_angle_diff(angles[i] - angles[i-1])

            if abs(angle_diff) > 0.1:  # Signifikante Änderung
                direction_changes += 1
                if self._is_correct_direction(angle_diff, clockwise):
                    correct_direction += 1

        return correct_direction / direction_changes if direction_changes > 0 else 0.0

    def _normalize_angle_diff(self, angle_diff: float) -> float:
        """Winkel-Differenz normalisieren"""
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi
        return angle_diff

    def _is_correct_direction(self, angle_diff: float, clockwise: bool) -> bool:
        """Prüfen ob Richtung korrekt ist"""
        if clockwise:
            return angle_diff < 0
        else:
            return angle_diff > 0

    def _quaternion_to_yaw(self, q: Tuple[float, float, float, float]) -> float:
        """Quaternion zu Yaw-Winkel"""
        w, x, y, z = q
        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)
        return math.atan2(siny_cosp, cosy_cosp)

    def _quaternion_to_pitch(self, q: Tuple[float, float, float, float]) -> float:
        """Quaternion zu Pitch-Winkel"""
        w, x, y, z = q
        sinp = 2 * (w * y - z * x)
        if abs(sinp) >= 1:
            return math.copysign(math.pi / 2, sinp)
        else:
            return math.asin(sinp)

    def _quaternion_to_roll(self, q: Tuple[float, float, float, float]) -> float:
        """Quaternion zu Roll-Winkel"""
        w, x, y, z = q
        sinr_cosp = 2 * (w * x + y * z)
        cosr_cosp = 1 - 2 * (x * x + y * y)
        return math.atan2(sinr_cosp, cosr_cosp)

    def set_sensitivity(self, sensitivity: float):
        """Sensitivität setzen"""
        self.sensitivity = max(0.1, min(3.0, sensitivity))

    def set_min_confidence(self, confidence: float):
        """Minimale Konfidenz setzen"""
        self.min_confidence = max(0.1, min(1.0, confidence))

    def get_stats(self) -> dict:
        """Recognizer-Statistiken"""
        return {
            "initialized": self.is_initialized,
            "history_size": len(self.pose_history),
            "sensitivity": self.sensitivity,
            "min_confidence": self.min_confidence,
            "last_gesture": self.last_gesture_type.value if self.last_gesture_type else None,
            "registered_callbacks": sum(len(callbacks) for callbacks in self.gesture_callbacks.values())
        }
