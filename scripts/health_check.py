import requests

services = {
    "auth": "http://auth-service:5000",
    "user": "http://user-service:5001",
    "payment": "http://payment-service:5002",
    "order": "http://order-service:5003",
    "frontend": "http://frontend-service"
}

for name, url in services.items():
    try:
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            print(f"✅ {name} is healthy at {url}")
        else:
            print(f"⚠️  {name} returned status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ {name} health check failed: {e}")

