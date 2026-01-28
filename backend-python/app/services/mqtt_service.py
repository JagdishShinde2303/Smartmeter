"""
MQTT Service - handles Mosquitto connection and telemetry ingestion
"""
import paho.mqtt.client as mqtt
import json
import logging
from datetime import datetime
from threading import Thread

logger = logging.getLogger(__name__)

class MQTTService:
    """MQTT broker connection and message handling"""
    
    def __init__(self, config, db):
        self.config = config
        self.db = db
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, config.MQTT_CLIENT_ID)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.connected = False
    
    def connect(self):
        """Connect to MQTT broker"""
        try:
            if self.config.MQTT_USERNAME:
                self.client.username_pw_set(self.config.MQTT_USERNAME, self.config.MQTT_PASSWORD)
            
            self.client.connect(self.config.MQTT_HOST, self.config.MQTT_PORT, keepalive=60)
            self.client.subscribe(self.config.MQTT_TOPIC_SUB)
            
            # Start loop in background thread
            self.client.loop_start()
            logger.info(f'MQTT client connecting to {self.config.MQTT_HOST}:{self.config.MQTT_PORT}')
        except Exception as e:
            logger.error(f'MQTT connection error: {e}')
    
    def on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            self.connected = True
            logger.info('MQTT broker connected')
            client.subscribe(self.config.MQTT_TOPIC_SUB)
            logger.info(f'Subscribed to {self.config.MQTT_TOPIC_SUB}')
        else:
            logger.error(f'MQTT connection failed with code {rc}')
    
    def on_disconnect(self, client, userdata, rc):
        """MQTT disconnect callback"""
        self.connected = False
        if rc != 0:
            logger.warning(f'Unexpected MQTT disconnection with code {rc}')
        else:
            logger.info('MQTT broker disconnected')
    
    def on_message(self, client, userdata, msg):
        """MQTT message received callback"""
        try:
            payload = json.loads(msg.payload.decode())
            self.process_telemetry(payload)
        except json.JSONDecodeError:
            logger.error(f'Invalid JSON payload: {msg.payload}')
        except Exception as e:
            logger.error(f'Error processing MQTT message: {e}')
    
    def process_telemetry(self, payload):
        """Process incoming telemetry and save to DB"""
        try:
            # Validate required fields
            required_fields = ['device_id', 'timestamp', 'voltage', 'current', 'power_w', 'energy_kwh']
            if not all(field in payload for field in required_fields):
                logger.warning(f'Missing required fields in payload: {payload}')
                return
            
            # Ensure timestamp is datetime
            if isinstance(payload['timestamp'], str):
                payload['timestamp'] = datetime.fromisoformat(payload['timestamp'].replace('Z', '+00:00'))
            
            payload['created_at'] = datetime.utcnow()
            
            # Save to MongoDB
            self.db.meter_readings.insert_one(payload)
            
            # Update device last_seen
            self.db.devices.update_one(
                {'device_id': payload['device_id']},
                {'$set': {'last_seen': datetime.utcnow(), 'status': 'online'}},
                upsert=True
            )
            
            logger.debug(f'Telemetry saved: {payload["device_id"]} @ {payload["timestamp"]}')
        
        except Exception as e:
            logger.error(f'Error processing telemetry: {e}')
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        self.client.loop_stop()
        self.client.disconnect()
        self.connected = False
        logger.info('MQTT client disconnected')
    
    def publish(self, topic, payload):
        """Publish message to MQTT topic"""
        try:
            self.client.publish(topic, json.dumps(payload), qos=1)
            logger.debug(f'Published to {topic}')
        except Exception as e:
            logger.error(f'Error publishing to MQTT: {e}')
