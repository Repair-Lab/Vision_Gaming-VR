#!/usr/bin/env python3
"""
VR Gaming Server - Startup Script mit GUI
Ein-Klick-Start für VR Game Streaming Server
"""

import sys
import os
import subprocess
import threading
import time
import webbrowser
from pathlib import Path

# GUI Framework
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, scrolledtext
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

class VRServerGUI:
    """GUI für VR Gaming Server"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("VR Gaming Server - Control Panel")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Server-Prozess
        self.server_process = None
        self.is_server_running = False
        
        self.setup_ui()
        self.update_status()
    
    def setup_ui(self):
        """UI-Setup"""
        # Haupt-Frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Logo und Titel
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        title_label = ttk.Label(title_frame, text="🥽 VR Gaming Server", font=('Arial', 24, 'bold'))
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame, text="Vision Pro Game Streaming", font=('Arial', 12))
        subtitle_label.pack()
        
        # Status-Bereich
        status_frame = ttk.LabelFrame(main_frame, text="Server Status", padding="10")
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text="Server: Gestoppt", font=('Arial', 12, 'bold'))
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        self.url_label = ttk.Label(status_frame, text="URL: Nicht verfügbar", font=('Arial', 10))
        self.url_label.grid(row=1, column=0, sticky=tk.W)
        
        # Steuerungs-Buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.start_button = ttk.Button(control_frame, text="🚀 Server Starten", command=self.start_server)
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="⏹️ Server Stoppen", command=self.stop_server, state='disabled')
        self.stop_button.grid(row=0, column=1, padx=(0, 10))
        
        self.browser_button = ttk.Button(control_frame, text="🌐 Browser Öffnen", command=self.open_browser, state='disabled')
        self.browser_button.grid(row=0, column=2, padx=(0, 10))
        
        self.restart_button = ttk.Button(control_frame, text="🔄 Neustarten", command=self.restart_server, state='disabled')
        self.restart_button.grid(row=0, column=3)
        
        # Einstellungen-Bereich
        settings_frame = ttk.LabelFrame(main_frame, text="Schnell-Einstellungen", padding="10")
        settings_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Port-Einstellung
        ttk.Label(settings_frame, text="Port:").grid(row=0, column=0, sticky=tk.W)
        self.port_var = tk.StringVar(value="8080")
        port_entry = ttk.Entry(settings_frame, textvariable=self.port_var, width=10)
        port_entry.grid(row=0, column=1, padx=(5, 20), sticky=tk.W)
        
        # Auto-Start Browser
        self.auto_browser_var = tk.BooleanVar(value=True)
        auto_browser_check = ttk.Checkbutton(settings_frame, text="Browser automatisch öffnen", variable=self.auto_browser_var)
        auto_browser_check.grid(row=0, column=2, sticky=tk.W)
        
        # Log-Bereich
        log_frame = ttk.LabelFrame(main_frame, text="Server-Log", padding="10")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Button-Frame unten
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        ttk.Button(bottom_frame, text="🧹 Log Löschen", command=self.clear_log).pack(side=tk.LEFT)
        ttk.Button(bottom_frame, text="💾 Log Speichern", command=self.save_log).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(bottom_frame, text="❌ Beenden", command=self.quit_app).pack(side=tk.RIGHT)
        
        # Grid-Gewichtung
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
    
    def log(self, message):
        """Nachricht im Log anzeigen"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def start_server(self):
        """Server starten"""
        if self.is_server_running:
            return
        
        self.log("Server wird gestartet...")
        
        try:
            # Server-Skript ausführen
            port = self.port_var.get()
            cmd = [
                sys.executable, "server/main.py",
                "--port", port
            ]
            
            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                cwd=os.getcwd()
            )
            
            # Log-Reader-Thread starten
            self.log_thread = threading.Thread(target=self.read_server_logs, daemon=True)
            self.log_thread.start()
            
            self.is_server_running = True
            self.update_status()
            
            self.log("Server erfolgreich gestartet!")
            
            # Browser automatisch öffnen
            if self.auto_browser_var.get():
                threading.Timer(2.0, self.open_browser).start()
                
        except Exception as e:
            self.log(f"Fehler beim Server-Start: {e}")
            messagebox.showerror("Fehler", f"Server konnte nicht gestartet werden:\n{e}")
    
    def stop_server(self):
        """Server stoppen"""
        if not self.is_server_running:
            return
        
        self.log("Server wird gestoppt...")
        
        try:
            if self.server_process:
                self.server_process.terminate()
                self.server_process.wait(timeout=10)
                self.server_process = None
            
            self.is_server_running = False
            self.update_status()
            self.log("Server gestoppt!")
            
        except Exception as e:
            self.log(f"Fehler beim Server-Stopp: {e}")
            if self.server_process:
                self.server_process.kill()
                self.server_process = None
            self.is_server_running = False
            self.update_status()
    
    def restart_server(self):
        """Server neustarten"""
        self.log("Server wird neu gestartet...")
        self.stop_server()
        time.sleep(1)
        self.start_server()
    
    def read_server_logs(self):
        """Server-Logs lesen und anzeigen"""
        if not self.server_process:
            return
        
        try:
            for line in iter(self.server_process.stdout.readline, ''):
                if line:
                    self.log(f"[SERVER] {line.strip()}")
                if self.server_process.poll() is not None:
                    break
                    
        except Exception as e:
            self.log(f"Log-Reader-Fehler: {e}")
    
    def update_status(self):
        """UI-Status aktualisieren"""
        if self.is_server_running:
            self.status_label.config(text="Server: Läuft", foreground="green")
            port = self.port_var.get()
            self.url_label.config(text=f"URL: http://localhost:{port}")
            
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.browser_button.config(state='normal')
            self.restart_button.config(state='normal')
        else:
            self.status_label.config(text="Server: Gestoppt", foreground="red")
            self.url_label.config(text="URL: Nicht verfügbar")
            
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            self.browser_button.config(state='disabled')
            self.restart_button.config(state='disabled')
    
    def open_browser(self):
        """Browser mit Server-URL öffnen"""
        if self.is_server_running:
            port = self.port_var.get()
            url = f"http://localhost:{port}"
            webbrowser.open(url)
            self.log(f"Browser geöffnet: {url}")
        else:
            messagebox.showwarning("Warnung", "Server ist nicht gestartet!")
    
    def clear_log(self):
        """Log löschen"""
        self.log_text.delete(1.0, tk.END)
    
    def save_log(self):
        """Log speichern"""
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                self.log(f"Log gespeichert: {filename}")
        except Exception as e:
            messagebox.showerror("Fehler", f"Log konnte nicht gespeichert werden:\n{e}")
    
    def quit_app(self):
        """Anwendung beenden"""
        if self.is_server_running:
            result = messagebox.askyesno("Server läuft", "Server ist noch aktiv. Trotzdem beenden?")
            if not result:
                return
            
            self.stop_server()
        
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """GUI starten"""
        # Window-Close-Handler
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)
        
        # Initialer Log
        self.log("VR Gaming Server Control Panel gestartet")
        self.log("Bereit für Server-Start...")
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.quit_app()

def check_dependencies():
    """Dependencies prüfen und installieren"""
    print("Prüfe Python-Dependencies...")
    
    required_packages = [
        'fastapi', 'uvicorn', 'opencv-python', 'mss', 
        'numpy', 'pynput', 'jinja2', 'websockets'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Fehlende Packages: {', '.join(missing_packages)}")
        print("Installiere Dependencies...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "-r", "requirements.txt"
            ])
            print("Dependencies erfolgreich installiert!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Dependency-Installation fehlgeschlagen: {e}")
            return False
    else:
        print("Alle Dependencies verfügbar!")
        return True

def setup_directories():
    """Verzeichnisstruktur erstellen"""
    directories = [
        "server", "web/static", "web/templates", 
        "profiles", "logs", "config"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("Verzeichnisstruktur erstellt!")

def main():
    """Hauptfunktion"""
    print("=" * 60)
    print("🥽 VR Gaming Server - Startup")
    print("=" * 60)
    
    # Arbeitsverzeichnis prüfen
    if not Path("requirements.txt").exists():
        print("❌ Fehler: requirements.txt nicht gefunden!")
        print("Bitte Skript im Projekt-Root-Verzeichnis ausführen.")
        input("Enter drücken zum Beenden...")
        return
    
    # Verzeichnisse einrichten
    setup_directories()
    
    # Dependencies prüfen
    if not check_dependencies():
        print("❌ Dependency-Installation fehlgeschlagen!")
        input("Enter drücken zum Beenden...")
        return
    
    # GUI oder Kommandozeile
    if GUI_AVAILABLE and len(sys.argv) == 1:
        print("🎮 Starte GUI...")
        gui = VRServerGUI()
        gui.run()
    else:
        print("💻 Starte Server direkt...")
        # Direkter Server-Start
        try:
            import uvicorn
            from server.main import app
            
            port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
            
            print(f"🚀 Server startet auf Port {port}")
            print(f"🌐 URL: http://localhost:{port}")
            
            uvicorn.run(app, host="0.0.0.0", port=port)
            
        except ImportError:
            print("❌ Server-Module nicht gefunden!")
            print("Bitte sicherstellen dass alle Dateien vorhanden sind.")
        except KeyboardInterrupt:
            print("\n👋 Server gestoppt!")
        except Exception as e:
            print(f"❌ Server-Fehler: {e}")

if __name__ == "__main__":
    main()