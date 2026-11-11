"""abstract notification interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from models.user import User


class Notifier(ABC):
    """define the interface for an alert notification channel."""

    @abstractmethod
    def send(
        self,
        user: User,
        message: str,
    ) -> bool:
        """send an alert message to a user."""
