"""
Test script for the Zephra ML API endpoints
Run this after starting the API server with: uvicorn api.app:app --host 0.0.0.0 --port 8080
"""

import requests
import json

def test_api():
    base_url = "http://localhost:8080"
    
    try:
        # Test root endpoint
        print("Testing root endpoint...")
        response = requests.get(f"{base_url}/")
        print(f"✅ Root: {response.json()}")
        
        # Test predict endpoint
        print("\nTesting predict endpoint...")
        response = requests.get(f"{base_url}/predict")
        result = response.json()
        print(f"✅ Predict: {result}")
        
        # Test forecast endpoint
        print("\nTesting forecast endpoint...")
        response = requests.get(f"{base_url}/forecast")
        result = response.json()
        print(f"✅ Forecast (first 5 hours): {result['forecast_24h'][:5]}")
        print(f"   Total forecast hours: {len(result['forecast_24h'])}")
        
    except requests.ConnectionError:
        print("❌ API server is not running. Start it with:")
        print("   uvicorn api.app:app --host 0.0.0.0 --port 8080")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api()