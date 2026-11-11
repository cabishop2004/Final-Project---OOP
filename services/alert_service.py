"""match congressional trades against user subscriptions."""

from __future__ import annotations

from models.alert_match import AlertMatch
from models.subscription import Subscription
from models.trade import Trade
from services.message_formatter import MessageFormatter


class AlertService:
    """find subscription rules that match newly retrieved trades."""

    def __init__(
        self,
        formatter: MessageFormatter | None = None,
    ) -> None:
        """initialize the alert service."""
        self.__formatter = formatter or MessageFormatter()

    def process(
        self,
        trades: list[Trade],
        subscriptions: list[Subscription],
    ) -> list[AlertMatch]:
        """return all matching trade and subscription pairs."""
        matches: list[AlertMatch] = []

        for trade in trades:
            for subscription in subscriptions:
                if not subscription.matches(trade):
                    continue

                matches.append(
                    AlertMatch(
                        subscription=subscription,
                        trade=trade,
                        message=self.__formatter.format(
                            trade
                        ),
                    )
                )

        return matches
