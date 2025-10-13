#!/bin/bash
# EcoFlow NUT Server Installation Script for Raspberry Pi

echo "🚀 Installing EcoFlow NUT Server..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
sudo apt install -y python3 python3-pip python3-venv

# Install MQTT client library
echo "📡 Installing MQTT client..."
pip3 install paho-mqtt

# Install HTTP client
echo "🌐 Installing HTTP client..."
pip3 install aiohttp

# Create systemd service
echo "⚙️ Creating systemd service..."
sudo tee /etc/systemd/system/ecoflow-nut.service > /dev/null <<EOF
[Unit]
Description=EcoFlow NUT Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/python3 $(pwd)/simple_nut_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable service
echo "🔧 Enabling service..."
sudo systemctl daemon-reload
sudo systemctl enable ecoflow-nut.service

echo "✅ Installation complete!"
echo ""
echo "📝 Next steps:"
echo "1. Copy config.example.json to config.json and configure your devices"
echo "2. Start the service: sudo systemctl start ecoflow-nut"
echo "3. Check status: sudo systemctl status ecoflow-nut"
echo "4. View logs: journalctl -u ecoflow-nut -f"
