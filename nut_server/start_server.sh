#!/bin/bash
# Start the EcoFlow NUT Server

echo "🚀 Starting EcoFlow NUT Server..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.7+"
    exit 1
fi

# Check if required packages are installed
echo "📦 Checking dependencies..."
python3 -c "import paho.mqtt.client, protobuf" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Installing dependencies..."
    pip3 install -r requirements.txt
fi

# Check if config exists
if [ ! -f "config.json" ]; then
    echo "❌ config.json not found. Please configure your MQTT credentials."
    exit 1
fi

# Start the server
echo "🚀 Starting NUT server..."
python3 ecoflow_nut_server.py
