# Smart Energy Meter Dashboard

React-based web dashboard for viewing real-time energy consumption, historical analytics, and managing billing.

## Features

- ✅ Live telemetry cards (Voltage, Current, Power, Energy)
- ✅ Real-time power consumption chart (WebSocket/MQTT)
- ✅ Historical consumption bar chart (last 30 days)
- ✅ Device management page
- ✅ Billing page with invoice list & PDF download
- ✅ Admin tariff slab configuration
- ✅ User authentication (JWT)
- ✅ Responsive design (Tailwind CSS)
- ✅ Dark/Light mode toggle (optional)

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Navbar.jsx
│   │   ├── Sidebar.jsx
│   │   ├── LiveCards.jsx
│   │   ├── PowerChart.jsx
│   │   ├── ConsumptionChart.jsx
│   │   └── BillingTable.jsx
│   ├── pages/
│   │   ├── Dashboard.jsx
│   │   ├── Devices.jsx
│   │   ├── Billing.jsx
│   │   ├── Tariff.jsx
│   │   └── Login.jsx
│   ├── hooks/
│   │   ├── useMqtt.js
│   │   ├── useAuth.js
│   │   └── useApi.js
│   ├── store/
│   │   ├── authStore.js
│   │   └── deviceStore.js
│   ├── services/
│   │   ├── api.js
│   │   └── mqtt.js
│   ├── App.jsx
│   ├── index.css
│   └── index.js
├── public/
│   ├── index.html
│   ├── favicon.ico
│   └── manifest.json
├── package.json
├── .env.example
├── tailwind.config.js
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
# Edit .env with backend URL and MQTT settings
REACT_APP_API_URL=http://localhost:5000
REACT_APP_MQTT_URL=ws://localhost:8083
```

### 3. Start Development Server

```bash
npm start
```

Dashboard opens on `http://localhost:3000`

## Key Components

### LiveCards.jsx

Displays real-time metrics (Voltage, Current, Power, Energy) fetched via MQTT.

```jsx
<LiveCards readings={currentReadings} />
```

### PowerChart.jsx

Line chart showing power consumption over the last 24 hours using Chart.js.

```jsx
<PowerChart data={lastReading} />
```

### ConsumptionChart.jsx

Bar chart of daily consumption for the last 30 days.

```jsx
<ConsumptionChart data={dailyData} />
```

### BillingTable.jsx

Displays monthly invoices with links to PDF download.

```jsx
<BillingTable invoices={invoices} onDownload={handleDownloadPDF} />
```

## Custom Hooks

### useMqtt()

Manages MQTT WebSocket connection and real-time telemetry subscription.

```javascript
const { readings, connected } = useMqtt({
  broker: process.env.REACT_APP_MQTT_URL,
  topic: process.env.REACT_APP_MQTT_TOPIC,
  device_id: 'meter-001'
});
```

### useAuth()

Manages JWT token and user authentication.

```javascript
const { token, user, login, logout, isAuthenticated } = useAuth();
```

### useApi()

Wrapper around axios for backend API calls.

```javascript
const { data, loading, error } = useApi(
  `${process.env.REACT_APP_API_URL}/api/devices`
);
```

## State Management

Using **Zustand** for lightweight state:

### authStore.js

```javascript
export const useAuthStore = create((set) => ({
  token: localStorage.getItem('token'),
  user: null,
  setToken: (token) => set({ token }),
  setUser: (user) => set({ user }),
  logout: () => {
    set({ token: null, user: null });
    localStorage.removeItem('token');
  }
}));
```

### deviceStore.js

```javascript
export const useDeviceStore = create((set) => ({
  selectedDeviceId: 'meter-001',
  devices: [],
  setSelectedDevice: (id) => set({ selectedDeviceId: id }),
  setDevices: (devices) => set({ devices })
}));
```

## Pages

### Dashboard.jsx

Home page with live cards and charts.

```
┌─────────────────────────────────────────┐
│ Live Telemetry Cards                    │
│ ┌────────┬────────┬────────┬────────┐   │
│ │Voltage │Current │ Power  │ Energy │   │
│ │230.4V  │ 2.73A  │628.99W │12.34kWh│   │
│ └────────┴────────┴────────┴────────┘   │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│ Power (Last 24h)                        │
│         [Line Chart]                    │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│ Daily Consumption (Last 30 days)        │
│         [Bar Chart]                     │
└─────────────────────────────────────────┘
```

### Devices.jsx

Manage registered meters (add, view, delete).

### Billing.jsx

View monthly invoices, download PDF, check payment status.

### Tariff.jsx

Admin page to set/update tariff slabs and rates.

### Login.jsx

JWT-based authentication.

## API Calls

```javascript
// Get current device readings
GET /api/devices/:id/readings?from=2026-01-28&to=2026-01-29&agg=hour

// Get billing for a month
GET /api/billing/:device_id?month=2026-01

// Download invoice PDF
GET /api/invoices/:invoice_id/pdf

// Get tariff config
GET /api/tariffs

// Update tariff (admin)
POST /api/tariffs
Body: { slabs, fixed_charge, tax_rate }
```

## MQTT Real-Time Updates

Dashboard subscribes to:

```
Topic: smartmeter/<device_id>/telemetry
Payload: {
  device_id: "meter-001",
  timestamp: "2026-01-29T09:45:00Z",
  voltage: 230.4,
  current: 2.73,
  power_w: 628.99,
  energy_kwh: 12.345,
  power_factor: 0.98,
  rssi: -60
}
```

Update charts in real-time as messages arrive.

## Styling

Using **Tailwind CSS** for responsive, utility-first design.

### Custom Theme

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: '#2563eb',
        accent: '#10b981'
      }
    }
  }
};
```

## Authentication Flow

1. User logs in via `/login` with email & password
2. Backend returns JWT token
3. Store token in localStorage and Zustand store
4. Include token in `Authorization: Bearer <token>` header for API calls
5. On logout, clear token and redirect to login

## Error Handling

- Display API errors in toast notifications
- Show connection status for MQTT broker
- Retry failed requests with exponential backoff
- Log errors to console in development

## Deployment

### Build

```bash
npm run build
```

Outputs optimized bundle to `build/` folder.

### Deploy to Vercel

```bash
npm install -g vercel
vercel
```

### Deploy to Netlify

```bash
npm install -g netlify-cli
netlify deploy --prod --dir=build
```

### Environment Variables (Production)

```
REACT_APP_API_URL=https://api.smartmeter.yourcompany.com
REACT_APP_MQTT_URL=wss://mqtt.smartmeter.yourcompany.com:8883
```

## Performance Optimization

- ✅ Lazy load pages with React.lazy()
- ✅ Memoize components to prevent unnecessary re-renders
- ✅ Debounce MQTT message handlers
- ✅ Use Chart.js data aggregation instead of raw points
- ✅ Cache API responses with React Query (optional)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| MQTT connection fails | Check broker URL, ensure WebSocket is enabled, verify firewall |
| Charts not updating | Confirm MQTT topic matches `smartmeter/<device_id>/telemetry` |
| API 401 errors | Token expired, log in again |
| Tariff page blank | Admin user role required |

## Next Steps

1. **Sprint 1:** Wire up API calls and device list
2. **Sprint 2:** Implement MQTT real-time charts
3. **Sprint 3:** Add billing page and invoice download
4. **Sprint 4:** Implement tariff admin page
5. **Sprint 5:** Add authentication & authorization

---

See main [README.md](../README.md) for full project overview.
