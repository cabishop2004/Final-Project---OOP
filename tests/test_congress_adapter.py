"""tests for CongressInvests response adaptation."""

from __future__ import annotations

from datetime import date

from adapters.congress_adapter import CongressAdapter
from models.trade import TradeType


def test_adapt_trade() -> None:
    """CongressInvests data should become an internal Trade."""
    payload = {
        "member": "Nancy Pelosi",
        "chamber": "House",
        "ticker": "NVDA",
        "trade_type": "buy",
        "amount": "$1,000,001 - $5,000,000",
        "tx_date": "2026-05-15",
        "disclosed": "2026-05-30",
        "asset": "NVIDIA Corp [ST]",
        "link": "https://example.com/filing",
    }

    trade = CongressAdapter.adapt_trade(
        payload
    )

    assert trade.politician == "Nancy Pelosi"
    assert trade.chamber == "House"
    assert trade.symbol == "NVDA"
    assert trade.trade_type == TradeType.PURCHASE
    assert trade.transaction_date == date(
        2026,
        5,
        15,
    )
    assert trade.disclosure_date == date(
        2026,
        5,
        30,
    )
