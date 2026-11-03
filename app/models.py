"""
The actual database table definition for a Signal.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database import Base

class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, index=True)
    schema_version = Column(String)
    source = Column(String)
    indicator_version = Column(String)
    
    # unique=True is the database-level guarantee against duplicates
    signal_id = Column(String, unique=True, index=True) 
    
    symbol = Column(String)
    timeframe = Column(String)
    bar_time = Column(DateTime)
    signal_type = Column(String)
    direction = Column(String)
    
    entry = Column(Float, nullable=True)
    stop = Column(Float, nullable=True)
    target = Column(Float, nullable=True)
    notes = Column(String, nullable=True)
    
    # When our system actually received the signal
    status = Column(String, default="pending") # pending, target_hit, stop_hit
    pnl = Column(Float, nullable=True)         # Profit/Loss percentage

    created_at = Column(DateTime, default=datetime.utcnow)