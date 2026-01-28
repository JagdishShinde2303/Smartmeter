# Complete Smart Energy Meter Project

**Python Backend + Vanilla JavaScript Frontend + ESP32 Firmware**

This is a complete, production-ready smart energy meter system with cloud connectivity, real-time monitoring, and automated billing.

## Quick Start (5 minutes)

### 1. **Backend (Python Flask)**

```bash
cd backend-python
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
python run.py
```

Backend runs on `http://localhost:5000`

### 2. **MongoDB (Cloud)**

1. Go to [MongoDB Atlas](https://mongodb.com/cloud/atlas)
2. Create free account → Create cluster → Get connection string
3. Update `MONGODB_URI` in `backend-python/.env`

### 3. **MQTT Broker (Local)**

```bash
docker run -it -p 1883:1883 eclipse-mosquitto
# Or: mosquitto -v
```

### 4. **Frontend (HTML/CSS/JavaScript)**

```bash
cd frontend-vanilla
python -m http.server 8000  # Or use VS Code Live Server
```

Open `http://localhost:8000` in browser

### 5. **ESP32 Firmware**

```bash
cd edge/esp32-firmware
# Edit platformio.ini with your WiFi and MQTT details
pio run -t upload
# Monitor: pio device monitor
```

**That's it!** Your dashboard is live 🎉

## System Architecture

```
ESP32 + PZEM Sensor
    ↓ MQTT (JSON)
Mosquitto MQTT Broker
    ↓ Subscribe
Python Flask Backend
    ↓ CRUD
MongoDB Atlas (Time-Series)
    ↓ Query
HTML/CSS/JavaScript Dashboard
    ↓ Visualize
Charts + Live Telemetry Cards
```

## Features

✅ **Real-time telemetry** — Live power, current, voltage, energy cards  
✅ **24-hour power chart** — Track consumption patterns  
✅ **30-day consumption graph** — Bar chart visualization  
✅ **Automated billing** — Slab-based rates, tax calculation, PDF export  
✅ **Device management** — Add/remove meters, track status  
✅ **Tariff configuration** — Admin panel for rates and charges  
✅ **MQTT integration** — Scalable IoT pub/sub architecture  
✅ **MongoDB time-series** — Efficient storage for metrics  
✅ **No build tools** — Frontend is pure HTML/CSS/JavaScript  

## Project Structure

```
Smartmeter/
├── backend-python/             # Flask app
│   ├── app/
│   │   ├── __init__.py         # App factory
│   │   ├── config/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── services/
│   │   │   ├── mqtt_service.py
│   │   │   └── billing_service.py
│   ├── run.py                  # Entry point
│   ├── requirements.txt
│   └── .env.example
├── frontend-vanilla/            # HTML/CSS/JS
│   ├── index.html              # Single page app
│   ├── assets/
│   │   ├── css/style.css
│   │   └── js/
│   │       ├── config.js
│   │       ├── api.js
│   │       ├── charts.js
│   │       └── app.js
│   └── SETUP.md
├── edge/esp32-firmware/         # Arduino/PlatformIO
│   ├── src/main.cpp
│   ├── platformio.ini
│   └── README.md
├── billing-python/              # Billing jobs
│   ├── src/billing_job.py
│   └── requirements.txt
└── README.md
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/devices` | GET | List all devices |
| `/api/devices/<id>` | GET | Get device details |
| `/api/devices` | POST | Create device |
| `/api/devices/<id>/readings` | GET | Get telemetry (queryable) |
| `/api/billing/<id>?month=YYYY-MM` | GET | Compute bill |
| `/api/invoices/<id>` | GET | List invoices |
| `/api/tariffs` | GET | Get tariff config |
| `/api/tariffs` | POST | Update tariffs |
| `/health` | GET | Health check |

## Database Schema

### meter_readings (Time-Series Collection)
```
{
  device_id: "meter-001",
  timestamp: ISODate,
  voltage: 230.4,
  current: 2.73,
  power_w: 628.99,
  energy_kwh: 12.345,
  power_factor: 0.98,
  rssi: -60
}
```

### invoices
```
{
  device_id: "meter-001",
  month: "2026-01",
  energy_kwh: 250,
  slabs: [...],
  subtotal: 1025,
  fixed_charge: 50,
  tax: 193.50,
  total: 1268.50,
  status: "issued"
}
```

### devices
```
{
  device_id: "meter-001",
  name: "Main Meter",
  location: "Flat-101",
  status: "online",
  last_seen: ISODate,
  firmware_version: "1.0.0"
}
```

### tariffs
```
{
  name: "default",
  slabs: [
    { range: "0-100", rate: 3.50 },
    { range: "101-300", rate: 4.50 },
    { range: "301+", rate: 6.00 }
  ],
  fixed_charge: 50,
  tax_rate: 0.18,
  currency: "INR"
}
```

## Billing Logic

**Example:** 250 kWh consumption

```
Slab 0-100:     100 units × ₹3.50 = ₹350
Slab 101-300:   150 units × ₹4.50 = ₹675
                              ─────────────
Subtotal:                       ₹1,025

Fixed charge:                   ₹50
Subtotal + Fixed:               ₹1,075

Tax (18% GST):                  ₹193.50
═══════════════════════════════════════
Total Bill:                     ₹1,268.50
```

## Configuration Files

All apps read from `.env`. See examples:
- `backend-python/.env.example`
- `frontend-vanilla/assets/js/config.js`
- `edge/esp32-firmware/platformio.ini`

## Development Commands

```bash
# Backend
cd backend-python
python run.py                    # Dev server
pytest                           # Run tests

# Frontend
cd frontend-vanilla
python -m http.server 8000      # Dev server

# Firmware
cd edge/esp32-firmware
pio run -t upload               # Build & flash
pio device monitor              # Serial monitor

# Billing
cd billing-python
python src/billing_job.py       # Manual run
```

## Deployment

### Docker (Backend)

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY backend-python/requirements.txt .
RUN pip install -r requirements.txt
COPY backend-python/app app
COPY backend-python/run.py .
CMD ["python", "run.py"]
```

### Render (Backend)

```bash
git push origin main
# Render auto-deploys on push
```

### Vercel (Frontend)

```bash
npm install -g vercel
cd frontend-vanilla
vercel --prod
```

### Production Checklist

- ✅ Set `FLASK_ENV=prod` in backend
- ✅ Use strong `JWT_SECRET` and `SECRET_KEY`
- ✅ Enable TLS for MQTT broker
- ✅ Set MongoDB IP allowlist
- ✅ Configure CORS for frontend domain only
- ✅ Enable HTTPS for all endpoints
- ✅ Set up monitoring & alerts
- ✅ Regular database backups

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Backend won't start | Check MongoDB URI, MQTT broker running |
| Frontend blank | Check API_URL in config.js, ensure backend running |
| No telemetry data | Verify ESP32 WiFi connected, MQTT topic correct |
| Bills not generating | Check energy readings exist in DB, run billing job |

## Learning Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [MongoDB Time-Series Collections](https://docs.mongodb.com/manual/core/timeseries-collections/)
- [MQTT Basics](https://mqtt.org/)
- [ESP32 Development](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/)
- [Chart.js](https://www.chartjs.org/)

## Contributing

1. Create feature branch: `git checkout -b feature/my-feature`
2. Commit changes: `git commit -m 'Add feature'`
3. Push: `git push origin feature/my-feature`
4. Open PR

## License

MIT

## Support

- Issues: Open GitHub issue with details
- Questions: Check README in each module
- Discussions: Create GitHub discussion

---

**Happy metering!** ⚡📊

For detailed setup instructions, see:
- [Backend Setup](backend-python/SETUP.md)
- [Frontend Setup](frontend-vanilla/SETUP.md)
- [Firmware Setup](edge/esp32-firmware/README.md)
