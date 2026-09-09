import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = FLASK_ENV == 'development'
    
    # Server
    HOST = '0.0.0.0'
    PORT = int(os.getenv('FLASK_PORT', 5000))
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///./ai_review.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # LLM
    OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'mistral')
    
    # Jira
    JIRA_HOST = os.getenv('JIRA_HOST', 'http://localhost:8080')
    JIRA_USERNAME = os.getenv('JIRA_USERNAME', 'admin')
    JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN', '')
    JIRA_PROJECT_KEY = os.getenv('JIRA_PROJECT_KEY', 'AICR')
    
    # Analysis
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 1000000))  # 1MB
    ANALYSIS_TIMEOUT = int(os.getenv('ANALYSIS_TIMEOUT', 30))  # 30 seconds
    CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'True').lower() == 'true'
    
    # CORS
    CORS_ORIGINS = ['http://localhost:*', 'vscode-webview://*']

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
