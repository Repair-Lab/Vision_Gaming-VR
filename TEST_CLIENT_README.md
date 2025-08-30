# VR Gaming Server - Connection Test Client

## Übersicht

Der **VR Connection Test Client** ist eine kleine Test-Software, die simuliert, ob die Verbindungen zum VR Gaming Server funktionieren. Sie testet in drei Szenarien: Full HD, 4K und 8K, mit jeweils 10 Sekunden Simulation von VR-Bewegungen.

## Features

- **Drei Test-Szenarien**: Full HD (1920x1080), 4K (3840x2160), 8K (7680x4320)
- **VR-Bewegungs-Simulation**: Hoch, runter, links, rechts in drei Geschwindigkeitsstufen
- **Server-Verbindungs-Test**: Simuliert die Verbindung zum VR Gaming Server
- **Visuelle Darstellung**: Zeigt die simulierten Bewegungen auf dem Bildschirm
- **Test-Ergebnisse**: Zeigt Erfolg/Fehlschlag für jeden Test an

## Installation

1. Stellen Sie sicher, dass alle Abhängigkeiten installiert sind:
```bash
pip install -r requirements.txt
```

2. Die Software verwendet Pygame für die GUI und WebSockets für die Server-Kommunikation.

## Verwendung

1. Starten Sie den Test-Client:
```bash
python vr_connection_test.py
```

2. Klicken Sie auf einen der drei Test-Buttons:
   - **Test Full HD**: Testet in Full HD Auflösung
   - **Test 4K**: Testet in 4K Auflösung
   - **Test 8K**: Testet in 8K Auflösung

3. Jeder Test läuft automatisch 10 Sekunden und zeigt:
   - Eine rote Kugel, die sich bewegt
   - Drei Bewegungsstufen (langsam → mittel → schnell)
   - Einen Fortschrittsbalken
   - Server-Verbindungsstatus

4. Nach jedem Test wird das Ergebnis angezeigt:
   - **Erfolgreich**: Test lief 10 Sekunden und Verbindung war stabil
   - **Fehlgeschlagen**: Test wurde unterbrochen oder Verbindung fehlte

## Wie es funktioniert

### Test-Szenarien
- **Full HD**: Simuliert VR in 1920x1080 (Standard-VR)
- **4K**: Simuliert VR in 3840x2160 (High-End VR)
- **8K**: Simuliert VR in 7680x4320 (Extreme VR mit 4K pro Auge)

### Bewegungs-Simulation
Die Software simuliert VR-Bewegungen durch:
1. **Langsam** (0-3.33s): Grundlegende Bewegungen
2. **Mittel** (3.33-6.67s): Erhöhte Geschwindigkeit
3. **Schnell** (6.67-10s): Maximale Geschwindigkeit

### Server-Verbindung
- Simuliert eine WebSocket-Verbindung zum VR Gaming Server
- Testet die Stabilität der Verbindung über 10 Sekunden
- Zeigt Verbindungsstatus in Echtzeit an

## Technische Details

- **Programmiersprache**: Python 3.8+
- **GUI-Framework**: Pygame
- **Netzwerk**: WebSockets (websockets Bibliothek)
- **Auflösungen**: Full HD, 4K, 8K
- **Test-Dauer**: 10 Sekunden pro Szenario
- **Bewegungsstufen**: 3 Stufen (langsam, mittel, schnell)

## Anforderungen

- Python 3.8 oder höher
- Pygame für die GUI
- websockets für Server-Kommunikation
- OpenGL-kompatible Grafikkarte (für Pygame)

## Fehlerbehebung

### Pygame-Import-Fehler
```bash
pip install pygame==2.5.2
```

### WebSocket-Verbindungsfehler
- Stellen Sie sicher, dass der VR Gaming Server läuft
- Überprüfen Sie die Server-Konfiguration in `config/server_config.yaml`
- Kontrollieren Sie Firewall-Einstellungen

### Performance-Probleme
- Bei 8K-Tests kann es zu Performance-Einbußen kommen
- Schließen Sie andere Anwendungen während des Tests
- Verwenden Sie eine dedizierte Grafikkarte

## Integration mit VR Gaming Server

Der Test-Client ist so konzipiert, dass er:
- Die gleichen Netzwerkprotokolle verwendet wie der Hauptserver
- Kompatibel ist mit der Server-Konfiguration
- Die gleichen Video-Codecs und Auflösungen testet
- Eine realistische Simulation der VR-Erfahrung bietet

## Erweiterte Features (zukünftig)

- **Echte WebRTC-Verbindung**: Direkte Verbindung zum Server
- **Hardware-Beschleunigung**: GPU-Beschleunigte Tests
- **Multi-Threading**: Parallele Tests für verschiedene Auflösungen
- **Automatisierte Tests**: CI/CD Integration
- **Performance-Metriken**: Detaillierte Analyse der Test-Ergebnisse

## Support

Bei Problemen:
1. Überprüfen Sie die Konsolen-Ausgabe für Fehlermeldungen
2. Stellen Sie sicher, dass alle Abhängigkeiten installiert sind
3. Testen Sie mit niedrigeren Auflösungen zuerst
4. Kontaktieren Sie den Support für komplexe Probleme

---

**Entwickelt für VR Gaming Server Enterprise Edition**
**Version 1.0.0 - 30. August 2025**
