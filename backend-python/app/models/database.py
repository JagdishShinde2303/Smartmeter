"""
Database Models for Smart Energy Meter
"""
from datetime import datetime
from pymongo import ASCENDING, DESCENDING
from bson import ObjectId

class Database:
    """MongoDB database wrapper"""
    def __init__(self, client, db_name):
        self.client = client
        self.db = client[db_name]
        self._init_collections()
    
    def _init_collections(self):
        """Initialize collections with indexes"""
        # Meter Readings (Time-Series)
        if 'meter_readings' not in self.db.list_collection_names():
            self.db.create_collection('meter_readings')
        
        self.db.meter_readings.create_index([('device_id', ASCENDING), ('timestamp', DESCENDING)])
        self.db.meter_readings.create_index([('timestamp', DESCENDING)])
        
        # Devices
        if 'devices' not in self.db.list_collection_names():
            self.db.create_collection('devices')
        self.db.devices.create_index([('device_id', ASCENDING)])
        
        # Users
        if 'users' not in self.db.list_collection_names():
            self.db.create_collection('users')
        self.db.users.create_index([('email', ASCENDING)])
        
        # Invoices
        if 'invoices' not in self.db.list_collection_names():
            self.db.create_collection('invoices')
        self.db.invoices.create_index([('device_id', ASCENDING), ('month', DESCENDING)])
        
        # Tariffs
        if 'tariffs' not in self.db.list_collection_names():
            self.db.create_collection('tariffs')
            # Insert default tariff
            self.db.tariffs.insert_one({
                'name': 'default',
                'slabs': [
                    {'range': '0-100', 'rate': 3.50},
                    {'range': '101-300', 'rate': 4.50},
                    {'range': '301+', 'rate': 6.00}
                ],
                'fixed_charge': 50,
                'tax_rate': 0.18,
                'currency': 'INR',
                'created_at': datetime.utcnow()
            })

# Device Schema
DEVICE_SCHEMA = {
    '_id': ObjectId,
    'device_id': str,
    'name': str,
    'location': str,
    'user_id': ObjectId,
    'status': str,  # online, offline, error
    'last_seen': datetime,
    'firmware_version': str,
    'created_at': datetime,
    'updated_at': datetime
}

# Meter Reading Schema (Time-Series)
METER_READING_SCHEMA = {
    '_id': ObjectId,
    'device_id': str,
    'timestamp': datetime,
    'voltage': float,
    'current': float,
    'power_w': float,
    'energy_kwh': float,
    'power_factor': float,
    'rssi': int,
    'created_at': datetime
}

# Invoice Schema
INVOICE_SCHEMA = {
    '_id': ObjectId,
    'device_id': str,
    'month': str,  # YYYY-MM
    'energy_kwh': float,
    'slabs': list,  # [{'slab': '0-100', 'units': 50, 'rate': 3.5, 'charge': 175}, ...]
    'subtotal': float,
    'fixed_charge': float,
    'tax': float,
    'total': float,
    'status': str,  # issued, paid, overdue
    'pdf_url': str,
    'email_sent': bool,
    'created_at': datetime,
    'due_date': datetime,
    'paid_date': datetime
}

# User Schema
USER_SCHEMA = {
    '_id': ObjectId,
    'email': str,
    'password_hash': str,
    'name': str,
    'phone': str,
    'role': str,  # user, admin
    'devices': list,  # [device_id, ...]
    'created_at': datetime,
    'updated_at': datetime
}

# Tariff Schema
TARIFF_SCHEMA = {
    '_id': ObjectId,
    'name': str,
    'slabs': list,  # [{'range': '0-100', 'rate': 3.5}, ...]
    'fixed_charge': float,
    'tax_rate': float,
    'currency': str,
    'created_at': datetime,
    'updated_at': datetime
}
