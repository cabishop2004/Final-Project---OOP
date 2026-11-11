"""abstract interfaces for external financial data providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from models.stock_quote import StockQuote
from models.trade import Trade


class DataProviderError(RuntimeError):
    """indicate a failure communicating with an external provider."""


class TradeDataProvider(ABC):
    """define congressional trade provider behavior."""

    @abstractmethod
    def fetch_new_trades(
        self,
        since: datetime | None = None,
        limit: int = 50,
    ) -> list[Trade]:
        """retrieve recent congressional trades."""


class QuoteDataProvider(ABC):
    """define stock quote provider behavior."""

    @abstractmethod
    def fetch_quote(
        self,
        symbol: str,
    ) -> StockQuote:
        """retrieve a stock quote."""
