"""
Database service for Microbe Insights
Handles SQLite database operations for reports and analytics
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

DATABASE_PATH = 'data/reports.db'

def init_database():
    """Initialize SQLite database with required tables"""
    os.makedirs('data', exist_ok=True)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create reports table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slide_name TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            location TEXT,
            user TEXT,
            microplastics_present BOOLEAN DEFAULT FALSE,
            particle_count INTEGER DEFAULT 0,
            confidence REAL DEFAULT 0.0,
            plankton_summary TEXT,
            image_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create analytics table for statistics
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_name TEXT NOT NULL,
            metric_value REAL NOT NULL,
            timestamp TEXT NOT NULL,
            metadata TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def create_report(slide_name: str, location: str, user: str, 
                 microplastic_result: Dict, plankton_result: Dict, 
                 image_path: str) -> int:
    """Create a new report record"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Extract microplastic data
    microplastics_present = microplastic_result.get('present', False)
    particle_count = microplastic_result.get('count', 0)
    confidence = microplastic_result.get('confidence', 0.0)
    
    # Extract plankton data
    plankton_summary = json.dumps(plankton_result) if plankton_result else None
    
    cursor.execute('''
        INSERT INTO reports (slide_name, timestamp, location, user, 
                           microplastics_present, particle_count, confidence, 
                           plankton_summary, image_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (slide_name, datetime.now().isoformat(), location, user,
          microplastics_present, particle_count, confidence, 
          plankton_summary, image_path))
    
    report_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return report_id

def get_report_by_id(report_id: int) -> Optional[Dict]:
    """Get a specific report by ID"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM reports WHERE id = ?', (report_id,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row:
        return dict(row)
    return None

def get_recent_reports(limit: int = 50, offset: int = 0) -> List[Dict]:
    """Get recent reports with pagination"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM reports 
        ORDER BY created_at DESC 
        LIMIT ? OFFSET ?
    ''', (limit, offset))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def search_reports(search_term: str = '', date_from: str = '', date_to: str = '', 
                  limit: int = 50, offset: int = 0) -> List[Dict]:
    """Search reports with filters"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = 'SELECT * FROM reports WHERE 1=1'
    params = []
    
    if search_term:
        query += ' AND (slide_name LIKE ? OR location LIKE ? OR user LIKE ?)'
        search_param = f'%{search_term}%'
        params.extend([search_param, search_param, search_param])
    
    if date_from:
        query += ' AND timestamp >= ?'
        params.append(date_from)
    
    if date_to:
        query += ' AND timestamp <= ?'
        params.append(date_to)
    
    query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def get_analytics_data() -> Dict:
    """Get analytics data for dashboard"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Get total reports count
    cursor.execute('SELECT COUNT(*) FROM reports')
    total_reports = cursor.fetchone()[0]
    
    # Get microplastic detection count
    cursor.execute('SELECT COUNT(*) FROM reports WHERE microplastics_present = 1')
    microplastic_detections = cursor.fetchone()[0]
    
    # Get average confidence
    cursor.execute('SELECT AVG(confidence) FROM reports WHERE microplastics_present = 1')
    avg_confidence = cursor.fetchone()[0] or 0
    
    # Get detection rate by month
    cursor.execute('''
        SELECT strftime('%Y-%m', timestamp) as month, 
               COUNT(*) as total,
               SUM(CASE WHEN microplastics_present = 1 THEN 1 ELSE 0 END) as detections
        FROM reports 
        GROUP BY month 
        ORDER BY month DESC 
        LIMIT 12
    ''')
    monthly_data = cursor.fetchall()
    
    # Get species distribution
    cursor.execute('SELECT plankton_summary FROM reports WHERE plankton_summary IS NOT NULL')
    species_data = cursor.fetchall()
    
    species_distribution = {}
    for row in species_data:
        try:
            plankton_data = json.loads(row[0])
            if 'summary' in plankton_data:
                for species, count in plankton_data['summary'].items():
                    species_distribution[species] = species_distribution.get(species, 0) + count
        except:
            continue
    
    conn.close()
    
    return {
        'total_reports': total_reports,
        'microplastic_detections': microplastic_detections,
        'detection_rate': (microplastic_detections / total_reports * 100) if total_reports > 0 else 0,
        'average_confidence': avg_confidence,
        'monthly_data': [{'month': row[0], 'total': row[1], 'detections': row[2]} for row in monthly_data],
        'species_distribution': species_distribution
    }

def update_report(report_id: int, **kwargs) -> bool:
    """Update a report record"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Build update query dynamically
    set_clauses = []
    params = []
    
    for key, value in kwargs.items():
        if key in ['slide_name', 'location', 'user', 'microplastics_present', 
                  'particle_count', 'confidence', 'plankton_summary', 'image_path']:
            set_clauses.append(f'{key} = ?')
            params.append(value)
    
    if not set_clauses:
        return False
    
    params.append(report_id)
    query = f'UPDATE reports SET {", ".join(set_clauses)} WHERE id = ?'
    
    cursor.execute(query, params)
    success = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    
    return success

def delete_report(report_id: int) -> bool:
    """Delete a report record"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM reports WHERE id = ?', (report_id,))
    success = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    
    return success

def get_report_statistics() -> Dict:
    """Get comprehensive report statistics"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Basic counts
    cursor.execute('SELECT COUNT(*) FROM reports')
    total_reports = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM reports WHERE microplastics_present = 1')
    microplastic_reports = cursor.fetchone()[0]
    
    # Confidence statistics
    cursor.execute('''
        SELECT MIN(confidence), MAX(confidence), AVG(confidence) 
        FROM reports WHERE microplastics_present = 1
    ''')
    confidence_stats = cursor.fetchone()
    
    # Recent activity (last 7 days)
    cursor.execute('''
        SELECT COUNT(*) FROM reports 
        WHERE created_at >= datetime('now', '-7 days')
    ''')
    recent_reports = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'total_reports': total_reports,
        'microplastic_reports': microplastic_reports,
        'detection_rate': (microplastic_reports / total_reports * 100) if total_reports > 0 else 0,
        'confidence_stats': {
            'min': confidence_stats[0] or 0,
            'max': confidence_stats[1] or 0,
            'avg': confidence_stats[2] or 0
        },
        'recent_activity': recent_reports
    }
