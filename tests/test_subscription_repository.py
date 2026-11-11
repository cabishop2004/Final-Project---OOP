"""tests for SQLite subscription persistence."""

from __future__ import annotations

from pathlib import Path

from models.subscription import Subscription
from models.trade import TradeType
from storage.subscription_repository import (
    SubscriptionRepository,
)


def test_add_list_delete(
    tmp_path: Path,
) -> None:
    """repository should persist and remove subscriptions."""
    repository = SubscriptionRepository(
        tmp_path / "test.db"
    )

    saved = repository.add(
        Subscription(
            subscription_id=None,
            user_id=1,
            ticker="NVDA",
            trade_type=TradeType.PURCHASE,
            channel="web",
        )
    )

    assert saved.subscription_id is not None

    subscriptions = repository.list_for_user(
        1
    )

    assert len(subscriptions) == 1
    assert subscriptions[0].ticker == "NVDA"

    assert repository.delete(
        saved.subscription_id,
        1,
    )

    assert (
        repository.list_for_user(1)
        == []
    )
