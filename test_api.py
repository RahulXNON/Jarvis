import time
import json
import httpx

print("⏳ Waiting for server to start...")
time.sleep(3)

try:
    print("🧪 Testing JARVIS API endpoint...\n")
    
    client = httpx.Client(timeout=10.0)
    response = client.get('http://127.0.0.1:8888/health')
    
    print("✅ SUCCESS! Server is running!\n")
    print("=" * 50)
    print("Status Code:", response.status_code)
    print("\nAPI Response:")
    print(json.dumps(response.json(), indent=2))
    print("=" * 50)
    
    print("\n📍 Your JARVIS API URL:")
    print("   http://127.0.0.1:8888")
    
    print("\n🔗 Available Endpoints:")
    print("   GET  http://127.0.0.1:8888/health")
    print("   POST http://127.0.0.1:8888/chat")
    print("   GET  http://127.0.0.1:8888/tasks?limit=10")
    print("   GET  http://127.0.0.1:8888/memory/search?q=hello")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
