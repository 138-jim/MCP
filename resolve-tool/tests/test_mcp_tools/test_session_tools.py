"""Tests for MCP session tools."""

import pytest
from unittest.mock import patch, MagicMock

from tests.mocks.mock_resolve import create_mock_resolve
from resolve_lib.session import Session
from resolve_mcp.state import ServerState


@pytest.fixture
def state():
    """Create a ServerState with a mock session."""
    s = ServerState()
    mock_resolve = create_mock_resolve()
    s._session = Session(mock_resolve)
    return s


def test_state_is_connected(state):
    assert state.is_connected is True


def test_state_session(state):
    assert state.session.get_version() == "19.0.0"


def test_state_disconnect(state):
    state.disconnect()
    assert state.is_connected is False


def test_state_lazy_connect():
    """Accessing session on a fresh state should attempt to connect."""
    s = ServerState()
    assert s.is_connected is False
    # Patch connect to raise, simulating no Resolve running
    with patch("resolve_mcp.state.connect", side_effect=Exception("no resolve")):
        with pytest.raises(Exception):
            _ = s.session
