# VR Gaming Server - AI Installation Guide
## Vollautomatische Systeminstallation und Konfiguration

**Datum:** 31. August 2025
**Version:** 1.0
**Ziel:** Vollständige, autonome Installation des VR Gaming Server Systems

---

## 🎯 MISSION BRIEFING

**KI-Auftrag:** Installiere und konfiguriere das VR Gaming Server System vollständig auf dem Zielsystem. Stelle sicher, dass alle Komponenten funktionieren und das System bereit für VR-Gaming ist.

**Erfolgskriterien:**
- ✅ Alle Abhängigkeiten installiert
- ✅ Python-Umgebung korrekt eingerichtet
- ✅ VR Gaming Server läuft stabil
- ✅ Connection Tests erfolgreich
- ✅ Web-Interface zugänglich
- ✅ Plattformspezifische Optimierungen angewendet

---

## 🔍 SYSTEM ANALYSE

### 1. Betriebssystem erkennen
```bash
# Automatische OS-Erkennung
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    OS="windows"
else
    echo "❌ Unbekanntes Betriebssystem: $OSTYPE"
    exit 1
fi
echo "✅ Erkanntes OS: $OS"
```

### 2. Systemanforderungen prüfen
```bash
# Mindestanforderungen
MIN_PYTHON="3.8"
MIN_MEMORY="4GB"
MIN_DISK="2GB"

# Python-Version prüfen
python_version=$(python3 --version 2>&1 | awk '{print $2}')
if [[ "$(printf '%s\n' "$MIN_PYTHON" "$python_version" | sort -V | head -n1)" != "$MIN_PYTHON" ]]; then
    echo "❌ Python $MIN_PYTHON oder höher erforderlich. Gefunden: $python_version"
    exit 1
fi

# Speicher prüfen (vereinfacht)
if [[ "$OS" == "linux" ]]; then
    total_mem=$(free -m | awk 'NR==2{printf "%.0f", $2/1024}')
elif [[ "$OS" == "macos" ]]; then
    total_mem=$(echo "$(sysctl -n hw.memsize) / 1024 / 1024 / 1024" | bc)
elif [[ "$OS" == "windows" ]]; then
    total_mem=$(wmic computersystem get totalphysicalmemory /value | awk -F= '{print int($2/1024/1024/1024)}')
fi

if [[ $total_mem -lt 4 ]]; then
    echo "❌ Mindestens 4GB RAM erforderlich. Gefunden: ${total_mem}GB"
    exit 1
fi

echo "✅ Systemanforderungen erfüllt"
```

---

## 📦 PHASE 1: GRUNDLAGEN INSTALLIEREN

### 1.1 Paketmanager aktualisieren
```bash
case $OS in
    "linux")
        # Distribution erkennen
        if command -v apt &> /dev/null; then
            PACKAGE_MANAGER="apt"
            sudo apt update && sudo apt upgrade -y
        elif command -v dnf &> /dev/null; then
            PACKAGE_MANAGER="dnf"
            sudo dnf update -y
        elif command -v pacman &> /dev/null; then
            PACKAGE_MANAGER="pacman"
            sudo pacman -Syu --noconfirm
        fi
        ;;
    "macos")
        # Homebrew installieren falls nicht vorhanden
        if ! command -v brew &> /dev/null; then
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        brew update
        ;;
    "windows")
        # Chocolatey installieren falls nicht vorhanden
        if ! command -v choco &> /dev/null; then
            powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))"
        fi
        choco upgrade chocolatey -y
        ;;
esac
```

### 1.2 Grundlegende Abhängigkeiten installieren
```bash
case $OS in
    "linux")
        case $PACKAGE_MANAGER in
            "apt")
                sudo apt install -y python3 python3-pip python3-venv git curl wget build-essential libssl-dev libffi-dev python3-dev
                ;;
            "dnf")
                sudo dnf install -y python3 python3-pip git curl wget gcc gcc-c++ openssl-devel libffi-devel python3-devel
                ;;
            "pacman")
                sudo pacman -S --noconfirm python python-pip git curl wget base-devel openssl libffi
                ;;
        esac
        ;;
    "macos")
        brew install python3 git curl wget
        ;;
    "windows")
        choco install -y python3 git curl wget
        ;;
esac
```

---

## 🐍 PHASE 2: PYTHON-UMGEBUNG EINRICHTEN

### 2.1 Virtuelle Umgebung erstellen
```bash
# Arbeitsverzeichnis erstellen
PROJECT_DIR="$HOME/vr-gaming-server"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Virtuelle Umgebung erstellen
python3 -m venv vr_env
source vr_env/bin/activate  # Linux/macOS
# oder: vr_env\Scripts\activate  # Windows

# Pip aktualisieren
python -m pip install --upgrade pip setuptools wheel
```

### 2.2 Projekt klonen und Abhängigkeiten installieren
```bash
# Repository klonen
if [[ ! -d ".git" ]]; then
    git clone https://github.com/Repair-Lab/Vision_Gaming-VR.git .
fi

# Abhängigkeiten installieren
pip install -r requirements.txt

# Entwicklungsabhängigkeiten (optional)
if [[ -f "requirements-dev.txt" ]]; then
    pip install -r requirements-dev.txt
fi
```

---

## ⚙️ PHASE 3: SYSTEMKONFIGURATION

### 3.1 Konfigurationsdateien vorbereiten
```bash
# Konfigurationsverzeichnis erstellen
mkdir -p config

# Standardkonfigurationen kopieren falls nicht vorhanden
if [[ ! -f "config/server_config.yaml" ]]; then
    cp config.yaml config/server_config.yaml
fi

# Plattformspezifische Konfiguration anpassen
case $OS in
    "linux")
        # Linux-spezifische Einstellungen
        sed -i 's/platform: .*/platform: linux/' config/server_config.yaml
        ;;
    "macos")
        # macOS-spezifische Einstellungen
        sed -i '' 's/platform: .*/platform: macos/' config/server_config.yaml
        ;;
    "windows")
        # Windows-spezifische Einstellungen
        sed -i 's/platform: .*/platform: windows/' config/server_config.yaml
        ;;
esac
```

### 3.2 Firewall und Netzwerk konfigurieren
```bash
case $OS in
    "linux")
        # UFW Firewall konfigurieren
        sudo ufw allow 8080/tcp  # Web-Interface
        sudo ufw allow 5000/tcp  # VR Server
        sudo ufw --force enable
        ;;
    "macos")
        # Firewall-Regeln (vereinfacht)
        echo "macOS Firewall sollte manuell konfiguriert werden für Ports 8080 und 5000"
        ;;
    "windows")
        # Windows Firewall
        powershell -Command "New-NetFirewallRule -DisplayName 'VR Gaming Server Web' -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow"
        powershell -Command "New-NetFirewallRule -DisplayName 'VR Gaming Server VR' -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow"
        ;;
esac
```

---

## 🚀 PHASE 4: VR GAMING SERVER INSTALLIEREN

### 4.1 Server-Komponenten installieren
```bash
# Python-Module für VR-Funktionalität installieren
pip install opencv-python-headless numpy pillow flask flask-socketio eventlet

# Plattformspezifische Treiber installieren
case $OS in
    "linux")
        # Linux-spezifische Bibliotheken
        pip install pyautogui pyscreenshot
        ;;
    "macos")
        # macOS-spezifische Bibliotheken
        pip install pyobjc-framework-Quartz pyobjc-framework-CoreGraphics
        ;;
    "windows")
        # Windows-spezifische Bibliotheken
        pip install pywin32 pyautogui
        ;;
esac
```

### 4.2 Web-Interface vorbereiten
```bash
# Web-Verzeichnis prüfen
if [[ ! -d "web" ]]; then
    echo "❌ Web-Verzeichnis nicht gefunden!"
    exit 1
fi

# Berechtigungen setzen
chmod +x run.py
chmod +x scripts/*.py
```

---

## 🧪 PHASE 5: TESTS UND VALIDIERUNG

### 5.1 Verbindungstest durchführen
```bash
# VR Connection Test ausführen
echo "🔍 Führe VR Connection Test durch..."
python3 vr_connection_test.py --auto

if [[ $? -eq 0 ]]; then
    echo "✅ VR Connection Test erfolgreich"
else
    echo "❌ VR Connection Test fehlgeschlagen"
    exit 1
fi
```

### 5.2 Server-Funktionalität testen
```bash
# Server starten im Hintergrund
python3 run.py &
SERVER_PID=$!

# Warten auf Server-Start
sleep 5

# Server-Status prüfen
if curl -s http://localhost:8080 > /dev/null; then
    echo "✅ Web-Interface ist erreichbar"
else
    echo "❌ Web-Interface nicht erreichbar"
    kill $SERVER_PID
    exit 1
fi

# Server stoppen
kill $SERVER_PID
```

### 5.3 Systemintegrität prüfen
```bash
# Alle erforderlichen Dateien prüfen
required_files=(
    "run.py"
    "server/main.py"
    "config/server_config.yaml"
    "web/templates/index.html"
    "vr_connection_test.py"
)

for file in "${required_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        echo "❌ Erforderliche Datei fehlt: $file"
        exit 1
    fi
done

echo "✅ Alle erforderlichen Dateien vorhanden"
```

---

## 🔧 PHASE 6: SYSTEMOPTIMIERUNG

### 6.1 Performance-Optimierungen
```bash
case $OS in
    "linux")
        # Linux Performance-Tuning
        echo "vm.swappiness=10" | sudo tee -a /etc/sysctl.conf
        sudo sysctl -p
        ;;
    "macos")
        # macOS Performance-Optimierungen
        echo "macOS Performance-Optimierungen können manuell durchgeführt werden"
        ;;
    "windows")
        # Windows Performance-Optimierungen
        powershell -Command "Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management' -Name 'LargeSystemCache' -Value 1"
        ;;
esac
```

### 6.2 Autostart konfigurieren (optional)
```bash
case $OS in
    "linux")
        # Systemd-Service erstellen
        sudo cp deployment/systemd.service /etc/systemd/system/vr-gaming-server.service
        sudo systemctl daemon-reload
        sudo systemctl enable vr-gaming-server
        ;;
    "macos")
        # LaunchAgent erstellen
        mkdir -p ~/Library/LaunchAgents
        cat > ~/Library/LaunchAgents/com.vr-gaming-server.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.vr-gaming-server</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PROJECT_DIR/vr_env/bin/python3</string>
        <string>$PROJECT_DIR/run.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF
        ;;
    "windows")
        # Windows-Service erstellen
        python deployment/windows_service.py install
        ;;
esac
```

---

## 📋 PHASE 7: DOKUMENTATION UND SUPPORT

### 7.1 Benutzerdokumentation erstellen
```bash
# Lokale Dokumentation generieren
echo "# VR Gaming Server - Installationsprotokoll" > installation_log.md
echo "" >> installation_log.md
echo "**Installationsdatum:** $(date)" >> installation_log.md
echo "**Betriebssystem:** $OS" >> installation_log.md
echo "**Python-Version:** $python_version" >> installation_log.md
echo "**Installationspfad:** $PROJECT_DIR" >> installation_log.md
echo "" >> installation_log.md
echo "## Installierte Komponenten:" >> installation_log.md
pip list >> installation_log.md
```

### 7.2 Support-Informationen sammeln
```bash
# Systeminformationen für Support sammeln
echo "## Systeminformationen:" >> installation_log.md
echo "" >> installation_log.md
case $OS in
    "linux")
        uname -a >> installation_log.md
        lsb_release -a >> installation_log.md 2>/dev/null || echo "lsb_release nicht verfügbar" >> installation_log.md
        ;;
    "macos")
        sw_vers >> installation_log.md
        ;;
    "windows")
        systeminfo >> installation_log.md
        ;;
esac
```

---

## 🎯 PHASE 8: FINALER SYSTEMTEST

### 8.1 Vollständiger Integrationstest
```bash
echo "🚀 Führe finalen Systemtest durch..."

# 1. Server starten
python3 run.py &
SERVER_PID=$!
sleep 10

# 2. Web-Interface testen
if curl -s http://localhost:8080 | grep -q "VR Gaming Server"; then
    echo "✅ Web-Interface funktioniert"
else
    echo "❌ Web-Interface Fehler"
    kill $SERVER_PID
    exit 1
fi

# 3. API-Endpunkte testen
if curl -s http://localhost:5000/api/status | grep -q "status"; then
    echo "✅ API-Endpunkte funktionieren"
else
    echo "❌ API-Endpunkte Fehler"
    kill $SERVER_PID
    exit 1
fi

# 4. VR Connection Test
python3 vr_connection_test.py --auto
if [[ $? -eq 0 ]]; then
    echo "✅ VR-Funktionalität bestätigt"
else
    echo "❌ VR-Funktionalität Fehler"
    kill $SERVER_PID
    exit 1
fi

# Server stoppen
kill $SERVER_PID

echo ""
echo "🎉 INSTALLATION ERFOLGREICH ABGESCHLOSSEN!"
echo "📍 Server starten mit: python3 run.py"
echo "🌐 Web-Interface: http://localhost:8080"
echo "📄 Dokumentation: cat installation_log.md"
```

---

## 🚨 NOTFALLPROTOKOLL

### Fehlerbehebung bei kritischen Fehlern
```bash
# Bei kritischen Fehlern: Vollständiges Cleanup
function emergency_cleanup() {
    echo "🚨 Notfall-Cleanup wird durchgeführt..."
    
    # Prozesse stoppen
    pkill -f "python3 run.py" || true
    pkill -f "vr-gaming-server" || true
    
    # Virtuelle Umgebung entfernen
    rm -rf vr_env
    
    # Temporäre Dateien entfernen
    rm -rf __pycache__ */__pycache__
    
    echo "✅ Cleanup abgeschlossen. Starte Neuinstallation..."
}

# Bei Fehlern automatisch aufrufen
trap emergency_cleanup ERR
```

---

## 📊 ERFOLGSMETRIKEN

**KI-Erfolgsindikatoren:**
- [ ] Systemanalyse abgeschlossen
- [ ] Alle Abhängigkeiten installiert
- [ ] Python-Umgebung funktionsfähig
- [ ] VR Gaming Server operational
- [ ] Web-Interface erreichbar
- [ ] Tests erfolgreich durchgeführt
- [ ] Plattformspezifische Optimierungen angewendet
- [ ] Dokumentation erstellt

**Zeitrahmen:** 15-30 Minuten (abhängig von System und Internetverbindung)

---

## 🎯 MISSION ACCOMPLISHED

**KI-Anweisung:** Nach erfolgreichem Abschluss aller Phasen ist das VR Gaming Server System vollständig installiert und konfiguriert. Der Benutzer kann sofort mit VR-Gaming beginnen.

**Letzte Schritte für Benutzer:**
1. Server starten: `python3 run.py`
2. Web-Interface öffnen: http://localhost:8080
3. VR-Headset anschließen und testen
4. Bei Problemen: `cat installation_log.md` für Diagnose

**Status:** 🟢 SYSTEM BEREIT FÜR VR-GAMING</content>
<parameter name="filePath">/Users/kayo/vr-gaming-server/AI_INSTALLATION_GUIDE.md
