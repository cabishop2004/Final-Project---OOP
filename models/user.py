"""domain model for an application user."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class User:
    """represent one user of the trade alert application."""

    user_id: int
    name: str
    email: str = ""
    phone: str = ""
