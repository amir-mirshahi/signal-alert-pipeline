import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import httpx
import yfinance as yf
from app.database import SessionLocal
from app.models import Signal


def get_current_price(symbol: str) -> float | None:
    """Live price from Binance (crypto) or Yahoo Finance (forex). None if unavailable."""
    try:
        if "USDT" in symbol.upper() or "BTC" in symbol.upper():
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol.upper()}"
            response = httpx.get(url, timeout=10)
            response.raise_for_status()
            return float(response.json()["price"])
        hist = yf.Ticker(f"{symbol.upper()}=X").history(period="1d", interval="1m")
        if hist.empty:
            return None
        return float(hist["Close"].iloc[-1])
    except Exception as e:
        print(f"Failed to fetch price for {symbol}: {e}")
        return None


def evaluate(direction: str, entry: float, stop: float, target: float, price: float):
    """Return (status, pnl_percent). Status is 'pending' if neither level was hit."""
    if direction == "long":
        if price >= target:
            return "target_hit", round((target - entry) / entry * 100, 2)
        if price <= stop:
            return "stop_hit", round((stop - entry) / entry * 100, 2)
    elif direction == "short":
        if price <= target:
            return "target_hit", round((entry - target) / entry * 100, 2)
        if price >= stop:
            return "stop_hit", round((entry - stop) / entry * 100, 2)
    return "pending", None


def track_outcomes():
    db = SessionLocal()
    try:
        pending = (
            db.query(Signal)
            .filter(Signal.status == "pending", Signal.signal_type == "entry")
            .all()
        )
        if not pending:
            print("No pending entry signals to track.")
            return

        print(f"Tracking {len(pending)} pending signals...\n" + "-" * 50)
        for signal in pending:
            if None in (signal.entry, signal.stop, signal.target) or signal.entry == 0:
                print(f"[{signal.signal_id}] skipped: missing entry/stop/target")
                continue

            price = get_current_price(signal.symbol)
            if price is None:
                print(f"[{signal.symbol}] skipped: no price available")
                continue

            status, pnl = evaluate(
                signal.direction, signal.entry, signal.stop, signal.target, price
            )
            print(f"[{signal.symbol}] {signal.direction.upper()} | price {price:.5f} -> {status}")
            if status != "pending":
                signal.status = status
                signal.pnl = pnl

        db.commit()
        print("Database updated.")
    finally:
        db.close()


if __name__ == "__main__":
    track_outcomes()
