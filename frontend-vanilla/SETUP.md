# Frontend Vanilla JS - Setup & Run

## Installation

```bash
# No build process needed - just open in browser!
# For local development with CORS support, use Python's http.server
```

## Quick Start

### Option 1: Python HTTP Server (Recommended)

```bash
cd frontend-vanilla
python -m http.server 8000
```

Open `http://localhost:8000` in browser

### Option 2: Live Server (VS Code)

1. Install "Live Server" extension in VS Code
2. Right-click `index.html` → "Open with Live Server"

### Option 3: Direct File

Just open `index.html` in your browser (limited functionality due to CORS)

## Configuration

Edit `assets/js/config.js`:

```javascript
const API_URL = 'http://localhost:5000/api';
const MQTT_HOST = 'localhost';
const MQTT_PORT = 8083;
```

## Features

- **Vanilla JavaScript** - No build tools needed
- **Responsive Design** - Works on desktop and mobile
- **Live Telemetry** - Real-time device status
- **Charts** - Chart.js for consumption visualization
- **Billing** - View invoices and download PDFs
- **Admin** - Manage devices and tariff slabs

## File Structure

```
frontend-vanilla/
├── index.html              # Single-page app
├── assets/
│   ├── css/
│   │   └── style.css       # Tailwind-like utility styles
│   └── js/
│       ├── config.js       # Configuration & global state
│       ├── api.js          # API calls to backend
│       ├── charts.js       # Chart.js integration
│       └── app.js          # Main application logic
```

## API Integration

All API calls are in `assets/js/api.js`. Example:

```javascript
// Fetch devices
const devices = await fetchDevices();

// Compute bill
const bill = await computeBill('meter-001', '2026-01');

// Update tariffs
await updateTariffs({
    slabs: [...],
    fixed_charge: 50,
    tax_rate: 0.18
});
```

## Browser Compatibility

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## Performance

- No dependencies (except Chart.js from CDN)
- ~50KB total size
- Fast load time
- Real-time updates

## Troubleshooting

| Issue | Solution |
|-------|----------|
| CORS errors | Ensure backend has CORS enabled, check origin URL |
| Charts not rendering | Verify Chart.js is loaded, check browser console |
| API calls fail | Check API_URL in config.js, ensure backend is running |

---

See [Frontend README](../README.md) for full documentation.
