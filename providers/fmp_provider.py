"""Financial Modeling Prep implementation of DataProvider."""

from __future__ import annotations

from datetime import datetime, time
from typing import Any

import requests

from adapters.fmp_adapter import FMPAdapter, FMPAdapterError
from models.stock_quote import StockQuote
from models.trade import Trade
from providers.data_provider import DataProvider


BASE_URL = "https://financialmodelingprep.com/stable"
DEFAULT_TIMEOUT = 10.0


class FMPProviderError(RuntimeError):
    """indicate an error communicating with FMP."""


class FMPProvider(DataProvider):
    """retrieve congressional trades and quotes from FMP."""

    def __init__(
        self,
        api_key: str,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        """initialize the FMP provider."""
        if not api_key.strip():
            raise FMPProviderError(
                "FMP_API_KEY is not configured"
            )

        self.__api_key = api_key.strip()
        self.__timeout = timeout

    @property
    def timeout(self) -> float:
        """return the request timeout."""
        return self.__timeout

    def _request(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """perform one authenticated FMP request."""
        request_params = dict(params or {})
        request_params["apikey"] = self.__api_key

        try:
            response = requests.get(
                f"{BASE_URL}/{endpoint}",
                params=request_params,
                timeout=self.__timeout,
            )

            response.raise_for_status()
            payload = response.json()

        except requests.RequestException as error:
            raise FMPProviderError(
                f"FMP request failed: {error}"
            ) from error

        except ValueError as error:
            raise FMPProviderError(
                "FMP returned invalid JSON"
            ) from error

        if isinstance(payload, dict):
            message = payload.get(
                "Error Message",
                payload.get("message", ""),
            )

            if message:
                raise FMPProviderError(str(message))

        if not isinstance(payload, list):
            raise FMPProviderError(
                "FMP returned an unexpected response"
            )

        return [
            item
            for item in payload
            if isinstance(item, dict)
        ]

    def fetch_new_trades(
        self,
        since: datetime | None = None,
        limit: int = 50,
    ) -> list[Trade]:
        """retrieve and normalize recent House and Senate trades."""
        if limit < 1:
            return []

        request_limit = min(max(limit, 10), 100)

        house_payload = self._request(
            "house-latest",
            {
                "page": 0,
                "limit": request_limit,
            },
        )

        senate_payload = self._request(
            "senate-latest",
            {
                "page": 0,
                "limit": request_limit,
            },
        )

        try:
            trades = [
                FMPAdapter.adapt_trade(item, "House")
                for item in house_payload
            ]

            trades.extend(
                FMPAdapter.adapt_trade(item, "Senate")
                for item in senate_payload
            )

        except FMPAdapterError as error:
            raise FMPProviderError(
                f"could not adapt FMP trade data: {error}"
            ) from error

        if since is not None:
            filtered: list[Trade] = []

            for trade in trades:
                if trade.disclosure_date is None:
                    continue

                disclosure_datetime = datetime.combine(
                    trade.disclosure_date,
                    time.min,
                )

                if disclosure_datetime >= since:
                    filtered.append(trade)

            trades = filtered

        trades.sort(
            key=lambda trade: (
                trade.disclosure_date
                or trade.transaction_date
            ),
            reverse=True,
        )

        return trades[:limit]

    def fetch_quote(
        self,
        symbol: str,
    ) -> StockQuote:
        """retrieve and normalize a current stock quote."""
        normalized_symbol = symbol.strip().upper()

        if not normalized_symbol:
            raise FMPProviderError(
                "a ticker symbol is required"
            )

        payload = self._request(
            "quote",
            {"symbol": normalized_symbol},
        )

        if not payload:
            raise FMPProviderError(
                f"no quote found for {normalized_symbol}"
            )

        try:
            return FMPAdapter.adapt_quote(payload[0])

        except FMPAdapterError as error:
            raise FMPProviderError(
                f"could not adapt FMP quote data: {error}"
            ) from error
