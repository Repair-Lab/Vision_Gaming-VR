# 🎮 VR Gaming Server

A powerful VR gaming server for real-time streaming and input injection with WebXR support.

## ✨ Features

- **Real-time Video Streaming** with WebRTC and H.264/H.265 encoding
- **Cross-Platform Support** (Windows, macOS, Linux)
- **WebXR Integration** for VR headsets
- **Automatic Game Detection** and profile management
- **Head Tracking** with gyroscope support
- **Input Injection** for keyboard/mouse control
- **Performance Monitoring** and benchmarking
- **RESTful API** with FastAPI
- **Modular Architecture** for easy extensions

## 🚀 Quick Start

### 1. Check System Requirements

```bash
# Check system requirements
python scripts/requirements_check.py
```

### 2. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

### 3. Start Server

```bash
# Start main server
python run.py

# Or start directly with uvicorn
uvicorn server.main:app --host 0.0.0.0 --port 8000
```

### 4. Open Web Interface

Open `http://localhost:8000` in your browser.

## 📊 Performance Benchmark

Run system performance tests:

```bash
# Run full benchmark
python scripts/benchmark.py

# Results are saved in logs/performance.log
```

## 🧪 Testing and Quality Assurance

### Environment Test

Run a quick system test:

```bash
# Simple environment test
python tests/test_simple.py

# Comprehensive test suite
python tests/test_environment.py
```

### Check System Requirements

```bash
# Detailed requirements check
python scripts/requirements_check.py
```

## 🏗️ Project Structure
```

**Benchmark includes:**
- 🔧 CPU performance tests
- 💾 Memory and disk I/O measurements
- 🌐 Network latency analysis
- 📊 VR-specific benchmarks

## 🏗️ Project Structure

```
vr-gaming-server/
├── server/                 # Server components
│   ├── main.py            # FastAPI main server
│   ├── game_capture.py    # Screen capture
│   ├── video_streamer.py  # Video streaming
│   ├── head_tracker.py    # Head tracking
│   ├── input_injector.py  # Input injection
│   ├── config_manager.py  # Configuration management
│   └── utils/             # Helper functions
├── web/                   # Web interface
│   ├── static/           # CSS, JS, assets
│   └── templates/        # HTML templates
├── config/               # Configuration files
├── profiles/             # Game profiles
├── scripts/              # Helper scripts
│   ├── requirements_check.py  # System check
│   ├── benchmark.py      # Performance tests
│   └── setup.py          # Setup script
├── logs/                 # Log files
└── docs/                 # Documentation
```

## ⚙️ Configuration

### Server Configuration

Edit `config/server_config.yaml`:

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
  keyboard_layout: "en"
  gesture_recognition: true
```

### Game Profiles

Game-specific profiles in `profiles/games/`:

- `cyberpunk2077.json` - Cyberpunk 2077 optimizations
- `minecraft.json` - Minecraft VR mode
- `forza.json` - Forza Horizon racing
- `flight-sim.json` - Microsoft Flight Simulator

## 🔧 API Endpoints

### Main Endpoints

- `GET /` - Web interface
- `GET /api/status` - Server status
- `POST /api/start-stream` - Start streaming
- `POST /api/stop-stream` - Stop streaming
- `GET /api/games` - List detected games
- `POST /api/profile/{game}` - Load profile

### WebSocket Endpoints

- `/ws/video` - Video stream
- `/ws/input` - Input events
- `/ws/sensors` - Sensor data

## 🛠️ Development

### Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Run linting
python -m flake8 server/ web/
```

### Adding New Features

1. Create new server component in `server/`
2. Add API endpoints in `server/main.py`
3. Extend web interface in `web/templates/`
4. Write tests in `tests/`

## 📈 Monitoring

### Performance Metrics

The server automatically collects:

- CPU and RAM usage
- Network latency
- Frame rate and encoding time
- Memory and disk I/O

### Logs

Logs are saved in `logs/`:

- `server.log` - Main server logs
- `performance.log` - Performance metrics
- `errors.log` - Error logs

## 🔒 Security

- HTTPS support with SSL certificates
- API key authentication
- Network firewall configuration
- Secure WebSocket connections

## 📚 Documentation

Detailed documentation in `docs/`:

- `API.md` - Complete API reference
- `INSTALLATION.md` - Detailed installation guide
- `TROUBLESHOOTING.md` - Troubleshooting guide

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see `LICENSE` for details.

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- OpenCV for computer vision functions
- WebRTC for real-time communication
- WebXR for VR integration

---

**Note:** This is an enterprise-quality VR gaming server with production readiness. Ensure your system meets the hardware requirements.
