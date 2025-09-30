from flask import Blueprint, request, jsonify, render_template, send_from_directory, Response, make_response
import os
import json
import base64
from datetime import datetime
import sqlite3
from werkzeug.utils import secure_filename
from PIL import Image
import io
import numpy as np
import cv2
import time

# Import models
from app.models.microplastic_model import microplastic_model
from app.models.plankton_model import plankton_model
from app.camera import camera_manager

bp = Blueprint('main', __name__)

# Database setup
def init_db():
    """Initialize SQLite database for storing results"""
    conn = sqlite3.connect('results/database.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS microplastic_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            image_path TEXT,
            detections TEXT,
            image_shape TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS plankton_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            image_path TEXT,
            species_name TEXT,
            confidence REAL,
            mask_data TEXT,
            image_shape TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def save_microplastic_result(image_path, detections, image_shape):
    """Save microplastic detection result to database"""
    conn = sqlite3.connect('results/database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO microplastic_results (timestamp, image_path, detections, image_shape)
        VALUES (?, ?, ?, ?)
    ''', (datetime.now().isoformat(), image_path, json.dumps(detections), json.dumps(image_shape)))
    
    conn.commit()
    conn.close()

def save_plankton_result(image_path, species_name, confidence, mask_data, image_shape):
    """Save plankton analysis result to database"""
    conn = sqlite3.connect('results/database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO plankton_results (timestamp, image_path, species_name, confidence, mask_data, image_shape)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (datetime.now().isoformat(), image_path, species_name, confidence, json.dumps(mask_data), json.dumps(image_shape)))
    
    conn.commit()
    conn.close()

def get_recent_results(limit=50):
    """Get recent results from database"""
    conn = sqlite3.connect('results/database.db')
    cursor = conn.cursor()
    
    # Get microplastic results
    cursor.execute('''
        SELECT timestamp, image_path, detections, image_shape 
        FROM microplastic_results 
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (limit,))
    microplastic_results = cursor.fetchall()
    
    # Get plankton results
    cursor.execute('''
        SELECT timestamp, image_path, species_name, confidence, mask_data, image_shape 
        FROM plankton_results 
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (limit,))
    plankton_results = cursor.fetchall()
    
    conn.close()
    
    return microplastic_results, plankton_results

def process_image_upload(image_data, filename):
    """Process uploaded image and save to uploads folder"""
    try:
        # Ensure uploads directory exists
        os.makedirs('uploads', exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = secure_filename(filename)
        name, ext = os.path.splitext(safe_filename)
        unique_filename = f"{name}_{timestamp}{ext}"
        filepath = os.path.join('uploads', unique_filename)
        
        # Save image
        image_data.save(filepath)
        
        # Validate image
        try:
            with Image.open(filepath) as img:
                img.verify()
            return filepath
        except Exception:
            os.remove(filepath)
            raise Exception("Invalid image file")
            
    except Exception as e:
        raise Exception(f"Image upload failed: {str(e)}")

@bp.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@bp.route('/data')
def data_dashboard():
    """Data collection dashboard"""
    microplastic_results, plankton_results = get_recent_results()
    
    # Process results for display
    processed_microplastic = []
    for result in microplastic_results:
        try:
            detections = json.loads(result[2])
            processed_microplastic.append({
                'timestamp': result[0],
                'image_path': result[1],
                'detection_count': len(detections.get('detections', [])),
                'detections': detections.get('detections', [])
            })
        except:
            continue
    
    processed_plankton = []
    for result in plankton_results:
        processed_plankton.append({
            'timestamp': result[0],
            'image_path': result[1],
            'species_name': result[2],
            'confidence': result[3]
        })
    
    return render_template('data_dashboard.html', 
                         microplastic_results=processed_microplastic,
                         plankton_results=processed_plankton)

@bp.route('/predict/microplastic', methods=['POST'])
def predict_microplastic():
    """Microplastic detection endpoint"""
    try:
        # Initialize database if not exists
        init_db()
        
        # Handle file upload
        if 'image' in request.files:
            file = request.files['image']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            image_path = process_image_upload(file, file.filename)
        
        # Handle base64 image
        elif 'image_data' in request.json:
            try:
                image_data = request.json['image_data']
                if image_data.startswith('data:image'):
                    image_data = image_data.split(',')[1]
                
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"microplastic_{timestamp}.jpg"
                image_path = os.path.join('uploads', filename)
                
                os.makedirs('uploads', exist_ok=True)
                image.save(image_path)
            except Exception as e:
                return jsonify({'error': f'Invalid base64 image: {str(e)}'}), 400
        
        else:
            return jsonify({'error': 'No image provided'}), 400
        
        # Run prediction
        result = microplastic_model.predict(image_path)
        
        if result['success']:
            # Save result to database
            save_microplastic_result(image_path, result['detections'], result['image_shape'])
            
            # Generate visualization
            vis_path = os.path.join('results', f"microplastic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
            os.makedirs('results', exist_ok=True)
            microplastic_model.draw_detections(image_path, result, vis_path)
            
            result['visualization_path'] = vis_path
            result['image_path'] = image_path
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/predict/plankton', methods=['POST'])
def predict_plankton():
    """Plankton analysis endpoint"""
    try:
        # Initialize database if not exists
        init_db()
        
        # Handle file upload
        if 'image' in request.files:
            file = request.files['image']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            image_path = process_image_upload(file, file.filename)
        
        # Handle base64 image
        elif 'image_data' in request.json:
            try:
                image_data = request.json['image_data']
                if image_data.startswith('data:image'):
                    image_data = image_data.split(',')[1]
                
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"plankton_{timestamp}.jpg"
                image_path = os.path.join('uploads', filename)
                
                os.makedirs('uploads', exist_ok=True)
                image.save(image_path)
            except Exception as e:
                return jsonify({'error': f'Invalid base64 image: {str(e)}'}), 400
        
        else:
            return jsonify({'error': 'No image provided'}), 400
        
        # Run prediction
        result = plankton_model.predict(image_path)
        
        if result['success']:
            # Save result to database
            classification = result['classification']
            save_plankton_result(image_path, classification['species_name'], 
                               classification['confidence'], result['segmentation_mask'], 
                               result['image_shape'])
            
            # Generate visualization
            vis_path = os.path.join('results', f"plankton_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
            os.makedirs('results', exist_ok=True)
            
            # Load original image for visualization
            import cv2
            original_image = cv2.imread(image_path)
            mask = np.array(result['segmentation_mask'])
            plankton_model.save_visualization(original_image, mask, classification, vis_path)
            
            result['visualization_path'] = vis_path
            result['image_path'] = image_path
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory('uploads', filename)

@bp.route('/results/<filename>')
def result_file(filename):
    """Serve result files"""
    return send_from_directory('results', filename)

@bp.route('/api/stats')
def get_stats():
    """Get statistics about collected data"""
    try:
        conn = sqlite3.connect('results/database.db')
        cursor = conn.cursor()
        
        # Get microplastic stats
        cursor.execute('SELECT COUNT(*) FROM microplastic_results')
        microplastic_count = cursor.fetchone()[0]
        
        # Get plankton stats
        cursor.execute('SELECT COUNT(*) FROM plankton_results')
        plankton_count = cursor.fetchone()[0]
        
        # Get species distribution
        cursor.execute('SELECT species_name, COUNT(*) FROM plankton_results GROUP BY species_name ORDER BY COUNT(*) DESC')
        species_dist = cursor.fetchall()
        
        # Get detection distribution for microplastics
        cursor.execute('SELECT detections FROM microplastic_results')
        detection_data = cursor.fetchall()
        
        class_counts = {'fiber': 0, 'fragment': 0, 'pellet': 0, 'film': 0}
        for row in detection_data:
            try:
                detections = json.loads(row[0])
                for detection in detections.get('detections', []):
                    class_name = detection.get('class_name', '')
                    if class_name in class_counts:
                        class_counts[class_name] += 1
            except:
                continue
        
        conn.close()
        
        return jsonify({
            'microplastic_count': microplastic_count,
            'plankton_count': plankton_count,
            'species_distribution': dict(species_dist),
            'microplastic_distribution': class_counts
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Camera and video streaming routes
@bp.route('/camera/stream')
def camera_stream():
    """Live camera feed endpoint"""
    def generate_frames():
        while True:
            frame = camera_manager.get_active_frame()
            if frame is not None:
                # Encode frame as JPEG
                ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                if ret:
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            else:
                time.sleep(0.1)
    
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@bp.route('/camera/snapshot')
def camera_snapshot():
    """Capture snapshot from camera"""
    try:
        frame = camera_manager.capture_snapshot()
        if frame is not None:
            # Encode as JPEG
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            if ret:
                response = make_response(buffer.tobytes())
                response.headers['Content-Type'] = 'image/jpeg'
                response.headers['Content-Disposition'] = 'inline; filename=snapshot.jpg'
                return response
        
        return jsonify({'error': 'Failed to capture snapshot'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/camera/start', methods=['POST'])
def start_camera():
    """Start camera streaming"""
    try:
        data = request.get_json() or {}
        camera_id = data.get('camera_id', 0)
        camera_type = data.get('camera_type', 'usb')
        width = data.get('width', 1280)
        height = data.get('height', 720)
        fps = data.get('fps', 30)
        
        # Add camera if not exists
        if camera_id not in camera_manager.get_camera_list():
            success = camera_manager.add_camera(
                camera_id=camera_id,
                camera_type=camera_type,
                width=width,
                height=height,
                fps=fps
            )
            if not success:
                return jsonify({'error': 'Failed to add camera'}), 500
        
        # Start camera
        success = camera_manager.start_camera(camera_id)
        if success:
            return jsonify({
                'success': True,
                'message': f'Camera {camera_id} started',
                'camera_info': camera_manager.get_camera_info(camera_id)
            })
        else:
            return jsonify({'error': 'Failed to start camera'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/camera/stop', methods=['POST'])
def stop_camera():
    """Stop camera streaming"""
    try:
        data = request.get_json() or {}
        camera_id = data.get('camera_id')
        
        if camera_id is not None:
            camera_manager.stop_camera(camera_id)
            return jsonify({'success': True, 'message': f'Camera {camera_id} stopped'})
        else:
            camera_manager.stop_all_cameras()
            return jsonify({'success': True, 'message': 'All cameras stopped'})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/camera/info')
def camera_info():
    """Get camera information"""
    try:
        camera_list = camera_manager.get_camera_list()
        info = {}
        
        for camera_id in camera_list:
            info[camera_id] = camera_manager.get_camera_info(camera_id)
        
        return jsonify({
            'cameras': info,
            'active_camera': camera_manager.active_camera_id,
            'available_cameras': camera_list
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/camera/capture', methods=['POST'])
def capture_from_camera():
    """Capture image from camera and run analysis"""
    try:
        data = request.get_json() or {}
        analysis_type = data.get('type', 'microplastic')  # 'microplastic' or 'plankton'
        
        # Capture snapshot
        frame = camera_manager.capture_snapshot()
        if frame is None:
            return jsonify({'error': 'No camera active or failed to capture'}), 400
        
        # Save temporary image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"camera_{analysis_type}_{timestamp}.jpg"
        image_path = os.path.join('uploads', filename)
        
        os.makedirs('uploads', exist_ok=True)
        cv2.imwrite(image_path, frame)
        
        # Run analysis based on type
        if analysis_type == 'microplastic':
            result = microplastic_model.predict(image_path)
            if result['success']:
                save_microplastic_result(image_path, result['detections'], result['image_shape'])
        elif analysis_type == 'plankton':
            result = plankton_model.predict(image_path)
            if result['success']:
                classification = result['classification']
                save_plankton_result(image_path, classification['species_name'], 
                                   classification['confidence'], result['segmentation_mask'], 
                                   result['image_shape'])
        else:
            return jsonify({'error': 'Invalid analysis type'}), 400
        
        result['image_path'] = image_path
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Initialize database on startup
init_db()
