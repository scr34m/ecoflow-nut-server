# GitHub Repository Setup

## 🚀 Upload to GitHub

### 1. Create Repository on GitHub
1. Go to [GitHub.com](https://github.com)
2. Click "New Repository"
3. Name: `ecoflow-nut-server`
4. Description: `NUT server for EcoFlow River 3 Plus devices - Home Assistant integration`
5. Make it **Private** (for now)
6. **Don't** initialize with README (we already have one)
7. Click "Create Repository"

### 2. Upload Your Code
```bash
# Add GitHub remote
git remote add origin https://github.com/andreanjos/ecoflow-nut-server.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### 3. Update README URLs
After creating the repository, update these URLs in the README:
- Replace `YOUR_PI_IP` with your Raspberry Pi's IP address
- Replace `YOUR_USERNAME` with your GitHub username

## 🍓 Raspberry Pi Setup

### 1. Clone on Your Pi
```bash
git clone https://github.com/andreanjos/ecoflow-nut-server.git
cd ecoflow-nut-server
```

### 2. Configure Your Devices
```bash
# Copy example config
cp config_multi.example.json config_multi.json

# Edit with your device details
nano config_multi.json
```

### 3. Install and Run
```bash
# Run installation script
chmod +x install.sh
./install.sh

# Configure your devices
cp config_multi.example.json config_multi.json
nano config_multi.json

# Start the service
sudo systemctl start ecoflow-nut

# Check status
sudo systemctl status ecoflow-nut
```

## 🏠 Home Assistant Setup

1. **Install NUT Integration** in Home Assistant
2. **Configure NUT** to connect to your Pi: `YOUR_PI_IP:3493`
3. **Add your devices** - they should appear as:
   - `basement_media_river_3_plus EcoFlow River 3 Plus`
   - `server_room_river_3_plus EcoFlow River 3 Plus`
   - `sitting_room_river_3_plus EcoFlow River 3 Plus`

## 📊 What You'll Get

- **Real-time battery monitoring** for all your River 3 Plus devices
- **Charging status** and power flow information
- **Temperature monitoring** 
- **Voltage and current** readings
- **Home Assistant dashboard** integration

## 🔧 Troubleshooting

### Check Service Status
```bash
sudo systemctl status ecoflow-nut
```

### View Logs
```bash
journalctl -u ecoflow-nut -f
```

### Test NUT Connection
```bash
python3 test_nut_connection.py
```

### Restart Service
```bash
sudo systemctl restart ecoflow-nut
```
