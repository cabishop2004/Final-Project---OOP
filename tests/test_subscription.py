"""tests for subscription matching."""

from __future__ import annotations

from datetime import date

import pytest

from models.subscription import Subscription
from models.trade import Trade, TradeType


@pytest.fixture
def trade() -> Trade:
    """provide one representative congressional trade."""
    return Trade(
        symbol="NVDA",
        politician="Nancy Pelosi",
        chamber="House",
        asset_description="NVIDIA Corp",
        trade_type=TradeType.PURCHASE,
        amount_range="$1,000,001 - $5,000,000",
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
        source_url="https://example.com",
    )


def test_ticker_subscription_matches(
    trade: Trade,
) -> None:
    """ticker-only subscriptions should match."""
    subscription = Subscription(
        subscription_id=1,
        user_id=1,
        ticker="nvda",
    )

    assert subscription.matches(
        trade
    )


def test_politician_subscription_matches(
    trade: Trade,
) -> None:
    """politician-only subscriptions should match."""
    subscription = Subscription(
        subscription_id=1,
        user_id=1,
        politician="Pelosi",
    )

    assert subscription.matches(
        trade
    )


def test_wrong_trade_type_does_not_match(
    trade: Trade,
) -> None:
    """trade type filtering should reject mismatches."""
    subscription = Subscription(
        subscription_id=1,
        user_id=1,
        ticker="NVDA",
        trade_type=TradeType.SALE,
    )

    assert not subscription.matches(
        trade
    )


def test_empty_subscription_is_invalid() -> None:
    """subscriptions need a politician or ticker."""
    with pytest.raises(
        ValueError
    ):
        Subscription(
            subscription_id=None,
            user_id=1,
        )
