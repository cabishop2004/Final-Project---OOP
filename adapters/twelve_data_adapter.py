"""adapt Twelve Data responses into application models."""

from __future__ import annotations

from typing import Any, Mapping

from models.stock_quote import StockQuote


class TwelveDataAdapterError(
    ValueError
):
    """indicate invalid Twelve Data quote data."""


class TwelveDataAdapter:
    """translate Twelve Data JSON into StockQuote objects."""

    @staticmethod
    def _text(
        payload: Mapping[str, Any],
        key: str,
    ) -> str:
        """return a field as text."""
        value = payload.get(key)

        if value is None:
            return ""

        return str(value).strip()

    @staticmethod
    def _number(
        payload: Mapping[str, Any],
        key: str,
    ) -> float:
        """return a field as float."""
        value = payload.get(key)

        if value in (
            None,
            "",
        ):
            return 0.0

        try:
            return float(
                value
            )

        except (
            TypeError,
            ValueError,
        ) as error:
            raise TwelveDataAdapterError(
                f"invalid numeric value for {key}"
            ) from error

    @classmethod
    def _integer(
        cls,
        payload: Mapping[str, Any],
        key: str,
    ) -> int:
        """return a field as integer."""
        return int(
            cls._number(
                payload,
                key,
            )
        )

    @classmethod
    def adapt_quote(
        cls,
        payload: Mapping[str, Any],
    ) -> StockQuote:
        """convert one Twelve Data quote into StockQuote."""
        symbol = cls._text(
            payload,
            "symbol",
        )

        if not symbol:
            raise TwelveDataAdapterError(
                "quote does not contain a symbol"
            )

        raw_range = payload.get(
            "fifty_two_week",
            {},
        )

        if isinstance(
            raw_range,
            Mapping,
        ):
            year_range = raw_range

        else:
            year_range = {}

        return StockQuote(
            symbol=symbol,
            company_name=cls._text(
                payload,
                "name",
            ),
            exchange=cls._text(
                payload,
                "exchange",
            ),
            currency=cls._text(
                payload,
                "currency",
            ),
            price=cls._number(
                payload,
                "close",
            ),
            open_price=cls._number(
                payload,
                "open",
            ),
            previous_close=cls._number(
                payload,
                "previous_close",
            ),
            change=cls._number(
                payload,
                "change",
            ),
            change_percentage=cls._number(
                payload,
                "percent_change",
            ),
            day_low=cls._number(
                payload,
                "low",
            ),
            day_high=cls._number(
                payload,
                "high",
            ),
            year_low=cls._number(
                year_range,
                "low",
            ),
            year_high=cls._number(
                year_range,
                "high",
            ),
            volume=cls._integer(
                payload,
                "volume",
            ),
            is_market_open=bool(
                payload.get(
                    "is_market_open",
                    False,
                )
            ),
        )
