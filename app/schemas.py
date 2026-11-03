from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

SignalDirection = Literal["long", "short"]
SignalType = Literal["entry", "exit", "update", "alert"]
Timeframe = Literal["1m", "5m", "15m", "30m", "1h", "4h", "1d"]


class SignalIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    schema_version: str = Field(alias="schema", min_length=1, max_length=16)
    source: str = Field(min_length=1, max_length=64)
    indicator_version: str = Field(min_length=1, max_length=64)
    signal_id: str = Field(min_length=1, max_length=128)
    symbol: str = Field(min_length=1, max_length=32)
    timeframe: Timeframe
    bar_time: datetime
    signal_type: SignalType = Field(alias="type")
    direction: SignalDirection

    entry: Optional[float] = None
    stop: Optional[float] = None
    target: Optional[float] = None
    notes: Optional[str] = Field(default=None, max_length=1000)