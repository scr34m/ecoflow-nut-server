# EcoFlow NUT Server

A Python-based NUT (Network UPS Tools) server that bridges EcoFlow River 3 Plus devices to Home Assistant via the standard NUT protocol. This allows you to monitor your EcoFlow devices as UPS devices in Home Assistant.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![EcoFlow River 3 Plus](https://img.shields.io/badge/EcoFlow-River%203%20Plus-green.svg)](https://ecoflow.com)

## 🔋 What This Solves

EcoFlow devices don't have native Home Assistant integration for battery monitoring. This NUT server bridges that gap by:

- Converting EcoFlow MQTT data to standard UPS protocol
- Enabling battery monitoring in Home Assistant
- Supporting multiple River 3 Plus devices simultaneously
- Providing real-time battery status, voltage, current, and temperature

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


## 🔧 Troubleshooting

### Common Issues

**"ERR UNKNOWN-UPS" in Home Assistant**
- Ensure the server is running: `python3 simple_nut_server.py`
- Check device serial numbers in config match your actual devices
- Verify MQTT credentials are correct

**No data received from devices**
- Check your EcoFlow app is working (devices online)
- Verify MQTT credentials in config file
- Check server logs for connection errors

**Home Assistant can't connect to NUT server**
- Ensure port 3493 is not blocked by firewall
- Check NUT server is running on correct IP address
- Verify Home Assistant NUT integration configuration

### Logs and Debugging

Enable debug logging by changing the log level in your config:
```json
{
  "logging": {
    "level": "DEBUG",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  }
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ✅ Status

**WORKING** - Successfully receiving live data from River 3 Plus devices and exposing via NUT protocol with real protobuf parsing.

## 🙏 Acknowledgments

- EcoFlow for their excellent portable power stations
- Home Assistant community for the NUT integration
- Python community for excellent MQTT and protobuf libraries
