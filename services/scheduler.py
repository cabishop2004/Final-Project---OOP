"""poll congressional trade data and process subscriptions."""

from __future__ import annotations

from models.alert_match import AlertMatch
from services.alert_service import AlertService
from services.market_manager import MarketManager
from storage.subscription_repository import (
    SubscriptionRepository,
)


class Scheduler:
    """coordinate one polling cycle of the alert system."""

    def __init__(
        self,
        manager: MarketManager,
        repository: SubscriptionRepository,
        alert_service: AlertService,
        interval_seconds: int = 900,
    ) -> None:
        """initialize scheduler dependencies."""
        if interval_seconds <= 0:
            raise ValueError(
                "interval_seconds must be greater than zero"
            )

        self.__manager = manager
        self.__repository = repository
        self.__alert_service = alert_service
        self.__interval_seconds = interval_seconds

    @property
    def interval_seconds(self) -> int:
        """return the configured polling interval."""
        return self.__interval_seconds

    def poll(
        self,
        user_id: int,
        limit: int = 50,
    ) -> list[AlertMatch]:
        """perform one trade retrieval and matching cycle."""
        trades = self.__manager.recent_trades(
            limit=limit
        )

        subscriptions = (
            self.__repository.list_for_user(
                user_id
            )
        )

        return self.__alert_service.process(
            trades,
            subscriptions,
        )
