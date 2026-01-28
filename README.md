# Smart Energy Meter with Billing System

A full-stack IoT solution for real-time energy consumption monitoring, cloud-based analytics, and automated billing.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  EDGE LAYER (Meter)                                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ ESP32 + PZEM-004T (Modbus)                               │   │
│  │ - Read V/I/P/kWh every 10s                               │   │
│  │ - Publish JSON to MQTT                                   │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────┬──────────────────────────────────────────────┘
                   │ MQTT
                   ↓
┌─────────────────────────────────────────────────────────────────┐
│  INGESTION LAYER                                                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ MQTT Broker (Mosquitto / EMQX)                           │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────┬──────────────────────────────────────────────┘
                   │ MQTT Subscribe
                   ↓
┌─────────────────────────────────────────────────────────────────┐
│  BACKEND LAYER                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Node.js + Express + MQTT Client                          │   │
│  │ - Validate & ingest telemetry                            │   │
│  │ - Compute billing                                        │   │
│  │ - REST API + WebSocket                                   │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────┬──────────────────────────────────────────────┘
                   │ Write
                   ↓
┌─────────────────────────────────────────────────────────────────┐
│  DATABASE LAYER                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ MongoDB Atlas (Time-Series Collections)                  │   │
│  │ - meter_readings, invoices, users, tariffs               │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────┬──────────────────────────────────────────────┘
                   │ Query
                   ↓
┌─────────────────────────────────────────────────────────────────┐
│  FRONTEND LAYER                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ React + Chart.js                                         │   │
│  │ - Live telemetry cards                                   │   │
│  │ - Historical consumption charts                          │   │
│  │ - Billing dashboard & PDF export                         │   │
│  │ - Admin tariff configuration                             │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
Smartmeter/
├── edge/
│   └── esp32-firmware/          # PlatformIO project for ESP32
│       ├── src/
│       │   └── main.cpp         # Firmware: PZEM + MQTT
│       ├── platformio.ini
│       └── README.md
├── backend/                     # Node.js + Express
│   ├── src/
│   │   ├── server.js            # Main entry point
│   │   ├── models/              # Mongoose schemas
│   │   ├── routes/              # API endpoints
│   │   ├── controllers/         # Business logic
│   │   └── config/              # Configuration
│   ├── package.json
│   ├── .env.example
│   └── README.md
├── frontend/                    # React dashboard
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.js
│   ├── public/
│   ├── package.json
│   └── README.md
├── billing/                     # Billing cron jobs
│   ├── src/
│   │   ├── billingJob.js
│   │   └── tariffConfig.js
│   ├── package.json
│   └── README.md
├── .github/
│   └── workflows/               # CI/CD pipelines
│       ├── backend-deploy.yml
│       └── frontend-deploy.yml
├── .gitignore
├── .env.example                 # Example environment variables
└── README.md
```

## Quick Start

### Prerequisites

- Node.js 16+ and npm
- MongoDB Atlas account (free tier)
- MQTT Broker (Mosquitto or managed EMQX)
- ESP32 + PZEM-004T sensor
- PlatformIO CLI or Arduino IDE

### 1. Clone and Setup

```bash
git clone <repo-url>
cd Smartmeter
cp .env.example .env
# Edit .env with your credentials
```

### 2. Backend Setup

```bash
cd backend
npm install
npm run dev           # Start dev server on port 5000
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm start            # Start React dev server on port 3000
```

### 4. Firmware Setup

```bash
cd edge/esp32-firmware
# Edit platformio.ini with your WiFi & MQTT broker details
pio run -t upload    # Build and flash to ESP32
```

### 5. Local MQTT Broker (Development)

```bash
docker run -it -p 1883:1883 eclipse-mosquitto
```

Or install Mosquitto locally and run `mosquitto -v`.

## Key Features

✅ **Real-time Telemetry** — ESP32 reads PZEM sensor, publishes to MQTT  
✅ **Time-Series Data** — Efficient storage in MongoDB with time-series collections  
✅ **Live Dashboard** — React UI with WebSocket for real-time updates  
✅ **Tariff-Based Billing** — Configurable slab rates, auto-bill generation  
✅ **PDF Export** — Download invoices  
✅ **Security** — TLS for MQTT, JWT authentication, secure OTA updates  
✅ **Scalability** — MQTT pub/sub scales to thousands of devices  
✅ **CI/CD** — GitHub Actions for automated testing and deployment

## API Endpoints (Backend)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/devices` | List all devices and last seen |
| GET | `/api/devices/:id/readings` | Time-series readings (query: from, to, agg) |
| GET | `/api/billing/:deviceId?month=YYYY-MM` | Compute bill for period |
| POST | `/api/tariffs` | Set tariff slabs (admin) |
| GET | `/api/invoices/:deviceId` | List invoices |

## Data Model

### Meter Telemetry (MQTT JSON)

```json
{
  "device_id": "meter-001",
  "timestamp": "2026-01-29T09:45:00Z",
  "voltage": 230.4,
  "current": 2.73,
  "power_w": 628.99,
  "energy_kwh": 12.345,
  "power_factor": 0.98,
  "rssi": -60
}
```

### MongoDB Collections

- **meter_readings** (time-series) — Raw telemetry from devices
- **invoices** — Generated monthly bills
- **users** — Consumer/admin accounts
- **tariffs** — Billing rate configuration
- **devices** — Registered meters and metadata

## Billing Logic

Example tariff (India slab):

```
0–100 kWh:   ₹3.50/unit
101–300 kWh: ₹4.50/unit
301+ kWh:    ₹6.00/unit
+ Fixed charge: ₹50/month
+ GST: 18%
```

## Deployment

### Production Stack

- **Backend:** Render / AWS EC2 / DigitalOcean  
- **Frontend:** Vercel / Netlify  
- **Database:** MongoDB Atlas  
- **MQTT Broker:** EMQX Cloud / AWS IoT Core  
- **Monitoring:** Prometheus + Grafana

### GitHub Actions CI/CD

Push to `main` triggers:
1. **Backend:** Tests, build Docker image, deploy to Render
2. **Frontend:** Build, deploy to Vercel
3. **Status:** Slack/email notification

See `.github/workflows/` for YAML configs.

## Security Checklist

- ✅ Device authentication (pre-shared keys or certificates)
- ✅ TLS for MQTT broker & HTTPS endpoints
- ✅ Input validation & rate limiting
- ✅ Secure firmware OTA (signed images)
- ✅ Encrypt PII at rest (MongoDB encryption)
- ✅ Rotate API keys and broker credentials regularly
- ✅ Implement audit logging for billing operations

## Development Roadmap

| Sprint | Focus |
|--------|-------|
| 0 | ✅ Scaffold & setup (this document) |
| 1 | ESP32 firmware + local MQTT integration |
| 2 | Backend API + MongoDB time-series queries |
| 3 | React dashboard + live charts |
| 4 | Billing logic & invoice generation |
| 5 | Security hardening & OTA updates |
| 6 | Production deployment & scaling |

## References

- [ESP32 + PZEM Community Examples](https://github.com/search?q=esp32+pzem+mqtt)
- [MQTT Best Practices for IoT](https://mqtt.org/)
- [MongoDB Time-Series Collections](https://docs.mongodb.com/manual/core/timeseries-collections/)
- [Node.js MQTT Client (mqtt.js)](https://github.com/mqttjs/MQTT.js)
- [React + Chart.js](https://react-chartjs-2.js.org/)

## License

MIT

## Contact & Support

For issues, feature requests, or contributions, open a GitHub issue or contact the team.

---

**Next:** Choose your first sprint task and follow the prompts in the respective README.
