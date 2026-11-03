"""
Sends the alert to Telegram with a simple retry loop.
"""
import time
import httpx
from app.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def send_telegram_alert(text: str, max_retries: int = 3):
    # If you haven't set up Telegram yet, just print to console so tests don't fail
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print(f"Mock Telegram (Missing ENV): {text}")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}

    for attempt in range(max_retries):
        try:
            # 5 second timeout so we don't hang forever
            response = httpx.post(url, json=payload, timeout=5.0)
            response.raise_for_status()
            return  # Success!
        except Exception as e:
            print(f"Telegram failed (attempt {attempt + 1}/{max_retries}): {e}")
            time.sleep(2)  # Wait 2 seconds before retrying