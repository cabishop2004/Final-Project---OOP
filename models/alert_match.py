"""domain model describing a matched trade alert."""

from __future__ import annotations

from dataclasses import dataclass

from models.subscription import Subscription
from models.trade import Trade


@dataclass(frozen=True, slots=True)
class AlertMatch:
    """associate a matching subscription with a congressional trade."""

    subscription: Subscription
    trade: Trade
    message: str
