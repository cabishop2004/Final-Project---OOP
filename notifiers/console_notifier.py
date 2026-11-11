"""console notification implementation used during development."""

from __future__ import annotations

from models.user import User
from notifiers.notifier import Notifier


class ConsoleNotifier(Notifier):
    """print alert messages to the application console."""

    def send(
        self,
        user: User,
        message: str,
    ) -> bool:
        """print a notification and report success."""
        print(
            f"[alert for {user.name}] {message}"
        )

        return True
