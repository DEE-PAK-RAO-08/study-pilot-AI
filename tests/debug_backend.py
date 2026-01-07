
import sys
import os
import json

# Add backend to path so we can import app
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from app import app
    print("✅ Successfully imported app.py")
except Exception as e:
    print(f"❌ Failed to import app.py: {e}")
    sys.exit(1)

def test_backend_logic():
    print("🚀 Testing /api/query endpoint logic internally...")
    
    # Create a test client
    client = app.test_client()
    
    # We need a valid API key. Let's look at the database or register one?
    # Or we can just mock the request context?
    # Easier: Register a user first to get a key.
    
    # 1. Register
    reg_payload = {
        "name": "Debug User",
        "email": "debug@example.com",
        "password": "pass"
    }
    res = client.post('/api/auth/register', json=reg_payload)
    if res.status_code == 409:
        # Login if exists
        res = client.post('/api/auth/login', json={"email": "debug@example.com", "password": "pass"})
        
    data = res.get_json()
    api_key = data.get('api_key')
    print(f"🔑 Obtained API Key: {api_key}")
    
    if not api_key:
        print(f"❌ Could not get API key. Response: {res.data}")
        return

    # 2. Test Query
    # This triggers the Cloud LLM logic if configured
    print("\n❓ Sending Query: 'What is deep learning?'")
    res = client.post('/api/query', 
                      headers={'X-API-Key': api_key},
                      json={'query': 'What is deep learning?', 'course_id': 1})
    
    print(f"📡 Status Code: {res.status_code}")
    try:
        response_json = res.get_json()
        print(f"📝 Response Body: {json.dumps(response_json, indent=2)}")
        
        if res.status_code == 200:
            print("✅ Endpoint works!")
        else:
            print("❌ Endpoint returned error.")
            
    except Exception as e:
        print(f"❌ Failed to parse JSON response: {res.data.decode(errors='ignore')}")
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_backend_logic()
