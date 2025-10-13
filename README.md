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

### 5. Test the Connection
```bash
python3 test_nut_connection.py
```

## 🍓 Raspberry Pi Installation

For automated installation on Raspberry Pi:

```bash
chmod +x install.sh
./install.sh
```

This will:
- Install Python dependencies
- Create a systemd service
- Enable auto-start on boot

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
  "device_serial": "R631ZABAWH3E4701",
  "mqtt": {
    "host": "mqtt.ecoflow.com",
    "port": 8883,
    "username": "your_email@example.com",
    "password": "your_ecoflow_password"
  },
  "nut": {
    "host": "127.0.0.1",
    "port": 3493,
    "ups_name": "basement_media_river_3_plus"
  }
}
```

### Multiple Devices
```json
{
  "devices": [
    {
      "serial": "R631ZABAWH3E4701",
      "ups_name": "basement_media_river_3_plus"
    },
    {
      "serial": "R631ZABAWH3E5371", 
      "ups_name": "server_room_river_3_plus"
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
- `test_nut_connection.py` - Test NUT connectivity
- `requirements.txt` - Python dependencies
- `install.sh` - Raspberry Pi installation script

## 🛠️ Systemd Service

The server can run as a systemd service:

```bash
# Start service
sudo systemctl start ecoflow-nut

# Stop service  
sudo systemctl stop ecoflow-nut

# Check status
sudo systemctl status ecoflow-nut

# View logs
journalctl -u ecoflow-nut -f
```

## ✅ Status

**WORKING** - Successfully receiving live data from River 3 Plus devices and exposing via NUT protocol with real protobuf parsing.
