"""Tests for MCP color grade tools."""

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
    from resolve_mcp.tools.color_grade_tools import register_color_grade_tools

    mcp = FastMCP("test")
    register_color_grade_tools(mcp, state)
    funcs = {}
    for tool in mcp._tool_manager.list_tools():
        funcs[tool.name] = mcp._tool_manager.get_tool(tool.name).fn
    return funcs


def test_copy_grades(tools):
    result = tools["resolve_copy_grades"](
        track_type="video", track_index=1, source_item_index=0,
        target_item_indices="1"
    )
    assert "Copied grade from Shot_001 to 1 clip(s)" in result


def test_copy_grades_multiple_targets(tools):
    result = tools["resolve_copy_grades"](
        track_type="video", track_index=1, source_item_index=0,
        target_item_indices="0,1"
    )
    assert "Copied grade from Shot_001 to 2 clip(s)" in result


def test_copy_grades_source_not_found(tools):
    result = tools["resolve_copy_grades"](
        track_type="video", track_index=1, source_item_index=99,
        target_item_indices="0"
    )
    assert "Source item not found" in result


def test_copy_grades_target_not_found(tools):
    result = tools["resolve_copy_grades"](
        track_type="video", track_index=1, source_item_index=0,
        target_item_indices="99"
    )
    assert "Target item at index 99 not found" in result


def test_export_lut(tools):
    result = tools["resolve_export_lut"](
        track_type="video", track_index=1, item_index=0,
        export_type="LUT_33PTCUBE", path="/tmp/grade.cube"
    )
    assert "Exported LUT to /tmp/grade.cube" in result


def test_export_lut_invalid_type(tools, state):
    # MagicMock auto-creates attributes, so patch get_export_constant
    # to return None for unknown types (matching real Resolve behaviour)
    state._session.get_export_constant = lambda name: None
    result = tools["resolve_export_lut"](
        track_type="video", track_index=1, item_index=0,
        export_type="INVALID", path="/tmp/grade.cube"
    )
    assert "Unknown export type" in result


def test_export_lut_item_not_found(tools):
    result = tools["resolve_export_lut"](
        track_type="video", track_index=1, item_index=99,
        export_type="LUT_33PTCUBE", path="/tmp/grade.cube"
    )
    assert "Item not found" in result


def test_get_color_output_cache(tools):
    result = tools["resolve_get_color_output_cache"](
        track_type="video", track_index=1, item_index=0
    )
    assert "Color output cache on Shot_001: enabled" in result


def test_set_color_output_cache(tools):
    result = tools["resolve_set_color_output_cache"](
        track_type="video", track_index=1, item_index=0,
        enabled=True
    )
    assert "Color output cache enabled on Shot_001" in result


def test_set_color_output_cache_disable(tools):
    result = tools["resolve_set_color_output_cache"](
        track_type="video", track_index=1, item_index=0,
        enabled=False
    )
    assert "Color output cache disabled on Shot_001" in result


def test_set_color_output_cache_item_not_found(tools):
    result = tools["resolve_set_color_output_cache"](
        track_type="video", track_index=1, item_index=99,
        enabled=True
    )
    assert "Item not found" in result
