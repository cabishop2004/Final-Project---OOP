"""translate Financial Modeling Prep data into internal models."""

from __future__ import annotations

from datetime import date
from typing import Any, Mapping

from models.stock_quote import StockQuote
from models.trade import Trade, TradeType


class FMPAdapterError(ValueError):
    """indicate malformed or unsupported FMP data."""


class FMPAdapter:
    """adapt FMP response objects into application domain models."""

    @staticmethod
    def _text(payload: Mapping[str, Any], key: str) -> str:
        """return a payload field as normalized text."""
        value = payload.get(key)

        if value is None:
            return ""

        return str(value).strip()

    @staticmethod
    def _number(payload: Mapping[str, Any], key: str) -> float:
        """return a payload field as a floating point number."""
        value = payload.get(key)

        if value in (None, ""):
            return 0.0

        try:
            return float(value)
        except (TypeError, ValueError) as error:
            raise FMPAdapterError(
                f"invalid numeric value for {key}"
            ) from error

    @staticmethod
    def _integer(payload: Mapping[str, Any], key: str) -> int:
        """return a payload field as an integer."""
        return int(FMPAdapter._number(payload, key))

    @staticmethod
    def _date(payload: Mapping[str, Any], key: str) -> date | None:
        """convert an ISO formatted FMP date into a date object."""
        value = FMPAdapter._text(payload, key)

        if not value:
            return None

        try:
            return date.fromisoformat(value[:10])
        except ValueError as error:
            raise FMPAdapterError(
                f"invalid date value for {key}"
            ) from error

    @classmethod
    def adapt_trade(
        cls,
        payload: Mapping[str, Any],
        chamber: str,
    ) -> Trade:
        """adapt an FMP congressional disclosure into a Trade."""
        first_name = cls._text(payload, "firstName")
        last_name = cls._text(payload, "lastName")

        politician = f"{first_name} {last_name}".strip()

        if not politician:
            politician = cls._text(payload, "office")

        return Trade(
            symbol=cls._text(payload, "symbol") or "N/A",
            politician=politician or "Unknown",
            chamber=chamber,
            asset_description=cls._text(
                payload,
                "assetDescription",
            ),
            trade_type=TradeType.from_api(
                cls._text(payload, "type")
            ),
            amount_range=cls._text(payload, "amount"),
            transaction_date=cls._date(
                payload,
                "transactionDate",
            ),
            disclosure_date=cls._date(
                payload,
                "disclosureDate",
            ),
            owner=cls._text(payload, "owner"),
            source_url=cls._text(payload, "link"),
        )

    @classmethod
    def adapt_quote(
        cls,
        payload: Mapping[str, Any],
    ) -> StockQuote:
        """adapt an FMP stock quote into a StockQuote."""
        symbol = cls._text(payload, "symbol")

        if not symbol:
            raise FMPAdapterError(
                "stock quote does not contain a symbol"
            )

        return StockQuote(
            symbol=symbol,
            company_name=cls._text(payload, "name"),
            price=cls._number(payload, "price"),
            change=cls._number(payload, "change"),
            change_percentage=cls._number(
                payload,
                "changePercentage",
            ),
            day_low=cls._number(payload, "dayLow"),
            day_high=cls._number(payload, "dayHigh"),
            year_low=cls._number(payload, "yearLow"),
            year_high=cls._number(payload, "yearHigh"),
            volume=cls._integer(payload, "volume"),
            market_cap=cls._integer(payload, "marketCap"),
        )
