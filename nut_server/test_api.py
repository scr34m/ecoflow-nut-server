#!/usr/bin/env python3
"""
Test EcoFlow API endpoints to find the correct MQTT credentials endpoint.
"""

import asyncio
import aiohttp
import base64
import json

async def test_api_endpoints():
    """Test different API endpoints to find the correct one."""
    
    email = "andreanjos@gmail.com"
    password = "pZX9D-umfZccou2R"
    
    async with aiohttp.ClientSession() as session:
        # Login first
        login_url = "https://api.ecoflow.com/auth/login"
        headers = {"lang": "en_US", "content-type": "application/json"}
        data = {
            "email": email,
            "password": base64.b64encode(password.encode()).decode(),
            "scene": "IOT_APP",
            "userType": "ECOFLOW",
        }
        
        print("🔐 Testing login...")
        async with session.post(login_url, json=data, headers=headers) as resp:
            print(f"Login status: {resp.status}")
            if resp.status == 200:
                login_data = await resp.json()
                print(f"Login response: {json.dumps(login_data, indent=2)}")
                
                if "data" in login_data and "token" in login_data["data"]:
                    token = login_data["data"]["token"]
                    print(f"✅ Got token: {token[:20]}...")
                    
                    # Test different MQTT endpoints
                    endpoints = [
                        "/certification",
                        "/iot-open/sign",
                        "/iot-auth/app/certification",
                        "/iot-open/sign/device/quota/all",
                        "/device/list",
                        "/user/info"
                    ]
                    
                    for endpoint in endpoints:
                        print(f"\n🔍 Testing endpoint: {endpoint}")
                        url = f"https://api.ecoflow.com{endpoint}"
                        headers_with_auth = {
                            "lang": "en_US",
                            "content-type": "application/json",
                            "authorization": f"Bearer {token}"
                        }
                        
                        try:
                            async with session.get(url, headers=headers_with_auth) as mqtt_resp:
                                print(f"  Status: {mqtt_resp.status}")
                                if mqtt_resp.status == 200:
                                    response_data = await mqtt_resp.json()
                                    print(f"  Response: {json.dumps(response_data, indent=2)}")
                                    
                                    # Check if this looks like MQTT credentials
                                    if "data" in response_data:
                                        data = response_data["data"]
                                        if any(key in data for key in ["url", "port", "certificateAccount", "certificatePassword"]):
                                            print(f"  🎯 FOUND MQTT CREDENTIALS!")
                                            return response_data
                                else:
                                    error_text = await mqtt_resp.text()
                                    print(f"  Error: {error_text}")
                        except Exception as e:
                            print(f"  Exception: {e}")
                else:
                    print("❌ No token in login response")
            else:
                error_text = await resp.text()
                print(f"❌ Login failed: {error_text}")

if __name__ == "__main__":
    asyncio.run(test_api_endpoints())
