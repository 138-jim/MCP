"""Tests for MCP color version tools."""

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
    from resolve_mcp.tools.color_version_tools import register_color_version_tools

    mcp = FastMCP("test")
    register_color_version_tools(mcp, state)
    funcs = {}
    for tool in mcp._tool_manager.list_tools():
        funcs[tool.name] = mcp._tool_manager.get_tool(tool.name).fn
    return funcs


def test_add_color_version(tools, state):
    result = tools["resolve_add_color_version"](
        track_type="video", track_index=1, item_index=0,
        name="Look A", version_type="local"
    )
    assert "Added local color version 'Look A'" in result
    assert "Shot_001" in result
    # Verify the raw API received int 0, not string "local"
    tl = state._session.get_project_manager().get_current_project().get_current_timeline()
    item = tl.get_item_list_in_track("video", 1)[0]
    item._obj.AddVersion.assert_called_with("Look A", 0)


def test_add_color_version_item_not_found(tools):
    result = tools["resolve_add_color_version"](
        track_type="video", track_index=1, item_index=99,
        name="Look A"
    )
    assert "Item not found" in result


def test_get_current_color_version(tools):
    result = tools["resolve_get_current_color_version"](
        track_type="video", track_index=1, item_index=0
    )
    assert "Current local version of Shot_001" in result
    assert "versionName" in result


def test_get_current_color_version_reports_actual_type(tools):
    result = tools["resolve_get_current_color_version"](
        track_type="video", track_index=1, item_index=0,
        version_type="remote"
    )
    assert "Current local version of Shot_001 (requested remote)" in result


def test_get_current_color_version_remote_active(tools, state):
    tl = state._session.get_project_manager().get_current_project().get_current_timeline()
    item = tl.get_item_list_in_track("video", 1)[0]
    item._obj.GetCurrentVersion.return_value = {
        "versionName": "Remote Grade",
        "versionType": 1,
    }

    result = tools["resolve_get_current_color_version"](
        track_type="video", track_index=1, item_index=0,
        version_type="remote"
    )
    assert "Current remote version of Shot_001" in result


def test_delete_color_version(tools):
    result = tools["resolve_delete_color_version"](
        track_type="video", track_index=1, item_index=0,
        name="Version 1", version_type="local"
    )
    assert "Deleted local version 'Version 1'" in result
    assert "Shot_001" in result


def test_rename_color_version(tools):
    result = tools["resolve_rename_color_version"](
        track_type="video", track_index=1, item_index=0,
        old_name="Version 1", new_name="Final Grade",
        version_type="local"
    )
    assert "Renamed local version 'Version 1' to 'Final Grade'" in result


def test_rename_color_version_item_not_found(tools):
    result = tools["resolve_rename_color_version"](
        track_type="video", track_index=1, item_index=99,
        old_name="V1", new_name="V2"
    )
    assert "Item not found" in result
