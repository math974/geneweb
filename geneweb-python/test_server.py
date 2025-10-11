#!/usr/bin/env python3
"""Quick server test."""

import subprocess
import time
import sys
import requests

def test_server():
    """Start server and test it."""
    print("🚀 Starting test server...")
    
    # Start server
    proc = subprocess.Popen(
        ["python", "-m", "geneweb.cli.main", "-p", "9999", "-bd", "../distribution/bases", "-hd", "../distribution/gw"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd="/Users/lucasmaelarnassalom/Project/geneweb/geneweb-python"
    )
    
    # Wait for server to start
    time.sleep(2)
    
    try:
        # Test health endpoint
        print("🔍 Testing /health endpoint...")
        response = requests.get("http://localhost:9999/health", timeout=5)
        
        if response.status_code == 200:
            print("✅ Server is running!")
            print(f"   Response: {response.json()}")
            
            # Test base endpoint
            print("\n🔍 Testing /galichet endpoint...")
            response2 = requests.get("http://localhost:9999/galichet", timeout=5)
            print(f"   Status: {response2.status_code}")
            if response2.status_code == 200:
                print(f"   Content preview: {response2.text[:200]}...")
            
            print("\n✅ All tests passed!")
            return 0
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return 1
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return 1
    finally:
        print("\n🛑 Stopping server...")
        proc.terminate()
        proc.wait(timeout=5)

if __name__ == "__main__":
    sys.exit(test_server())
