"""Twelve Data stock quote provider."""

from __future__ import annotations

from typing import Any

import requests

from adapters.twelve_data_adapter import (
    TwelveDataAdapter,
    TwelveDataAdapterError,
)
from models.stock_quote import StockQuote
from providers.data_provider import (
    DataProviderError,
    QuoteDataProvider,
)


BASE_URL = "https://api.twelvedata.com"
DEFAULT_TIMEOUT = 10.0


class TwelveDataProvider(
    QuoteDataProvider
):
    """retrieve current stock quotes from Twelve Data."""

    def __init__(
        self,
        api_key: str,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        """initialize the quote provider."""
        if not api_key.strip():
            raise DataProviderError(
                "TWELVE_DATA_API_KEY is not configured"
            )

        if timeout <= 0:
            raise ValueError(
                "timeout must be greater than zero"
            )

        self.__api_key = (
            api_key.strip()
        )

        self.__timeout = timeout

    @property
    def timeout(self) -> float:
        """return the request timeout."""
        return self.__timeout

    def _request(
        self,
        endpoint: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """perform one authenticated Twelve Data request."""
        headers = {
            "Authorization": (
                f"apikey {self.__api_key}"
            )
        }

        try:
            response = requests.get(
                f"{BASE_URL}/{endpoint}",
                params=params,
                headers=headers,
                timeout=self.__timeout,
            )

        except requests.RequestException as error:
            raise DataProviderError(
                "could not connect to Twelve Data"
            ) from error

        try:
            payload = response.json()

        except ValueError as error:
            raise DataProviderError(
                "Twelve Data returned invalid JSON"
            ) from error

        if not isinstance(
            payload,
            dict,
        ):
            raise DataProviderError(
                "Twelve Data returned an "
                "unexpected response"
            )

        if response.status_code != 200:
            raise DataProviderError(
                "Twelve Data returned "
                f"HTTP {response.status_code}"
            )

        if (
            payload.get("status")
            == "error"
        ):
            raise DataProviderError(
                str(
                    payload.get(
                        "message",
                        "Twelve Data returned an error",
                    )
                )
            )

        return payload

    def fetch_quote(
        self,
        symbol: str,
    ) -> StockQuote:
        """retrieve one current stock quote."""
        normalized_symbol = (
            symbol.strip().upper()
        )

        if not normalized_symbol:
            raise DataProviderError(
                "a ticker symbol is required"
            )

        payload = self._request(
            "quote",
            {
                "symbol": normalized_symbol,
            },
        )

        try:
            return (
                TwelveDataAdapter.adapt_quote(
                    payload
                )
            )

        except TwelveDataAdapterError as error:
            raise DataProviderError(
                "could not adapt Twelve Data "
                f"quote data: {error}"
            ) from error
