/* Simple ESP32 MQTT Publisher for PZEM-004T */

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <ModbusMaster.h>
#include <HardwareSerial.h>

// Configuration
#define WIFI_SSID "YourWiFi"
#define WIFI_PASSWORD "YourPassword"
#define MQTT_HOST "192.168.1.10"
#define MQTT_PORT 1883
#define MQTT_USER "smartmeter_user"
#define MQTT_PASS "secure_password_123"
#define DEVICE_ID "meter-001"

// Pins for PZEM Modbus
#define PZEM_RX_PIN 16
#define PZEM_TX_PIN 17
#define PZEM_BAUDRATE 9600
#define PZEM_SLAVE_ID 1

// Globals
WiFiClient espClient;
PubSubClient client(espClient);
HardwareSerial PZEM_SERIAL(2);  // UART2
ModbusMaster node;
unsigned long lastPublish = 0;
const unsigned long PUBLISH_INTERVAL = 10000;  // 10 seconds

// Function prototypes
void setupWiFi();
void reconnectMQTT();
void publishTelemetry();
void readPZEM();

void setup() {
    Serial.begin(115200);
    PZEM_SERIAL.begin(PZEM_BAUDRATE, SERIAL_8N1, PZEM_RX_PIN, PZEM_TX_PIN);
    
    Serial.println("\n\nStarting Smart Energy Meter Firmware");
    
    // Initialize ModbusMaster
    node.begin(PZEM_SLAVE_ID, PZEM_SERIAL);
    
    // Setup WiFi
    setupWiFi();
    
    // Setup MQTT
    client.setServer(MQTT_HOST, MQTT_PORT);
}

void loop() {
    // Reconnect WiFi if needed
    if (WiFi.status() != WL_CONNECTED) {
        setupWiFi();
    }
    
    // Reconnect MQTT if needed
    if (!client.connected()) {
        reconnectMQTT();
    }
    
    client.loop();
    
    // Publish telemetry at interval
    unsigned long currentTime = millis();
    if (currentTime - lastPublish >= PUBLISH_INTERVAL) {
        lastPublish = currentTime;
        readPZEM();
        publishTelemetry();
    }
}

void setupWiFi() {
    Serial.println("Connecting to WiFi...");
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\nWiFi connected!");
        Serial.print("IP: ");
        Serial.println(WiFi.localIP());
        Serial.print("RSSI: ");
        Serial.println(WiFi.RSSI());
    } else {
        Serial.println("\nWiFi failed to connect");
    }
}

void reconnectMQTT() {
    int attempts = 0;
    while (!client.connected() && attempts < 3) {
        Serial.print("Connecting to MQTT broker...");
        
        if (client.connect(DEVICE_ID, MQTT_USER, MQTT_PASS)) {
            Serial.println("MQTT connected");
        } else {
            Serial.print("failed, rc=");
            Serial.println(client.state());
            delay(1000);
        }
        attempts++;
    }
}

void readPZEM() {
    // Read voltage (Register 0x0000, count 1)
    uint8_t result = node.readHoldingRegisters(0x0000, 1);
    float voltage = 0;
    if (result == node.ku8MBSuccess) {
        voltage = node.getResponseBuffer(0) / 10.0;  // Scale
    }
    
    // Read current (Register 0x0001, count 1)
    result = node.readHoldingRegisters(0x0001, 1);
    float current = 0;
    if (result == node.ku8MBSuccess) {
        current = node.getResponseBuffer(0) / 1000.0;
    }
    
    // Read power (Register 0x0003, count 1)
    result = node.readHoldingRegisters(0x0003, 1);
    float power = 0;
    if (result == node.ku8MBSuccess) {
        power = node.getResponseBuffer(0);
    }
    
    // Read energy (Register 0x0005, count 2)
    result = node.readHoldingRegisters(0x0005, 2);
    float energy = 0;
    if (result == node.ku8MBSuccess) {
        uint32_t energyRaw = (node.getResponseBuffer(0) << 16) | node.getResponseBuffer(1);
        energy = energyRaw / 1000.0;
    }
    
    // Read power factor (Register 0x000D, count 1)
    result = node.readHoldingRegisters(0x000D, 1);
    float pf = 0;
    if (result == node.ku8MBSuccess) {
        pf = node.getResponseBuffer(0) / 100.0;
    }
    
    // Create JSON
    StaticJsonDocument<256> doc;
    doc["device_id"] = DEVICE_ID;
    doc["timestamp"] = getISOTimestamp();
    doc["voltage"] = voltage;
    doc["current"] = current;
    doc["power_w"] = power;
    doc["energy_kwh"] = energy;
    doc["power_factor"] = pf;
    doc["rssi"] = WiFi.RSSI();
    
    // Serialize to string
    String jsonString;
    serializeJson(doc, jsonString);
    
    // Store for publishing
    strcpy(lastPayload, jsonString.c_str());
    
    Serial.print("PZEM: V=");
    Serial.print(voltage);
    Serial.print("V I=");
    Serial.print(current);
    Serial.print("A P=");
    Serial.print(power);
    Serial.print("W E=");
    Serial.print(energy);
    Serial.println("kWh");
}

char lastPayload[256];

void publishTelemetry() {
    if (client.connected()) {
        String topic = "smartmeter/" + String(DEVICE_ID) + "/telemetry";
        client.publish(topic.c_str(), lastPayload);
        Serial.println("Published to MQTT");
    }
}

String getISOTimestamp() {
    // For simplicity, return a fixed ISO time
    // In production, use NTP to sync time
    return "2026-01-29T12:00:00Z";
}
