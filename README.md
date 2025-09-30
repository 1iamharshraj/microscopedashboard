# Microbe Insights 🔬

**Advanced microscopy analysis platform for microplastic detection and plankton classification**

Powered by AI and optimized for Jetson Nano, Microbe Insights provides a complete solution for analyzing microscopic samples with real-time camera streaming, AI-powered detection, and comprehensive data management.

---

## 🌟 Features

### Core Capabilities
- **Real-time Camera Streaming** - GStreamer-powered camera integration supporting USB, CSI, and IP cameras
- **AI-Powered Detection** - Dual AI models for microplastic detection and plankton classification
- **7-Step Workflow** - Guided capture process from sample preparation to results
- **Interactive Dashboard** - Beautiful, responsive UI built with Bootstrap 5
- **AI Lab** - Chat interface for AI-assisted analysis guidance
- **Comprehensive Reporting** - Export results as CSV, PDF, or JSON
- **Analytics Dashboard** - Visualize trends with Chart.js integration
- **Cloud Sync** - Optional cloud backup and synchronization

### Analysis Types
1. **Microplastic Detection**
   - Identify plastic particles: fibers, fragments, pellets, films
   - Particle counting and classification
   - Confidence scoring for each detection

2. **Plankton Classification**
   - Identify 20+ plankton species
   - Automated segmentation
   - ROI extraction and species distribution analysis

---

## 📂 Project Structure

```
microbe_insights/
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── routes/                     # Route handlers
│   ├── __init__.py
│   ├── home.py                # Dashboard
│   ├── capture.py             # 7-step workflow
│   ├── chat.py                # AI Lab
│   ├── reports.py             # Report listing
│   ├── results.py             # Result details
│   ├── analytics.py           # Analytics dashboard
│   ├── settings.py            # Configuration
│   └── help.py                # Documentation
│
├── services/                   # Business logic
│   ├── __init__.py
│   ├── camera.py              # GStreamer camera interface
│   ├── database.py            # SQLite operations
│   ├── model_microplastics.py # Microplastic detection
│   └── model_plankton.py      # Plankton classification
│
├── templates/                  # Jinja2 templates
│   ├── base.html              # Base layout with sidebar
│   ├── home.html              # Dashboard
│   ├── capture.html           # Capture workflow
│   ├── chat.html              # AI chat interface
│   ├── reports.html           # Report listing
│   ├── results.html           # Result details
│   ├── analytics.html         # Analytics dashboard
│   ├── settings.html          # Settings page
│   ├── help.html              # Help & documentation
│   ├── 404.html               # Error pages
│   └── 500.html
│
├── static/                     # Static assets
│   ├── css/
│   ├── js/
│   └── icons/
│
└── data/                       # Application data
    ├── reports.db             # SQLite database
    ├── captures/              # Captured images
    ├── uploads/               # Uploaded files
    └── results/               # Analysis results
```

---

## 🚀 Installation

### Prerequisites
- Python 3.6.9+ (optimized for Jetson Nano)
- OpenCV with GStreamer support
- SQLite3

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd microbe_insights
   ```

2. **Create virtual environment** (optional but recommended)
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database**
   ```bash
   python3 -c "from services.database import init_database; init_database()"
   ```

5. **Run the application**
   ```bash
   python3 app.py
   ```

6. **Access the application**
   - Open your browser and navigate to: `http://localhost:5000`
   - Or access from another device: `http://<jetson-ip>:5000`

---

## 💻 Usage

### Quick Start Guide

1. **Home Dashboard** (`/`)
   - View system status and recent analyses
   - Quick access to all features
   - System health monitoring

2. **Capture Workflow** (`/capture`)
   - Follow the 7-step guided process:
     1. Sample Preparation
     2. Camera Setup
     3. Lighting Configuration
     4. Sample Information Entry
     5. Preview & Capture
     6. AI Analysis
     7. Results Review

3. **AI Lab** (`/chat`)
   - Ask questions about your analysis
   - Get guidance on sample preparation
   - Upload files for assistance

4. **Reports** (`/reports`)
   - Browse all analysis reports
   - Filter by date, location, or researcher
   - Export individual or bulk data

5. **Results** (`/results/<id>`)
   - View detailed analysis results
   - Examine ROI images
   - Export in multiple formats

6. **Analytics** (`/analytics`)
   - Visualize detection trends
   - Species distribution charts
   - Performance metrics

7. **Settings** (`/settings`)
   - Configure camera parameters
   - Select AI model versions
   - Enable cloud synchronization
   - System preferences

8. **Help** (`/help`)
   - Comprehensive documentation
   - Video tutorials
   - FAQ section
   - Contact support

---

## 🎥 Camera Configuration

### Supported Cameras

1. **USB Cameras**
   - Most USB webcams and microscope cameras
   - Auto-detection on `/dev/video0`, `/dev/video1`, etc.

2. **CSI Cameras** (Jetson Nano)
   - Raspberry Pi Camera Module V2
   - IMX219-based cameras
   - Hardware-accelerated capture

3. **IP Cameras**
   - RTSP stream support
   - Network cameras

### Camera Settings
Configure in `/settings`:
- Resolution (640×480 to 1920×1080)
- Frame rate (10-60 FPS)
- Exposure, brightness, contrast
- White balance

---

## 🤖 AI Models

### Microplastic Detection Model
- **Input**: RGB images (224×224)
- **Output**: Bounding boxes and classifications
- **Classes**: Fiber, Fragment, Pellet, Film
- **Confidence threshold**: Adjustable (default 0.7)

### Plankton Classification Model
- **Input**: RGB images (224×224)
- **Output**: Species classification + segmentation
- **Classes**: 20+ plankton species
- **Features**: ROI extraction, species counting

*Note: Current implementation includes placeholder models for demonstration. Replace with trained models for production use.*

---

## 📊 Database Schema

### Reports Table
```sql
CREATE TABLE reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slide_name TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    location TEXT,
    user TEXT,
    microplastics_present BOOLEAN,
    particle_count INTEGER,
    confidence REAL,
    plankton_summary TEXT,
    image_path TEXT
);
```

---

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Database
DATABASE_PATH = 'data/reports.db'

# Camera defaults
DEFAULT_CAMERA_ID = 0
DEFAULT_RESOLUTION = (1280, 720)
DEFAULT_FPS = 30

# AI Models
MICROPLASTIC_MODEL_PATH = 'models/microplastic_model.pth'
PLANKTON_MODEL_PATH = 'models/plankton_model.pth'

# Cloud sync
CLOUD_SYNC_ENABLED = False
```

---

## 🌐 API Endpoints

### Camera Control
- `POST /camera/start` - Start camera streaming
- `POST /camera/stop` - Stop camera streaming
- `POST /camera/snapshot` - Capture snapshot

### Analysis
- `POST /capture/api/process` - Run analysis
- `GET /analytics/api/stats` - Get statistics
- `GET /reports/api/search` - Search reports

### Data
- `GET /results/<id>` - Get report details
- `GET /results/<id>/export/csv` - Export as CSV
- `GET /results/<id>/export/pdf` - Export as PDF

---

## 🛠️ Development

### Running in Debug Mode
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python3 app.py
```

### Adding New Features
1. Create route in `routes/`
2. Add service logic in `services/`
3. Create template in `templates/`
4. Register blueprint in `app.py`

---

## 📝 License

This project is provided as-is for educational and research purposes.

---

## 👥 Support

- **Documentation**: Navigate to `/help` in the application
- **AI Assistant**: Use the AI Lab at `/chat`
- **Email**: support@microbeinsights.com
- **Issues**: Report bugs via the feedback form

---

## 🎯 Roadmap

- [ ] Integration with real AI models
- [ ] Multi-language support
- [ ] Mobile app
- [ ] Advanced image preprocessing
- [ ] Batch analysis
- [ ] Team collaboration features
- [ ] API for external integrations

---

## 🙏 Acknowledgments

- Built with Flask, Bootstrap 5, and Chart.js
- Optimized for NVIDIA Jetson Nano
- GStreamer for camera streaming
- SQLite for data management

---

**Microbe Insights** - Advancing microscopy analysis through AI 🔬✨