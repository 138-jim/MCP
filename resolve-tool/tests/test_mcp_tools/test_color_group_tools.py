"""Tests for MCP color group tools."""

import pytest
from unittest.mock import MagicMock

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
    from resolve_mcp.tools.color_group_tools import register_color_group_tools

    mcp = FastMCP("test")
    register_color_group_tools(mcp, state)
    funcs = {}
    for tool in mcp._tool_manager.list_tools():
        funcs[tool.name] = mcp._tool_manager.get_tool(tool.name).fn
    return funcs


# --- Delete ---


def test_delete_color_group(tools):
    result = tools["resolve_delete_color_group"](group_name="Group A")
    assert "Deleted color group: Group A" in result


def test_delete_color_group_not_found(tools):
    result = tools["resolve_delete_color_group"](group_name="Nonexistent")
    assert "not found" in result


# --- Rename ---


def test_set_color_group_name(tools):
    result = tools["resolve_set_color_group_name"](
        current_name="Group A", new_name="Group B"
    )
    assert "Renamed color group 'Group A' to 'Group B'" in result


def test_set_color_group_name_not_found(tools):
    result = tools["resolve_set_color_group_name"](
        current_name="Nonexistent", new_name="New"
    )
    assert "not found" in result


# --- Clips in group ---


def test_get_clips_in_color_group(tools):
    result = tools["resolve_get_clips_in_color_group"](group_name="Group A")
    assert "clips in 'Group A'" in result


def test_get_clips_in_color_group_not_found(tools):
    result = tools["resolve_get_clips_in_color_group"](group_name="Nonexistent")
    assert "not found" in result


# --- Pre/Post node graphs ---


def test_get_color_group_pre_node_graph(tools):
    result = tools["resolve_get_color_group_pre_node_graph"](group_name="Group A")
    assert "Pre-clip node graph for 'Group A'" in result
    assert "3 node(s)" in result


def test_get_color_group_post_node_graph(tools):
    result = tools["resolve_get_color_group_post_node_graph"](group_name="Group A")
    assert "Post-clip node graph for 'Group A'" in result
    assert "3 node(s)" in result


def test_get_color_group_pre_node_graph_not_found(tools):
    result = tools["resolve_get_color_group_pre_node_graph"](
        group_name="Nonexistent"
    )
    assert "not found" in result


# --- Item color group ---


def test_get_item_color_group_none(tools):
    result = tools["resolve_get_item_color_group"](
        track_type="video", track_index=1, item_index=0
    )
    assert "not assigned to any color group" in result


def test_get_item_color_group_assigned(tools, state):
    # Configure mock to return a color group
    tl = state.session.get_project_manager().get_current_project().get_current_timeline()
    item = tl.get_item_list_in_track("video", 1)[0]
    cg_mock = MagicMock(name="ColorGroup")
    cg_mock.GetName.return_value = "Group A"
    item._obj.GetColorGroup.return_value = cg_mock

    result = tools["resolve_get_item_color_group"](
        track_type="video", track_index=1, item_index=0
    )
    assert "is in color group: Group A" in result


def test_get_item_color_group_not_found(tools):
    result = tools["resolve_get_item_color_group"](
        track_type="video", track_index=1, item_index=99
    )
    assert "Item not found" in result


# --- Assign / Remove ---


def test_assign_to_color_group(tools):
    result = tools["resolve_assign_to_color_group"](
        track_type="video", track_index=1, item_index=0,
        group_name="Group A"
    )
    assert "Assigned Shot_001 to color group 'Group A'" in result


def test_assign_to_color_group_not_found(tools):
    result = tools["resolve_assign_to_color_group"](
        track_type="video", track_index=1, item_index=0,
        group_name="Nonexistent"
    )
    assert "not found" in result


def test_remove_from_color_group(tools):
    result = tools["resolve_remove_from_color_group"](
        track_type="video", track_index=1, item_index=0
    )
    assert "Removed Shot_001 from its color group" in result


def test_remove_from_color_group_item_not_found(tools):
    result = tools["resolve_remove_from_color_group"](
        track_type="video", track_index=1, item_index=99
    )
    assert "Item not found" in result
