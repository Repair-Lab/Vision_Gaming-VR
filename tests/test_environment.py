#!/usr/bin/env python3
"""
VR Gaming Server - Comprehensive Test Suite
Umfassende Tests für alle Komponenten
"""

import sys
import os
import time
import json
import logging
from pathlib import Path
from typing import Dict, List, Any
import unittest
import subprocess
import threading
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Projekt-Root zum Python-Pfad hinzufügen
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class VRGamingServerTestSuite(unittest.TestCase):
    """Umfassende Test-Suite für VR Gaming Server"""

    def setUp(self):
        """Test-Setup"""
        self.logger = logging.getLogger(__name__)
        self.test_results = {
            "timestamp": time.time(),
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "details": {}
        }

        # Test-Konfiguration
        self.test_config = {
            "timeout": 30,
            "retries": 3,
            "parallel_tests": True
        }

    def tearDown(self):
        """Test-Cleanup"""
        pass

    def test_01_system_requirements(self):
        """Test 1: System-Anforderungen prüfen"""
        self.logger.info("Test 1: System-Anforderungen prüfen")

        try:
            # Requirements-Checker importieren und ausführen
            from scripts.requirements_check import RequirementsChecker

            checker = RequirementsChecker()
            results = checker.run_full_check()

            # Ergebnisse validieren
            self.assertIn("overall_status", results)
            self.assertIn("system_check", results)
            self.assertIn("python_check", results)

            # System-spezifische Tests
            system = results["system_check"]
            self.assertIn("os_supported", system)

            # Python-Tests
            python = results["python_check"]
            self.assertTrue(python.get("version_compatible", False))

            self.test_results["details"]["system_requirements"] = "PASSED"
            self.logger.info("✅ System-Anforderungen erfüllt")

        except Exception as e:
            self.test_results["details"]["system_requirements"] = f"FAILED: {str(e)}"
            self.logger.error(f"❌ System-Anforderungen Test fehlgeschlagen: {e}")
            raise

    def test_02_configuration_files(self):
        """Test 2: Konfigurationsdateien validieren"""
        self.logger.info("Test 2: Konfigurationsdateien validieren")

        config_files = [
            "config/server_config.yaml",
            "config/input_config.yaml",
            "config/network_config.yaml",
            "config/video_config.yaml"
        ]

        try:
            import yaml

            for config_file in config_files:
                file_path = project_root / config_file
                self.assertTrue(file_path.exists(), f"Konfigurationsdatei fehlt: {config_file}")

                # YAML validieren
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)

                self.assertIsInstance(config, dict, f"Ungültige YAML-Struktur in {config_file}")
                self.assertGreater(len(config), 0, f"Leere Konfiguration in {config_file}")

            self.test_results["details"]["configuration_files"] = "PASSED"
            self.logger.info("✅ Konfigurationsdateien valid")

        except Exception as e:
            self.test_results["details"]["configuration_files"] = f"FAILED: {str(e)}"
            self.logger.error(f"❌ Konfigurationsdateien Test fehlgeschlagen: {e}")
            raise

    def test_03_game_profiles(self):
        """Test 3: Spiel-Profile validieren"""
        self.logger.info("Test 3: Spiel-Profile validieren")

        profile_files = [
            "profiles/default.json",
            "profiles/games/cyberpunk2077.json",
            "profiles/games/minecraft.json",
            "profiles/games/forza.json",
            "profiles/games/flight-sim.json"
        ]

        required_keys = ["name", "input_mapping", "video_settings"]

        try:
            for profile_file in profile_files:
                file_path = project_root / profile_file
                self.assertTrue(file_path.exists(), f"Profil-Datei fehlt: {profile_file}")

                # JSON validieren
                with open(file_path, 'r', encoding='utf-8') as f:
                    profile = json.load(f)

                self.assertIsInstance(profile, dict, f"Ungültige JSON-Struktur in {profile_file}")

                # Erforderliche Keys prüfen
                for key in required_keys:
                    self.assertIn(key, profile, f"Fehlender Key '{key}' in {profile_file}")

            self.test_results["details"]["game_profiles"] = "PASSED"
            self.logger.info("✅ Spiel-Profile valid")

        except Exception as e:
            self.test_results["details"]["game_profiles"] = f"FAILED: {str(e)}"
            self.logger.error(f"❌ Spiel-Profile Test fehlgeschlagen: {e}")
            raise

    def test_04_capture_systems(self):
        """Test 4: Capture-Systeme testen"""
        self.logger.info("Test 4: Capture-Systeme testen")

        try:
            # Universal Capture testen
            from capture.universal_capture import get_screen_capture

            capture = get_screen_capture()
            self.assertIsNotNone(capture)

            # Plattform-spezifische Capture-Klassen
            import platform
            system = platform.system().lower()

            if system == "windows":
                from capture.windows_capture import WindowsScreenCapture
                win_capture = WindowsScreenCapture()
                self.assertTrue(win_capture.initialize())

            elif system == "darwin":
                from capture.macos_capture import MacOSScreenCapture
                mac_capture = MacOSScreenCapture()
                self.assertTrue(mac_capture.initialize())

            elif system == "linux":
                from capture.linux_capture import LinuxScreenCapture
                linux_capture = LinuxScreenCapture()
                self.assertTrue(linux_capture.initialize())

            self.test_results["details"]["capture_systems"] = "PASSED"
            self.logger.info("✅ Capture-Systeme funktionieren")

        except Exception as e:
            self.test_results["details"]["capture_systems"] = f"FAILED: {str(e)}"
            self.logger.error(f"❌ Capture-Systeme Test fehlgeschlagen: {e}")
            raise

    def test_05_input_systems(self):
        """Test 5: Input-Systeme testen"""
        self.logger.info("Test 5: Input-Systeme testen")

        try:
            # Mouse Controller testen
            from input.mouse_controller import get_mouse_controller
            mouse = get_mouse_controller()
            self.assertIsNotNone(mouse)

            # Keyboard Controller testen
            from input.keyboard_controller import get_keyboard_controller
            keyboard = get_keyboard_controller()
            self.assertIsNotNone(keyboard)

            # Head Pose Processor testen
            from input.head_pose_processor import HeadPoseProcessor
            processor = HeadPoseProcessor()
            self.assertTrue(processor.initialize())

            # Gesture Recognizer testen
            from input.gesture_recognizer import GestureRecognizer
            recognizer = GestureRecognizer()
            self.assertTrue(recognizer.initialize())

            self.test_results["details"]["input_systems"] = "PASSED"
            self.logger.info("✅ Input-Systeme funktionieren")

        except Exception as e:
            self.test_results["details"]["input_systems"] = f"FAILED: {str(e)}"
            self.logger.error(f"❌ Input-Systeme Test fehlgeschlagen: {e}")
            raise

    def test_06_server_components(self):
        """Test 6: Server-Komponenten testen"""
        self.logger.info("Test 6: Server-Komponenten testen")

        try:
            # Server-Komponenten importieren
            from server.config_manager import ConfigManager
            from server.game_detector import GameDetector
            from server.performance_monitor import PerformanceMonitor

            # Config Manager testen
            config = ConfigManager()
            self.assertIsNotNone(config)

            # Game Detector testen
            detector = GameDetector()
            self.assertTrue(detector.initialize())

            # Performance Monitor testen
            monitor = PerformanceMonitor()
            self.assertIsNotNone(monitor)

            self.test_results["details"]["server_components"] = "PASSED"
            self.logger.info("✅ Server-Komponenten funktionieren")

        except Exception as e:
            self.test_results["details"]["server_components"] = f"FAILED: {str(e)}"
            self.logger.error(f"❌ Server-Komponenten Test fehlgeschlagen: {e}")
            raise

    def test_07_benchmark_system(self):
        """Test 7: Benchmark-System testen"""
        self.logger.info("Test 7: Benchmark-System testen")

        try:
            # Benchmark-Modul importieren
            from scripts.benchmark import SystemBenchmark

            benchmark = SystemBenchmark()
            self.assertIsNotNone(benchmark)

            # Kurzen Benchmark ausführen (ohne langwierige Tests)
            results = benchmark.run_quick_benchmark()

            self.assertIsInstance(results, dict)
            self.assertIn("timestamp", results)
            self.assertIn("system_info", results)

            self.test_results["details"]["benchmark_system"] = "PASSED"
            self.logger.info("✅ Benchmark-System funktioniert")

        except Exception as e:
            self.test_results["details"]["benchmark_system"] = f"FAILED: {str(e)}"
            self.logger.error(f"❌ Benchmark-System Test fehlgeschlagen: {e}")
            raise

    def test_08_web_interface(self):
        """Test 8: Web-Interface testen"""
        self.logger.info("Test 8: Web-Interface testen")

        try:
            # Templates prüfen
            template_files = [
                "web/templates/index.html",
                "web/templates/sensor-check.html",
                "web/templates/server-control.html",
                "web/templates/game-setup.html",
                "web/templates/settings.html",
                "web/templates/vr-gaming.html"
            ]

            for template_file in template_files:
                file_path = project_root / template_file
                self.assertTrue(file_path.exists(), f"Template fehlt: {template_file}")

                # HTML-Struktur prüfen
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                self.assertIn("<!DOCTYPE html>", content, f"Ungültiges HTML in {template_file}")
                self.assertIn("</html>", content, f"Unvollständiges HTML in {template_file}")

            # Static Files prüfen
            static_files = [
                "web/static/css/main.css",
                "web/static/js/server-client.js",
                "web/static/js/video-player.js"
            ]

            for static_file in static_files:
                file_path = project_root / static_file
                self.assertTrue(file_path.exists(), f"Static file fehlt: {static_file}")

            self.test_results["details"]["web_interface"] = "PASSED"
            self.logger.info("✅ Web-Interface vollständig")

        except Exception as e:
            self.test_results["details"]["web_interface"] = f"FAILED: {str(e)}"
            self.logger.error(f"❌ Web-Interface Test fehlgeschlagen: {e}")
            raise

    def test_09_integration_test(self):
        """Test 9: Integrations-Test"""
        self.logger.info("Test 9: Integrations-Test")

        try:
            # Vollständigen Server-Start simulieren
            from server.main import VRServer

            # Server ohne tatsächlichen Start initialisieren
            server = VRServer()

            # Komponenten prüfen
            self.assertIsNotNone(server.config)
            self.assertIsNotNone(server.game_capture)
            self.assertIsNotNone(server.video_streamer)
            self.assertIsNotNone(server.head_tracker)
            self.assertIsNotNone(server.input_injector)
            self.assertIsNotNone(server.game_detector)
            self.assertIsNotNone(server.performance_monitor)

            self.test_results["details"]["integration_test"] = "PASSED"
            self.logger.info("✅ Integration erfolgreich")

        except Exception as e:
            self.test_results["details"]["integration_test"] = f"FAILED: {str(e)}"
            self.logger.error(f"❌ Integration Test fehlgeschlagen: {e}")
            raise

    def test_10_performance_test(self):
        """Test 10: Performance-Test"""
        self.logger.info("Test 10: Performance-Test")

        try:
            # Performance-Test durchführen
            import psutil
            import time

            # CPU-Test
            start_time = time.time()
            for _ in range(100000):
                _ = 2 ** 10
            cpu_time = time.time() - start_time

            # Memory-Test
            process = psutil.Process()
            memory_usage = process.memory_info().rss / 1024 / 1024  # MB

            # Ergebnisse validieren
            self.assertLess(cpu_time, 1.0, "CPU-Performance zu langsam")
            self.assertLess(memory_usage, 500, "Zu hoher Speicherverbrauch")

            self.test_results["details"]["performance_test"] = "PASSED"
            self.logger.info("✅ Performance-Test bestanden")

        except Exception as e:
            self.test_results["details"]["performance_test"] = f"FAILED: {str(e)}"
            self.logger.error(f"❌ Performance-Test fehlgeschlagen: {e}")
            raise


class TestRunner:
    """Test-Runner für die VR Gaming Server Test-Suite"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.test_results = {}

    def run_all_tests(self) -> Dict[str, Any]:
        """Alle Tests ausführen"""
        self.logger.info("🚀 Starte VR Gaming Server Test-Suite")

        # Test-Suite laden
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(VRGamingServerTestSuite)

        # Tests ausführen
        runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
        result = runner.run(suite)

        # Ergebnisse sammeln
        self.test_results = {
            "total_tests": result.testsRun,
            "passed": len(result.successes) if hasattr(result, 'successes') else 0,
            "failed": len(result.failures),
            "errors": len(result.errors),
            "timestamp": time.time(),
            "duration": time.time() - time.time(),  # Vereinfacht
            "success_rate": 0.0
        }

        if result.testsRun > 0:
            self.test_results["success_rate"] = (self.test_results["passed"] / result.testsRun) * 100

        # Detaillierte Ergebnisse
        if result.failures:
            self.test_results["failures"] = [str(failure) for failure in result.failures]

        if result.errors:
            self.test_results["errors"] = [str(error) for error in result.errors]

        return self.test_results

    def generate_report(self) -> str:
        """Test-Bericht generieren"""
        results = self.test_results

        report = []
        report.append("=" * 60)
        report.append("VR GAMING SERVER - TEST REPORT")
        report.append("=" * 60)
        report.append(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(results.get('timestamp', time.time())))}")
        report.append(f"Total Tests: {results.get('total_tests', 0)}")
        report.append(f"Passed: {results.get('passed', 0)}")
        report.append(f"Failed: {results.get('failed', 0)}")
        report.append(f"Errors: {results.get('errors', 0)}")
        report.append(".1f")
        report.append("")

        # Status
        success_rate = results.get('success_rate', 0)
        if success_rate >= 90:
            report.append("✅ OVERALL STATUS: EXCELLENT")
        elif success_rate >= 75:
            report.append("⚠️  OVERALL STATUS: GOOD")
        elif success_rate >= 50:
            report.append("❌ OVERALL STATUS: NEEDS IMPROVEMENT")
        else:
            report.append("💥 OVERALL STATUS: CRITICAL ISSUES")

        # Detaillierte Fehler
        if results.get('failures'):
            report.append("")
            report.append("FAILURES:")
            for failure in results['failures'][:5]:  # Nur erste 5
                report.append(f"• {failure[:100]}...")

        if results.get('errors'):
            report.append("")
            report.append("ERRORS:")
            for error in results['errors'][:5]:  # Nur erste 5
                report.append(f"• {error[:100]}...")

        report.append("=" * 60)

        return "\n".join(report)

    def save_report(self, filename: str = "test_report.json"):
        """Test-Bericht speichern"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Test-Bericht gespeichert: {filename}")


def main():
    """Hauptfunktion"""
    # Logging konfigurieren
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Test-Runner erstellen und ausführen
    runner = TestRunner()
    results = runner.run_all_tests()

    # Bericht generieren und anzeigen
    report = runner.generate_report()
    print("\n" + report)

    # Bericht speichern
    runner.save_report()

    # Exit-Code basierend auf Erfolg
    success_rate = results.get('success_rate', 0)
    if success_rate >= 75:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
