"""domain model for congressional stock trades."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum


class TradeType(str, Enum):
    """supported congressional trade transaction types."""

    PURCHASE = "Purchase"
    SALE = "Sale"
    EXCHANGE = "Exchange"
    OTHER = "Other"

    @classmethod
    def from_api(
        cls,
        value: str,
    ) -> "TradeType":
        """convert an external transaction label into TradeType."""
        normalized = value.strip().lower()

        if (
            "purchase" in normalized
            or "buy" in normalized
        ):
            return cls.PURCHASE

        if (
            "sale" in normalized
            or "sell" in normalized
        ):
            return cls.SALE

        if "exchange" in normalized:
            return cls.EXCHANGE

        return cls.OTHER


@dataclass(frozen=True, slots=True)
class Trade:
    """represent one normalized congressional stock disclosure."""

    symbol: str
    politician: str
    chamber: str
    asset_description: str
    trade_type: TradeType
    amount_range: str
    transaction_date: date | None
    disclosure_date: date | None
    owner: str
    source_url: str
