import os
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
if not WEBHOOK_SECRET or len(WEBHOOK_SECRET) < 16:
    raise RuntimeError(
        "WEBHOOK_SECRET is missing or too short (min 16 characters). See .env.example"
    )

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./signals.db")
