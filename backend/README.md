# Smart Energy Meter Backend

Node.js + Express backend that ingests MQTT telemetry, stores in MongoDB time-series collections, and exposes REST API for dashboard and billing.

## Features

- ✅ MQTT client subscribes to device telemetry
- ✅ Validates and ingests JSON payloads
- ✅ Time-series data storage (MongoDB time-series collections)
- ✅ REST API for readings, device management, billing
- ✅ JWT authentication
- ✅ Tariff slab configuration
- ✅ Automated billing job (cron)
- ✅ Invoice generation & PDF export
- ✅ Email notifications
- ✅ Rate limiting & input validation
- ✅ Comprehensive logging

## Project Structure

```
backend/
├── src/
│   ├── server.js              # Express app & MQTT setup
│   ├── models/
│   │   ├── deviceSchema.js
│   │   ├── readingSchema.js
│   │   ├── invoiceSchema.js
│   │   ├── tariffSchema.js
│   │   └── userSchema.js
│   ├── routes/
│   │   ├── devices.js
│   │   ├── readings.js
│   │   ├── billing.js
│   │   ├── tariffs.js
│   │   └── auth.js
│   ├── controllers/
│   │   ├── deviceController.js
│   │   ├── readingController.js
│   │   ├── billingController.js
│   │   └── authController.js
│   ├── middleware/
│   │   ├── auth.js
│   │   ├── errorHandler.js
│   │   └── validation.js
│   ├── config/
│   │   ├── database.js
│   │   ├── mqtt.js
│   │   └── logger.js
│   ├── jobs/
│   │   ├── billingJob.js      # Monthly billing cron
│   │   └── invoiceGenerator.js
│   └── utils/
│       ├── tariffCalculator.js
│       └── emailService.js
├── package.json
├── .env.example
└── README.md
```

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials:
# - MQTT_HOST, MQTT_PORT, MQTT_USERNAME, MQTT_PASSWORD
# - MONGODB_URI
# - JWT_SECRET
# - SMTP settings (for email)
```

### 3. Start Backend (Development)

```bash
npm run dev
```

Server runs on `http://localhost:5000`

## API Endpoints

### Authentication

```
POST /api/auth/register
  Body: { email, password, name }
  
POST /api/auth/login
  Body: { email, password }
  Response: { token, user }
```

### Devices

```
GET /api/devices
  Response: [{ device_id, name, location, last_seen, status }]
  
GET /api/devices/:id
  Response: { device_id, name, ...metadata }
  
POST /api/devices
  Body: { device_id, name, location }
  
DELETE /api/devices/:id
```

### Readings (Telemetry)

```
GET /api/devices/:id/readings?from=2026-01-01&to=2026-01-29&agg=hour
  Query params:
    - from: ISO date (default: 24h ago)
    - to: ISO date (default: now)
    - agg: hour|day|week|month (optional aggregation)
  Response: [{ timestamp, power_w, energy_kwh, voltage, current, ... }]
```

### Billing

```
GET /api/billing/:device_id?month=2026-01
  Response: {
    device_id,
    month,
    energy_kwh,
    units_slab_0_100: { units: 50, rate: 3.5, charge: 175 },
    units_slab_101_300: { units: 40, rate: 4.5, charge: 180 },
    subtotal,
    tax,
    total
  }
  
GET /api/invoices/:device_id
  Response: [{ invoice_id, month, total, pdf_url, created_at }]
  
GET /api/invoices/:invoice_id/pdf
  Download PDF invoice
```

### Tariffs (Admin)

```
GET /api/tariffs
  Response: { slabs: [...], fixed_charge, tax_rate }
  
POST /api/tariffs
  Body: { slabs: [{ range_start, range_end, rate }], fixed_charge, tax_rate }
  
PUT /api/tariffs
```

## Data Models

### MeterReading (Time-Series Collection)

```javascript
{
  timeField: "timestamp",
  metaField: "metadata",
  granularity: "minutes",
  documents: {
    timestamp: ISODate("2026-01-29T09:45:00Z"),
    device_id: "meter-001",
    voltage: 230.4,
    current: 2.73,
    power_w: 628.99,
    energy_kwh: 12.345,
    power_factor: 0.98,
    rssi: -60,
    metadata: {
      location: "Flat-101"
    }
  }
}
```

### Invoice

```javascript
{
  _id: ObjectId,
  device_id: "meter-001",
  month: "2026-01",
  energy_kwh: 90,
  slabs: [
    { slab: "0-100", units: 90, rate: 3.5, charge: 315 }
  ],
  subtotal: 315,
  fixed_charge: 50,
  tax: 58.5,  // 18% GST
  total: 423.5,
  status: "issued",  // issued, paid, overdue
  pdf_url: "s3://invoices/meter-001-2026-01.pdf",
  created_at: ISODate,
  due_date: ISODate,
  paid_date: ISODate
}
```

### Device

```javascript
{
  _id: ObjectId,
  device_id: "meter-001",
  name: "Main Meter",
  location: "Flat-101",
  user_id: ObjectId,
  wifi_ssid: "MyWiFi",
  status: "online",  // online, offline, error
  last_seen: ISODate,
  firmware_version: "1.0.0",
  created_at: ISODate
}
```

## MQTT Integration

### Topic Structure

```
smartmeter/<device_id>/telemetry
  → JSON payload with voltage, current, power, energy, pf, rssi
```

### Backend MQTT Client

The backend subscribes to `smartmeter/+/telemetry` and on each message:

1. Validates payload schema
2. Extracts device_id and timestamp
3. Writes to MongoDB time-series collection
4. Broadcasts to connected WebSocket clients (real-time dashboard)

## Billing Logic

### Tariff Slab Example

```javascript
const tariffConfig = {
  slabs: [
    { range: "0-100", rate: 3.50 },      // ₹3.50/unit
    { range: "101-300", rate: 4.50 },    // ₹4.50/unit
    { range: "301+", rate: 6.00 }        // ₹6.00/unit
  ],
  fixed_charge: 50,                      // ₹50/month
  tax_rate: 0.18                         // 18% GST
};
```

### Bill Calculation

```
month_consumption = 250 kWh

Slab 0-100:     100 × 3.50 = ₹350
Slab 101-300:   150 × 4.50 = ₹675
Subtotal:                    ₹1025

Fixed charge:                ₹50
Tax (18%):                   ₹193.5
---
Total:                       ₹1268.5
```

## Billing Job (Cron)

The job runs at **00:05 on the 1st of each month**:

1. Fetches all active devices
2. Aggregates previous month's energy from MongoDB
3. Applies tariff slabs
4. Generates invoice document
5. Creates PDF file
6. Sends email to user

Trigger manually:
```bash
npm run billing:run
```

## Testing

```bash
npm test                    # Run all tests
npm run test:watch         # Watch mode
```

## Deployment

### Production Checklist

- ✅ Set `NODE_ENV=production`
- ✅ Use managed MongoDB Atlas with IP allowlist
- ✅ Configure TLS for MQTT broker
- ✅ Set strong JWT_SECRET
- ✅ Enable CORS for frontend domain only
- ✅ Configure SMTP for email delivery
- ✅ Set up monitoring (Prometheus, Sentry)
- ✅ Enable audit logging for billing

### Docker Deployment

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY src/ ./src/
EXPOSE 5000
CMD ["npm", "start"]
```

## Monitoring

### Health Check Endpoint

```
GET /health
Response: { status: "ok", uptime, mqtt_connected, db_connected }
```

### Metrics

- Request count & latency (Prometheus)
- MQTT connection status
- MongoDB connection pool
- Error rate by endpoint

## Troubleshooting

| Issue | Solution |
|-------|----------|
| MQTT connection fails | Check MQTT broker URL, credentials, firewall |
| MongoDB timeout | Verify connection string, IP allowlist |
| JWT verification fails | Ensure JWT_SECRET matches frontend |
| Emails not sending | Verify SMTP credentials, enable 2FA app passwords |

## Next Steps

1. **Sprint 1:** Implement models, routes, and MQTT ingestion
2. **Sprint 2:** Add time-series aggregation queries
3. **Sprint 3:** Build billing logic and invoice PDF
4. **Sprint 4:** Add authentication and rate limiting
5. **Sprint 5:** Deploy to production

---

See main [README.md](../README.md) for full project overview.
