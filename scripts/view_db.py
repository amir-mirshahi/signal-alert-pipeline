import sys
import os
# This tells Python to look in the parent folder for the 'app' module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app.models import Signal

db = SessionLocal()
signals = db.query(Signal).all()

print(f"\nTotal signals: {len(signals)}\n" + "-"*40)
for s in signals:
    print(f"[{s.created_at}] {s.direction.upper()} {s.symbol}")
    print(f"  Entry: {s.entry} | Target: {s.target} | Stop: {s.stop}")
    print(f"  Status: {s.status} | PnL: {s.pnl}%")
    print(f"  ID: {s.signal_id}\n")
db.close()