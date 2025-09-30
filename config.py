"""
Configuration settings for Microbe Insights Flask application
"""

import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'microbe_insights_secret_key_2024'
    
    # Database
    DATABASE_PATH = 'data/reports.db'
    
    # File uploads
    UPLOAD_FOLDER = 'data/uploads'
    CAPTURE_FOLDER = 'data/captures'
    RESULTS_FOLDER = 'data/results'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Camera settings
    DEFAULT_CAMERA_ID = 0
    DEFAULT_CAMERA_TYPE = 'usb'  # 'usb', 'csi', 'ip'
    DEFAULT_RESOLUTION = (1280, 720)
    DEFAULT_FPS = 30
    
    # AI Model settings
    MICROPLASTIC_MODEL_PATH = 'models/microplastic_model.pth'
    PLANKTON_MODEL_PATH = 'models/plankton_model.pth'
    
    # Application settings
    ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    # User settings (can be configured via settings page)
    USER_NAME = os.environ.get('USER_NAME', 'Researcher')
    LAB_LOCATION = os.environ.get('LAB_LOCATION', 'Lab Station 1')
    
    # Cloud sync settings
    CLOUD_SYNC_ENABLED = os.environ.get('CLOUD_SYNC_ENABLED', 'False').lower() == 'true'
    CLOUD_API_KEY = os.environ.get('CLOUD_API_KEY', '')
    CLOUD_BUCKET = os.environ.get('CLOUD_BUCKET', '')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    ENVIRONMENT = 'development'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    ENVIRONMENT = 'production'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
