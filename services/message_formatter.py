"""format matched congressional stock trades into alert messages."""

from __future__ import annotations

from models.trade import Trade


class MessageFormatter:
    """create user-friendly congressional trade alert messages."""

    @staticmethod
    def format(
        trade: Trade,
    ) -> str:
        """format one trade into an alert message."""
        transaction_date = (
            trade.transaction_date.isoformat()
            if trade.transaction_date is not None
            else "unknown date"
        )

        return (
            f"{trade.politician} "
            f"{trade.trade_type.value.lower()} "
            f"{trade.symbol} "
            f"({trade.amount_range or 'amount unknown'}) "
            f"on {transaction_date}"
        )
