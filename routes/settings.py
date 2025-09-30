"""
Settings route - Application configuration and preferences
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
import os
import json

bp = Blueprint('settings', __name__)

# Default settings
DEFAULT_SETTINGS = {
    'camera': {
        'resolution': {'width': 1280, 'height': 720},
        'fps': 30,
        'exposure': 0,
        'brightness': 0,
        'contrast': 0
    },
    'models': {
        'microplastic_version': 'v1.0',
        'plankton_version': 'v1.0',
        'confidence_threshold': 0.7
    },
    'cloud': {
        'sync_enabled': False,
        'auto_upload': False,
        'compression': True
    },
    'system': {
        'auto_save': True,
        'backup_enabled': True,
        'notifications': True
    }
}

def load_settings():
    """Load settings from file"""
    settings_file = 'data/settings.json'
    if os.path.exists(settings_file):
        try:
            with open(settings_file, 'r') as f:
                settings = json.load(f)
                # Merge with defaults for any missing keys
                return merge_settings(DEFAULT_SETTINGS, settings)
        except:
            pass
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    """Save settings to file"""
    os.makedirs('data', exist_ok=True)
    settings_file = 'data/settings.json'
    try:
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
        return True
    except:
        return False

def merge_settings(default, user):
    """Merge user settings with defaults"""
    result = default.copy()
    for key, value in user.items():
        if key in result and isinstance(value, dict) and isinstance(result[key], dict):
            result[key] = merge_settings(result[key], value)
        else:
            result[key] = value
    return result

@bp.route('/settings')
def settings():
    """Settings page"""
    current_settings = load_settings()
    return render_template('settings.html', settings=current_settings)

@bp.route('/settings/camera', methods=['POST'])
def update_camera_settings():
    """Update camera settings"""
    try:
        settings = load_settings()
        
        data = request.get_json()
        settings['camera']['resolution']['width'] = data.get('width', 1280)
        settings['camera']['resolution']['height'] = data.get('height', 720)
        settings['camera']['fps'] = data.get('fps', 30)
        settings['camera']['exposure'] = data.get('exposure', 0)
        settings['camera']['brightness'] = data.get('brightness', 0)
        settings['camera']['contrast'] = data.get('contrast', 0)
        
        if save_settings(settings):
            return jsonify({'success': True, 'message': 'Camera settings updated'})
        else:
            return jsonify({'error': 'Failed to save settings'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/settings/models', methods=['POST'])
def update_model_settings():
    """Update model settings"""
    try:
        settings = load_settings()
        
        data = request.get_json()
        settings['models']['microplastic_version'] = data.get('microplastic_version', 'v1.0')
        settings['models']['plankton_version'] = data.get('plankton_version', 'v1.0')
        settings['models']['confidence_threshold'] = data.get('confidence_threshold', 0.7)
        
        if save_settings(settings):
            return jsonify({'success': True, 'message': 'Model settings updated'})
        else:
            return jsonify({'error': 'Failed to save settings'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/settings/cloud', methods=['POST'])
def update_cloud_settings():
    """Update cloud sync settings"""
    try:
        settings = load_settings()
        
        data = request.get_json()
        settings['cloud']['sync_enabled'] = data.get('sync_enabled', False)
        settings['cloud']['auto_upload'] = data.get('auto_upload', False)
        settings['cloud']['compression'] = data.get('compression', True)
        
        if save_settings(settings):
            return jsonify({'success': True, 'message': 'Cloud settings updated'})
        else:
            return jsonify({'error': 'Failed to save settings'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/settings/system', methods=['POST'])
def update_system_settings():
    """Update system settings"""
    try:
        settings = load_settings()
        
        data = request.get_json()
        settings['system']['auto_save'] = data.get('auto_save', True)
        settings['system']['backup_enabled'] = data.get('backup_enabled', True)
        settings['system']['notifications'] = data.get('notifications', True)
        
        if save_settings(settings):
            return jsonify({'success': True, 'message': 'System settings updated'})
        else:
            return jsonify({'error': 'Failed to save settings'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/settings/reset', methods=['POST'])
def reset_settings():
    """Reset all settings to defaults"""
    try:
        if save_settings(DEFAULT_SETTINGS):
            return jsonify({'success': True, 'message': 'Settings reset to defaults'})
        else:
            return jsonify({'error': 'Failed to reset settings'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/settings/export', methods=['GET'])
def export_settings():
    """Export settings as JSON"""
    try:
        settings = load_settings()
        return jsonify({
            'success': True,
            'settings': settings,
            'export_date': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/settings/import', methods=['POST'])
def import_settings():
    """Import settings from JSON"""
    try:
        data = request.get_json()
        settings = data.get('settings', {})
        
        # Validate settings structure
        if not isinstance(settings, dict):
            return jsonify({'error': 'Invalid settings format'}), 400
        
        # Merge with defaults to ensure all required keys exist
        merged_settings = merge_settings(DEFAULT_SETTINGS, settings)
        
        if save_settings(merged_settings):
            return jsonify({'success': True, 'message': 'Settings imported successfully'})
        else:
            return jsonify({'error': 'Failed to save imported settings'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
