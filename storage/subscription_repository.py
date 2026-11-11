"""SQLite persistence for trade alert subscriptions."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from models.subscription import Subscription
from models.trade import TradeType


class SubscriptionRepository:
    """persist and retrieve subscription objects using SQLite."""

    def __init__(
        self,
        database_path: str | Path,
    ) -> None:
        """initialize the repository and database table."""
        self.__database_path = Path(database_path)

        self.__database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.__initialize()

    @property
    def database_path(self) -> Path:
        """return the configured SQLite database path."""
        return self.__database_path

    def __connect(self) -> sqlite3.Connection:
        """create a SQLite connection."""
        connection = sqlite3.connect(
            self.__database_path
        )

        connection.row_factory = sqlite3.Row

        return connection

    def __initialize(self) -> None:
        """create the subscriptions table if needed."""
        with self.__connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    politician TEXT NOT NULL DEFAULT '',
                    ticker TEXT NOT NULL DEFAULT '',
                    trade_type TEXT,
                    channel TEXT NOT NULL DEFAULT 'web'
                )
                """
            )

    def add(
        self,
        subscription: Subscription,
    ) -> Subscription:
        """save a subscription and return it with its database ID."""
        trade_type = (
            subscription.trade_type.value
            if subscription.trade_type is not None
            else None
        )

        with self.__connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO subscriptions (
                    user_id,
                    politician,
                    ticker,
                    trade_type,
                    channel
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    subscription.user_id,
                    subscription.politician,
                    subscription.ticker,
                    trade_type,
                    subscription.channel,
                ),
            )

            new_id = cursor.lastrowid

        return Subscription(
            subscription_id=new_id,
            user_id=subscription.user_id,
            politician=subscription.politician,
            ticker=subscription.ticker,
            trade_type=subscription.trade_type,
            channel=subscription.channel,
        )

    def list_for_user(
        self,
        user_id: int,
    ) -> list[Subscription]:
        """return all subscriptions belonging to a user."""
        with self.__connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    user_id,
                    politician,
                    ticker,
                    trade_type,
                    channel
                FROM subscriptions
                WHERE user_id = ?
                ORDER BY id DESC
                """,
                (user_id,),
            ).fetchall()

        subscriptions: list[Subscription] = []

        for row in rows:
            trade_type_value = row["trade_type"]

            trade_type = (
                TradeType(trade_type_value)
                if trade_type_value
                else None
            )

            subscriptions.append(
                Subscription(
                    subscription_id=row["id"],
                    user_id=row["user_id"],
                    politician=row["politician"],
                    ticker=row["ticker"],
                    trade_type=trade_type,
                    channel=row["channel"],
                )
            )

        return subscriptions

    def delete(
        self,
        subscription_id: int,
        user_id: int,
    ) -> bool:
        """delete one subscription belonging to a user."""
        with self.__connect() as connection:
            cursor = connection.execute(
                """
                DELETE FROM subscriptions
                WHERE id = ?
                  AND user_id = ?
                """,
                (
                    subscription_id,
                    user_id,
                ),
            )

            return cursor.rowcount > 0
