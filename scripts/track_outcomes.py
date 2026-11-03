import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import httpx
import yfinance as yf
from app.database import SessionLocal
from app.models import Signal

def get_current_price(symbol: str) -> float:
    """Fetches price from Binance for Crypto, Yahoo Finance for Forex."""
    try:
        # If it's crypto (e.g., BTCUSDT), use Binance
        if "USDT" in symbol.upper() or "BTC" in symbol.upper():
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol.upper()}"
            response = httpx.get(url, timeout=10)
            response.raise_for_status()
            return float(response.json()["price"])
        
        # If it's Forex (e.g., EURUSD), use Yahoo Finance (needs '=X' suffix)
        else:
            ticker = f"{symbol.upper()}=X"
            data = yf.Ticker(ticker)
            # Get the most recent 1-minute data
            hist = data.history(period="1d", interval="1m")
            if hist.empty:
                return None
            return float(hist['Close'].iloc[-1])
            
    except Exception as e:
        print(f"Failed to fetch price for {symbol}: {e}")
        return None

def track_outcomes():
    db = SessionLocal()
    pending_signals = db.query(Signal).filter(Signal.status == "pending").all()
    
    if not pending_signals:
        print("No pending signals to track.")
        db.close()
        return

    print(f"Tracking {len(pending_signals)} pending signals...\n" + "-"*50)

    for signal in pending_signals:
        current_price = get_current_price(signal.symbol)
        
        if not current_price:
            continue
            
        print(f"[{signal.symbol}] {signal.direction.upper()} | Entry: {signal.entry:.5f} | Target: {signal.target:.5f} | Stop: {signal.stop:.5f}")
        print(f"Current Live Price: {current_price:.5f}")

        if signal.direction == "long":
            if current_price >= signal.target:
                signal.status = "target_hit"
                signal.pnl = round(((signal.target - signal.entry) / signal.entry) * 100, 2)
                print(f"🎯 TARGET HIT! PnL: +{signal.pnl}%")
            elif current_price <= signal.stop:
                signal.status = "stop_hit"
                signal.pnl = round(((signal.stop - signal.entry) / signal.entry) * 100, 2)
                print(f"🛑 STOP HIT! PnL: {signal.pnl}%")
            else:
                print("⏳ Still pending (Price is between Stop and Target)")

        elif signal.direction == "short":
            if current_price <= signal.target:
                signal.status = "target_hit"
                signal.pnl = round(((signal.entry - signal.target) / signal.entry) * 100, 2)
                print(f"🎯 TARGET HIT! PnL: +{signal.pnl}%")
            elif current_price >= signal.stop:
                signal.status = "stop_hit"
                signal.pnl = round(((signal.entry - signal.stop) / signal.entry) * 100, 2)
                print(f"🛑 STOP HIT! PnL: {signal.pnl}%")
            else:
                print("⏳ Still pending (Price is between Stop and Target)")

        print("-" * 50)
    
    db.commit()
    db.close()
    print("Database updated.")

if __name__ == "__main__":
    track_outcomes()