# Smart Energy Meter Firmware (ESP32 + PZEM)

Arduino/PlatformIO firmware for ESP32 that reads energy metrics from PZEM-004T sensor via Modbus and publishes telemetry to MQTT broker.

## Hardware Requirements

- **ESP32 Development Board** (e.g., ESP32 DevKit v1)
- **PZEM-004T v3** (Digital Power Meter with Modbus interface)
- **USB Cable** (for flashing)
- **5V Power Supply** for ESP32
- **Jumper Wires** (Modbus connection: RX/TX)

## Wiring Diagram

```
PZEM-004T          ESP32 (UART2)
┌──────────┐        ┌──────────┐
│  RX      │─────→  │ TX (17)  │
│  TX      │←─────  │ RX (16)  │
│  GND     │─────→  │ GND      │
│  +5V     │        │ (ext PS) │
└──────────┘        └──────────┘

PZEM measures voltage and current from utility line
ESP32 reads via Modbus RTU (9600 baud)
```

## Installation

### 1. Install PlatformIO CLI

```bash
# On Windows with pip
pip install platformio

# Or use VS Code extension: PlatformIO IDE
```

### 2. Clone and Setup

```bash
git clone <repo-url>
cd Smartmeter/edge/esp32-firmware
```

### 3. Configure Firmware

Edit `src/config.h` (you'll create this in the next step):

```cpp
// WiFi
#define WIFI_SSID "MyWiFi"
#define WIFI_PASS "password123"

// MQTT Broker
#define MQTT_HOST "192.168.1.10"        // MQTT broker IP
#define MQTT_PORT 1883
#define MQTT_USER "smartmeter_user"
#define MQTT_PASS "broker_password"
#define MQTT_CLIENT_ID "meter-001"

// PZEM Modbus
#define PZEM_RX_PIN 16
#define PZEM_TX_PIN 17
#define PZEM_BAUDRATE 9600
#define PZEM_SLAVE_ID 1                // Default PZEM address

// Telemetry
#define PUBLISH_INTERVAL_SECONDS 10    // Read & publish every 10 sec
#define TOPIC_PUBLISH "smartmeter/meter-001/telemetry"
```

### 4. Build and Upload

```bash
# Build for development
pio run -e esp32dev

# Upload to ESP32
pio run -e esp32dev -t upload

# Monitor serial output
pio device monitor -b 115200
```

## Firmware Features

### 1. PZEM Modbus Reading

- Reads voltage (V), current (A), power (W), energy (kWh), power factor every 10s
- Uses UART2 (pins 16/17) for Modbus RTU communication at 9600 baud
- Implements slave ID polling (default 0x01)

### 2. WiFi Connectivity

- Auto-connects to configured SSID on startup
- Reconnection logic with exponential backoff
- Reports RSSI (signal strength) with telemetry

### 3. MQTT Publishing

- Publishes JSON telemetry to `smartmeter/<device_id>/telemetry`
- Implements last-will message (LWT) for offline detection
- Retries on connection failure
- QoS level 1 (at least once delivery)

### 4. Telemetry Payload

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

### 5. OTA Firmware Updates

- Listens for OTA update commands on MQTT topic `smartmeter/meter-001/ota/request`
- Downloads and verifies firmware image
- Automatic rollback on failure (optional)

### 6. Error Handling

- Graceful degradation (publishes last-known values if sensor fails)
- Serial logging of errors and connection status
- Watchdog timer to reset on hang

## Code Structure

```
src/
├── main.cpp                  # Entry point, loop, and main logic
├── config.h                  # Configuration constants
├── pzem.h / pzem.cpp         # PZEM Modbus reading functions
├── mqtt.h / mqtt.cpp         # MQTT connection & publishing
├── wifi.h / wifi.cpp         # WiFi connection & reconnect logic
├── ota.h / ota.cpp           # OTA update handling
├── timestamp.h               # ISO8601 timestamp generation
└── README.md                 # This file
```

## Key Functions

### `void setupWiFi()`

Connect to WiFi with retry logic.

### `void setupMQTT()`

Initialize MQTT client and set up callbacks.

### `void readPZEM()`

Poll PZEM-004T via Modbus RTU and extract readings.

### `void publishTelemetry()`

Format JSON payload and publish to MQTT broker.

### `void handleOTA()`

Listen for OTA requests and update firmware.

### `void loop()`

Main loop: read sensor, publish every 10s, handle MQTT/OTA.

## Testing

### 1. Local MQTT Broker

```bash
# Run Mosquitto in Docker
docker run -it -p 1883:1883 eclipse-mosquitto

# Or install locally
# Debian/Ubuntu: sudo apt-get install mosquitto
# macOS: brew install mosquitto
# Windows: download from https://mosquitto.org/download/
```

### 2. Subscribe to Telemetry

```bash
mosquitto_sub -h localhost -t "smartmeter/#" -u smartmeter_user -P broker_password
```

Monitor incoming messages from ESP32.

### 3. Monitor Serial Output

```bash
pio device monitor -b 115200
```

Expected output:

```
[INFO] Starting Smart Energy Meter Firmware v1.0.0
[INFO] Connecting to WiFi: MyWiFi...
[INFO] WiFi connected. IP: 192.168.1.100
[INFO] Connecting to MQTT broker: 192.168.1.10:1883...
[INFO] MQTT connected.
[INFO] Reading PZEM-004T (Modbus ID 1)...
[INFO] V: 230.4V, I: 2.73A, P: 628.99W, E: 12.345kWh, PF: 0.98
[INFO] Publishing to topic: smartmeter/meter-001/telemetry
[INFO] Message published successfully.
...
```

## Troubleshooting

| Issue | Diagnosis | Solution |
|-------|-----------|----------|
| PZEM not responding | Serial monitor shows "Modbus timeout" | Check RX/TX wiring, verify UART pins, test with different baud rate |
| WiFi not connecting | Serial shows "WiFi connect failed" | Verify SSID and password, check WiFi range, inspect antenna connection |
| MQTT connection fails | "MQTT connect failed" or "Connection refused" | Verify broker IP, check firewall, test broker with mosquitto_sub |
| No telemetry published | Broker connected but no messages | Check MQTT topic, verify sensor is sending data, inspect logs |
| ESP32 resets repeatedly | Watchdog timeout or memory exhaustion | Reduce publish frequency, check for memory leaks, enable debug logs |

## Production Checklist

- ✅ Change MQTT credentials to strong, random password
- ✅ Enable TLS for MQTT (port 8883)
- ✅ Load device certificate for mTLS authentication
- ✅ Configure OTA signing to prevent unauthorized updates
- ✅ Test OTA update with signed firmware image
- ✅ Reduce serial logging (set `CORE_DEBUG_LEVEL=0`)
- ✅ Optimize code for minimal power consumption (optional sleep modes)
- ✅ Test failover behavior (WiFi outage, broker down)
- ✅ Document device ID and firmware version in deployment log

## OTA Firmware Update Process

1. **Prepare signed firmware:**
   ```bash
   pio run -e esp32-production
   # Output: .pio/build/esp32-production/firmware.bin
   ```

2. **Send OTA command to device:**
   ```bash
   mosquitto_pub -h <broker> -t smartmeter/meter-001/ota/request \
     -m '{"url": "https://s3.aws.com/firmware/v2.0.0.bin", "checksum": "abc123..."}'
   ```

3. **Device downloads, verifies, and installs:**
   ```
   [INFO] OTA request received
   [INFO] Downloading from: https://s3.aws.com/firmware/v2.0.0.bin
   [INFO] Verifying checksum... OK
   [INFO] Flashing firmware...
   [INFO] Firmware updated successfully. Rebooting...
   ```

## Power Consumption (Typical)

- **Active (WiFi + MQTT + Modbus):** ~80–120 mA
- **Idle (between publishes):** ~40–60 mA
- **Deep sleep (optional):** ~10 µA

For battery-powered deployments, implement adaptive sleep intervals or power-gating.

## Libraries Used

- **PubSubClient** — MQTT client
- **ModbusMaster** — Modbus RTU protocol
- **ArduinoJson** — JSON serialization
- **ESP32 WiFi** — Built-in WiFi stack

## Next Steps

1. **Sprint 1:** Flash firmware to ESP32, verify PZEM readings via serial
2. **Sprint 2:** Connect to local MQTT broker, publish telemetry
3. **Sprint 3:** Connect to production broker with TLS
4. **Sprint 4:** Implement and test OTA firmware updates
5. **Sprint 5:** Deploy to field meters with monitoring

## References

- [PZEM-004T Modbus Protocol](https://github.com/mandulaj/PZEM-004T-v3)
- [PubSubClient Documentation](https://pubsubclient.knolleary.net/)
- [ESP32 Arduino Core](https://github.com/espressif/arduino-esp32)
- [PlatformIO Documentation](https://docs.platformio.org/)

---

See main [README.md](../../README.md) for full project overview.
