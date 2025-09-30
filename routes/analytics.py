"""
Analytics route - Data visualization and statistics
"""

from flask import Blueprint, render_template, jsonify
from services.database import get_analytics_data, get_recent_reports
from datetime import datetime, timedelta
import json

bp = Blueprint('analytics', __name__)

@bp.route('/analytics')
def analytics():
    """Analytics dashboard page"""
    return render_template('analytics.html')

@bp.route('/analytics/api/stats')
def get_stats():
    """Get analytics statistics"""
    try:
        # Get recent reports for analysis
        reports = get_recent_reports(limit=100)
        
        # Calculate basic statistics
        total_reports = len(reports)
        microplastic_reports = sum(1 for r in reports if r.get('microplastics_present', False))
        detection_rate = (microplastic_reports / total_reports * 100) if total_reports > 0 else 0
        
        # Calculate average processing time (simulated)
        avg_processing_time = 2.5  # seconds
        
        # Calculate storage usage (simulated)
        storage_usage = total_reports * 2.5  # MB per report
        
        # Get species distribution
        species_dist = {}
        for report in reports:
            if report.get('plankton_summary'):
                try:
                    plankton_data = json.loads(report['plankton_summary'])
                    if 'summary' in plankton_data:
                        for species, count in plankton_data['summary'].items():
                            species_dist[species] = species_dist.get(species, 0) + count
                except:
                    continue
        
        # Get daily detection trends (last 7 days)
        daily_trends = []
        for i in range(7):
            date = datetime.now() - timedelta(days=i)
            day_reports = [r for r in reports if r['timestamp'].startswith(date.strftime('%Y-%m-%d'))]
            daily_trends.append({
                'date': date.strftime('%Y-%m-%d'),
                'total': len(day_reports),
                'detections': sum(1 for r in day_reports if r.get('microplastics_present', False))
            })
        
        return jsonify({
            'success': True,
            'stats': {
                'total_reports': total_reports,
                'microplastic_detections': microplastic_reports,
                'detection_rate': round(detection_rate, 1),
                'avg_processing_time': avg_processing_time,
                'storage_usage': round(storage_usage, 1),
                'species_distribution': species_dist,
                'daily_trends': daily_trends
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/analytics/api/charts')
def get_charts_data():
    """Get data for charts"""
    try:
        reports = get_recent_reports(limit=50)
        
        # Microplastic type distribution
        microplastic_types = {'fiber': 0, 'fragment': 0, 'pellet': 0, 'film': 0}
        for report in reports:
            if report.get('microplastics_present', False):
                # Simulate type distribution based on count
                count = report.get('particle_count', 0)
                if count > 10:
                    microplastic_types['fragment'] += 1
                elif count > 5:
                    microplastic_types['fiber'] += 1
                elif count > 2:
                    microplastic_types['pellet'] += 1
                else:
                    microplastic_types['film'] += 1
        
        # Confidence distribution
        confidence_ranges = {'0-0.5': 0, '0.5-0.7': 0, '0.7-0.9': 0, '0.9-1.0': 0}
        for report in reports:
            confidence = report.get('confidence', 0)
            if confidence < 0.5:
                confidence_ranges['0-0.5'] += 1
            elif confidence < 0.7:
                confidence_ranges['0.5-0.7'] += 1
            elif confidence < 0.9:
                confidence_ranges['0.7-0.9'] += 1
            else:
                confidence_ranges['0.9-1.0'] += 1
        
        # Processing time trends (simulated)
        processing_times = [2.1, 2.3, 2.0, 2.4, 2.2, 2.5, 2.1, 2.6, 2.3, 2.2]
        
        return jsonify({
            'success': True,
            'charts': {
                'microplastic_types': microplastic_types,
                'confidence_distribution': confidence_ranges,
                'processing_times': processing_times
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/analytics/api/export')
def export_analytics():
    """Export analytics data"""
    try:
        reports = get_recent_reports(limit=1000)
        
        # Generate summary data
        summary = {
            'export_date': datetime.now().isoformat(),
            'total_reports': len(reports),
            'date_range': {
                'from': min(r['timestamp'] for r in reports) if reports else None,
                'to': max(r['timestamp'] for r in reports) if reports else None
            },
            'microplastic_detection_rate': sum(1 for r in reports if r.get('microplastics_present', False)) / len(reports) * 100 if reports else 0,
            'average_confidence': sum(r.get('confidence', 0) for r in reports) / len(reports) if reports else 0
        }
        
        return jsonify({
            'success': True,
            'summary': summary,
            'reports': reports
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
