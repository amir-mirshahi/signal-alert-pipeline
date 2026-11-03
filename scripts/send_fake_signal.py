import httpx
import os
from dotenv import load_dotenv

load_dotenv()

# We use the local URL and your secret from .env
URL = "http://127.0.0.1:8000/webhook"
SECRET = os.getenv("WEBHOOK_SECRET", "my_super_secret_token")

# Base payload
payload = {
    "schema": "1.0",
    "source": "python_test",
    "indicator_version": "1.0.0",
    "signal_id": "test-live-2",
    "symbol": "BTCUSDT",
    "timeframe": "1h",
    "bar_time": "2025-01-01T00:00:00Z",
    "type": "entry",
    "direction": "long",
    "entry": 42000.0,
    "stop": 41000.0,
    "target": 44000.0
}

print("1. Sending VALID signal...")
r = httpx.post(URL, json=payload, headers={"X-Webhook-Secret": SECRET})
print(f"Response: {r.status_code} - {r.json()}\n")

print("2. Sending DUPLICATE signal...")
r = httpx.post(URL, json=payload, headers={"X-Webhook-Secret": SECRET})
print(f"Response: {r.status_code} - {r.json()}\n")

print("3. Sending WRONG TOKEN...")
r = httpx.post(URL, json=payload, headers={"X-Webhook-Secret": "wrong_password"})
print(f"Response: {r.status_code} - {r.text}\n")

print("4. Sending BAD FORMAT (missing symbol)...")
bad_payload = payload.copy()
del bad_payload["symbol"]
bad_payload["signal_id"] = "test-999"
r = httpx.post(URL, json=bad_payload, headers={"X-Webhook-Secret": SECRET})
print(f"Response: {r.status_code} - {r.text}\n")