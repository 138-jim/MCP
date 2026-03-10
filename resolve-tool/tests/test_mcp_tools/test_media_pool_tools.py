"""Tests for MCP media pool tools — resolution mismatch warnings."""

import pytest

from tests.mocks.mock_resolve import create_mock_resolve
from resolve_lib.session import Session
from resolve_mcp.state import ServerState


@pytest.fixture
def state():
    s = ServerState()
    s._session = Session(create_mock_resolve())
    return s


@pytest.fixture
def tools(state):
    from mcp.server.fastmcp import FastMCP
    from resolve_mcp.tools.media_pool_tools import register_media_pool_tools

    mcp = FastMCP("test")
    register_media_pool_tools(mcp, state)
    funcs = {}
    for tool in mcp._tool_manager.list_tools():
        funcs[tool.name] = mcp._tool_manager.get_tool(tool.name).fn
    return funcs


# --- create_timeline_from_clips ---


def test_create_timeline_no_resolution_warning(tools):
    """No warning when clip resolution matches timeline (both 1920x1080)."""
    result = tools["resolve_create_timeline_from_clips"](
        name="TL", clip_names=["Clip_A.mov"]
    )
    assert "Created timeline" in result
    assert "WARNING" not in result


def test_create_timeline_resolution_warning(tools, state):
    """Warning when clip resolution differs from timeline."""
    # Change clip resolution to 4K while timeline stays 1920x1080
    pool = state._session.get_project_manager().get_current_project().get_media_pool()
    folder = pool.get_current_folder()
    clip = folder.get_clips()[0]
    clip._obj.GetClipProperty.side_effect = (
        lambda key=None: {"Format": "mov", "FPS": "24", "Resolution": "3840x2160"}.get(key, "")
        if key else {"Format": "mov", "FPS": "24", "Resolution": "3840x2160"}
    )
    result = tools["resolve_create_timeline_from_clips"](
        name="TL", clip_names=["Clip_A.mov"]
    )
    assert "WARNING" in result
    assert "resolution" in result.lower()
    assert "3840x2160" in result
    assert "1920x1080" in result
