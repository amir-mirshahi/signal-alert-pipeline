from unittest.mock import patch
import pytest

# A valid base payload for testing
payload = {
    "schema": "1.0",
    "source": "pytest",
    "indicator_version": "1.0.0",
    "signal_id": "test-pytest-001",
    "symbol": "BTCUSDT",
    "timeframe": "1h",
    "bar_time": "2025-01-01T00:00:00Z",
    "type": "entry",
    "direction": "long",
    "entry": 42000.0,
    "stop": 41000.0,
    "target": 44000.0
}

# We use the client fixture from conftest.py
def test_valid_signal(client):
    # Mock the telegram function so it doesn't try to hit the real API
    with patch("app.main.send_telegram_alert") as mock_telegram:
        response = client.post("/webhook", json=payload, headers={"X-Webhook-Secret": "my_super_secret_token"})
        
        assert response.status_code == 200
        assert response.json()["status"] == "accepted"
        # Verify the background task was called with the right message
        mock_telegram.assert_called_once()

def test_duplicate_signal(client):
    with patch("app.main.send_telegram_alert"):
        # Send the first time
        client.post("/webhook", json=payload, headers={"X-Webhook-Secret": "my_super_secret_token"})
        # Send it again
        response = client.post("/webhook", json=payload, headers={"X-Webhook-Secret": "my_super_secret_token"})
        
        assert response.status_code == 200
        assert response.json()["status"] == "duplicate"

def test_wrong_token(client):
    response = client.post("/webhook", json=payload, headers={"X-Webhook-Secret": "wrong_token"})
    assert response.status_code == 401
    assert "Invalid" in response.json()["detail"]

def test_bad_format(client):
    bad_payload = payload.copy()
    del bad_payload["symbol"] # Remove a required field
    
    response = client.post("/webhook", json=bad_payload, headers={"X-Webhook-Secret": "my_super_secret_token"})
    
    assert response.status_code == 422 # Pydantic validation error
    assert response.json()["detail"][0]["type"] == "missing"