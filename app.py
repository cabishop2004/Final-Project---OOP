"""Flask frontend for the Congressional Stock Trade Tracker."""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from models.alert_match import AlertMatch
from models.subscription import Subscription
from models.trade import Trade, TradeType
from models.user import User
from providers.data_provider import DataProviderError
from services.alert_service import AlertService
from services.market_manager import MarketManager
from services.scheduler import Scheduler
from storage.subscription_repository import (
    SubscriptionRepository,
)


load_dotenv()

DATABASE_PATH = Path(
    os.getenv(
        "TRACKER_DB_PATH",
        "data/tracker.db",
    )
)

DEMO_USER = User(
    user_id=1,
    name="Demo User",
)


app = Flask(__name__)

app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    "development-secret",
)


def quote_api_key() -> str:
    """return the configured Twelve Data API key."""
    return os.getenv(
        "TWELVE_DATA_API_KEY",
        "",
    ).strip()


def market_manager() -> MarketManager:
    """return the singleton market manager."""
    return MarketManager.instance(
        quote_api_key()
    )


def subscription_repository() -> SubscriptionRepository:
    """return the subscription repository."""
    return SubscriptionRepository(
        DATABASE_PATH
    )


def scheduler() -> Scheduler:
    """create the polling service."""
    return Scheduler(
        manager=market_manager(),
        repository=subscription_repository(),
        alert_service=AlertService(),
    )


@app.template_filter("display_date")
def display_date(
    value: date | None,
) -> str:
    """format a date for the frontend."""
    if value is None:
        return "Unknown"

    return value.strftime(
        "%b %d, %Y"
    )


@app.template_filter("money")
def money(
    value: float | int,
) -> str:
    """format a numeric value as currency."""
    return f"${value:,.2f}"


@app.template_filter("compact_number")
def compact_number(
    value: int,
) -> str:
    """format a large integer for display."""
    if value >= 1_000_000_000_000:
        return (
            f"{value / 1_000_000_000_000:.2f}T"
        )

    if value >= 1_000_000_000:
        return (
            f"{value / 1_000_000_000:.2f}B"
        )

    if value >= 1_000_000:
        return (
            f"{value / 1_000_000:.2f}M"
        )

    if value >= 1_000:
        return (
            f"{value / 1_000:.2f}K"
        )

    return str(value)


@app.route("/")
def dashboard() -> str:
    """display recent congressional trade activity."""
    error: str | None = None
    trades: list[Trade] = []

    query = request.args.get(
        "q",
        "",
    ).strip().lower()

    chamber = request.args.get(
        "chamber",
        "",
    ).strip().lower()

    trade_type = request.args.get(
        "type",
        "",
    ).strip().lower()

    try:
        trades = (
            market_manager().recent_trades(
                limit=50
            )
        )

    except DataProviderError as caught_error:
        error = str(
            caught_error
        )

    if query:
        trades = [
            trade
            for trade in trades
            if (
                query in trade.politician.lower()
                or query in trade.symbol.lower()
                or query
                in trade.asset_description.lower()
            )
        ]

    if chamber:
        trades = [
            trade
            for trade in trades
            if trade.chamber.lower() == chamber
        ]

    if trade_type:
        trades = [
            trade
            for trade in trades
            if (
                trade.trade_type.value.lower()
                == trade_type
            )
        ]

    purchase_count = sum(
        trade.trade_type
        == TradeType.PURCHASE
        for trade in trades
    )

    sale_count = sum(
        trade.trade_type
        == TradeType.SALE
        for trade in trades
    )

    member_count = len(
        {
            trade.politician
            for trade in trades
        }
    )

    return render_template(
        "dashboard.html",
        trades=trades,
        query=query,
        chamber=chamber,
        trade_type=trade_type,
        purchase_count=purchase_count,
        sale_count=sale_count,
        member_count=member_count,
        trade_api_online=(
            error is None
        ),
        quote_configured=bool(
            quote_api_key()
        ),
        error=error,
    )


@app.route(
    "/subscriptions",
    methods=["GET", "POST"],
)
def subscriptions() -> str:
    """display or create trade alert subscriptions."""
    repository = subscription_repository()

    if request.method == "POST":
        politician = request.form.get(
            "politician",
            "",
        ).strip()

        ticker = request.form.get(
            "ticker",
            "",
        ).strip()

        trade_type_value = request.form.get(
            "trade_type",
            "",
        ).strip()

        channel = request.form.get(
            "channel",
            "web",
        ).strip()

        trade_type: TradeType | None

        if trade_type_value:
            try:
                trade_type = TradeType(
                    trade_type_value
                )

            except ValueError:
                flash(
                    "Invalid trade type.",
                    "error",
                )

                return redirect(
                    url_for(
                        "subscriptions"
                    )
                )

        else:
            trade_type = None

        try:
            repository.add(
                Subscription(
                    subscription_id=None,
                    user_id=DEMO_USER.user_id,
                    politician=politician,
                    ticker=ticker,
                    trade_type=trade_type,
                    channel=channel,
                )
            )

        except ValueError as error:
            flash(
                str(error),
                "error",
            )

        else:
            flash(
                "Subscription created.",
                "success",
            )

        return redirect(
            url_for(
                "subscriptions"
            )
        )

    saved_subscriptions = (
        repository.list_for_user(
            DEMO_USER.user_id
        )
    )

    return render_template(
        "subscriptions.html",
        subscriptions=saved_subscriptions,
        user=DEMO_USER,
    )


@app.post(
    "/subscriptions/<int:subscription_id>/delete"
)
def delete_subscription(
    subscription_id: int,
) -> str:
    """delete a saved subscription."""
    deleted = (
        subscription_repository().delete(
            subscription_id,
            DEMO_USER.user_id,
        )
    )

    if deleted:
        flash(
            "Subscription removed.",
            "success",
        )

    else:
        flash(
            "Subscription not found.",
            "error",
        )

    return redirect(
        url_for(
            "subscriptions"
        )
    )


@app.route("/alerts")
def alerts() -> str:
    """preview current trades matching saved subscriptions."""
    matches: list[AlertMatch] = []
    error: str | None = None

    try:
        matches = scheduler().poll(
            user_id=DEMO_USER.user_id,
            limit=50,
        )

    except DataProviderError as caught_error:
        error = str(
            caught_error
        )

    return render_template(
        "alerts.html",
        matches=matches,
        error=error,
    )


@app.route("/stock")
def stock_lookup() -> str:
    """display current stock quote information."""
    symbol = request.args.get(
        "symbol",
        "",
    ).strip().upper()

    quote = None
    error: str | None = None

    if symbol:
        try:
            quote = (
                market_manager().stock_quote(
                    symbol
                )
            )

        except DataProviderError as caught_error:
            error = str(
                caught_error
            )

    return render_template(
        "stock.html",
        symbol=symbol,
        quote=quote,
        quote_configured=bool(
            quote_api_key()
        ),
        error=error,
    )


@app.route("/about")
def about() -> str:
    """display project information."""
    return render_template(
        "about.html"
    )


def main() -> None:
    """run the Flask development server."""
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )


if __name__ == "__main__":
    main()
