# api/test_auth_api.py
import requests
import json

BASE_URL = "http://localhost:8000"

# Test API keys
TEST_API_KEY = "sk-test-1234567890abcdef"
PROD_API_KEY = "sk-prod-abcdef1234567890"
INVALID_API_KEY = "sk-invalid-key"

def test_auth_api():
    """Test the authenticated API endpoints."""
    
    print("🔐 Testing Authenticated Campaign Performance API\n")
    print("=" * 60)
    
    # Test 1: Root endpoint (no auth required)
    print("1. Testing root endpoint (no auth required)...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Status: {response.status_code}")
        data = response.json()
        print(f"📋 Version: {data['version']}")
        print(f"🔐 Auth Required: {data['authentication']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    # Test 2: Auth verification with valid key
    print("2. Testing auth verification with valid API key...")
    try:
        headers = {"Authorization": f"Bearer {TEST_API_KEY}"}
        response = requests.get(f"{BASE_URL}/auth/verify", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Authenticated: {data['authenticated']}")
            print(f"🔑 API Key: {data['api_key_info']['name']}")
            print(f"⚡ Rate Limit: {data['api_key_info']['rate_limit']}")
        else:
            print(f"❌ Status: {response.status_code}")
            print(f"   Error: {response.json()['detail']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    # Test 3: Auth verification with invalid key
    print("3. Testing auth verification with invalid API key...")
    try:
        headers = {"Authorization": f"Bearer {INVALID_API_KEY}"}
        response = requests.get(f"{BASE_URL}/auth/verify", headers=headers)
        if response.status_code == 401:
            print(f"✅ Correctly rejected invalid API key: {response.json()['detail']}")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    # Test 3b: Auth verification without auth header
    print("3b. Testing auth verification without Authorization header...")
    try:
        response = requests.get(f"{BASE_URL}/auth/verify")
        if response.status_code == 403:
            print(f"✅ Correctly rejected request without auth header: {response.json()['detail']}")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    # Test 4: Protected endpoint with valid key
    print("4. Testing protected endpoint with valid API key...")
    try:
        headers = {"Authorization": f"Bearer {TEST_API_KEY}"}
        response = requests.get(f"{BASE_URL}/campaigns/summary", headers=headers)
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Success! Total campaigns: {stats['total_campaigns']:,}")
        else:
            print(f"❌ Status: {response.status_code}")
            print(f"   Error: {response.json()['detail']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    # Test 5: Protected endpoint without auth
    print("5. Testing protected endpoint without authentication...")
    try:
        response = requests.get(f"{BASE_URL}/campaigns/summary")
        if response.status_code == 403:
            print(f"✅ Correctly rejected request without auth: {response.json()['detail']}")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    # Test 7: Different API key with different rate limits
    print("7. Testing production API key...")
    try:
        headers = {"Authorization": f"Bearer {PROD_API_KEY}"}
        response = requests.get(f"{BASE_URL}/auth/verify", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Production key: {data['api_key_info']['name']}")
            print(f"⚡ Rate Limit: {data['api_key_info']['rate_limit']}")
        else:
            print(f"❌ Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    # Test 8: Rate limiting test
    print("8. Testing rate limiting (making multiple requests)...")
    try:
        headers = {"Authorization": f"Bearer {TEST_API_KEY}"}
        for i in range(5):
            response = requests.get(f"{BASE_URL}/campaigns/100", headers=headers)
            print(f"   Request {i+1}: {response.status_code}")
            if response.status_code == 429:
                print(f"   ⚠️  Rate limit hit after {i+1} requests")
                break
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    print("=" * 60)
    print("🎉 Authentication testing completed!")
    print("\n💡 Key Features:")
    print("   • Bearer token authentication")
    print("   • API key validation")
    print("   • Rate limiting per endpoint")
    print("   • Different rate limits per API key")
    print("   • Proper error responses")
    print("   • Logging of API key usage")

if __name__ == "__main__":
    test_auth_api() 