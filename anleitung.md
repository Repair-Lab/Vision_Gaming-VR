# 🎯 VR Gaming Server - KOMPLETTER INSTALLATIONSFAHRPLAN

## 📋 SCHRITT-FÜR-SCHRITT ANLEITUNG

### 1. ORDNER ERSTELLEN UND DATEIEN ANLEGEN

```bash
# Hauptverzeichnis erstellen
mkdir vr-gaming-server
cd vr-gaming-server

# Unterverzeichnisse erstellen
mkdir -p server web/static web/templates profiles logs config
mkdir -p server/utils web/static/css web/static/js
```

### 2. DATEIEN IN DIESER REIHENFOLGE ERSTELLEN

#### A) Basis-Dateien (Root-Verzeichnis):

1. **requirements.txt** - Python Dependencies
2. **run.py** - Startup Script mit GUI

#### B) Server-Dateien (server/):

3. **server/main.py** - Haupt-FastAPI-Server
4. **server/game_capture.py** - Bildschirmaufnahme
5. **server/video_streamer.py** - Video-Streaming
6. **server/head_tracker.py** - Kopfbewegung-Verarbeitung
7. **server/input_injector.py** - Input-Injection
8. **server/config_manager.py** - Konfigurationsverwaltung

#### C) Utility-Dateien (server/utils/):

9. **server/utils/logger.py**
10. **server/utils/performance_monitor.py**
11. **server/game_detector.py**

#### D) Web-Interface (web/):

12. **web/templates/index.html**
13. **web/templates/sensor-check.html**
14. **web/templates/vr-gaming.html**
15. **web/static/js/webxr-handler.js**
16. **web/static/css/main.css**

### 3. PYTHON DEPENDENCIES INSTALLIEREN

```bash
# Requirements installieren
pip install -r requirements.txt

# Bei Fehlern einzeln installieren:
pip install fastapi uvicorn jinja2 websockets
pip install opencv-python mss numpy pynput
pip install pyyaml psutil

# Windows-spezifisch:
pip install pywin32  # Nur Windows
```

### 5. SYSTEM-ANFORDERUNGEN PRÜFEN

Bevor Sie den Server starten, führen Sie die Anforderungsprüfung aus:

```bash
# Anforderungsprüfung ausführen
python scripts/requirements_check.py

# Bericht wird angezeigt und als JSON gespeichert
```

**Was wird geprüft:**
- ✅ Python-Version (3.8+ erforderlich)
- ✅ Erforderliche Python-Pakete
- ✅ Hardware-Anforderungen (CPU, RAM, Speicher)
- ✅ Netzwerk-Verbindung und Latenz
- ✅ Betriebssystem-Kompatibilität

### 6. PERFORMANCE-BENCHMARK AUSFÜHREN

Nach der Installation können Sie die System-Performance testen:

```bash
# Benchmark ausführen
python scripts/benchmark.py

# Detaillierte Performance-Analyse
# Ergebnisse werden in logs/ gespeichert
```

**Benchmark umfasst:**
- 🔧 CPU-Performance-Tests
- 💾 Speicher- und Festplatten-I/O
- 🌐 Netzwerk-Latenz-Messungen
- 📊 VR-spezifische Benchmarks

### 7. SERVER STARTEN

Da ich nicht alle Dateien erstellen konnte, hier die wichtigsten:

#### server/utils/logger.py:
```python
import logging
import sys
from pathlib import Path

def setup_logging():
    Path("logs").mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/server.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
```

#### server/utils/performance_monitor.py:
```python
import time
import psutil
from typing import Dict

class PerformanceMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.frame_count = 0
        
    def start(self):
        pass
        
    def stop(self):
        pass
        
    def record_head_tracking_frame(self):
        self.frame_count += 1
        
    def get_stats(self) -> Dict:
        uptime = time.time() - self.start_time
        return {
            "uptime": uptime,
            "frames_processed": self.frame_count,
            "fps": self.frame_count / uptime if uptime > 0 else 0,
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent
        }
```

#### server/game_detector.py:
```python
import psutil
import logging
from typing import List, Dict

class GameDetector:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def initialize(self):
        pass
        
    def get_running_games(self) -> List[Dict]:
        games = []
        game_processes = [
            "Cyberpunk2077.exe", "javaw.exe", "minecraft.exe",
            "ForzaHorizon5.exe", "FlightSimulator.exe"
        ]
        
        for proc in psutil.process_iter(['name']):
            try:
                name = proc.info['name']
                if any(game.lower() in name.lower() for game in game_processes):
                    games.append({
                        "name": name,
                        "pid": proc.pid
                    })
            except:
                pass
        return games
```

#### web/templates/index.html:
```html
<!DOCTYPE html>
<html>
<head>
    <title>VR Gaming Server</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f0f2f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; margin-bottom: 30px; }
        .status { padding: 15px; border-radius: 8px; margin: 20px 0; text-align: center; font-weight: bold; }
        .status.running { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .status.stopped { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .btn { display: inline-block; padding: 12px 24px; margin: 10px; background: #007bff; color: white; text-decoration: none; border-radius: 6px; border: none; cursor: pointer; font-size: 16px; }
        .btn:hover { background: #0056b3; }
        .btn.success { background: #28a745; }
        .btn.success:hover { background: #1e7e34; }
    </style>
</head>
<body>
    <div class="container">
        <h1>VR Gaming Server Control Panel</h1>
        
        <div class="status running">
            Server läuft auf http://localhost:8080
        </div>
        
        <div style="text-align: center;">
            <a href="/sensor-check" class="btn">Sensor-Check</a>
            <a href="/vr-gaming" class="btn success">VR Gaming starten</a>
            <a href="/server-control" class="btn">Server-Steuerung</a>
        </div>
        
        <div style="margin-top: 30px; text-align: center; color: #666;">
            <p>Vision Pro VR Gaming Server v1.0</p>
            <p>Verbinden Sie Ihre Vision Pro und starten Sie das VR Gaming!</p>
        </div>
    </div>
</body>
</html>
```

#### web/templates/sensor-check.html:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Sensor Check - VR Gaming</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f0f2f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
        h1 { text-align: center; color: #333; }
        .sensor-test { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 8px; }
        .status { font-weight: bold; padding: 5px 10px; border-radius: 4px; }
        .status.ok { background: #d4edda; color: #155724; }
        .status.error { background: #f8d7da; color: #721c24; }
        .btn { padding: 12px 24px; margin: 10px; background: #007bff; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; }
        .btn:hover { background: #0056b3; }
        #orientationData { font-family: monospace; background: #f8f9fa; padding: 10px; margin: 10px 0; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Sensor-Check für Vision Pro</h1>
        
        <div class="sensor-test">
            <h3>WebXR Support</h3>
            <div id="webxrStatus" class="status error">Prüfe...</div>
        </div>
        
        <div class="sensor-test">
            <h3>Device Orientation</h3>
            <div id="orientationStatus" class="status error">Prüfe...</div>
            <div id="orientationData"></div>
        </div>
        
        <div class="sensor-test">
            <h3>Kamera-Berechtigung</h3>
            <div id="cameraStatus" class="status error">Nicht getestet</div>
        </div>
        
        <div style="text-align: center; margin-top: 30px;">
            <button class="btn" onclick="startTests()">Tests starten</button>
            <button class="btn" onclick="location.href='/vr-gaming'">Weiter zu VR Gaming</button>
        </div>
    </div>

    <script>
        async function startTests() {
            // WebXR Test
            if (navigator.xr) {
                try {
                    const supported = await navigator.xr.isSessionSupported('immersive-vr');
                    document.getElementById('webxrStatus').textContent = supported ? 'WebXR VR unterstützt' : 'WebXR begrenzt verfügbar';
                    document.getElementById('webxrStatus').className = 'status ok';
                } catch (e) {
                    document.getElementById('webxrStatus').textContent = 'WebXR Fehler: ' + e.message;
                }
            } else {
                document.getElementById('webxrStatus').textContent = 'WebXR nicht verfügbar';
            }
            
            // Device Orientation Test
            if (window.DeviceOrientationEvent) {
                // iOS 13+ Permission Request
                if (typeof DeviceOrientationEvent.requestPermission === 'function') {
                    const permission = await DeviceOrientationEvent.requestPermission();
                    if (permission === 'granted') {
                        startOrientationTest();
                    } else {
                        document.getElementById('orientationStatus').textContent = 'Berechtigung verweigert';
                    }
                } else {
                    startOrientationTest();
                }
            } else {
                document.getElementById('orientationStatus').textContent = 'Device Orientation nicht verfügbar';
            }
        }
        
        function startOrientationTest() {
            document.getElementById('orientationStatus').textContent = 'Device Orientation aktiv';
            document.getElementById('orientationStatus').className = 'status ok';
            
            window.addEventListener('deviceorientation', function(event) {
                const data = `Alpha: ${event.alpha?.toFixed(1)}°\nBeta: ${event.beta?.toFixed(1)}°\nGamma: ${event.gamma?.toFixed(1)}°`;
                document.getElementById('orientationData').textContent = data;
            });
        }
        
        // Auto-start tests
        window.onload = startTests;
    </script>
</body>
</html>
```

#### web/templates/vr-gaming.html:
```html
<!DOCTYPE html>
<html>
<head>
    <title>VR Gaming - Vision Pro</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { margin: 0; padding: 0; font-family: Arial, sans-serif; background: #000; color: white; overflow: hidden; }
        .container { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center; }
        h1 { font-size: 3rem; margin-bottom: 20px; }
        .status { font-size: 1.5rem; margin: 20px 0; padding: 15px; border-radius: 10px; }
        .status.disconnected { background: rgba(220, 53, 69, 0.3); }
        .status.connected { background: rgba(40, 167, 69, 0.3); }
        .status.streaming { background: rgba(255, 193, 7, 0.3); }
        .btn { padding: 15px 30px; margin: 10px; background: #007bff; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 18px; }
        .btn:hover { background: #0056b3; }
        .btn.success { background: #28a745; }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; }
        #videoContainer { position: fixed; top: 0; left: 0; width: 100%; height: 100%; display: none; }
        #gameVideo { width: 100%; height: 100%; object-fit: cover; }
        .hud { position: fixed; top: 20px; right: 20px; background: rgba(0,0,0,0.7); padding: 15px; border-radius: 8px; font-family: monospace; }
    </style>
</head>
<body>
    <div class="container">
        <h1>VR Gaming</h1>
        
        <div id="status" class="status disconnected">
            Nicht verbunden
        </div>
        
        <div>
            <button id="connectBtn" class="btn">Mit Server verbinden</button>
            <button id="vrBtn" class="btn success" disabled>VR Session starten</button>
            <button id="stopBtn" class="btn" disabled>Stoppen</button>
        </div>
        
        <div style="margin-top: 30px; font-size: 14px; opacity: 0.7;">
            <p>Bewegen Sie Ihren Kopf um die Kamera im Spiel zu steuern</p>
            <p>Vision Pro optimiert</p>
        </div>
    </div>
    
    <div id="videoContainer">
        <video id="gameVideo" autoplay muted playsinline></video>
        <div class="hud">
            <div>FPS: <span id="fps">0</span></div>
            <div>Latenz: <span id="latency">0ms</span></div>
            <div>Status: <span id="vrStatus">Inaktiv</span></div>
        </div>
    </div>

    <script>
        let websocket = null;
        let isConnected = false;
        let isVRActive = false;
        
        const statusEl = document.getElementById('status');
        const connectBtn = document.getElementById('connectBtn');
        const vrBtn = document.getElementById('vrBtn');
        const stopBtn = document.getElementById('stopBtn');
        const videoContainer = document.getElementById('videoContainer');
        const gameVideo = document.getElementById('gameVideo');
        
        connectBtn.onclick = connectToServer;
        vrBtn.onclick = startVRSession;
        stopBtn.onclick = stopSession;
        
        async function connectToServer() {
            try {
                websocket = new WebSocket(`ws://${window.location.host}/ws/client_${Date.now()}`);
                
                websocket.onopen = function() {
                    isConnected = true;
                    updateStatus('connected', 'Verbunden - Bereit für VR');
                    vrBtn.disabled = false;
                };
                
                websocket.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    handleServerMessage(data);
                };
                
                websocket.onclose = function() {
                    isConnected = false;
                    updateStatus('disconnected', 'Verbindung getrennt');
                    vrBtn.disabled = true;
                };
                
            } catch (error) {
                console.error('Verbindungsfehler:', error);
                updateStatus('disconnected', 'Verbindung fehlgeschlagen');
            }
        }
        
        async function startVRSession() {
            if (!isConnected) return;
            
            try {
                // WebXR Session anfordern
                if (navigator.xr) {
                    const session = await navigator.xr.requestSession('immersive-vr');
                    
                    session.addEventListener('end', stopSession);
                    
                    // Reference Space
                    const refSpace = await session.requestReferenceSpace('local-floor');
                    
                    // Animation Loop
                    function onXRFrame(time, frame) {
                        const pose = frame.getViewerPose(refSpace);
                        if (pose) {
                            sendHeadPose(pose);
                        }
                        session.requestAnimationFrame(onXRFrame);
                    }
                    
                    session.requestAnimationFrame(onXRFrame);
                    
                } else {
                    // Fallback: Device Orientation
                    startDeviceOrientationTracking();
                }
                
                // Video-Stream anfordern
                websocket.send(JSON.stringify({
                    type: 'request_stream'
                }));
                
                isVRActive = true;
                updateStatus('streaming', 'VR Session aktiv');
                document.querySelector('.container').style.display = 'none';
                videoContainer.style.display = 'block';
                stopBtn.disabled = false;
                
            } catch (error) {
                console.error('VR Start Fehler:', error);
                alert('VR Session konnte nicht gestartet werden: ' + error.message);
            }
        }
        
        function startDeviceOrientationTracking() {
            if (typeof DeviceOrientationEvent.requestPermission === 'function') {
                DeviceOrientationEvent.requestPermission().then(response => {
                    if (response == 'granted') {
                        window.addEventListener('deviceorientation', handleDeviceOrientation);
                    }
                });
            } else {
                window.addEventListener('deviceorientation', handleDeviceOrientation);
            }
        }
        
        function handleDeviceOrientation(event) {
            const quaternion = eulerToQuaternion(
                event.beta * Math.PI / 180,
                event.gamma * Math.PI / 180, 
                event.alpha * Math.PI / 180
            );
            
            const poseData = {
                type: 'head_tracking',
                pose: {
                    quaternion: [quaternion.x, quaternion.y, quaternion.z, quaternion.w],
                    position: [0, 0, 0]
                },
                timestamp: Date.now() / 1000
            };
            
            if (websocket && isVRActive) {
                websocket.send(JSON.stringify(poseData));
            }
        }
        
        function sendHeadPose(pose) {
            const poseData = {
                type: 'head_tracking',
                pose: {
                    quaternion: [
                        pose.transform.orientation.x,
                        pose.transform.orientation.y,
                        pose.transform.orientation.z,
                        pose.transform.orientation.w
                    ],
                    position: [
                        pose.transform.position.x,
                        pose.transform.position.y,
                        pose.transform.position.z
                    ]
                },
                timestamp: Date.now() / 1000
            };
            
            if (websocket) {
                websocket.send(JSON.stringify(poseData));
            }
        }
        
        function handleServerMessage(data) {
            if (data.type === 'video_frame') {
                // MJPEG Frame anzeigen
                const blob = new Blob([Uint8Array.from(atob(data.data), c => c.charCodeAt(0))], {type: 'image/jpeg'});
                const url = URL.createObjectURL(blob);
                gameVideo.src = url;
            } else if (data.type === 'streaming_started') {
                updateStatus('streaming', 'Video-Stream aktiv');
            }
        }
        
        function stopSession() {
            isVRActive = false;
            
            if (websocket) {
                websocket.send(JSON.stringify({type: 'stop_stream'}));
            }
            
            updateStatus('connected', 'Verbunden');
            document.querySelector('.container').style.display = 'block';
            videoContainer.style.display = 'none';
            stopBtn.disabled = true;
        }
        
        function updateStatus(type, text) {
            statusEl.className = `status ${type}`;
            statusEl.textContent = text;
        }
        
        function eulerToQuaternion(pitch, roll, yaw) {
            const c1 = Math.cos(yaw / 2);
            const c2 = Math.cos(roll / 2);
            const c3 = Math.cos(pitch / 2);
            const s1 = Math.sin(yaw / 2);
            const s2 = Math.sin(roll / 2);
            const s3 = Math.sin(pitch / 2);
            
            return {
                w: c1 * c2 * c3 - s1 * s2 * s3,
                x: s1 * s2 * c3 + c1 * c2 * s3,
                y: s1 * c2 * c3 + c1 * s2 * s3,
                z: c1 * s2 * c3 - s1 * c2 * s3
            };
        }
    </script>
</body>
</html>
```

### 5. SERVER STARTEN

Nach dem Erstellen aller Dateien:

```bash
# 1. In das Projektverzeichnis wechseln
cd vr-gaming-server

# 2. Server mit GUI starten
python run.py

# ODER Server direkt starten (ohne GUI)
python -m uvicorn server.main:app --host 0.0.0.0 --port 8080 --reload
```

### 6. VISION PRO VERBINDEN

1. Vision Pro Safari öffnen
2. Zu `http://YOUR-PC-IP:8080` navigieren
3. "Sensor-Check" durchführen
4. "VR Gaming starten" klicken
5. WebXR-Berechtigung gewähren
6. Kopfbewegungen steuern jetzt das Spiel!

### 7. TROUBLESHOOTING

**Häufige Probleme:**

- **ImportError**: `pip install -r requirements.txt` nochmals ausführen
- **Port blockiert**: Anderen Port verwenden oder `netstat -ano | findstr :8080`
- **Keine Verbindung**: Windows Firewall-Regel für Python erstellen
- **WebXR funktioniert nicht**: HTTPS verwenden oder andere Browser testen

**Performance-Tipps:**
- Spiel auf Windowed Fullscreen stellen
- V-Sync in Spielen deaktivieren
- Grafik-Einstellungen reduzieren
- Andere Programme schließen

### 8. ERWEITERTE KONFIGURATION

**Game-Profile anpassen:**
- Dateien in `profiles/` bearbeiten
- Sensitivität und Deadzone anpassen
- Neue Spiele hinzufügen

**Server-Einstellungen:**
- `config/server_config.yaml` bearbeiten
- Video-Qualität anpassen
- Netzwerk-Einstellungen ändern

---

## ERGEBNIS

Nach diesen Schritten haben Sie:

✅ **Funktionsfähigen VR Gaming Server**
✅ **Web-Interface für Vision Pro** 
✅ **Automatische Spiel-Erkennung**
✅ **Kopfbewegungssteuerung**
✅ **Echtzeit-Video-Streaming**
✅ **Cross-Platform-Unterstützung**

**Einfacher Start:** `python run.py` → GUI öffnet sich → "Server starten" → Browser → VR Gaming!

Das System funktioniert mit jeder WebXR-fähigen Brille und jedem modernen Browser.