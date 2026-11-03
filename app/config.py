"""
Loads secrets from the .env file so they never live in the code.
"""
import os
from dotenv import load_dotenv

# Load the .env file into the environment
load_dotenv()

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "default_secret")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./signals.db")