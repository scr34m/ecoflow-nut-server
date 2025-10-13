# EcoFlow NUT Server

A Python-based NUT (Network UPS Tools) server that bridges EcoFlow River 3 Plus devices to Home Assistant via the standard NUT protocol. This allows you to monitor your EcoFlow devices as UPS devices in Home Assistant.

## 🎯 What This Does

- Connects to EcoFlow MQTT broker using your account credentials
- Receives live data from your River 3 Plus devices
- Parses binary protobuf messages to extract real device data
- Exposes battery data via NUT protocol on `127.0.0.1:3493`
- Compatible with Home Assistant NUT integration
- Supports multiple devices simultaneously

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/andreanjos/ecoflow-nut-server.git
cd ecoflow-nut-server
```

### 2. Configure Your Devices
```bash
# For single device
cp config.example.json config.json
# Edit config.json with your device serial and credentials

# For multiple devices  
cp config_multi.example.json config_multi.json
# Edit config_multi.json with your devices
```

### 3. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 4. Start the Server
```bash
python3 simple_nut_server.py
```



## 📊 Supported Data

- **Battery Charge** (percentage)
- **Battery Voltage** (volts) 
- **Battery Current** (amps)
- **Temperature** (celsius)
- **Charging Status** (CHRG/ONBATT)

## 🏠 Home Assistant Integration

1. Install the **NUT** integration in Home Assistant
2. Configure it to connect to your Pi's IP: `YOUR_PI_IP:3493`
3. Add your River 3 Plus devices as UPS devices
4. Monitor battery status in HA dashboard

## 🔧 Configuration

### Single Device
```json
{
  "device_serial": "YOUR_DEVICE_SERIAL",
  "mqtt": {
    "host": "mqtt.ecoflow.com",
    "port": 8883,
    "username": "your_email@example.com",
    "password": "your_ecoflow_password"
  },
  "nut": {
    "host": "127.0.0.1",
    "port": 3493,
    "ups_name": "your_device_name"
  }
}
```

### Multiple Devices
```json
{
  "devices": [
    {
      "serial": "YOUR_DEVICE_SERIAL_1",
      "ups_name": "device_1_name"
    },
    {
      "serial": "YOUR_DEVICE_SERIAL_2", 
      "ups_name": "device_2_name"
    }
  ],
  "mqtt": {
    "host": "mqtt.ecoflow.com",
    "port": 8883,
    "username": "your_email@example.com",
    "password": "your_ecoflow_password"
  }
}
```

## 📁 Files

- `simple_nut_server.py` - Main NUT server
- `real_ecoflow_parser.py` - Protobuf message parser
- `config.example.json` - Single device configuration template
- `config_multi.example.json` - Multiple devices configuration template
- `requirements.txt` - Python dependencies


## ✅ Status

**WORKING** - Successfully receiving live data from River 3 Plus devices and exposing via NUT protocol with real protobuf parsing.
