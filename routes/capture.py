"""
Capture route - 7-step workflow for sample analysis
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
import os
import uuid
from datetime import datetime
from services.camera import camera_manager
from services.database import create_report
from services.model_microplastics import analyze_microplastics
from services.model_plankton import classify_plankton

bp = Blueprint('capture', __name__)

@bp.route('/capture')
def capture():
    """Capture page with 7-step workflow"""
    return render_template('capture.html')

@bp.route('/capture/step/<int:step>')
def capture_step(step):
    """Individual capture steps"""
    if step < 1 or step > 7:
        return redirect(url_for('capture.capture'))
    
    return render_template('capture.html', current_step=step)

@bp.route('/capture/api/validate_form', methods=['POST'])
def validate_form():
    """Validate form data from step 4"""
    data = request.get_json()
    
    required_fields = ['slide_name', 'location', 'user']
    errors = []
    
    for field in required_fields:
        if not data.get(field):
            errors.append(f"{field.replace('_', ' ').title()} is required")
    
    if errors:
        return jsonify({'valid': False, 'errors': errors})
    
    return jsonify({'valid': True})

@bp.route('/capture/api/preview', methods=['POST'])
def preview_capture():
    """Preview live feed and capture button"""
    try:
        # Check if camera is active
        if not camera_manager.get_active_frame():
            return jsonify({'error': 'Camera not active'}), 400
        
        return jsonify({'success': True, 'camera_active': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/capture/api/process', methods=['POST'])
def process_analysis():
    """Process analysis with fake progress bar"""
    try:
        data = request.get_json()
        
        # Capture frame from camera
        frame = camera_manager.capture_snapshot()
        if frame is None:
            return jsonify({'error': 'Failed to capture frame'}), 400
        
        # Save captured image
        import cv2
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"capture_{timestamp}.jpg"
        filepath = os.path.join('data/captures', filename)
        cv2.imwrite(filepath, frame)
        
        # Run analysis
        microplastic_result = analyze_microplastics(frame)
        plankton_result = classify_plankton(frame)
        
        # Create report
        report_id = create_report(
            slide_name=data.get('slide_name', 'Unknown'),
            location=data.get('location', 'Unknown'),
            user=data.get('user', 'Unknown'),
            microplastic_result=microplastic_result,
            plankton_result=plankton_result,
            image_path=filepath
        )
        
        return jsonify({
            'success': True,
            'report_id': report_id,
            'microplastic_result': microplastic_result,
            'plankton_result': plankton_result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/capture/api/progress/<report_id>')
def get_progress(report_id):
    """Get processing progress (fake progress bar)"""
    # Simulate progress
    import time
    progress = min(100, int(time.time() * 10) % 100)
    
    return jsonify({
        'progress': progress,
        'status': 'Processing...' if progress < 100 else 'Complete',
        'completed': progress >= 100
    })
