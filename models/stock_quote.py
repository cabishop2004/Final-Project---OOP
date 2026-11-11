"""domain model for stock quote information."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StockQuote:
    """represent normalized stock market quote data."""

    symbol: str
    company_name: str
    exchange: str
    currency: str
    price: float
    open_price: float
    previous_close: float
    change: float
    change_percentage: float
    day_low: float
    day_high: float
    year_low: float
    year_high: float
    volume: int
    is_market_open: bool
