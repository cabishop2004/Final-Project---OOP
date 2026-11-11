"""CongressInvests congressional trade provider."""

from __future__ import annotations

from datetime import datetime, time
from typing import Any

import requests

from adapters.congress_adapter import (
    CongressAdapter,
    CongressAdapterError,
)
from models.trade import Trade
from providers.data_provider import (
    DataProviderError,
    TradeDataProvider,
)


BASE_URL = (
    "https://congressinfor-production.up.railway.app"
)

DEFAULT_TIMEOUT = 10.0


class CongressInvestsProvider(
    TradeDataProvider
):
    """retrieve congressional disclosures from CongressInvests."""

    def __init__(
        self,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        """initialize the provider."""
        if timeout <= 0:
            raise ValueError(
                "timeout must be greater than zero"
            )

        self.__timeout = timeout

    @property
    def timeout(self) -> float:
        """return the request timeout."""
        return self.__timeout

    def _request(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """perform one CongressInvests request."""
        try:
            response = requests.get(
                f"{BASE_URL}/{endpoint}",
                params=params,
                timeout=self.__timeout,
            )

        except requests.RequestException as error:
            raise DataProviderError(
                "could not connect to CongressInvests"
            ) from error

        if response.status_code != 200:
            raise DataProviderError(
                "CongressInvests returned "
                f"HTTP {response.status_code}"
            )

        try:
            payload = response.json()

        except ValueError as error:
            raise DataProviderError(
                "CongressInvests returned invalid JSON"
            ) from error

        if not isinstance(
            payload,
            dict,
        ):
            raise DataProviderError(
                "CongressInvests returned an "
                "unexpected response"
            )

        return payload

    def fetch_new_trades(
        self,
        since: datetime | None = None,
        limit: int = 50,
    ) -> list[Trade]:
        """retrieve recent normalized congressional trades."""
        if limit < 1:
            return []

        request_limit = min(
            limit,
            500,
        )

        payload = self._request(
            "trades/recent",
            {
                "limit": request_limit,
                "offset": 0,
            },
        )

        raw_trades = payload.get(
            "trades",
            [],
        )

        if not isinstance(
            raw_trades,
            list,
        ):
            raise DataProviderError(
                "CongressInvests returned invalid trade data"
            )

        trades: list[Trade] = []

        try:
            for item in raw_trades:
                if not isinstance(
                    item,
                    dict,
                ):
                    continue

                trades.append(
                    CongressAdapter.adapt_trade(
                        item
                    )
                )

        except CongressAdapterError as error:
            raise DataProviderError(
                "could not adapt congressional "
                f"trade data: {error}"
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
                    filtered.append(
                        trade
                    )

            trades = filtered

        return trades[:limit]
