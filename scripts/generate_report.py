import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app.models import Signal

def generate_report():
    db = SessionLocal()
    signals = db.query(Signal).all()
    
    if not signals:
        print("No signals found in the database.")
        db.close()
        return

    total_signals = len(signals)
    wins = 0
    losses = 0
    pending = 0
    total_pnl = 0.0
    
    for s in signals:
        if s.status == "target_hit":
            wins += 1
            total_pnl += (s.pnl or 0.0)
        elif s.status == "stop_hit":
            losses += 1
            total_pnl += (s.pnl or 0.0)
        else:
            pending += 1

    # Calculate Win Rate
    closed_trades = wins + losses
    win_rate = (wins / closed_trades * 100) if closed_trades > 0 else 0.0

    # Print the Report
    print("=" * 45)
    print("📊  SIGNAL PIPELINE PERFORMANCE REPORT  📊")
    print("=" * 45)
    print(f"Total Signals Processed : {total_signals}")
    print(f"Pending (Open)          : {pending}")
    print(f"Closed Trades           : {closed_trades}")
    print("-" * 45)
    print(f"✅ Target Hit (Wins)     : {wins}")
    print(f"❌ Stop Hit (Losses)     : {losses}")
    print(f"🏆 Win Rate             : {win_rate:.2f}%")
    print(f"💰 Total Cumulative PnL : {total_pnl:+.2f}%")
    print("=" * 45)

    db.close()

if __name__ == "__main__":
    generate_report()