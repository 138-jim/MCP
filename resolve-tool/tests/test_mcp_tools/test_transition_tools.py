"""Tests for MCP transition tools."""

import pytest

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


@pytest.fixture
def tools(state):
    """Register transition tools and return the tool functions via a helper dict."""
    from mcp.server.fastmcp import FastMCP
    from resolve_mcp.tools.transition_tools import register_transition_tools

    mcp = FastMCP("test")
    register_transition_tools(mcp, state)

    # Extract registered tool functions by name
    funcs = {}
    for tool in mcp._tool_manager.list_tools():
        funcs[tool.name] = mcp._tool_manager.get_tool(tool.name).fn
    return funcs


def test_import_transition_preset_success(tools, state):
    result = tools["resolve_import_transition_preset"](
        track_type="video", track_index=1, item_index=0,
        preset_path="/tmp/custom_transition.comp",
    )
    assert "Imported Fusion comp" in result
    assert "Shot_001" in result

    # Verify ImportFusionComp was called with the custom path
    tl = state.session.get_project_manager().get_current_project().get_current_timeline()
    item = tl.get_item_list_in_track("video", 1)[0]
    item._obj.ImportFusionComp.assert_called_with("/tmp/custom_transition.comp")


def test_import_transition_preset_item_not_found(tools):
    result = tools["resolve_import_transition_preset"](
        track_type="video", track_index=1, item_index=99,
        preset_path="/tmp/custom_transition.comp",
    )
    assert "Item not found" in result
