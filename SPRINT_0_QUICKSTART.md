# Sprint 0: Quick-Start Guide

Welcome! This guide walks you through the **complete project skeleton** setup and prepares you for Sprint 1 (firmware + backend integration).

## What You Now Have

✅ **Project Structure:** `/edge`, `/backend`, `/frontend`, `/billing` directories  
✅ **Documentation:** READMEs for each module  
✅ **Configuration:** `.env.example` and module-specific templates  
✅ **CI/CD:** GitHub Actions workflows for backend and frontend  
✅ **Dependencies:** `package.json` files for Node.js modules  
✅ **Firmware Setup:** PlatformIO configuration for ESP32

## Next: Choose Your First Sprint Task

### Option 1: **Backend Setup** (Recommended Start)
This is the backbone. Get MQTT ingestion and MongoDB integration working first.

**Time:** 2–3 hours

```bash
cd backend
cp .env.example .env
# Edit .env:
#   MQTT_HOST=localhost
#   MQTT_PORT=1883
#   MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/smartmeter

npm install
npm run dev
# Server runs on http://localhost:5000
```

**What you'll do:**
1. Set up MongoDB Atlas (free tier, takes 10 min)
2. Create Mongoose schemas (device, reading, invoice, user)
3. Implement MQTT client to subscribe to `smartmeter/+/telemetry`
4. Write first REST endpoint: `GET /api/devices`

**Use this prompt** with ChatGPT or your coding assistant:

> **Prompt (Paste into ChatGPT):**
>
> I'm building a Node.js backend for a smart energy meter system. Create a complete Express server scaffold that:
> - Connects to MongoDB Atlas (use environment variables)
> - Connects to an MQTT broker and subscribes to `smartmeter/+/telemetry`
> - Validates and logs incoming telemetry JSON (device_id, timestamp, voltage, current, power_w, energy_kwh, pf, rssi)
> - Writes valid readings to MongoDB time-series collection `meter_readings`
> - Exposes REST endpoint GET `/api/devices` that returns list of devices and their last-seen timestamp
> - Uses middleware for error handling, logging (Winston), and CORS
> - Include example `.env` variables and a basic test using Postman collection format
>
> Stack: Express.js, Mongoose, mqtt.js, Winston logger. Return full server.js, models, and routes files.

---

### Option 2: **ESP32 Firmware Setup**
Get your hardware reading the sensor and publishing to local MQTT.

**Time:** 2–3 hours

**What you'll do:**
1. Install PlatformIO CLI or use VS Code extension
2. Wire PZEM-004T to ESP32 (Modbus RX/TX)
3. Configure `platformio.ini` with WiFi & MQTT credentials
4. Flash firmware and verify PZEM readings on serial monitor

**Use this prompt:**

> **Prompt (Paste into ChatGPT):**
>
> Create a complete Arduino/PlatformIO sketch for ESP32 + PZEM-004T that:
> - Reads voltage, current, power, energy, power factor from PZEM-004T via Modbus RTU (9600 baud, pins 16/17)
> - Connects to WiFi (SSID/password from defines)
> - Connects to MQTT broker (host, port, username, password configurable)
> - Every 10 seconds: read PZEM, format JSON payload, publish to `smartmeter/<device_id>/telemetry`
> - JSON payload: { device_id, timestamp (ISO8601), voltage, current, power_w, energy_kwh, power_factor, rssi }
> - Include error handling, serial logging, MQTT reconnect with exponential backoff, and last-will message
> - Libraries: PubSubClient, ModbusMaster, ArduinoJson
>
> Return complete main.cpp with detailed comments and setup instructions for PlatformIO.

---

### Option 3: **React Dashboard Setup**
Build the UI that consumes backend APIs and visualizes data.

**Time:** 1.5–2 hours

**What you'll do:**
1. Set up React with Vite or create-react-app
2. Create Tailwind CSS setup
3. Build main dashboard component with live cards and a sample chart
4. Wire up API calls to backend

**Use this prompt:**

> **Prompt (Paste into ChatGPT):**
>
> Create a React dashboard component (Vite or create-react-app) for a smart energy meter system that:
> - Fetches device list from `GET /api/devices` and displays selector
> - Displays live telemetry as cards: Voltage (V), Current (A), Power (W), Energy (kWh)
> - Shows a line chart of power consumption over last 24 hours using Chart.js
> - Uses Tailwind CSS for styling
> - Handles loading/error states
> - Includes JWT auth token in Authorization header for all requests
>
> Stack: React 18, Axios, Chart.js, Tailwind. Return App.jsx, components (Cards.jsx, Chart.jsx), and .env.example.

---

### Option 4: **Billing Module Setup**
Implement automated invoice generation and tariff logic.

**Time:** 2–3 hours

**Use this prompt:**

> **Prompt (Paste into ChatGPT):**
>
> Create a Node.js billing module (standalone or as a service) that:
> - Connects to MongoDB and fetches monthly energy consumption from `meter_readings` collection
> - Applies configurable tariff slabs (example: 0-100 kWh @ ₹3.50, 101-300 @ ₹4.50, 301+ @ ₹6.00)
> - Calculates bill with fixed charge (₹50) and tax (18% GST)
> - Generates a PDF invoice using PDFKit
> - Sends invoice PDF via email using Nodemailer
> - Saves invoice to MongoDB `invoices` collection
> - Can be triggered manually or by a cron job (node-cron) at 00:05 on 1st of month
>
> Return billingService.js, invoiceGenerator.js, emailService.js, and tariffConfig.js with examples.

---

## Step-by-Step for Backend Start

If you choose **Option 1**, follow these steps:

### 1. MongoDB Atlas Setup (10 min)

1. Go to [mongodb.com/cloud/atlas](https://mongodb.com/cloud/atlas)
2. Sign up free account
3. Create a cluster (free tier M0)
4. Create database user and get connection string: `mongodb+srv://user:pass@cluster.mongodb.net/smartmeter?retryWrites=true&w=majority`
5. Add your IP to network access allowlist

### 2. MQTT Broker (local for testing)

```bash
# Option A: Docker (easiest)
docker run -it -p 1883:1883 eclipse-mosquitto

# Option B: Install locally
# Debian/Ubuntu: sudo apt-get install mosquitto
# macOS: brew install mosquitto
# Windows: download from mosquitto.org

# Then run:
mosquitto -v
```

### 3. Backend Code

```bash
cd backend
npm install

# Create .env from template
cp .env.example .env

# Edit .env with your MongoDB URI and MQTT broker details
nano .env   # or use VS Code

# Start dev server
npm run dev
```

### 4. Test MQTT Connection

In another terminal:

```bash
# Subscribe to telemetry topic
mosquitto_sub -h localhost -t "smartmeter/#"

# Or publish a test message
mosquitto_pub -h localhost -t "smartmeter/meter-001/telemetry" \
  -m '{"device_id":"meter-001","timestamp":"2026-01-29T10:00:00Z","voltage":230.4,"current":2.73,"power_w":628.99,"energy_kwh":12.345,"pf":0.98,"rssi":-60}'
```

### 5. Test API

```bash
# Get devices (empty at first)
curl http://localhost:5000/api/devices

# Health check
curl http://localhost:5000/health
```

---

## File Reference

| Path | Purpose |
|------|---------|
| [README.md](README.md) | Main project overview & architecture |
| [.env.example](.env.example) | Global environment variables template |
| [backend/README.md](backend/README.md) | Backend module guide |
| [backend/package.json](backend/package.json) | Node.js backend dependencies |
| [frontend/README.md](frontend/README.md) | Frontend module guide |
| [frontend/package.json](frontend/package.json) | React dependencies |
| [edge/esp32-firmware/README.md](edge/esp32-firmware/README.md) | Firmware setup guide |
| [edge/esp32-firmware/platformio.ini](edge/esp32-firmware/platformio.ini) | PlatformIO configuration |
| [billing/README.md](billing/README.md) | Billing service guide |
| [.github/workflows/](https://github.com/your-org/smartmeter/tree/main/.github/workflows) | CI/CD pipelines |

---

## Architecture Reminder

```
ESP32 + PZEM
    ↓ (MQTT)
Mosquitto/EMQX
    ↓ (MQTT Subscribe)
Node.js Backend
    ↓ (Write)
MongoDB Atlas
    ↓ (Query)
React Dashboard
```

---

## Common Issues & Fixes

| Problem | Solution |
|---------|----------|
| "Cannot connect to MongoDB" | Check connection string in .env, verify IP allowlist in Atlas |
| "MQTT broker unreachable" | Ensure Mosquitto is running, check firewall, verify host/port |
| "Port 5000 already in use" | Change `PORT=5001` in .env or kill process on 5000 |
| "npm install fails" | Use Node 16+, delete `node_modules` and `package-lock.json`, try again |
| "PZEM not responding" | Check RX/TX wiring, verify UART pins in code, test with serial monitor |

---

## What's Next After Sprint 0?

Once the skeleton is solid and you've chosen your first module, move to:

- **Sprint 1 (Firmware + Backend):** Full MQTT integration, save readings to MongoDB, query API endpoints
- **Sprint 2 (Dashboard):** Real-time charts, WebSocket updates, historical data queries
- **Sprint 3 (Billing):** Implement slab logic, generate invoices, email delivery
- **Sprint 4 (Security):** TLS for MQTT, JWT auth, OTA firmware updates
- **Sprint 5 (Production):** Deploy to Render (backend), Vercel (frontend), EMQX Cloud (MQTT)

---

## Getting Help

- **Backend issues:** See [backend/README.md](backend/README.md) Troubleshooting section
- **Firmware issues:** See [edge/esp32-firmware/README.md](edge/esp32-firmware/README.md) Troubleshooting
- **Dashboard issues:** See [frontend/README.md](frontend/README.md) Troubleshooting
- **Billing issues:** See [billing/README.md](billing/README.md) Troubleshooting

---

## Summary

You now have:

✅ Complete project scaffold with folders, configs, and documentation  
✅ Ready-to-use environment variables templates  
✅ CI/CD pipelines for automated testing and deployment  
✅ Detailed READMEs for each module  
✅ Copy-paste prompts to generate code for each sprint  

**Next step:** Pick **Option 1, 2, 3, or 4** above, run the prompt in ChatGPT (or paste into your IDE Copilot), and start building Sprint 1!

---

**Questions?** Refer to the module READMEs or the main [README.md](README.md).

Happy building! 🚀
