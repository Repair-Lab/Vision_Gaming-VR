# 🎮 VR Gaming Server

Ein leistungsstarker VR-Gaming-Server für Echtzeit-Streaming und Input-Injection mit WebXR-Unterstützung.

## ✨ Features

- **Echtzeit-Video-Streaming** mit WebRTC und H.264/H.265
- **Cross-Platform-Support** (Windows, macOS, Linux)
- **WebXR-Integration** für VR-Headsets
- **Automatische Spiel-Erkennung** und Profil-Verwaltung
- **Head-Tracking** mit Gyroskop-Unterstützung
- **Input-Injection** für Tastatur/Maus-Steuerung
- **Performance-Monitoring** und Benchmarking
- **RESTful API** mit FastAPI
- **Modulare Architektur** für einfache Erweiterungen

## 🚀 Schnellstart

### 1. Anforderungen prüfen

```bash
# System-Anforderungen überprüfen
python scripts/requirements_check.py
```

### 2. Abhängigkeiten installieren

```bash
# Python-Pakete installieren
pip install -r requirements.txt

# Entwicklungsabhängigkeiten (optional)
pip install -r requirements-dev.txt
```

### 3. Server starten

```bash
# Hauptserver starten
python run.py

# Oder direkt mit uvicorn
uvicorn server.main:app --host 0.0.0.0 --port 8000
```

### 4. Web-Interface öffnen

Öffnen Sie `http://localhost:8000` in Ihrem Browser.

## 📊 Performance-Benchmark

Führen Sie System-Performance-Tests durch:

```bash
# Vollständigen Benchmark ausführen
python scripts/benchmark.py

# Ergebnisse werden in logs/performance.log gespeichert
```

## 🧪 Tests und Qualitätssicherung

### Umgebungs-Test

Führen Sie einen schnellen System-Test durch:

```bash
# Einfacher Umgebungs-Test
python tests/test_simple.py

# Umfassende Test-Suite
python tests/test_environment.py
```

### System-Anforderungen prüfen

```bash
# Detaillierte Anforderungsprüfung
python scripts/requirements_check.py
```

## 🏗️ Projekt-Struktur

```
vr-gaming-server/
├── server/                 # Server-Komponenten
│   ├── main.py            # FastAPI-Hauptserver
│   ├── game_capture.py    # Bildschirm-Capture
│   ├── video_streamer.py  # Video-Streaming
│   ├── head_tracker.py    # Head-Tracking
│   ├── input_injector.py  # Input-Injection
│   ├── config_manager.py  # Konfigurationsverwaltung
│   └── utils/             # Hilfsfunktionen
├── web/                   # Web-Interface
│   ├── static/           # CSS, JS, Assets
│   └── templates/        # HTML-Templates
├── config/               # Konfigurationsdateien
├── profiles/             # Spiel-Profile
├── scripts/              # Hilfs-Skripte
│   ├── requirements_check.py  # System-Prüfung
│   ├── benchmark.py      # Performance-Tests
│   └── setup.py          # Setup-Script
├── logs/                 # Log-Dateien
└── docs/                 # Dokumentation
```

## ⚙️ Konfiguration

### Server-Konfiguration

Bearbeiten Sie `config/server_config.yaml`:

```yaml
server:
  host: "0.0.0.0"
  port: 8000
  workers: 4
  log_level: "INFO"

video:
  resolution: "1920x1080"
  fps: 60
  codec: "h264"
  bitrate: "8000k"

input:
  mouse_sensitivity: 1.0
  keyboard_layout: "de"
  gesture_recognition: true
```

### Spiel-Profile

Spiel-spezifische Profile in `profiles/games/`:

- `cyberpunk2077.json` - Cyberpunk 2077 Optimierungen
- `minecraft.json` - Minecraft VR-Modus
- `forza.json` - Forza Horizon Racing
- `flight-sim.json` - Microsoft Flight Simulator

## 🔧 API-Endpunkte

### Haupt-Endpunkte

- `GET /` - Web-Interface
- `GET /api/status` - Server-Status
- `POST /api/start-stream` - Streaming starten
- `POST /api/stop-stream` - Streaming stoppen
- `GET /api/games` - Verfügbare Spiele
- `POST /api/profile/{game}` - Profil laden

### WebSocket-Endpunkte

- `/ws/video` - Video-Stream
- `/ws/input` - Input-Events
- `/ws/sensors` - Sensor-Daten

## 🛠️ Entwicklung

### Setup für Entwickler

```bash
# Virtuelle Umgebung erstellen
python -m venv venv
source venv/bin/activate  # Linux/macOS
# oder venv\Scripts\activate  # Windows

# Abhängigkeiten installieren
pip install -r requirements-dev.txt

# Tests ausführen
python -m pytest tests/

# Linting
python -m flake8 server/ web/
```

### Neue Features hinzufügen

1. Neue Server-Komponente in `server/` erstellen
2. API-Endpunkte in `server/main.py` hinzufügen
3. Web-Interface in `web/templates/` erweitern
4. Tests in `tests/` schreiben

## 📈 Monitoring

### Performance-Metriken

Der Server sammelt automatisch:

- CPU- und RAM-Auslastung
- Netzwerk-Latenz
- Frame-Rate und Encoding-Zeit
- Speicher- und Festplatten-I/O

### Logs

Logs werden in `logs/` gespeichert:

- `server.log` - Hauptserver-Logs
- `performance.log` - Performance-Metriken
- `errors.log` - Fehlerprotokolle

## 🔒 Sicherheit

- HTTPS-Unterstützung mit SSL-Zertifikaten
- API-Key-Authentifizierung
- Netzwerk-Firewall-Konfiguration
- Sichere WebSocket-Verbindungen

## 📚 Dokumentation

Detaillierte Dokumentation in `docs/`:

- `API.md` - Vollständige API-Referenz
- `INSTALLATION.md` - Detaillierte Installationsanleitung
- `TROUBLESHOOTING.md` - Fehlerbehebung

## 🤝 Beitragen

1. Fork das Repository
2. Feature-Branch erstellen (`git checkout -b feature/AmazingFeature`)
3. Änderungen committen (`git commit -m 'Add some AmazingFeature'`)
4. Branch pushen (`git push origin feature/AmazingFeature`)
5. Pull Request erstellen

## 📄 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe `LICENSE` für Details.

## 🙏 Danksagungen

- FastAPI für das hervorragende Web-Framework
- OpenCV für Computer-Vision-Funktionen
- WebRTC für Echtzeit-Kommunikation
- WebXR für VR-Integration

---

**Hinweis:** Dies ist ein Enterprise-Qualitäts-VR-Gaming-Server mit Produktionsbereitschaft. Stellen Sie sicher, dass Ihr System die Hardware-Anforderungen erfüllt.
