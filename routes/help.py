"""
Help route - Documentation and support information
"""

from flask import Blueprint, render_template, jsonify

bp = Blueprint('help', __name__)

# Help content data
HELP_SECTIONS = {
    'getting_started': {
        'title': 'Getting Started',
        'content': '''
        <h5>Welcome to Microbe Insights!</h5>
        <p>This platform helps you analyze microscopic samples for microplastics and plankton detection.</p>
        
        <h6>Quick Start Guide:</h6>
        <ol>
            <li>Navigate to the <strong>Capture</strong> page to start a new analysis</li>
            <li>Follow the 7-step workflow to process your sample</li>
            <li>View results on the <strong>Results</strong> page</li>
            <li>Check <strong>Analytics</strong> for trends and statistics</li>
        </ol>
        
        <h6>Camera Setup:</h6>
        <ul>
            <li>Connect your camera (USB, CSI, or IP)</li>
            <li>Configure camera settings in the <strong>Settings</strong> page</li>
            <li>Test the camera feed before starting analysis</li>
        </ul>
        '''
    },
    'capture_workflow': {
        'title': 'Capture Workflow',
        'content': '''
        <h5>7-Step Analysis Workflow</h5>
        
        <div class="step-item">
            <h6>Step 1: Sample Preparation</h6>
            <p>Prepare your sample slide and ensure proper mounting.</p>
        </div>
        
        <div class="step-item">
            <h6>Step 2: Camera Setup</h6>
            <p>Position the camera and adjust focus for optimal imaging.</p>
        </div>
        
        <div class="step-item">
            <h6>Step 3: Lighting</h6>
            <p>Configure appropriate lighting conditions for your sample type.</p>
        </div>
        
        <div class="step-item">
            <h6>Step 4: Sample Information</h6>
            <p>Enter sample details including name, location, and user information.</p>
        </div>
        
        <div class="step-item">
            <h6>Step 5: Preview & Capture</h6>
            <p>Preview the live feed and capture the image for analysis.</p>
        </div>
        
        <div class="step-item">
            <h6>Step 6: AI Analysis</h6>
            <p>Run microplastic detection and plankton classification algorithms.</p>
        </div>
        
        <div class="step-item">
            <h6>Step 7: Results</h6>
            <p>Review and export your analysis results.</p>
        </div>
        '''
    },
    'ai_models': {
        'title': 'AI Models',
        'content': '''
        <h5>Artificial Intelligence Models</h5>
        
        <h6>Microplastic Detection Model</h6>
        <p>This model identifies and classifies microplastics into four categories:</p>
        <ul>
            <li><strong>Fibers:</strong> Thread-like plastic particles</li>
            <li><strong>Fragments:</strong> Broken pieces of larger plastic items</li>
            <li><strong>Pellets:</strong> Small spherical plastic particles</li>
            <li><strong>Films:</strong> Thin plastic sheets or membranes</li>
        </ul>
        
        <h6>Plankton Classification Model</h6>
        <p>This model identifies and classifies various plankton species:</p>
        <ul>
            <li><strong>Diatoms:</strong> Silica-shelled phytoplankton</li>
            <li><strong>Dinoflagellates:</strong> Motile phytoplankton with flagella</li>
            <li><strong>Copepods:</strong> Small crustacean zooplankton</li>
            <li><strong>And many more species...</strong></li>
        </ul>
        
        <h6>Model Performance</h6>
        <p>Both models are trained on extensive datasets and provide confidence scores for each detection. 
        Results with confidence scores above 0.7 are generally considered reliable.</p>
        '''
    },
    'data_management': {
        'title': 'Data Management',
        'content': '''
        <h5>Managing Your Data</h5>
        
        <h6>Reports</h6>
        <p>All analysis results are automatically saved to the database and can be accessed through the <strong>Reports</strong> page.</p>
        
        <h6>Export Options</h6>
        <ul>
            <li><strong>CSV Export:</strong> Export raw data for further analysis</li>
            <li><strong>PDF Reports:</strong> Generate formatted reports</li>
            <li><strong>Image Downloads:</strong> Save analysis visualizations</li>
        </ul>
        
        <h6>Data Backup</h6>
        <p>Enable automatic backup in Settings to protect your data. The system stores:</p>
        <ul>
            <li>Original captured images</li>
            <li>Analysis results and metadata</li>
            <li>ROI (Region of Interest) images</li>
            <li>Processing logs and statistics</li>
        </ul>
        
        <h6>Cloud Sync</h6>
        <p>Optional cloud synchronization allows you to:</p>
        <ul>
            <li>Access data from multiple devices</li>
            <li>Share results with colleagues</li>
            <li>Create automated backups</li>
        </ul>
        '''
    },
    'troubleshooting': {
        'title': 'Troubleshooting',
        'content': '''
        <h5>Common Issues and Solutions</h5>
        
        <h6>Camera Not Working</h6>
        <ul>
            <li>Check camera connections and power</li>
            <li>Verify camera permissions</li>
            <li>Try different camera types (USB/CSI/IP)</li>
            <li>Restart the application</li>
        </ul>
        
        <h6>Poor Analysis Results</h6>
        <ul>
            <li>Ensure proper lighting and focus</li>
            <li>Check image quality and resolution</li>
            <li>Verify sample preparation</li>
            <li>Adjust confidence thresholds in Settings</li>
        </ul>
        
        <h6>Slow Performance</h6>
        <ul>
            <li>Reduce image resolution in camera settings</li>
            <li>Close unnecessary applications</li>
            <li>Check available disk space</li>
            <li>Restart the system if needed</li>
        </ul>
        
        <h6>Database Issues</h6>
        <ul>
            <li>Check disk space availability</li>
            <li>Verify database file permissions</li>
            <li>Restart the application</li>
            <li>Contact support for data recovery</li>
        </ul>
        '''
    },
    'support': {
        'title': 'Support',
        'content': '''
        <h5>Getting Help</h5>
        
        <h6>Documentation</h6>
        <p>Comprehensive documentation is available in this help section. Browse through the topics above to find answers to common questions.</p>
        
        <h6>Contact Information</h6>
        <div class="contact-info">
            <p><strong>Technical Support:</strong> support@microbeinsights.com</p>
            <p><strong>General Inquiries:</strong> info@microbeinsights.com</p>
            <p><strong>Phone:</strong> +1 (555) 123-4567</p>
            <p><strong>Hours:</strong> Monday - Friday, 9 AM - 5 PM EST</p>
        </div>
        
        <h6>System Information</h6>
        <p>When contacting support, please include:</p>
        <ul>
            <li>Application version</li>
            <li>Operating system details</li>
            <li>Error messages or screenshots</li>
            <li>Steps to reproduce the issue</li>
        </ul>
        
        <h6>Feature Requests</h6>
        <p>We welcome your feedback and suggestions for improving Microbe Insights. Please send feature requests to our support email.</p>
        '''
    }
}

@bp.route('/help')
def help():
    """Help page with documentation"""
    return render_template('help.html', help_sections=HELP_SECTIONS)

@bp.route('/help/api/section/<section_name>')
def get_help_section(section_name):
    """API endpoint to get specific help section"""
    if section_name in HELP_SECTIONS:
        return jsonify({
            'success': True,
            'section': HELP_SECTIONS[section_name]
        })
    else:
        return jsonify({'error': 'Section not found'}), 404

@bp.route('/help/api/search')
def search_help():
    """Search help content"""
    try:
        query = request.args.get('q', '').lower()
        if not query:
            return jsonify({'results': []})
        
        results = []
        for section_name, section_data in HELP_SECTIONS.items():
            if (query in section_data['title'].lower() or 
                query in section_data['content'].lower()):
                results.append({
                    'section': section_name,
                    'title': section_data['title'],
                    'content': section_data['content'][:200] + '...' if len(section_data['content']) > 200 else section_data['content']
                })
        
        return jsonify({
            'success': True,
            'results': results,
            'query': query
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/help/api/feedback', methods=['POST'])
def submit_feedback():
    """Submit feedback or support request"""
    try:
        data = request.get_json()
        feedback_type = data.get('type', 'general')
        message = data.get('message', '')
        user_email = data.get('email', '')
        
        # In a real application, you would save this to a database or send an email
        # For now, we'll just return a success response
        
        return jsonify({
            'success': True,
            'message': 'Thank you for your feedback! We will get back to you soon.'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
