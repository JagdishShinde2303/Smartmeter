/* Configuration */
const API_URL = 'http://localhost:5000/api';
const MQTT_HOST = 'localhost';
const MQTT_PORT = 8083;

// Chart instances
let powerChart = null;
let consumptionChart = null;

// Current state
let currentDevice = null;
let currentReadings = {};
let allDevices = [];
