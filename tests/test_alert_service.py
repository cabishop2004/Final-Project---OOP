"""tests for congressional trade alert matching."""

from __future__ import annotations

from datetime import date

from models.subscription import Subscription
from models.trade import Trade, TradeType
from services.alert_service import AlertService


def test_process_matching_trade() -> None:
    """matching trades should produce an alert."""
    trade = Trade(
        symbol="NVDA",
        politician="Nancy Pelosi",
        chamber="House",
        asset_description="NVIDIA Corp",
        trade_type=TradeType.PURCHASE,
        amount_range="$1,001 - $15,000",
        transaction_date=date(
            2026,
            5,
            15,
        ),
        disclosure_date=date(
            2026,
            5,
            30,
        ),
        owner="",
        source_url="",
    )

    subscription = Subscription(
        subscription_id=1,
        user_id=1,
        ticker="NVDA",
    )

    matches = AlertService().process(
        [trade],
        [subscription],
    )

    assert len(matches) == 1
    assert matches[0].trade == trade
    assert "NVDA" in matches[0].message
