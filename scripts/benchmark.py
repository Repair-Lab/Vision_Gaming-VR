#!/usr/bin/env python3
"""
VR Gaming Server - Performance Benchmark Script
Misst System-Performance und Netzwerk-Latenz
"""

import time
import psutil
import platform
import subprocess
import json
from pathlib import Path
import logging
from typing import Dict, List, Any
import numpy as np

class PerformanceBenchmark:
    """Performance-Benchmark für VR Gaming Server"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.results = {}
        self.system = platform.system().lower()

    def run_full_benchmark(self) -> Dict:
        """Führt vollständigen Benchmark durch"""
        self.logger.info("Starte vollständigen Performance-Benchmark...")

        self.results = {
            "timestamp": time.time(),
            "system_info": self.get_system_info(),
            "cpu_benchmark": self.benchmark_cpu(),
            "memory_benchmark": self.benchmark_memory(),
            "disk_benchmark": self.benchmark_disk(),
            "network_benchmark": self.benchmark_network(),
            "gpu_benchmark": self.benchmark_gpu(),
            "vr_readiness": self.check_vr_readiness(),
            "recommendations": []
        }

        self.results["score"] = self.calculate_overall_score()
        self.results["recommendations"] = self.generate_recommendations()

        return self.results

    def get_system_info(self) -> Dict:
        """Sammelt System-Informationen"""
        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "architecture": platform.architecture(),
            "processor": platform.processor(),
            "cpu_count": psutil.cpu_count(),
            "cpu_logical": psutil.cpu_count(logical=True),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "disk_total": psutil.disk_usage('/').total,
            "disk_free": psutil.disk_usage('/').free
        }

    def benchmark_cpu(self) -> Dict:
        """CPU-Performance-Test"""
        self.logger.info("CPU-Benchmark läuft...")

        # Single-threaded test
        start_time = time.time()
        result = 0
        for i in range(1000000):
            result += i ** 2
        single_time = time.time() - start_time

        # Multi-threaded test
        import threading

        def worker():
            local_result = 0
            for i in range(250000):
                local_result += i ** 2
            return local_result

        start_time = time.time()
        threads = []
        for _ in range(4):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        multi_time = time.time() - start_time

        return {
            "single_thread_score": 1000000 / single_time,
            "multi_thread_score": 1000000 / multi_time,
            "cpu_usage": psutil.cpu_percent(interval=1),
            "cpu_freq": psutil.cpu_freq().current if psutil.cpu_freq() else None
        }

    def benchmark_memory(self) -> Dict:
        """Memory-Performance-Test"""
        self.logger.info("Memory-Benchmark läuft...")

        # Memory allocation test
        arrays = []
        start_time = time.time()

        for i in range(100):
            arrays.append(np.random.random((1000, 1000)))

        allocation_time = time.time() - start_time

        # Memory access test
        start_time = time.time()
        total = 0
        for arr in arrays:
            total += np.sum(arr)

        access_time = time.time() - start_time

        # Cleanup
        del arrays

        return {
            "allocation_score": 100 / allocation_time,
            "access_score": 100 / access_time,
            "memory_usage": psutil.virtual_memory().percent,
            "swap_usage": psutil.swap_memory().percent
        }

    def benchmark_disk(self) -> Dict:
        """Disk-Performance-Test"""
        self.logger.info("Disk-Benchmark läuft...")

        test_file = Path("benchmark_test.tmp")
        test_data = b"0" * 1024 * 1024  # 1MB

        # Write test
        start_time = time.time()
        with open(test_file, 'wb') as f:
            for _ in range(100):
                f.write(test_data)
        write_time = time.time() - start_time

        # Read test
        start_time = time.time()
        with open(test_file, 'rb') as f:
            for _ in range(100):
                f.read(1024 * 1024)
        read_time = time.time() - start_time

        # Cleanup
        test_file.unlink(missing_ok=True)

        return {
            "write_score": 100 / write_time,
            "read_score": 100 / read_time,
            "disk_usage": psutil.disk_usage('/').percent
        }

    def benchmark_network(self) -> Dict:
        """Network-Performance-Test"""
        self.logger.info("Network-Benchmark läuft...")

        try:
            # Ping test to Google DNS
            result = subprocess.run(
                ['ping', '-c', '4', '8.8.8.8'],
                capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'avg' in line or 'Average' in line:
                        # Parse ping time
                        parts = line.split('/')
                        if len(parts) >= 5:
                            avg_ping = float(parts[4])
                            break
                else:
                    avg_ping = 50.0  # Default
            else:
                avg_ping = 100.0

            return {
                "ping_google": avg_ping,
                "network_interfaces": len(psutil.net_if_addrs()),
                "bytes_sent": psutil.net_io_counters().bytes_sent,
                "bytes_recv": psutil.net_io_counters().bytes_recv
            }
        except Exception as e:
            self.logger.error(f"Network-Benchmark fehlgeschlagen: {e}")
            return {"error": str(e)}

    def benchmark_gpu(self) -> Dict:
        """GPU-Performance-Test (falls verfügbar)"""
        self.logger.info("GPU-Benchmark läuft...")

        try:
            # OpenGL test
            import cv2
            test_image = np.random.random((1920, 1080, 3)).astype(np.float32)

            start_time = time.time()
            for _ in range(100):
                blurred = cv2.GaussianBlur(test_image, (5, 5), 0)
            gpu_time = time.time() - start_time

            return {
                "opengl_score": 100 / gpu_time,
                "opencv_available": True
            }
        except Exception as e:
            self.logger.error(f"GPU-Benchmark fehlgeschlagen: {e}")
            return {"opencv_available": False, "error": str(e)}

    def check_vr_readiness(self) -> Dict:
        """Prüft VR-Bereitschaft des Systems"""
        vr_check = {
            "webxr_support": False,
            "webgl_support": False,
            "websocket_support": True,  # Assume available
            "recommended_settings": {}
        }

        # CPU check
        cpu_count = psutil.cpu_count()
        if cpu_count >= 4:
            vr_check["cpu_ready"] = True
        else:
            vr_check["cpu_ready"] = False

        # Memory check
        memory_gb = psutil.virtual_memory().total / (1024**3)
        if memory_gb >= 8:
            vr_check["memory_ready"] = True
        else:
            vr_check["memory_ready"] = False

        # Network check
        try:
            result = subprocess.run(
                ['ping', '-c', '1', '8.8.8.8'],
                capture_output=True, timeout=5
            )
            vr_check["network_ready"] = result.returncode == 0
        except:
            vr_check["network_ready"] = False

        return vr_check

    def calculate_overall_score(self) -> float:
        """Berechnet Gesamt-Score"""
        score = 0

        # CPU score
        if "cpu_benchmark" in self.results:
            cpu = self.results["cpu_benchmark"]
            score += min(100, cpu.get("single_thread_score", 0) / 10000)

        # Memory score
        if "memory_benchmark" in self.results:
            mem = self.results["memory_benchmark"]
            score += min(100, mem.get("allocation_score", 0) / 10)

        # Disk score
        if "disk_benchmark" in self.results:
            disk = self.results["disk_benchmark"]
            score += min(100, disk.get("read_score", 0) / 10)

        return score / 3  # Average

    def generate_recommendations(self) -> List[str]:
        """Generiert Empfehlungen basierend auf Ergebnissen"""
        recommendations = []

        system_info = self.results.get("system_info", {})
        cpu_bench = self.results.get("cpu_benchmark", {})
        mem_bench = self.results.get("memory_benchmark", {})

        # CPU recommendations
        if cpu_bench.get("cpu_usage", 0) > 80:
            recommendations.append("Hohe CPU-Auslastung: Schließen Sie unnötige Programme")

        # Memory recommendations
        memory_gb = system_info.get("memory_total", 0) / (1024**3)
        if memory_gb < 8:
            recommendations.append("Weniger als 8GB RAM: Erwägen Sie RAM-Upgrade für bessere VR-Performance")

        # Network recommendations
        network = self.results.get("network_benchmark", {})
        if network.get("ping_google", 50) > 50:
            recommendations.append("Hohe Netzwerk-Latenz: Prüfen Sie Ihre Internet-Verbindung")

        if not recommendations:
            recommendations.append("System ist für VR-Gaming bereit!")

        return recommendations

    def save_results(self, filename: str = "benchmark_results.json"):
        """Speichert Benchmark-Ergebnisse"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        self.logger.info(f"Benchmark-Ergebnisse gespeichert in {filename}")

    def print_summary(self):
        """Gibt Benchmark-Zusammenfassung aus"""
        print("\n" + "="*60)
        print("VR GAMING SERVER - PERFORMANCE BENCHMARK")
        print("="*60)

        score = self.results.get("score", 0)
        print(f"Gesamt-Score: {score:.1f}")
        if score >= 80:
            print("🎉 Ausgezeichnete Performance für VR-Gaming!")
        elif score >= 60:
            print("✅ Gute Performance für VR-Gaming")
        elif score >= 40:
            print("⚠️ Akzeptable Performance, Optimierungen empfohlen")
        else:
            print("❌ Performance-Optimierungen dringend empfohlen")

        print("\nEmpfehlungen:")
        for rec in self.results.get("recommendations", []):
            print(f"• {rec}")

        print("\nDetaillierte Ergebnisse gespeichert in benchmark_results.json")


def main():
    """Hauptfunktion"""
    logging.basicConfig(level=logging.INFO)

    benchmark = PerformanceBenchmark()
    results = benchmark.run_full_benchmark()
    benchmark.save_results()
    benchmark.print_summary()


if __name__ == "__main__":
    main()
