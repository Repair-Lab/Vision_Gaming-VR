#!/usr/bin/env python3
"""
VR Gaming Server - Requirements Check Script
Prüft System-Anforderungen und Abhängigkeiten
"""

import sys
import platform
import subprocess
import importlib
import json
from pathlib import Path
from typing import Dict, List, Tuple
import logging

class RequirementsChecker:
    """Prüft System-Anforderungen für VR Gaming Server"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.system = platform.system().lower()
        self.results = {
            "system_check": {},
            "python_check": {},
            "dependencies_check": {},
            "hardware_check": {},
            "network_check": {},
            "overall_status": "unknown"
        }

    def run_full_check(self) -> Dict:
        """Führt vollständige Anforderungsprüfung durch"""
        self.logger.info("Starte Anforderungsprüfung...")

        self.results["system_check"] = self.check_system_requirements()
        self.results["python_check"] = self.check_python_requirements()
        self.results["dependencies_check"] = self.check_dependencies()
        self.results["hardware_check"] = self.check_hardware_requirements()
        self.results["network_check"] = self.check_network_requirements()

        self.results["overall_status"] = self.determine_overall_status()

        return self.results

    def check_system_requirements(self) -> Dict:
        """Prüft grundlegende System-Anforderungen"""
        result = {
            "os_supported": False,
            "os_version": platform.version(),
            "architecture": platform.architecture()[0],
            "supported_os": ["windows", "darwin", "linux"]
        }

        if self.system in result["supported_os"]:
            result["os_supported"] = True
        else:
            result["os_supported"] = False
            result["warning"] = f"Betriebssystem {self.system} wird nicht offiziell unterstützt"

        return result

    def check_python_requirements(self) -> Dict:
        """Prüft Python-Version und -Features"""
        result = {
            "python_version": sys.version,
            "python_version_info": sys.version_info,
            "version_compatible": False,
            "required_version": (3, 8, 0)
        }

        if sys.version_info >= result["required_version"]:
            result["version_compatible"] = True
        else:
            result["version_compatible"] = False
            result["error"] = f"Python {result['required_version']} oder höher erforderlich"

        # Prüfe wichtige Python-Features
        result["asyncio_available"] = hasattr(sys.modules.get("asyncio"), "__version__") if "asyncio" in sys.modules else True
        result["typing_available"] = hasattr(sys.modules.get("typing"), "__version__") if "typing" in sys.modules else True

        return result

    def check_dependencies(self) -> Dict:
        """Prüft Python-Abhängigkeiten"""
        required_packages = {
            "fastapi": "0.100.0",
            "uvicorn": "0.20.0",
            "opencv-python": "4.8.0",
            "numpy": "1.24.0",
            "mss": "9.0.0",
            "psutil": "5.9.0",
            "pyyaml": "6.0.0",
            "jinja2": "3.1.0",
            "websockets": "12.0.0"
        }

        optional_packages = {
            "pynput": "1.7.0",
            "aiortc": "1.6.0",
            "pywin32": "306",
            "sounddevice": "0.4.0"
        }

        result = {
            "required_packages": {},
            "optional_packages": {},
            "missing_required": [],
            "missing_optional": []
        }

        # Prüfe erforderliche Pakete
        for package, min_version in required_packages.items():
            status = self.check_package(package, min_version)
            result["required_packages"][package] = status
            if not status["installed"]:
                result["missing_required"].append(package)

        # Prüfe optionale Pakete
        for package, min_version in optional_packages.items():
            status = self.check_package(package, min_version)
            result["optional_packages"][package] = status
            if not status["installed"]:
                result["missing_optional"].append(package)

        return result

    def check_package(self, package_name: str, min_version: str) -> Dict:
        """Prüft einzelnes Python-Paket"""
        try:
            module = importlib.import_module(package_name.replace("-", "_"))
            version = getattr(module, "__version__", "unknown")
            return {
                "installed": True,
                "version": version,
                "version_ok": version >= min_version if version != "unknown" else True
            }
        except ImportError:
            return {
                "installed": False,
                "version": None,
                "version_ok": False
            }

    def check_hardware_requirements(self) -> Dict:
        """Prüft Hardware-Anforderungen"""
        result = {
            "cpu_cores": 0,
            "memory_gb": 0,
            "disk_space_gb": 0,
            "cpu_ok": False,
            "memory_ok": False,
            "disk_ok": False
        }

        try:
            import psutil

            # CPU
            result["cpu_cores"] = psutil.cpu_count(logical=True)
            result["cpu_ok"] = result["cpu_cores"] >= 4

            # Memory
            memory_bytes = psutil.virtual_memory().total
            result["memory_gb"] = memory_bytes / (1024**3)
            result["memory_ok"] = result["memory_gb"] >= 8

            # Disk
            disk_bytes = psutil.disk_usage('/').free
            result["disk_space_gb"] = disk_bytes / (1024**3)
            result["disk_ok"] = result["disk_space_gb"] >= 10

        except ImportError:
            result["error"] = "psutil nicht verfügbar für Hardware-Check"

        return result

    def check_network_requirements(self) -> Dict:
        """Prüft Netzwerk-Anforderungen"""
        result = {
            "internet_connection": False,
            "latency_ms": 0,
            "bandwidth_mbps": 0,
            "ports_available": False
        }

        # Internet-Verbindung prüfen
        result["internet_connection"] = self._check_internet_connection()

        if result["internet_connection"]:
            # Latenz messen
            result["latency_ms"] = self._measure_latency()

        # Port-Verfügbarkeit prüfen (vereinfacht)
        result["ports_available"] = True  # Assume available

        return result

    def _check_internet_connection(self) -> bool:
        """Prüft Internet-Verbindung"""
        try:
            result_ping = subprocess.run(
                ['ping', '-c', '1', '8.8.8.8'],
                capture_output=True, timeout=5
            )
            return result_ping.returncode == 0
        except Exception:
            return False

    def _measure_latency(self) -> float:
        """Misst Netzwerk-Latenz"""
        try:
            ping_output = subprocess.run(
                ['ping', '-c', '4', '8.8.8.8'],
                capture_output=True, text=True, timeout=10
            )
            if ping_output.returncode == 0:
                for line in ping_output.stdout.split('\n'):
                    if 'avg' in line or 'Average' in line:
                        parts = line.split('/')
                        if len(parts) >= 5:
                            return float(parts[4])
            return 0.0
        except Exception:
            return 0.0

    def determine_overall_status(self) -> str:
        """Bestimmt Gesamtstatus"""
        system = self.results["system_check"]
        python = self.results["python_check"]
        deps = self.results["dependencies_check"]
        hardware = self.results["hardware_check"]

        if not system.get("os_supported", False):
            return "unsupported_os"

        if not python.get("version_compatible", False):
            return "python_incompatible"

        if deps.get("missing_required"):
            return "missing_dependencies"

        if not hardware.get("cpu_ok", True) or not hardware.get("memory_ok", True):
            return "hardware_insufficient"

        return "ready"

    def generate_report(self) -> str:
        """Generiert detaillierten Bericht"""
        status = self.results["overall_status"]

        report = []
        report.append("="*60)
        report.append("VR GAMING SERVER - REQUIREMENTS CHECK")
        report.append("="*60)

        if status == "ready":
            report.append("✅ System ist bereit für VR Gaming Server!")
        elif status == "unsupported_os":
            report.append("❌ Betriebssystem wird nicht unterstützt")
        elif status == "python_incompatible":
            report.append("❌ Python-Version nicht kompatibel")
        elif status == "missing_dependencies":
            report.append("❌ Erforderliche Abhängigkeiten fehlen")
        elif status == "hardware_insufficient":
            report.append("⚠️ Hardware-Anforderungen nicht erfüllt")

        # System-Info
        sys_check = self.results["system_check"]
        report.append(f"\nSystem: {platform.system()} {sys_check['os_version']}")
        report.append(f"Architektur: {sys_check['architecture']}")

        # Python-Info
        py_check = self.results["python_check"]
        report.append(f"\nPython: {py_check['python_version']}")

        # Hardware-Info
        hw_check = self.results["hardware_check"]
        report.append(f"\nCPU-Kerne: {hw_check['cpu_cores']}")
        report.append(f"RAM: {hw_check['memory_gb']:.1f} GB")
        report.append(f"Freier Speicher: {hw_check['disk_space_gb']:.1f} GB")

        # Dependencies
        deps_check = self.results["dependencies_check"]
        if deps_check["missing_required"]:
            report.append(f"\nFehlende erforderliche Pakete: {', '.join(deps_check['missing_required'])}")

        if deps_check["missing_optional"]:
            report.append(f"Fehlende optionale Pakete: {', '.join(deps_check['missing_optional'])}")

        return "\n".join(report)

    def save_report(self, filename: str = "requirements_report.json"):
        """Speichert detaillierten Bericht"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        self.logger.info(f"Anforderungsbericht gespeichert in {filename}")


def main():
    """Hauptfunktion"""
    logging.basicConfig(level=logging.INFO)

    checker = RequirementsChecker()
    results = checker.run_full_check()

    print(checker.generate_report())
    checker.save_report()

    # Exit-Code basierend auf Status
    status = results["overall_status"]
    if status == "ready":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
