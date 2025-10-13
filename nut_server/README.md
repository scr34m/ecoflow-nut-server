# EcoFlow NUT Server

A Network UPS Tools (NUT) server that bridges EcoFlow River 3 Plus v3 protobuf data to Home Assistant's NUT integration.

## 🎯 **What This Does**

- **Connects** to your River 3 Plus via MQTT
- **Parses** v3 protobuf messages in real-time
- **Presents** the data as a standard UPS to Home Assistant
- **Provides** battery status, voltage, current, temperature, and charging state

## 🚀 **Quick Start**

### 1. **Install Dependencies**
```bash
cd nut_server
pip install -r requirements.txt
```

### 2. **Configure MQTT Credentials**
Edit `config_multi.json` with your EcoFlow MQTT credentials and device serials:
```json
{
  "devices": [
    {
      "serial": "R631ZABAWH3E4701",
      "ups_name": "ecoflow_river_3_plus_1"
    },
    {
      "serial": "R631ZABAWH3E4702",
      "ups_name": "ecoflow_river_3_plus_2"
    }
  ],
  "mqtt": {
    "host": "mqtt.ecoflow.com",
    "port": 8883,
    "username": "your_actual_username",
    "password": "your_actual_password"
  }
}
```

### 3. **Run the Server**
```bash
python ecoflow_nut_server.py
```

### 4. **Add to Home Assistant**
In your `configuration.yaml`:
```yaml
nut:
  - host: 127.0.0.1
    port: 3493
    name: ecoflow_river_3_plus_1
    username: admin
    password: admin
  - host: 127.0.0.1
    port: 3493
    name: ecoflow_river_3_plus_2
    username: admin
    password: admin
```

## 📊 **Available Data**

The NUT server provides these UPS variables:

- **`battery.charge`** - State of charge (0-100%)
- **`battery.voltage`** - Battery voltage (V)
- **`battery.current`** - Battery current (A)
- **`battery.temperature`** - Battery temperature (°C)
- **`ups.status`** - UPS status (OL/CHRG/ONBATT)

## 🔧 **Testing**

### Test NUT Connection
```bash
# Install NUT client tools
sudo apt-get install nut-client

# Test connection
upsc ecoflow_river_3_plus@127.0.0.1
```

### Test MQTT Connection
```bash
# Install MQTT client
pip install paho-mqtt

# Test MQTT
python -c "
import paho.mqtt.client as mqtt
client = mqtt.Client()
client.username_pw_set('your_username', 'your_password')
client.connect('mqtt.ecoflow.com', 8883, 60)
print('MQTT connection test')
client.disconnect()
"
```

## 🐛 **Troubleshooting**

### Common Issues

1. **MQTT Connection Failed**
   - Check credentials in `config.json`
   - Verify device is online in EcoFlow app
   - Test with MQTT client tools

2. **NUT Connection Failed**
   - Check if port 3493 is available
   - Verify NUT client tools are installed
   - Check firewall settings

3. **No Data Received**
   - Check device serial number
   - Verify MQTT topics are correct
   - Enable debug logging

### Debug Mode
```bash
# Run with debug logging
python ecoflow_nut_server.py --debug
```

## 📈 **Benefits**

- **Standard Integration**: Uses HA's built-in NUT integration
- **Reliable**: No custom integration dependencies
- **Real-time**: Live data from your River 3 Plus
- **Flexible**: Easy to modify for other EcoFlow devices
- **Testable**: Can run independently of HA

## 🔄 **Data Flow**

```
River 3 Plus → MQTT → NUT Server → Home Assistant NUT Integration
```

1. **River 3 Plus** sends v3 protobuf data via MQTT
2. **NUT Server** parses protobuf and maps to UPS variables
3. **Home Assistant** reads UPS data via NUT protocol
4. **You** get real-time battery monitoring in HA!

## 🎉 **Success!**

Once running, you'll see:
- Battery charge percentage
- Voltage and current readings
- Temperature monitoring
- Charging status
- All in Home Assistant's standard UPS entities!

This approach is much more reliable than a custom integration and gives you full control over the data flow.
