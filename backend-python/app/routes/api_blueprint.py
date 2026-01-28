"""
API Routes
"""
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pytz
from app.services.billing_service import BillingService

bp = Blueprint('api', __name__, url_prefix='/api')

# Helper functions
def get_db():
    """Get database from Flask app context"""
    return current_app.db.db

def get_billing_service():
    """Get billing service"""
    return BillingService(get_db(), current_app.config)

# DEVICES endpoints
@bp.route('/devices', methods=['GET'])
def list_devices():
    """Get all devices"""
    try:
        db = get_db()
        devices = list(db.devices.find({}, {
            '_id': 0,
            'device_id': 1,
            'name': 1,
            'location': 1,
            'status': 1,
            'last_seen': 1,
            'firmware_version': 1
        }).sort('device_id', 1))
        
        return jsonify({'devices': devices, 'count': len(devices)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/devices/<device_id>', methods=['GET'])
def get_device(device_id):
    """Get device details"""
    try:
        db = get_db()
        device = db.devices.find_one({'device_id': device_id}, {'_id': 0})
        
        if not device:
            return jsonify({'error': 'Device not found'}), 404
        
        return jsonify(device), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/devices', methods=['POST'])
def create_device():
    """Create new device"""
    try:
        data = request.get_json()
        db = get_db()
        
        device = {
            'device_id': data.get('device_id'),
            'name': data.get('name', 'Meter'),
            'location': data.get('location', ''),
            'status': 'offline',
            'last_seen': None,
            'firmware_version': '1.0.0',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = db.devices.insert_one(device)
        device['_id'] = str(result.inserted_id)
        
        return jsonify({'message': 'Device created', 'device': device}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# READINGS endpoints
@bp.route('/devices/<device_id>/readings', methods=['GET'])
def get_readings(device_id):
    """Get device readings with optional aggregation"""
    try:
        db = get_db()
        
        # Query parameters
        from_date = request.args.get('from')
        to_date = request.args.get('to')
        agg = request.args.get('agg', 'raw')  # raw, hour, day, week, month
        
        # Default: last 24 hours
        if not to_date:
            to_dt = datetime.utcnow()
        else:
            to_dt = datetime.fromisoformat(to_date.replace('Z', '+00:00'))
        
        if not from_date:
            from_dt = to_dt - timedelta(hours=24)
        else:
            from_dt = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
        
        # Query readings
        query = {
            'device_id': device_id,
            'timestamp': {'$gte': from_dt, '$lte': to_dt}
        }
        
        readings = list(db.meter_readings.find(query).sort('timestamp', 1))
        
        # Convert ObjectId to string and datetime to ISO format
        for reading in readings:
            reading['_id'] = str(reading['_id'])
            if isinstance(reading.get('timestamp'), datetime):
                reading['timestamp'] = reading['timestamp'].isoformat()
        
        return jsonify({
            'device_id': device_id,
            'from': from_dt.isoformat(),
            'to': to_dt.isoformat(),
            'count': len(readings),
            'readings': readings
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# BILLING endpoints
@bp.route('/billing/<device_id>', methods=['GET'])
def get_billing(device_id):
    """Get bill for a specific month"""
    try:
        month = request.args.get('month')
        if not month:
            # Default: current month
            month = datetime.utcnow().strftime('%Y-%m')
        
        billing_svc = get_billing_service()
        bill = billing_svc.compute_bill(device_id, month)
        
        if not bill:
            return jsonify({'error': 'Unable to compute bill'}), 400
        
        return jsonify(bill), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/invoices/<device_id>', methods=['GET'])
def get_invoices(device_id):
    """Get list of invoices for device"""
    try:
        db = get_db()
        limit = request.args.get('limit', 12, type=int)
        
        invoices = list(db.invoices.find(
            {'device_id': device_id}
        ).sort('month', -1).limit(limit))
        
        # Convert ObjectId to string
        for inv in invoices:
            inv['_id'] = str(inv['_id'])
            if isinstance(inv.get('created_at'), datetime):
                inv['created_at'] = inv['created_at'].isoformat()
            if isinstance(inv.get('due_date'), datetime):
                inv['due_date'] = inv['due_date'].isoformat()
        
        return jsonify({'invoices': invoices}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/invoices/<invoice_id>/download', methods=['GET'])
def download_invoice(invoice_id):
    """Download invoice PDF (placeholder)"""
    try:
        db = get_db()
        from bson import ObjectId
        
        invoice = db.invoices.find_one({'_id': ObjectId(invoice_id)})
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
        
        # Return JSON representation for now (PDF generation in frontend)
        invoice['_id'] = str(invoice['_id'])
        return jsonify(invoice), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# TARIFFS endpoints
@bp.route('/tariffs', methods=['GET'])
def get_tariffs():
    """Get tariff configuration"""
    try:
        db = get_db()
        tariff = db.tariffs.find_one({'name': 'default'}, {'_id': 0})
        
        if not tariff:
            return jsonify({'error': 'Tariff not found'}), 404
        
        return jsonify(tariff), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/tariffs', methods=['POST'])
def update_tariffs():
    """Update tariff configuration (admin only)"""
    try:
        data = request.get_json()
        db = get_db()
        
        updated_tariff = {
            'slabs': data.get('slabs', []),
            'fixed_charge': data.get('fixed_charge', 50),
            'tax_rate': data.get('tax_rate', 0.18),
            'currency': data.get('currency', 'INR'),
            'updated_at': datetime.utcnow()
        }
        
        db.tariffs.update_one(
            {'name': 'default'},
            {'$set': updated_tariff},
            upsert=True
        )
        
        return jsonify({'message': 'Tariff updated', 'tariff': updated_tariff}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
