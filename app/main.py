from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app.models import Base, Signal
from app.schemas import SignalIn
from app.security import verify_token
from app.telegram import send_telegram_alert

# Create the database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Signal Alert Pipeline")

# Helper to get a DB session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/webhook", dependencies=[Depends(verify_token)])
def receive_signal(signal: SignalIn, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    
    # 1. Check for duplicates by signal_id
    existing = db.query(Signal).filter(Signal.signal_id == signal.signal_id).first()
    if existing:
        # Return 200 with a status so the sender knows it wasn't an error, just ignored
        return {"status": "duplicate", "signal_id": signal.signal_id}

    # 2. Save to database
    db_signal = Signal(
        schema_version=signal.schema_version,
        source=signal.source,
        indicator_version=signal.indicator_version,
        signal_id=signal.signal_id,
        symbol=signal.symbol,
        timeframe=signal.timeframe,
        bar_time=signal.bar_time,
        signal_type=signal.signal_type,
        direction=signal.direction,
        entry=signal.entry,
        stop=signal.stop,
        target=signal.target,
        notes=signal.notes
    )
    db.add(db_signal)
    db.commit()

    # 3. Prepare the Telegram message
    msg = f"🚨 {signal.direction.upper()} {signal.symbol} ({signal.timeframe})\n"
    msg += f"Type: {signal.signal_type}\n"
    if signal.entry: msg += f"Entry: {signal.entry}\n"
    if signal.stop: msg += f"Stop: {signal.stop}\n"
    if signal.target: msg += f"Target: {signal.target}\n"
    msg += f"Source: {signal.source}"

    # 4. Send alert in the background so the API responds instantly
    background_tasks.add_task(send_telegram_alert, msg)

    return {"status": "accepted", "signal_id": signal.signal_id}