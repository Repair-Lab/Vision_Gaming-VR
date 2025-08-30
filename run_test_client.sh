#!/bin/bash
# VR Gaming Server - Test Client Launcher
# Startet den VR Connection Test Client

echo "VR Gaming Server - Connection Test Client"
echo "========================================="
echo ""
echo "Starte Test-Software..."

# Wechsle zum Projekt-Verzeichnis
cd "$(dirname "$0")"

# Überprüfe Python-Version
python3 --version
if [ $? -ne 0 ]; then
    echo "Fehler: Python 3 ist nicht installiert!"
    exit 1
fi

# Überprüfe und installiere Abhängigkeiten
echo "Überprüfe Abhängigkeiten..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Fehler beim Installieren der Abhängigkeiten!"
    echo "Versuchen Sie: pip3 install pygame websockets"
    exit 1
fi

# Starte die Test-Software
echo ""
echo "Starte VR Connection Test Client..."
python3 vr_connection_test.py

echo ""
echo "Test beendet."
