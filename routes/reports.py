"""
Reports route - View and filter analysis reports
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from services.database import get_recent_reports, get_report_by_id, search_reports

bp = Blueprint('reports', __name__)

@bp.route('/reports')
def reports():
    """Reports listing page"""
    # Get filter parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search_term = request.args.get('search', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    # Get reports based on filters
    if search_term or date_from or date_to:
        reports = search_reports(
            search_term=search_term,
            date_from=date_from,
            date_to=date_to,
            limit=per_page,
            offset=(page - 1) * per_page
        )
        total_count = len(search_reports(search_term, date_from, date_to))
    else:
        reports = get_recent_reports(limit=per_page, offset=(page - 1) * per_page)
        total_count = len(get_recent_reports(limit=1000))  # Get total count
    
    # Calculate pagination
    total_pages = (total_count + per_page - 1) // per_page
    
    pagination = {
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages,
        'total_count': total_count,
        'has_prev': page > 1,
        'has_next': page < total_pages
    }
    
    return render_template('reports.html', 
                         reports=reports, 
                         pagination=pagination,
                         filters={
                             'search': search_term,
                             'date_from': date_from,
                             'date_to': date_to
                         })

@bp.route('/reports/<int:report_id>')
def view_report(report_id):
    """View individual report"""
    report = get_report_by_id(report_id)
    if not report:
        return redirect(url_for('reports.reports'))
    
    return redirect(url_for('results.results', report_id=report_id))

@bp.route('/reports/api/search', methods=['POST'])
def api_search():
    """API endpoint for report search"""
    try:
        data = request.get_json()
        search_term = data.get('search', '')
        date_from = data.get('date_from', '')
        date_to = data.get('date_to', '')
        
        reports = search_reports(search_term, date_from, date_to, limit=50)
        
        return jsonify({
            'success': True,
            'reports': reports
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/reports/api/export/<int:report_id>')
def export_report(report_id):
    """Export report as CSV"""
    try:
        report = get_report_by_id(report_id)
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        # Generate CSV content
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(['Field', 'Value'])
        
        # Write data
        writer.writerow(['ID', report['id']])
        writer.writerow(['Slide Name', report['slide_name']])
        writer.writerow(['Location', report['location']])
        writer.writerow(['User', report['user']])
        writer.writerow(['Timestamp', report['timestamp']])
        writer.writerow(['Microplastics Present', report['microplastics_present']])
        writer.writerow(['Particle Count', report['particle_count']])
        writer.writerow(['Confidence', report['confidence']])
        writer.writerow(['Plankton Summary', report['plankton_summary']])
        
        csv_content = output.getvalue()
        output.close()
        
        return jsonify({
            'success': True,
            'csv_content': csv_content,
            'filename': f"report_{report_id}.csv"
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
