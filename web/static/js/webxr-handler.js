/**
 * WebXR Handler - WebXR Integration für VR Gaming
 */

class WebXRHandler {
    constructor() {
        this.session = null;
        this.referenceSpace = null;
        this.isSupported = false;
        this.isRunning = false;
        
        this.init();
    }
    
    async init() {
        // WebXR Support prüfen
        if ('xr' in navigator) {
            try {
                this.isSupported = await navigator.xr.isSessionSupported('immersive-vr');
                console.log('WebXR VR Support:', this.isSupported);
            } catch (error) {
                console.error('WebXR Support Check fehlgeschlagen:', error);
            }
        } else {
            console.warn('WebXR nicht verfügbar');
        }
    }
    
    async startVR() {
        if (!this.isSupported) {
            alert('WebXR VR wird nicht unterstützt auf diesem Gerät');
            return false;
        }
        
        try {
            // WebXR Session starten
            this.session = await navigator.xr.requestSession('immersive-vr', {
                requiredFeatures: ['local-floor'],
                optionalFeatures: ['bounded-floor']
            });
            
            // Reference Space erstellen
            this.referenceSpace = await this.session.requestReferenceSpace('local-floor');
            
            // Session Event Listener
            this.session.addEventListener('end', () => {
                this.endVR();
            });
            
            // Frame Loop starten
            this.session.requestAnimationFrame(this.onXRFrame.bind(this));
            
            this.isRunning = true;
            console.log('WebXR Session gestartet');
            
            return true;
        } catch (error) {
            console.error('WebXR Session Start fehlgeschlagen:', error);
            return false;
        }
    }
    
    endVR() {
        if (this.session) {
            this.session.end();
            this.session = null;
            this.referenceSpace = null;
            this.isRunning = false;
            console.log('WebXR Session beendet');
        }
    }
    
    onXRFrame(time, frame) {
        if (!this.session || !this.isRunning) return;
        
        // Pose für beide Augen holen
        const pose = frame.getViewerPose(this.referenceSpace);
        
        if (pose) {
            // Kopfbewegungsdaten verarbeiten
            this.processHeadPose(pose.transform);
            
            // Views für beide Augen rendern
            for (const view of pose.views) {
                this.renderView(view);
            }
        }
        
        // Nächsten Frame anfordern
        this.session.requestAnimationFrame(this.onXRFrame.bind(this));
    }
    
    processHeadPose(transform) {
        // Quaternion und Position aus Transform extrahieren
        const position = transform.position;
        const orientation = transform.orientation;
        
        // Daten an Server senden
        const headData = {
            type: 'head_pose',
            position: {
                x: position.x,
                y: position.y,
                z: position.z
            },
            quaternion: {
                x: orientation.x,
                y: orientation.y,
                z: orientation.z,
                w: orientation.w
            },
            timestamp: Date.now()
        };
        
        // WebSocket senden (falls verfügbar)
        if (window.headTrackingWS && window.headTrackingWS.readyState === WebSocket.OPEN) {
            window.headTrackingWS.send(JSON.stringify(headData));
        }
    }
    
    renderView(view) {
        // Hier würde das Rendering für VR erfolgen
        // Für diesen Prototyp nur Logging
        console.log('Rendering View:', view.eye);
    }
    
    getSupportedFeatures() {
        return {
            webxr: 'xr' in navigator,
            immersiveVR: this.isSupported,
            isRunning: this.isRunning
        };
    }
}

// Global Instance
const webxrHandler = new WebXRHandler();

// Export für globale Verwendung
window.WebXRHandler = WebXRHandler;
window.webxrHandler = webxrHandler;
