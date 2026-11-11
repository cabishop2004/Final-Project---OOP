"""tests for the CongressInvests API provider."""

from __future__ import annotations

from unittest.mock import Mock, patch

from models.trade import TradeType
from providers.congress_invests_provider import (
    CongressInvestsProvider,
)


@patch(
    "providers.congress_invests_provider.requests.get"
)
def test_fetch_new_trades(
    mock_get: Mock,
) -> None:
    """provider should normalize API trade responses."""
    response = Mock()

    response.status_code = 200

    response.json.return_value = {
        "total": 1,
        "trades": [
            {
                "member": "Nancy Pelosi",
                "chamber": "House",
                "ticker": "NVDA",
                "trade_type": "buy",
                "amount": "$1,001 - $15,000",
                "tx_date": "2026-05-15",
                "disclosed": "2026-05-30",
                "asset": "NVIDIA Corp",
                "link": "https://example.com",
            }
        ],
    }

    mock_get.return_value = response

    provider = CongressInvestsProvider()

    trades = provider.fetch_new_trades(
        limit=10
    )

    assert len(trades) == 1
    assert trades[0].symbol == "NVDA"
    assert (
        trades[0].trade_type
        == TradeType.PURCHASE
    )

    mock_get.assert_called_once()
