# Microscope Dashboard

A Flask-based web application for analyzing microplastic detection and plankton classification using machine learning models. Designed for compatibility with Jetson Nano and ARM-based systems.

## Features

- **Microplastic Detection**: Upload images and detect microplastics with bounding boxes and confidence scores
- **Plankton Analysis**: Segment and classify plankton species with visualization overlays
- **Data Collection**: Store analysis results in SQLite database with export capabilities
- **Real-time Dashboard**: Bootstrap-based UI with drag-and-drop image upload
- **Data Visualization**: Charts and statistics for collected data analysis
- **Jetson Nano Compatible**: Optimized for ARM systems with CPU-only inference

## Project Structure

```
microscopedashboard/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── routes.py                # API endpoints and routes
│   └── models/
│       ├── microplastic_model.py    # Microplastic detection model
│       └── plankton_model.py        # Plankton analysis model
├── templates/
│   ├── dashboard.html           # Main analysis dashboard
│   └── data_dashboard.html      # Data collection dashboard
├── static/                      # CSS, JS, images
├── uploads/                     # Uploaded images (auto-created)
├── results/                     # Analysis results (auto-created)
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── start.sh                     # One-click startup script
└── README.md                    # This file
```

## Quick Start

### Prerequisites

- Python 3.7 or higher
- Linux system (tested on Ubuntu 20.04+ and Jetson Nano)

### Installation

1. **Clone or download the project**
2. **Make the startup script executable** (Linux/Jetson Nano):
   ```bash
   chmod +x start.sh
   ```
3. **Run the one-click startup script**:
   ```bash
   ./start.sh
   ```

The script will:
- Create a virtual environment
- Install all dependencies
- Load ML models
- Start the Flask server

### Manual Installation (Alternative)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p uploads results static/css static/js

# Start the application
python3 main.py
```

## Usage

### Web Interface

1. **Main Dashboard** (`http://localhost:5000`):
   - Upload images via drag-and-drop or file selection
   - Run microplastic detection or plankton analysis
   - View results with visualizations

2. **Data Dashboard** (`http://localhost:5000/data`):
   - View collected data and statistics
   - Export data to CSV
   - Analyze trends and distributions

### API Endpoints

- `POST /predict/microplastic` - Microplastic detection
- `POST /predict/plankton` - Plankton analysis
- `GET /api/stats` - Get analysis statistics
- `GET /data` - Data collection dashboard

### Image Upload

Supports both file upload and base64 encoded images:
- **File upload**: `multipart/form-data` with `image` field
- **Base64**: JSON with `image_data` field

## API Examples

### Microplastic Detection

```bash
curl -X POST -F "image=@sample.jpg" http://localhost:5000/predict/microplastic
```

### Plankton Analysis

```bash
curl -X POST -F "image=@sample.jpg" http://localhost:5000/predict/plankton
```

## Model Information

### Microplastic Detection Model
- **Classes**: fiber, fragment, pellet, film, background
- **Output**: Bounding boxes with confidence scores
- **Architecture**: Custom CNN with object detection capabilities

### Plankton Analysis Model
- **Species**: 20 different plankton species
- **Output**: Segmentation mask + species classification
- **Architecture**: U-Net for segmentation + CNN for classification

## Data Storage

- **Database**: SQLite (`results/database.db`)
- **Tables**: 
  - `microplastic_results`: Detection results with bounding boxes
  - `plankton_results`: Classification results with species and confidence
- **Export**: CSV export functionality available

## System Requirements

### Minimum Requirements
- **CPU**: ARM Cortex-A57 or x86_64
- **RAM**: 4GB (Jetson Nano compatible)
- **Storage**: 2GB free space
- **OS**: Linux (Ubuntu 18.04+)

### Recommended for Jetson Nano
- **RAM**: 8GB (for better performance)
- **Storage**: 16GB+ (for model storage and data)
- **Power**: 5V/4A power supply

## Configuration

### Environment Variables

- `FLASK_HOST`: Server host (default: 0.0.0.0)
- `FLASK_PORT`: Server port (default: 5000)
- `FLASK_DEBUG`: Debug mode (default: False)

### Model Configuration

Models are configured to use CPU inference for maximum compatibility:
- PyTorch CPU-only mode
- No CUDA dependencies required
- Optimized for ARM processors

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed in the virtual environment
2. **Memory Issues**: Close other applications on Jetson Nano
3. **Port Conflicts**: Change `FLASK_PORT` environment variable
4. **Model Loading**: Check available memory (4GB minimum recommended)

### Performance Optimization

- Use SSD storage for better I/O performance
- Ensure adequate cooling on Jetson Nano
- Close unnecessary background processes
- Consider using a swap file for memory management

## Development

### Adding New Models

1. Create model class in `app/models/`
2. Follow the existing pattern for `predict()` method
3. Update routes to include new endpoint
4. Add UI elements in templates

### Extending the API

1. Add new routes in `app/routes.py`
2. Update database schema if needed
3. Add corresponding frontend functionality

## License

This project is provided as-is for educational and research purposes.

## Support

For issues and questions:
1. Check the logs in `app.log`
2. Verify system requirements
3. Test with sample images
4. Check available memory and storage
