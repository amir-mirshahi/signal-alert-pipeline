# 📈 Algorithmic Signal Alert Pipeline

A production-ready, asynchronous trading-signal pipeline that receives webhooks from any sender (MetaTrader 5, TradingView, Python scripts), validates and saves them to a database, broadcasts them to Telegram, and tracks their performance against live market prices.

## 🏗️ Architecture & Flow
1. **Sender**: An MQL5 script (MT5) or Python script sends a JSON webhook.
2. **FastAPI Webhook**: Validates the secret token and parses the payload with Pydantic.
3. **Database**: Saves the signal to SQLite and blocks duplicate `signal_id`s.
4. **Telegram Alert**: Sends a formatted alert in a background task so the API responds instantly.
5. **Outcome Tracker**: A script that fetches live Crypto (Binance) and Forex (Yahoo Finance) prices to determine if the signal hit its Target or Stop Loss.
6. **Analytics**: A script that generates a performance report (Win Rate, Total PnL).

## 🛠️ Tech Stack
- **Framework**: FastAPI, Uvicorn
- **Data Validation**: Pydantic v2
- **Database**: SQLAlchemy, SQLite
- **Integration**: MetaTrader 5 (MQL5), Telegram Bot API, Binance API, Yahoo Finance
- **Testing**: Pytest, HTTPX

## 🚀 Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/signal-alert-pipeline.git
   cd signal-alert-pipeline