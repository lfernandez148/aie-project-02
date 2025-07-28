import requests
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_root_health():
    """Test the root endpoint as a simple health check."""
    
    print("🏥 Testing Root Health Check\n")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/")
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response.elapsed.total_seconds():.3f}s")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ API Status: {data.get('status', 'unknown')}")
            print(f"📝 Message: {data.get('message', 'No message')}")
            print(f"🔢 Version: {data.get('version', 'Unknown')}")
            print("\n🎉 Root endpoint is healthy!")
        else:
            print(f"❌ Root endpoint failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API server")
        print("Make sure the API is running: python main.py")
    except Exception as e:
        print(f"❌ Error testing root health: {e}")

def test_health_endpoint():
    """Test the dedicated health endpoint."""
    
    print("\n🏥 Testing Dedicated Health Endpoint\n")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response.elapsed.total_seconds():.3f}s")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Health Status: {data.get('status', 'unknown')}")
            print(f"📝 Message: {data.get('message', 'No message')}")
            print(f"🔢 Version: {data.get('version', 'Unknown')}")
            print(f"⏰ Timestamp: {datetime.fromtimestamp(data.get('timestamp', 0))}")
            print("\n🎉 Health endpoint is working!")
        else:
            print(f"❌ Health endpoint failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API server")
        print("Make sure the API is running: python main.py")
    except Exception as e:
        print(f"❌ Error testing health endpoint: {e}")

def test_both_endpoints():
    """Test both health check endpoints."""
    
    print("🏥 Testing Both Health Check Endpoints\n")
    print("=" * 60)
    
    endpoints = [
        ("Root (/)", "/"),
        ("Health (/health)", "/health")
    ]
    
    for name, endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {name}: {response.status_code} ({response.elapsed.total_seconds():.3f}s)")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Status: {data.get('status', 'unknown')}")
                print(f"   Message: {data.get('message', 'No message')}")
            
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
    
    print("\n✅ Health check test completed!")

if __name__ == "__main__":
    test_root_health()
    test_health_endpoint()
    test_both_endpoints() 