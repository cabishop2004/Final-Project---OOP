"""domain model for congressional trade alert subscriptions."""

from __future__ import annotations

from dataclasses import dataclass

from models.trade import Trade, TradeType


@dataclass(slots=True)
class Subscription:
    """represent one user's congressional trade alert rule."""

    subscription_id: int | None
    user_id: int
    politician: str = ""
    ticker: str = ""
    trade_type: TradeType | None = None
    channel: str = "web"

    def __post_init__(self) -> None:
        """normalize subscription fields."""
        self.politician = self.politician.strip()
        self.ticker = self.ticker.strip().upper()
        self.channel = self.channel.strip().lower() or "web"

        if not self.politician and not self.ticker:
            raise ValueError(
                "a subscription requires a politician or ticker"
            )

    def matches(
        self,
        trade: Trade,
    ) -> bool:
        """return whether a trade satisfies this subscription."""
        if self.politician:
            if (
                self.politician.casefold()
                not in trade.politician.casefold()
            ):
                return False

        if self.ticker:
            if self.ticker != trade.symbol.upper():
                return False

        if self.trade_type is not None:
            if self.trade_type != trade.trade_type:
                return False

        return True
