#!/usr/bin/env python3
"""
Simplified NUT server that directly parses River 3 Plus binary protobuf data.
"""

import asyncio
import json
import base64
import logging
import sys
import os
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
import paho.mqtt.client as mqtt
import socket
import threading
import hashlib
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
LOG = logging.getLogger(__name__)

class SimpleEcoFlowNUTServer:
    def __init__(self, devices: List[Dict[str, str]], mqtt_config: Dict[str, Any], nut_config: Dict[str, Any]):
        self.devices = devices
        self.mqtt_config = mqtt_config
        self.mqtt_client = None
        self.nut_server = None
        self.ups_data = {}
        self.running = False
        
        # NUT server configuration
        self.nut_host = nut_config["host"]
        self.nut_port = nut_config["port"]
        
    async def get_mqtt_credentials(self):
        """Get MQTT credentials from EcoFlow API."""
        import aiohttp
        
        LOG.info("🔐 Getting MQTT credentials from EcoFlow API...")
        
        async with aiohttp.ClientSession() as session:
            # Login to EcoFlow API
            login_url = "https://api.ecoflow.com/auth/login"
            headers = {"lang": "en_US", "content-type": "application/json"}
            data = {
                "email": self.mqtt_config["username"],
                "password": base64.b64encode(self.mqtt_config["password"].encode()).decode(),
                "scene": "IOT_APP",
                "userType": "ECOFLOW",
            }
            
            try:
                async with session.post(login_url, json=data, headers=headers) as resp:
                    if resp.status != 200:
                        raise Exception(f"Login failed: {resp.status} - {await resp.text()}")
                    
                    login_data = await resp.json()
                    if login_data.get("message", "").lower() != "success":
                        raise Exception(f"Login failed: {login_data.get('message', 'Unknown error')}")
                    
                    # Get MQTT credentials
                    mqtt_url = "https://api.ecoflow.com/iot-auth/app/certification"
                    mqtt_headers = {
                        "lang": "en_US",
                        "content-type": "application/json",
                        "authorization": f"Bearer {login_data['data']['token']}"
                    }
                    
                    async with session.get(mqtt_url, headers=mqtt_headers) as mqtt_resp:
                        if mqtt_resp.status != 200:
                            raise Exception(f"MQTT credentials failed: {mqtt_resp.status} - {await mqtt_resp.text()}")
                        
                        mqtt_data = await mqtt_resp.json()
                        if mqtt_data.get("message", "").lower() != "success":
                            raise Exception(f"MQTT credentials failed: {mqtt_data.get('message', 'Unknown error')}")
                        
                        # Extract MQTT credentials
                        mqtt_info = mqtt_data["data"]
                        self.mqtt_host = mqtt_info["url"]
                        self.mqtt_port = int(mqtt_info["port"])
                        self.mqtt_username = mqtt_info["certificateAccount"]
                        self.mqtt_password = mqtt_info["certificatePassword"]
                        
                        # Generate client_id like the original integration
                        user_id = login_data["data"]["user"]["userId"]

                        self.mqtt_client_id = self._generate_client_id(user_id);

                        LOG.info(f"✅ Got MQTT credentials: {self.mqtt_host}:{self.mqtt_port}")
                        LOG.info(f"✅ Client ID: {self.mqtt_client_id}")
                        return True
                        
            except Exception as e:
                LOG.error(f"❌ Failed to get MQTT credentials: {e}")
                return False

    def _generate_client_id(self, user_id):
        verify_info = "988f28e96e2245a0ab80ec23c6c2c56fd2c0f6ea64194ae78e659acb0317c4c6"
        verify_info_s = verify_info[0:32]
        verify_info_s2 = verify_info[32:]

        first_part = "ANDROID_"  + str(uuid.uuid4()).upper() + "_" + str(user_id)

        ts = str(round(time.time() * 1000))

        checksum = hashlib.md5((verify_info_s2 + first_part + ts).encode("utf-8")).hexdigest().upper()

        return first_part + "_" + verify_info_s + "_" + ts + "_" + checksum;


    def setup_mqtt_client(self):
        """Setup MQTT client to connect to EcoFlow."""
        LOG.info("🔌 Setting up MQTT client...")
        
        self.mqtt_client = mqtt.Client(client_id=self.mqtt_client_id)
        self.mqtt_client.username_pw_set(
            self.mqtt_username, 
            self.mqtt_password
        )
        
        # Set up SSL/TLS like the original integration
        import ssl
        self.mqtt_client.tls_set(certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED)
        self.mqtt_client.tls_insecure_set(False)
        
        # Set up callbacks
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        self.mqtt_client.on_disconnect = self.on_mqtt_disconnect
        
        # Connect to broker
        try:
            self.mqtt_client.connect(
                self.mqtt_host, 
                self.mqtt_port, 
                60
            )
            LOG.info("✅ MQTT client configured")
        except Exception as e:
            LOG.error(f"❌ MQTT connection failed: {e}")
            raise
    
    def on_mqtt_connect(self, client, userdata, flags, rc):
        """MQTT connection callback."""
        if rc == 0:
            LOG.info("✅ MQTT broker connected")
            # Subscribe to topics for all devices
            for device in self.devices:
                serial = device["serial"]
                ups_name = device["ups_name"]
                topics = [
                    f"/app/device/property/{serial}",
                    f"/app/device/thing/property/set_reply/{serial}",
                    f"/app/device/thing/property/post/{serial}",
                ]
                for topic in topics:
                    client.subscribe(topic)
                    LOG.info(f"📡 Subscribed to: {topic} (UPS: {ups_name})")
        else:
            LOG.error(f"❌ MQTT connection failed with code {rc}")
    
    def on_mqtt_message(self, client, userdata, msg):
        """MQTT message callback - parse binary protobuf and update UPS data."""
        try:
            topic = msg.topic
            LOG.debug(f"📨 Received message on {topic} ({len(msg.payload)} bytes)")
            
            # Find which device this message is for
            device_serial = None
            ups_name = None
            for device in self.devices:
                if device["serial"] in topic:
                    device_serial = device["serial"]
                    ups_name = device["ups_name"]
                    break
            
            if not device_serial:
                LOG.warning(f"⚠️ Unknown device for topic: {topic}")
                return
            
            if msg.payload[0] == 0x7B and msg.payload[1] == 0x22:
                log.debug(f"📨 JSON message, ignore")
                return            

            # This is binary protobuf data, try to parse it directly
            LOG.debug(f"📨 Binary protobuf message ({len(msg.payload)} bytes)")
            try:
                # Simple binary parsing - just extract basic info
                parsed_data = self.parse_simple_binary(msg.payload, ups_name)
                if parsed_data:
                    self.update_ups_data(ups_name, parsed_data)
                    LOG.info(f"✅ Updated UPS data from binary for {ups_name}: {parsed_data}")
            except Exception as e:
                LOG.error(f"❌ Failed to parse binary protobuf for {ups_name}: {e}")
            
        except Exception as e:
            LOG.error(f"❌ Error processing MQTT message: {e}")
    
    def parse_simple_binary(self, binary_data: bytes, ups_name: str) -> Optional[Dict[str, Any]]:
        """Parse binary protobuf data using real EcoFlow parser."""
        try:
            # Import the real parser
            from real_ecoflow_parser import EcoFlowProtobufParser
            
            # Create parser instance
            parser = EcoFlowProtobufParser()
            
            # Extract device serial from UPS name
            device_serial = self._get_device_serial_from_ups_name(ups_name)
            
            # Parse the binary data
            data = parser.decode(binary_data, device_serial)
            
            if data:
                return data
            else:
                return None
            
        except Exception as e:
            LOG.error(f"❌ Binary parsing failed: {e}")
            return None
    
    def _get_device_serial_from_ups_name(self, ups_name: str) -> str:
        return next((item["serial"] for item in self.devices if item["ups_name"] == ups_name), "UNKNOWN")
    
    # see https://github.com/foxthefox/ioBroker.ecoflow-mqtt/blob/main/doc/devices/river3plus.md
    def update_ups_data(self, ups_name: str, data: Dict[str, Any]):
        """Update UPS data from parsed message."""

        # Initialize UPS data if not exists
        if ups_name not in self.ups_data:
            self.ups_data[ups_name] = {"packs": {}}

        self.ups_data[ups_name]["packs"][data["num"]] = data

        ups = self.ups_data[ups_name]
        fields = ["soc", "vol", "temp", "remainCap", "designCap", "remainTime"]

        for f in fields:
            ups[f] = 0

        ups_status = "OL"
        battery_status = "CHRG"
        count = len(ups["packs"])
        for pack in ups["packs"].values():
            for f in fields:
                ups[f] += pack.get(f, 0)
            if pack["chgDsgState"] == 1: # if any of the packs are in discharge state
                battery_status = "ONBATT"
                ups_status = "OB"

        for f in fields:
            if f != "remainCap" and f != "designCap":
                ups[f] = ups[f] / count if count else 0


        self.ups_data[ups_name]["battery.charge"] = ups["soc"]

        # Convert milliamper hours to amper hour
        self.ups_data[ups_name]["battery.capacity"] = ups["remainCap"] / 1000.0
        self.ups_data[ups_name]["battery.capacity.nominal"] = ups["designCap"] / 1000.0

        # Convert millivolts to volts
        self.ups_data[ups_name]["battery.voltage"] = ups["vol"] / 1000.0

        self.ups_data[ups_name]["battery.temperature"] = ups["temp"]

        # so so calculation
        self.ups_data[ups_name]["battery.runtime"] = int((ups["remainTime"] / 100) * 3600)

        self.ups_data[ups_name]["battery.status"] = battery_status

        # Set timestamp
        self.ups_data[ups_name]["ups.timestamp"] = int(time.time())

        self.ups_data[ups_name]["ups.status"] = ups_status

    def on_mqtt_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback."""
        LOG.info(f"🔌 MQTT disconnected (rc={rc})")
    
    def start_nut_server(self):
        """Start the NUT server."""
        LOG.info("🚀 Starting NUT server...")
        
        # Create server socket
        self.nut_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.nut_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.nut_server.bind((self.nut_host, self.nut_port))
            self.nut_server.listen(5)
            LOG.info(f"✅ NUT server listening on {self.nut_host}:{self.nut_port}")
            
            self.running = True
            
            # Start server in background thread
            server_thread = threading.Thread(target=self._run_nut_server, daemon=True)
            server_thread.start()
            
        except Exception as e:
            LOG.error(f"❌ Failed to start NUT server: {e}")
            raise
    
    def _run_nut_server(self):
        """Run the NUT server loop."""
        while self.running:
            try:
                client_socket, address = self.nut_server.accept()
                LOG.info(f"📡 NUT client connected from {address}")
                
                # Handle client in separate thread
                client_thread = threading.Thread(
                    target=self._handle_nut_client, 
                    args=(client_socket,), 
                    daemon=True
                )
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    LOG.error(f"❌ NUT server error: {e}")
    
    def _handle_nut_client(self, client_socket):
        """Handle NUT client requests."""
        try:
            while self.running:
                # Read command from client
                data = client_socket.recv(1024)
                if not data:
                    break
                
                command = data.decode().strip()
                LOG.debug(f"📨 NUT command: {command}")
                
                # Process NUT commands
                response = self._process_nut_command(command)
                
                # Send response
                if response:
                    client_socket.send(response.encode())
                    LOG.debug(f"📤 NUT response: {response}")
                
        except Exception as e:
            LOG.error(f"❌ NUT client error: {e}")
        finally:
            client_socket.close()
    
    def _process_nut_command(self, command: str) -> Optional[str]:
        """Process NUT protocol commands."""
        if command == "LIST UPS":
            # List all UPS devices
            ups_list = []
            for device in self.devices:
                ups_name = device["ups_name"]
                ups_list.append(f"{ups_name} EcoFlow River 3 Plus")
            return f"BEGIN LIST UPS\n" + "\n".join(ups_list) + "\nEND LIST UPS\n"
        
        elif command.startswith("LIST VAR "):
            # Extract UPS name from command
            ups_name = command.split("LIST VAR ")[1]
            if ups_name in self.ups_data:
                return self._get_ups_variables(ups_name)
            else:
                return f"ERR UNKNOWN-UPS\n"
        
        elif command.startswith("GET VAR "):
            # Extract UPS name and variable from command
            parts = command.split(" ")
            if len(parts) >= 4:
                ups_name = parts[2]
                var_name = parts[3]
                if ups_name in self.ups_data:
                    value = self.ups_data[ups_name].get(var_name, 0)
                    if isinstance(value, float):
                        return f"VAR {ups_name} {var_name} {value:.1f}\n"
                    else:
                        return f"VAR {ups_name} {var_name} {value}\n"
                else:
                    return f"ERR UNKNOWN-UPS\n"
        
        elif command == "USERNAME admin":
            return "OK\n"
        
        elif command == "PASSWORD admin":
            return "OK\n"
        
        elif command == "LOGIN":
            return "OK\n"
        
        elif command == "LOGOUT":
            return "OK\n"
        
        else:
            LOG.debug(f"Unknown NUT command: {command}")
            return None
    
    def _get_ups_variables(self, ups_name: str) -> str:
        """Get all UPS variables in NUT format."""
        if ups_name not in self.ups_data:
            return f"ERR UNKNOWN-UPS\n"
        
        data = self.ups_data[ups_name]
        variables = [
            f"VAR {ups_name} battery.charge {data.get('battery.charge', 0)}",
            f"VAR {ups_name} battery.capacity {data.get('battery.capacity', 0):.1f}",
            f"VAR {ups_name} battery.capacity.nominal {data.get('battery.capacity.nominal', 0):.1f}",
            f"VAR {ups_name} battery.voltage {data.get('battery.voltage', 0):.1f}",
            f"VAR {ups_name} battery.temperature {data.get('battery.temperature', 0)}",
            f"VAR {ups_name} battery.runtime {data.get('battery.runtime', 0)}",
            f"VAR {ups_name} battery.status {data.get('battery.status', 'UNKNOWN')}",
            f"VAR {ups_name} ups.status {data.get('ups.status', 'UNKNOWN')}",
            f"VAR {ups_name} ups.timestamp {data.get('ups.timestamp', 0)}",
        ]
        
        return "BEGIN LIST VAR\n" + "\n".join(variables) + "\nEND LIST VAR\n"
    
    async def start(self):
        """Start the EcoFlow NUT server."""
        LOG.info("🚀 Starting Simple EcoFlow NUT Server")
        
        try:
            # Get MQTT credentials from EcoFlow API
            if not await self.get_mqtt_credentials():
                raise Exception("Failed to get MQTT credentials from EcoFlow API")
            
            # Setup MQTT client
            self.setup_mqtt_client()
            
            # Start NUT server
            self.start_nut_server()
            
            # Start MQTT loop
            self.mqtt_client.loop_start()
            
            LOG.info("✅ Simple EcoFlow NUT Server started successfully!")
            LOG.info(f"📡 NUT server: {self.nut_host}:{self.nut_port}")
            LOG.info(f"🔋 UPS devices: {[device['ups_name'] for device in self.devices]}")
            LOG.info("🎯 Ready for Home Assistant NUT integration!")
            
            # Keep running
            while self.running:
                await asyncio.sleep(1)
                
        except Exception as e:
            LOG.error(f"❌ Failed to start server: {e}")
            raise
    
    def stop(self):
        """Stop the server."""
        LOG.info("🛑 Stopping Simple EcoFlow NUT Server...")
        self.running = False
        
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        
        if self.nut_server:
            self.nut_server.close()
        
        LOG.info("✅ Simple EcoFlow NUT Server stopped")

async def main():
    """Main function."""
    # Load configuration from file
    import json
    config_path = os.path.join(os.path.dirname(__file__), "config_multi.json")
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
        devices = config["devices"]
        mqtt_config = config["mqtt"]
        nut_config = config["nut"]
    else:
        LOG.error(f"❌ Missing configuration file: config_multi.json")
        exit(1)

    
    # Create and start server
    server = SimpleEcoFlowNUTServer(devices, mqtt_config, nut_config)
    
    try:
        await server.start()
    except KeyboardInterrupt:
        LOG.info("🛑 Received interrupt signal")
    finally:
        server.stop()

if __name__ == "__main__":
    asyncio.run(main())
