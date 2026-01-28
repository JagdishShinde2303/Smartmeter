# Backend Python - Setup & Run

## Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

```bash
cp .env.example .env
# Edit .env with your settings
```

## MongoDB Setup

```bash
# Make sure MongoDB is running
# For local development: mongod
# For MongoDB Atlas: update MONGODB_URI in .env
```

## MQTT Broker Setup

```bash
# Docker (recommended)
docker run -it -p 1883:1883 eclipse-mosquitto

# Or install locally and run
mosquitto -v
```

## Running the Backend

```bash
# Development
python run.py

# Production (with gunicorn)
gunicorn -w 4 -b 0.0.0.0:5000 'app:create_app()'
```

Server runs on `http://localhost:5000`

## API Endpoints

### Devices
- `GET /api/devices` - List all devices
- `GET /api/devices/<device_id>` - Get device details
- `POST /api/devices` - Create device

### Readings
- `GET /api/devices/<device_id>/readings` - Get telemetry readings

### Billing
- `GET /api/billing/<device_id>?month=YYYY-MM` - Compute bill
- `GET /api/invoices/<device_id>` - List invoices
- `GET /api/invoices/<invoice_id>/download` - Get invoice

### Tariffs
- `GET /api/tariffs` - Get tariff config
- `POST /api/tariffs` - Update tariff

## Testing

```bash
# Test API with curl
curl http://localhost:5000/health
curl http://localhost:5000/api/devices

# Test MQTT
mosquitto_pub -h localhost -t "smartmeter/meter-001/telemetry" \
  -m '{"device_id":"meter-001","timestamp":"2026-01-29T10:00:00Z","voltage":230,"current":2.5,"power_w":575,"energy_kwh":10.5,"power_factor":0.98,"rssi":-60}'
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| MongoDB connection error | Check MongoDB URI, verify service is running |
| MQTT connection error | Check broker is running and accessible |
| Port already in use | Change PORT in .env or kill process on port 5000 |

---

See [Backend Python README](README.md) for full documentation.
