#!/usr/bin/env python3
"""
VR Gaming Server - Simple Environment Test
Einfacher Test für grundlegende Funktionalität
"""

import sys
import os
import time
import json
import logging
from pathlib import Path
from typing import Dict, List, Any

# Projekt-Root zum Python-Pfad hinzufügen
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class SimpleEnvironmentTester:
    """Einfacher Umgebungs-Tester"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.results = {
            "timestamp": time.time(),
            "tests": {},
            "overall_status": "unknown"
        }

    def run_all_tests(self) -> Dict[str, Any]:
        """Alle Tests ausführen"""
        self.logger.info("🧪 Starte einfache Umgebungs-Tests")

        # Basis-Tests
        self.test_project_structure()
        self.test_python_environment()
        self.test_configuration_files()
        self.test_basic_imports()

        # Gesamtstatus bestimmen
        self.determine_overall_status()

        return self.results

    def test_project_structure(self):
        """Test 1: Projekt-Struktur prüfen"""
        self.logger.info("Test 1: Projekt-Struktur prüfen")

        required_dirs = [
            "server", "web", "config", "profiles", "scripts", "logs", "tests"
        ]

        required_files = [
            "requirements.txt", "run.py", "README.md",
            "scripts/requirements_check.py", "scripts/benchmark.py"
        ]

        status = "PASSED"
        issues = []

        # Verzeichnisse prüfen
        for dir_name in required_dirs:
            if not (project_root / dir_name).exists():
                issues.append(f"Fehlendes Verzeichnis: {dir_name}")
                status = "FAILED"

        # Dateien prüfen
        for file_name in required_files:
            if not (project_root / file_name).exists():
                issues.append(f"Fehlende Datei: {file_name}")
                status = "FAILED"

        self.results["tests"]["project_structure"] = {
            "status": status,
            "issues": issues
        }

        if status == "PASSED":
            self.logger.info("✅ Projekt-Struktur korrekt")
        else:
            self.logger.error(f"❌ Projekt-Struktur Probleme: {issues}")

    def test_python_environment(self):
        """Test 2: Python-Umgebung prüfen"""
        self.logger.info("Test 2: Python-Umgebung prüfen")

        try:
            import sys
            import platform

            python_version = sys.version_info
            python_version_str = f"{python_version.major}.{python_version.minor}.{python_version.micro}"

            # Python-Version prüfen (3.8+ erforderlich)
            version_ok = python_version >= (3, 8, 0)

            # Plattform-Info
            platform_info = platform.platform()

            self.results["tests"]["python_environment"] = {
                "status": "PASSED" if version_ok else "FAILED",
                "python_version": python_version_str,
                "platform": platform_info,
                "version_compatible": version_ok
            }

            if version_ok:
                self.logger.info(f"✅ Python {python_version_str} kompatibel")
            else:
                self.logger.error(f"❌ Python {python_version_str} nicht kompatibel (3.8+ erforderlich)")

        except Exception as e:
            self.results["tests"]["python_environment"] = {
                "status": "FAILED",
                "error": str(e)
            }
            self.logger.error(f"❌ Python-Umgebung Fehler: {e}")

    def test_configuration_files(self):
        """Test 3: Konfigurationsdateien prüfen"""
        self.logger.info("Test 3: Konfigurationsdateien prüfen")

        config_files = [
            "config/server_config.yaml",
            "config/input_config.yaml",
            "config/network_config.yaml",
            "config/video_config.yaml"
        ]

        status = "PASSED"
        issues = []

        for config_file in config_files:
            file_path = project_root / config_file
            if not file_path.exists():
                issues.append(f"Fehlende Konfigurationsdatei: {config_file}")
                status = "FAILED"
                continue

            # Grundlegende Struktur prüfen
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                if not content.strip():
                    issues.append(f"Leere Konfigurationsdatei: {config_file}")
                    status = "FAILED"

            except Exception as e:
                issues.append(f"Fehler beim Lesen von {config_file}: {str(e)}")
                status = "FAILED"

        self.results["tests"]["configuration_files"] = {
            "status": status,
            "issues": issues
        }

        if status == "PASSED":
            self.logger.info("✅ Konfigurationsdateien vorhanden")
        else:
            self.logger.error(f"❌ Konfigurationsdateien Probleme: {issues}")

    def test_basic_imports(self):
        """Test 4: Grundlegende Imports prüfen"""
        self.logger.info("Test 4: Grundlegende Imports prüfen")

        # Zu testende Module (ohne komplexe Abhängigkeiten)
        basic_modules = [
            "pathlib",
            "json",
            "logging",
            "typing"
        ]

        # Projekt-spezifische Module (falls verfügbar)
        project_modules = [
            "scripts.requirements_check",
            "scripts.benchmark"
        ]

        status = "PASSED"
        import_issues = []

        # Basis-Module testen
        for module in basic_modules:
            try:
                __import__(module)
            except ImportError as e:
                import_issues.append(f"Fehlendes Basis-Modul: {module} - {str(e)}")
                status = "FAILED"

        # Projekt-Module testen (optional)
        for module in project_modules:
            try:
                __import__(module)
            except ImportError:
                import_issues.append(f"Projekt-Modul nicht verfügbar: {module}")
                # Kein Fehler für optionale Module
            except Exception as e:
                import_issues.append(f"Fehler beim Import von {module}: {str(e)}")
                status = "FAILED"

        self.results["tests"]["basic_imports"] = {
            "status": status,
            "issues": import_issues
        }

        if status == "PASSED":
            self.logger.info("✅ Grundlegende Imports funktionieren")
        else:
            self.logger.error(f"❌ Import-Probleme: {import_issues}")

    def determine_overall_status(self):
        """Gesamtstatus bestimmen"""
        test_results = self.results["tests"]

        passed_tests = 0
        total_tests = len(test_results)

        for test_name, test_result in test_results.items():
            if test_result.get("status") == "PASSED":
                passed_tests += 1

        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

        if success_rate >= 90:
            self.results["overall_status"] = "EXCELLENT"
        elif success_rate >= 75:
            self.results["overall_status"] = "GOOD"
        elif success_rate >= 50:
            self.results["overall_status"] = "FAIR"
        else:
            self.results["overall_status"] = "POOR"

        self.results["success_rate"] = success_rate
        self.results["passed_tests"] = passed_tests
        self.results["total_tests"] = total_tests

    def generate_report(self) -> str:
        """Test-Bericht generieren"""
        results = self.results

        report = []
        report.append("=" * 60)
        report.append("VR GAMING SERVER - ENVIRONMENT TEST REPORT")
        report.append("=" * 60)
        report.append(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(results['timestamp']))}")
        report.append(f"Total Tests: {results.get('total_tests', 0)}")
        report.append(f"Passed: {results.get('passed_tests', 0)}")
        report.append(".1f")
        report.append("")

        # Status
        status = results.get('overall_status', 'UNKNOWN')
        if status == "EXCELLENT":
            report.append("✅ OVERALL STATUS: EXCELLENT - System bereit!")
        elif status == "GOOD":
            report.append("⚠️  OVERALL STATUS: GOOD - Kleine Probleme")
        elif status == "FAIR":
            report.append("❌ OVERALL STATUS: FAIR - Verbesserungen nötig")
        else:
            report.append("💥 OVERALL STATUS: POOR - Kritische Probleme")

        # Detaillierte Testergebnisse
        report.append("")
        report.append("DETAILED RESULTS:")
        for test_name, test_result in results.get("tests", {}).items():
            status_icon = "✅" if test_result.get("status") == "PASSED" else "❌"
            report.append(f"{status_icon} {test_name.replace('_', ' ').title()}")

            if test_result.get("issues"):
                for issue in test_result["issues"]:
                    report.append(f"   • {issue}")

        report.append("=" * 60)

        return "\n".join(report)

    def save_report(self, filename: str = "environment_test_report.json"):
        """Test-Bericht speichern"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Test-Bericht gespeichert: {filename}")


def main():
    """Hauptfunktion"""
    # Logging konfigurieren
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Tester erstellen und ausführen
    tester = SimpleEnvironmentTester()
    results = tester.run_all_tests()

    # Bericht generieren und anzeigen
    report = tester.generate_report()
    print("\n" + report)

    # Bericht speichern
    tester.save_report()

    # Exit-Code basierend auf Erfolg
    success_rate = results.get('success_rate', 0)
    if success_rate >= 75:
        print("\n🎉 System ist bereit für VR Gaming Server!")
        sys.exit(0)
    else:
        print("\n⚠️  System benötigt weitere Konfiguration.")
        sys.exit(1)


if __name__ == "__main__":
    main()
