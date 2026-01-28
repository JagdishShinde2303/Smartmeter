import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    DEBUG = False
    TESTING = False
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-prod')
    
    # MongoDB
    MONGO_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/smartmeter')
    DB_NAME = os.getenv('MONGODB_DB_NAME', 'smartmeter')
    
    # MQTT
    MQTT_HOST = os.getenv('MQTT_HOST', 'localhost')
    MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
    MQTT_USERNAME = os.getenv('MQTT_USERNAME', '')
    MQTT_PASSWORD = os.getenv('MQTT_PASSWORD', '')
    MQTT_CLIENT_ID = os.getenv('MQTT_CLIENT_ID', 'backend-service')
    MQTT_TOPIC_SUB = os.getenv('MQTT_TOPIC_SUBSCRIBE', 'smartmeter/+/telemetry')
    
    # JWT
    JWT_SECRET = os.getenv('JWT_SECRET', 'jwt-secret-key')
    JWT_EXPIRY = os.getenv('JWT_EXPIRY', '7d')
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGIN', 'http://localhost:3000').split(',')
    
    # Billing
    TIMEZONE = os.getenv('TIMEZONE', 'Asia/Kolkata')
    CURRENCY = os.getenv('DEFAULT_CURRENCY', 'INR')
    
    # Email
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USER = os.getenv('SMTP_USER', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    SMTP_FROM = os.getenv('SMTP_FROM', 'noreply@smartmeter.local')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    MONGO_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/smartmeter-dev')

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    MONGO_URI = 'mongodb://localhost:27017/smartmeter-test'
    JWT_SECRET = 'test-secret'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

config_by_name = {
    'dev': DevelopmentConfig,
    'test': TestingConfig,
    'prod': ProductionConfig,
}

def get_config():
    """Get configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'dev')
    return config_by_name.get(env, DevelopmentConfig)
