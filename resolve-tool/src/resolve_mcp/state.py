"""Session singleton and connection management for the MCP server."""

from __future__ import annotations

import logging

from resolve_lib.connect import connect
from resolve_lib.exceptions import ResolveConnectionError
from resolve_lib.session import Session

logger = logging.getLogger("resolve_mcp")


class ServerState:
    """Holds the lazy Session singleton for the MCP server."""

    def __init__(self):
        self._session: Session | None = None

    @property
    def session(self) -> Session:
        """Return the current Session, connecting if needed.

        If the cached session is stale (Resolve restarted / disconnected),
        a lightweight health check detects it and reconnects automatically.
        """
        if self._session is not None:
            try:
                self._session.get_current_page()  # lightweight health check
            except Exception:
                logger.warning("Connection lost, reconnecting to Resolve...")
                self._session = None
        if self._session is None:
            self.connect()
        return self._session  # type: ignore[return-value]

    def connect(self) -> Session:
        """Establish connection to DaVinci Resolve."""
        try:
            raw = connect()
        except ResolveConnectionError:
            raise
        self._session = Session(raw)
        try:
            logger.info("Connected to DaVinci Resolve %s", self._session.get_version())
        except Exception:
            logger.info("Connected to DaVinci Resolve")
        return self._session

    def disconnect(self) -> None:
        """Clear the session reference."""
        self._session = None

    @property
    def is_connected(self) -> bool:
        """Check if we have an active session."""
        return self._session is not None
