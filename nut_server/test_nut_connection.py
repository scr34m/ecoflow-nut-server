#!/usr/bin/env python3
"""
Test NUT connection to verify the server is working.
"""

import socket
import time

def test_nut_connection(host="127.0.0.1", port=3493, ups_names=None):
    """Test connection to NUT server."""
    if ups_names is None:
        ups_names = ["basement_media_river_3_plus", "server_room_river_3_plus", "sitting_room_river_3_plus"]
    
    print(f"🔌 Testing NUT connection to {host}:{port}")
    
    try:
        # Connect to NUT server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((host, port))
        print("✅ Connected to NUT server")
        
        # Send authentication
        sock.send(b"USERNAME admin\n")
        response = sock.recv(1024).decode()
        print(f"📤 USERNAME: {response.strip()}")
        
        sock.send(b"PASSWORD admin\n")
        response = sock.recv(1024).decode()
        print(f"📤 PASSWORD: {response.strip()}")
        
        sock.send(b"LOGIN\n")
        response = sock.recv(1024).decode()
        print(f"📤 LOGIN: {response.strip()}")
        
        # List UPS devices
        sock.send(b"LIST UPS\n")
        response = sock.recv(1024).decode()
        print(f"📤 LIST UPS: {response.strip()}")
        
        # Test each UPS device
        for ups_name in ups_names:
            print(f"\n🔋 Testing UPS: {ups_name}")
            
            # Get UPS variables
            sock.send(f"LIST VAR {ups_name}\n".encode())
            response = sock.recv(1024).decode()
            print(f"📤 LIST VAR: {response.strip()}")
            
            # Get specific variables
            variables = ["battery.charge", "battery.voltage", "battery.current", "ups.status"]
            for var in variables:
                sock.send(f"GET VAR {ups_name} {var}\n".encode())
                response = sock.recv(1024).decode()
                print(f"📤 {var}: {response.strip()}")
        
        # Logout
        sock.send(b"LOGOUT\n")
        response = sock.recv(1024).decode()
        print(f"📤 LOGOUT: {response.strip()}")
        
        sock.close()
        print("✅ NUT connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ NUT connection test failed: {e}")
        return False

if __name__ == "__main__":
    test_nut_connection()
