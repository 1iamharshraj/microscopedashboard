"""
AI Lab route - Chat interface for AI assistance
"""

from flask import Blueprint, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
from datetime import datetime

bp = Blueprint('chat', __name__)

@bp.route('/chat')
def chat():
    """AI Lab chat page"""
    return render_template('chat.html')

@bp.route('/chat_api', methods=['POST'])
def chat_api():
    """Chat API endpoint"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        file_data = data.get('file_data')
        
        # Simple AI response simulation
        responses = {
            'microplastic': 'Based on the analysis, I can help you understand microplastic detection patterns. Microplastics are typically classified into fibers, fragments, pellets, and films.',
            'plankton': 'I can assist with plankton classification. Common plankton types include diatoms, dinoflagellates, copepods, and various larval forms.',
            'analysis': 'For detailed analysis, I recommend checking the Analytics page for comprehensive statistics and trends.',
            'help': 'I\'m here to help with microscopy analysis questions. Ask me about microplastics, plankton classification, or data interpretation.'
        }
        
        # Simple keyword-based response
        response = "I understand you're working with microscopy data. How can I help you with microplastic detection or plankton analysis?"
        
        for keyword, reply in responses.items():
            if keyword.lower() in message.lower():
                response = reply
                break
        
        return jsonify({
            'success': True,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/chat_api/upload', methods=['POST'])
def upload_file():
    """File upload endpoint for chat"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file:
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name, ext = os.path.splitext(filename)
            unique_filename = f"{name}_{timestamp}{ext}"
            
            # Save file to uploads directory
            os.makedirs('data/uploads', exist_ok=True)
            filepath = os.path.join('data/uploads', unique_filename)
            file.save(filepath)
            
            return jsonify({
                'success': True,
                'filename': unique_filename,
                'message': f'File {filename} uploaded successfully'
            })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
