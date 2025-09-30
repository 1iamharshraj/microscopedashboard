"""
Microbe Insights - Flask Application
Complete microscopy analysis platform with AI-powered microplastic and plankton detection
"""

from flask import Flask, render_template, request, jsonify, send_from_directory, Response, make_response, redirect, url_for, flash
import os
import sys
from datetime import datetime
import sqlite3
import json

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from services.database import init_database, get_recent_reports, get_report_by_id, create_report
from services.camera import camera_manager

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.secret_key = 'microbe_insights_secret_key_2024'
    
    # Configuration
    app.config['UPLOAD_FOLDER'] = 'data/uploads'
    app.config['CAPTURE_FOLDER'] = 'data/captures'
    app.config['RESULTS_FOLDER'] = 'data/results'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Ensure directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['CAPTURE_FOLDER'], exist_ok=True)
    os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    # Initialize database
    init_database()
    
    # Register blueprints
    from routes.home import bp as home_bp
    from routes.capture import bp as capture_bp
    from routes.chat import bp as chat_bp
    from routes.reports import bp as reports_bp
    from routes.results import bp as results_bp
    from routes.analytics import bp as analytics_bp
    from routes.settings import bp as settings_bp
    from routes.help import bp as help_bp
    
    app.register_blueprint(home_bp)
    app.register_blueprint(capture_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(results_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(help_bp)
    
    # Static file routes
    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
    @app.route('/captures/<filename>')
    def captured_file(filename):
        return send_from_directory(app.config['CAPTURE_FOLDER'], filename)
    
    @app.route('/results/<filename>')
    def result_file(filename):
        return send_from_directory(app.config['RESULTS_FOLDER'], filename)
    
    # Video feed route for persistent camera
    @app.route('/video_feed')
    def video_feed():
        """Live camera feed endpoint"""
        def generate_frames():
            while True:
                frame = camera_manager.get_active_frame()
                if frame is not None:
                    import cv2
                    ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                    if ret:
                        frame_bytes = buffer.tobytes()
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                else:
                    import time
                    time.sleep(0.1)
        
        return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    
    # Camera control routes
    @app.route('/camera/start', methods=['POST'])
    def start_camera():
        """Start camera streaming"""
        try:
            data = request.get_json() or {}
            camera_id = data.get('camera_id', 0)
            camera_type = data.get('camera_type', 'usb')
            width = data.get('width', 1280)
            height = data.get('height', 720)
            fps = data.get('fps', 30)
            
            success = camera_manager.add_camera(
                camera_id=camera_id,
                camera_type=camera_type,
                width=width,
                height=height,
                fps=fps
            )
            
            if success:
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
    
    @app.route('/camera/stop', methods=['POST'])
    def stop_camera():
        """Stop camera streaming"""
        try:
            data = request.get_json() or {}
            camera_id = data.get('camera_id')
            
            if camera_id is not None:
                camera_manager.stop_camera(camera_id)
            else:
                camera_manager.stop_all_cameras()
            
            return jsonify({'success': True, 'message': 'Camera stopped'})
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/camera/snapshot', methods=['POST'])
    def capture_snapshot():
        """Capture snapshot from camera"""
        try:
            frame = camera_manager.capture_snapshot()
            if frame is not None:
                import cv2
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"snapshot_{timestamp}.jpg"
                filepath = os.path.join(app.config['CAPTURE_FOLDER'], filename)
                
                cv2.imwrite(filepath, frame)
                
                return jsonify({
                    'success': True,
                    'filename': filename,
                    'filepath': filepath
                })
            else:
                return jsonify({'error': 'Failed to capture snapshot'}), 500
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)