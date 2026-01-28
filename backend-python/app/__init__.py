"""
Flask App Factory
"""
from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import logging
from app.config.config import get_config
from app.models.database import Database
from app.services.mqtt_service import MQTTService
from app.routes import api_blueprint

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure Flask app"""
    config = get_config()
    app = Flask(__name__)
    app.config.from_object(config)
    
    # Enable CORS
    CORS(app, resources={r'/api/*': {'origins': config.CORS_ORIGINS}})
    
    # MongoDB connection
    try:
        mongo_client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=5000)
        mongo_client.server_info()  # Test connection
        app.db = Database(mongo_client, config.DB_NAME)
        logger.info(f'Connected to MongoDB: {config.DB_NAME}')
    except Exception as e:
        logger.error(f'MongoDB connection failed: {e}')
        raise
    
    # MQTT Service
    try:
        app.mqtt = MQTTService(config, app.db.db)
        app.mqtt.connect()
    except Exception as e:
        logger.error(f'MQTT service initialization failed: {e}')
    
    # Register blueprints
    app.register_blueprint(api_blueprint.bp)
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'ok',
            'mqtt_connected': app.mqtt.connected if hasattr(app, 'mqtt') else False,
            'db_connected': True
        }), 200
    
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        """Clean up on app shutdown"""
        pass
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
