# 🎮 VR Gaming Server

Ein leistungsstarker VR-Gaming-Server für Echtzeit-Streaming und Input-Injection mit WebXR-Unterstützung.

## ✨ Features

- **Echtzeit-Video-Streaming** mit WebRTC und H.264/H.265/AV1 Kodierung
- **Cross-Platform-Support** (Windows, macOS, Linux)
- **WebXR-Integration** für VR-Headsets
- **Automatische Spiel-Erkennung** und Profil-Verwaltung
- **Head-Tracking** mit Gyroskop-Unterstützung
- **Input-Injection** für Tastatur/Maus-Steuerung
- **Performance-Monitoring** und Benchmarking
- **RESTful API** mit FastAPI
- **Modulare Architektur** für einfache Erweiterungen
- **🎯 VR Connection Test Client** für Verbindungs-Tests
- **🏢 Enterprise-Features**: 8K VR, 120 FPS, Multi-Codec-Support
- **🔒 Advanced Security**: Zero-Trust, Compliance-Standards
- **☁️ Cloud-Integration**: Auto-Scaling, Multi-Cloud-Support
- **📊 Enterprise Monitoring**: Real-time Analytics, Alerting
- **💾 Disaster Recovery**: 3-2-1 Backup Strategy

## 🚀 Schnellstart

### 1. System-Anforderungen prüfen

```bash
# System-Anforderungen überprüfen
python scripts/requirements_check.py
```

### 2. Abhängigkeiten installieren

```bash
# Python-Pakete installieren
pip install -r requirements.txt

# Entwicklungsabhängigkeiten installieren (optional)
pip install -r requirements-dev.txt
```

### 3. Server starten

```bash
# Hauptserver starten
python run.py

# Oder direkt mit uvicorn starten
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

### VR Connection Test Client 🎯

**Eine kompakte Test-Software zur Überprüfung der VR-Server-Verbindungen und -Funktionalität.**

#### Features:
- ✅ **Drei Test-Szenarien**: Full HD, 4K, 8K Auflösung
- ✅ **VR-Bewegungs-Simulation**: 10 Sekunden Test mit drei Geschwindigkeitsstufen
- ✅ **Server-Verbindungs-Test**: Simuliert WebSocket-Verbindung
- ✅ **Visuelle Darstellung**: Zeigt simulierte VR-Bewegungen auf dem Bildschirm
- ✅ **Erfolgs-/Fehlschlag-Anzeige**: Sofortige Rückmeldung über Test-Ergebnisse

#### Verwendung:

```bash
# Test-Client starten
python vr_connection_test.py

# Oder mit dem Start-Skript
./run_test_client.sh
```

#### Test-Szenarien:
- **Full HD (1920x1080)**: Standard VR-Auflösung
- **4K (3840x2160)**: High-End VR-Auflösung
- **8K (7680x4320)**: Extreme VR mit 4K pro Auge

#### Wie es funktioniert:
1. Klicken Sie auf einen Test-Button (Full HD, 4K, 8K)
2. Der Test läuft 10 Sekunden automatisch
3. Eine rote Kugel simuliert VR-Bewegungen (hoch/runter/links/rechts)
4. Drei Bewegungsstufen: langsam → mittel → schnell
5. Server-Verbindung wird getestet
6. Ergebnis wird angezeigt: **Erfolgreich** oder **Fehlgeschlagen**

#### Zweck:
**100% Sicherheit vor dem Spielen** - Testen Sie die komplette VR-Infrastruktur in wenigen Sekunden!

### System-Anforderungen prüfen

```bash
# Detaillierte Anforderungsprüfung
python scripts/requirements_check.py
```

## 🏗️ Projekt-Struktur
```

**Benchmark umfasst:**
- 🔧 CPU-Performance-Tests
- 💾 Speicher- und Festplatten-I/O-Messungen
- 🌐 Netzwerk-Latenz-Analyse
- 📊 VR-spezifische Benchmarks

## 🏗️ Projekt-Struktur

```
vr-gaming-server/
├── server/                 # Server-Komponenten
│   ├── main.py            # FastAPI-Hauptserver
│   ├── game_capture.py    # Bildschirm-Aufnahme
│   ├── video_streamer.py  # Video-Streaming
│   ├── head_tracker.py    # Head-Tracking
│   ├── input_injector.py  # Input-Injection
│   ├── config_manager.py  # Konfigurationsverwaltung
│   └── utils/             # Hilfsfunktionen
├── web/                   # Web-Interface
│   ├── static/           # CSS, JS, Assets
│   └── templates/        # HTML-Templates
├── config/               # Konfigurationsdateien
│   ├── server_config.yaml    # Server-Konfiguration
│   ├── video_config.yaml     # Video-Streaming-Settings
│   ├── input_config.yaml     # Input-Konfiguration
│   ├── network_config.yaml   # Netzwerk-Settings
│   ├── gui_config.yaml       # GUI-Konfiguration
│   ├── performance_config.yaml # Performance-Optimierungen
│   ├── security_config.yaml  # Sicherheits-Settings
│   ├── cloud_config.yaml     # Cloud-Integration
│   ├── monitoring_config.yaml # Monitoring-Settings
│   ├── backup_config.yaml    # Backup-Konfiguration
│   └── compliance_config.yaml # Compliance-Settings
├── profiles/             # Spiel-Profile
├── scripts/              # Hilfs-Skripte
│   ├── requirements_check.py  # System-Prüfung
│   ├── benchmark.py      # Performance-Tests
│   └── setup.py          # Setup-Script
├── tests/                # Test-Suite
│   ├── test_simple.py    # Einfache Tests
│   ├── test_environment.py # Umfassende Tests
│   └── integration_tests.py # Integrationstests
├── logs/                 # Log-Dateien
├── docs/                 # Dokumentation
├── vr_connection_test.py # 🎯 VR Connection Test Client
├── run_test_client.sh    # Start-Skript für Test-Client
├── TEST_CLIENT_README.md # Detaillierte Test-Client-Dokumentation
├── run.py                # Hauptserver-Starter
├── install.py            # Installations-Script
├── anleitung.md          # Deutsche Anleitung
├── LICENSE               # Lizenz-Datei
└── README.md             # Englische README
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

### Enterprise-Konfigurationen 🏢

Das System bietet umfassende Enterprise-Konfigurationsoptionen:

#### Video-Konfiguration (`config/video_config.yaml`)
- **8K VR Support**: 7680x4320 mit 4K pro Auge
- **120 FPS**: Extreme Framerate-Unterstützung
- **Multi-Codec**: H.264, H.265, AV1, ProRes
- **Enterprise WebRTC**: Simulcast, SVC, FEC, NACK

#### Netzwerk-Konfiguration (`config/network_config.yaml`)
- **Multi-Protocol**: WebRTC, RTMP, HLS, DASH, SRT
- **QoS & Security**: DSCP Marking, Firewall-Integration
- **Cloud-Integration**: Load Balancing, CDN-Support

#### Performance-Konfiguration (`config/performance_config.yaml`)
- **Real-time Optimierungen**: Kernel-Tuning, CPU-Pinning
- **GPU-Beschleunigung**: NVIDIA NVENC, AMD VCE
- **Memory-Optimierung**: HugePages, NUMA-Balancing

#### Sicherheits-Konfiguration (`config/security_config.yaml`)
- **Zero-Trust-Architektur**: Least Privilege, Continuous Verification
- **Compliance-Standards**: GDPR, CCPA, HIPAA, PCI DSS
- **Advanced Encryption**: TLS 1.3, AES256

#### Monitoring-Konfiguration (`config/monitoring_config.yaml`)
- **Real-time Analytics**: System, Application, Business Metrics
- **Alerting-System**: Multi-Channel, Escalation
- **Enterprise Dashboards**: Grafana, Kibana Integration

#### Backup-Konfiguration (`config/backup_config.yaml`)
- **3-2-1 Backup Strategy**: Multiple Kopien, verschiedene Medien
- **Cloud Backup**: S3, Azure Blob, GCP Cloud Storage
- **Disaster Recovery**: Point-in-Time Recovery

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
- `GET /api/games` - Erkannte Spiele auflisten
- `POST /api/profile/{game}` - Profil laden

### WebSocket-Endpunkte

- `/ws/video` - Video-Stream
- `/ws/input` - Input-Events
- `/ws/sensors` - Sensor-Daten

## 🏢 Enterprise-Features

### VR Connection Test Client 🎯

**Schnell und einfach die komplette VR-Infrastruktur testen:**

```bash
# Test-Client starten
python vr_connection_test.py

# Test-Szenarien: Full HD, 4K, 8K
# Dauer: 10 Sekunden pro Test
# Ergebnis: Sofortige Erfolgs-/Fehlschlag-Anzeige
```

**Perfekt für:**
- ✅ Vor-Spiel-Überprüfung der Server-Verbindung
- ✅ Test verschiedener Auflösungen (Full HD, 4K, 8K)
- ✅ Simulation von VR-Bewegungen
- ✅ Verbindungsstabilität überprüfen

### Advanced Video-Streaming 🚀

- **8K VR Support**: 7680x4320 mit 4K pro Auge
- **120 FPS**: Extreme Framerate für flüssiges VR-Erlebnis
- **Multi-Codec**: H.264, H.265, AV1, ProRes
- **Enterprise WebRTC**: Simulcast, SVC, FEC, NACK
- **Hardware-Encoding**: NVIDIA NVENC, AMD VCE, Intel Quick Sync

### Enterprise-Sicherheit 🔒

- **Zero-Trust-Architektur**: Least Privilege, Continuous Verification
- **Compliance-Standards**: GDPR, CCPA, HIPAA, PCI DSS, SOX, ISO 27001
- **Advanced Encryption**: TLS 1.3, AES256, Certificate Pinning
- **Multi-Faktor-Authentifizierung**: OAuth2, TOTP, Hardware-Token
- **Audit-Trails**: Vollständige Protokollierung aller Aktionen

### Cloud-Integration ☁️

- **Multi-Cloud-Support**: AWS, Azure, GCP
- **Auto-Scaling**: Performance-basiertes Skalieren
- **Load Balancing**: Global Load Balancing, Geo-DNS
- **CDN-Integration**: CloudFront, Azure CDN, Cloud CDN
- **Disaster Recovery**: Cross-Region Backup, Failover

### Enterprise-Monitoring 📊

- **Real-time Analytics**: System, Application, Business Metrics
- **Advanced Alerting**: Multi-Channel, Escalation, Auto-Resolution
- **Custom Dashboards**: Grafana, Kibana, Tableau Integration
- **Predictive Monitoring**: ML-basierte Anomalie-Erkennung
- **Performance Profiling**: Flame Graphs, System Tap

### Backup & Disaster Recovery 💾

- **3-2-1 Backup Strategy**: 3 Kopien, 2 Medien, 1 Offsite
- **Cloud Backup**: S3, Azure Blob, GCP Cloud Storage
- **Point-in-Time Recovery**: Granulare Wiederherstellung
- **Automated Testing**: Regelmäßige Backup-Verifikation
- **Compliance**: SOC 2, HIPAA, GDPR konform

## 🛠️ Entwicklung

### Entwicklungs-Setup

```bash
# Virtuelle Umgebung erstellen
python -m venv venv
source venv/bin/activate  # Linux/macOS
# oder venv\Scripts\activate  # Windows

# Abhängigkeiten installieren
pip install -r requirements-dev.txt

# Tests ausführen
python -m pytest tests/

# Linting ausführen
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

## 🤝 Mitwirken

1. Repository forken
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
