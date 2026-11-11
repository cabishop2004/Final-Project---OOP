"""tests for the Twelve Data quote provider."""

from __future__ import annotations

from unittest.mock import Mock, patch

from providers.twelve_data_provider import (
    TwelveDataProvider,
)


@patch(
    "providers.twelve_data_provider.requests.get"
)
def test_fetch_quote(
    mock_get: Mock,
) -> None:
    """quote retrieval should work using a mocked API."""
    response = Mock()

    response.status_code = 200

    response.json.return_value = {
        "symbol": "NVDA",
        "name": "NVIDIA Corp",
        "exchange": "NASDAQ",
        "currency": "USD",
        "open": "185.00",
        "high": "190.00",
        "low": "183.00",
        "close": "188.50",
        "volume": "50000000",
        "previous_close": "184.00",
        "change": "4.50",
        "percent_change": "2.45",
        "is_market_open": True,
        "fifty_two_week": {
            "low": "86.00",
            "high": "195.00",
        },
    }

    mock_get.return_value = response

    provider = TwelveDataProvider(
        "fake-test-key"
    )

    quote = provider.fetch_quote(
        "nvda"
    )

    assert quote.symbol == "NVDA"
    assert quote.price == 188.50

    request = mock_get.call_args

    assert (
        request.kwargs["headers"]["Authorization"]
        == "apikey fake-test-key"
    )
