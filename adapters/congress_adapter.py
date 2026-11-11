"""adapt CongressInvests responses into application models."""

from __future__ import annotations

from datetime import date
from typing import Any, Mapping

from models.trade import Trade, TradeType


class CongressAdapterError(ValueError):
    """indicate invalid congressional trade data."""


class CongressAdapter:
    """translate CongressInvests JSON into Trade objects."""

    @staticmethod
    def _text(
        payload: Mapping[str, Any],
        key: str,
    ) -> str:
        """return one field as normalized text."""
        value = payload.get(key)

        if value is None:
            return ""

        return str(value).strip()

    @classmethod
    def _date(
        cls,
        payload: Mapping[str, Any],
        key: str,
    ) -> date | None:
        """convert an ISO date field into a date."""
        value = cls._text(
            payload,
            key,
        )

        if not value:
            return None

        try:
            return date.fromisoformat(
                value[:10]
            )

        except ValueError as error:
            raise CongressAdapterError(
                f"invalid date in field {key}"
            ) from error

    @classmethod
    def adapt_trade(
        cls,
        payload: Mapping[str, Any],
    ) -> Trade:
        """convert one CongressInvests trade into Trade."""
        politician = cls._text(
            payload,
            "member",
        )

        chamber = cls._text(
            payload,
            "chamber",
        )

        ticker = cls._text(
            payload,
            "ticker",
        ).upper()

        return Trade(
            symbol=ticker or "N/A",
            politician=politician or "Unknown",
            chamber=chamber or "Unknown",
            asset_description=cls._text(
                payload,
                "asset",
            ),
            trade_type=TradeType.from_api(
                cls._text(
                    payload,
                    "trade_type",
                )
            ),
            amount_range=cls._text(
                payload,
                "amount",
            ),
            transaction_date=cls._date(
                payload,
                "tx_date",
            ),
            disclosure_date=cls._date(
                payload,
                "disclosed",
            ),
            owner="",
            source_url=cls._text(
                payload,
                "link",
            ),
        )
