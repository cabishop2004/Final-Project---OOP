"""tests for Twelve Data response adaptation."""

from __future__ import annotations

from adapters.twelve_data_adapter import (
    TwelveDataAdapter,
)


def test_adapt_quote() -> None:
    """Twelve Data quote JSON should become StockQuote."""
    payload = {
        "symbol": "AAPL",
        "name": "Apple Inc",
        "exchange": "NASDAQ",
        "currency": "USD",
        "open": "148.44",
        "high": "148.97",
        "low": "147.22",
        "close": "148.85",
        "volume": "67903927",
        "previous_close": "149.09",
        "change": "-0.24",
        "percent_change": "-0.16",
        "is_market_open": False,
        "fifty_two_week": {
            "low": "103.10",
            "high": "157.26",
        },
    }

    quote = TwelveDataAdapter.adapt_quote(
        payload
    )

    assert quote.symbol == "AAPL"
    assert quote.company_name == "Apple Inc"
    assert quote.price == 148.85
    assert quote.day_low == 147.22
    assert quote.day_high == 148.97
    assert quote.year_low == 103.10
    assert quote.year_high == 157.26
