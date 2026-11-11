"""coordinate congressional trade and stock quote providers."""

from __future__ import annotations

from typing import ClassVar

from models.stock_quote import StockQuote
from models.trade import Trade
from providers.congress_invests_provider import (
    CongressInvestsProvider,
)
from providers.data_provider import (
    DataProviderError,
    QuoteDataProvider,
    TradeDataProvider,
)
from providers.twelve_data_provider import (
    TwelveDataProvider,
)


class MarketManager:
    """coordinate application access to external providers."""

    __instance: ClassVar[
        "MarketManager | None"
    ] = None

    def __new__(
        cls,
        quote_api_key: str = "",
        trade_provider: TradeDataProvider | None = None,
        quote_provider: QuoteDataProvider | None = None,
    ) -> "MarketManager":
        """return the singleton manager instance."""
        if cls.__instance is None:
            cls.__instance = super().__new__(
                cls
            )

        return cls.__instance

    def __init__(
        self,
        quote_api_key: str = "",
        trade_provider: TradeDataProvider | None = None,
        quote_provider: QuoteDataProvider | None = None,
    ) -> None:
        """initialize provider dependencies once."""
        if hasattr(
            self,
            "_MarketManager__trade_provider",
        ):
            return

        self.__trade_provider = (
            trade_provider
            or CongressInvestsProvider()
        )

        if quote_provider is not None:
            self.__quote_provider = (
                quote_provider
            )

        elif quote_api_key.strip():
            self.__quote_provider = (
                TwelveDataProvider(
                    quote_api_key
                )
            )

        else:
            self.__quote_provider = None

    @classmethod
    def instance(
        cls,
        quote_api_key: str = "",
    ) -> "MarketManager":
        """return the singleton MarketManager."""
        return cls(
            quote_api_key=quote_api_key
        )

    def recent_trades(
        self,
        limit: int = 50,
    ) -> list[Trade]:
        """retrieve recent congressional trades."""
        return (
            self.__trade_provider.fetch_new_trades(
                limit=limit
            )
        )

    def stock_quote(
        self,
        symbol: str,
    ) -> StockQuote:
        """retrieve current market quote information."""
        if self.__quote_provider is None:
            raise DataProviderError(
                "TWELVE_DATA_API_KEY is not configured"
            )

        return (
            self.__quote_provider.fetch_quote(
                symbol
            )
        )
