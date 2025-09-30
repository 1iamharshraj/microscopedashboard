"""
Home route - Main dashboard page
"""

from flask import Blueprint, render_template, jsonify
from services.database import get_recent_reports

bp = Blueprint('home', __name__)

@bp.route('/')
def home():
    """Main dashboard page"""
    # Get recent reports for dashboard stats
    reports = get_recent_reports(limit=10)
    
    # Calculate statistics
    total_reports = len(reports)
    microplastic_detections = sum(1 for r in reports if r.get('microplastics_present', False))
    plankton_analyses = sum(1 for r in reports if r.get('plankton_summary'))
    
    stats = {
        'total_reports': total_reports,
        'microplastic_detections': microplastic_detections,
        'plankton_analyses': plankton_analyses,
        'recent_reports': reports[:5]  # Show 5 most recent
    }
    
    return render_template('home.html', stats=stats)

@bp.route('/api/dashboard_stats')
def dashboard_stats():
    """API endpoint for dashboard statistics"""
    reports = get_recent_reports(limit=50)
    
    stats = {
        'total_reports': len(reports),
        'microplastic_detections': sum(1 for r in reports if r.get('microplastics_present', False)),
        'plankton_analyses': sum(1 for r in reports if r.get('plankton_summary')),
        'last_analysis': reports[0].get('timestamp') if reports else None
    }
    
    return jsonify(stats)
