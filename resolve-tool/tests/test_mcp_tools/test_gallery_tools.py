"""Tests for MCP gallery and stills tools."""

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
    from resolve_mcp.tools.gallery_tools import register_gallery_tools

    mcp = FastMCP("test")
    register_gallery_tools(mcp, state)
    funcs = {}
    for tool in mcp._tool_manager.list_tools():
        funcs[tool.name] = mcp._tool_manager.get_tool(tool.name).fn
    return funcs


# --- Stills capture ---


def test_grab_still(tools):
    result = tools["resolve_grab_still"]()
    assert "Still grabbed from current frame" in result


def test_grab_all_stills(tools):
    result = tools["resolve_grab_all_stills"](still_frame_source=1)
    assert "still(s) from timeline" in result


# --- Album management ---


def test_get_current_still_album(tools):
    result = tools["resolve_get_current_still_album"]()
    assert "Current still album: Album 1" in result


def test_set_current_still_album(tools):
    result = tools["resolve_set_current_still_album"](album_index=1)
    assert "Set current still album to: Album 1" in result


def test_set_current_still_album_out_of_range(tools):
    result = tools["resolve_set_current_still_album"](album_index=99)
    assert "out of range" in result


def test_list_powergrade_albums(tools):
    result = tools["resolve_list_powergrade_albums"]()
    assert "PowerGrade albums" in result


def test_create_still_album(tools):
    result = tools["resolve_create_still_album"]()
    assert "Created still album" in result


def test_create_powergrade_album(tools):
    result = tools["resolve_create_powergrade_album"]()
    assert "Created PowerGrade album" in result


def test_set_album_name(tools):
    result = tools["resolve_set_album_name"](album_index=1, name="My Album")
    assert "Renamed album 1 to: My Album" in result


def test_set_album_name_out_of_range(tools):
    result = tools["resolve_set_album_name"](album_index=99, name="X")
    assert "out of range" in result


# --- Stills within albums ---


def test_list_stills(tools):
    result = tools["resolve_list_stills"]()
    assert "stills" in result
    assert "Still Label" in result


def test_get_still_label(tools):
    result = tools["resolve_get_still_label"](still_index=1)
    assert "Still 1 label: Still Label" in result


def test_get_still_label_out_of_range(tools):
    result = tools["resolve_get_still_label"](still_index=99)
    assert "out of range" in result


def test_set_still_label(tools):
    result = tools["resolve_set_still_label"](still_index=1, label="Hero Shot")
    assert "Set still 1 label to: Hero Shot" in result


def test_set_still_label_out_of_range(tools):
    result = tools["resolve_set_still_label"](still_index=99, label="X")
    assert "out of range" in result


def test_import_stills(tools):
    result = tools["resolve_import_stills"](
        paths="/tmp/still1.dpx, /tmp/still2.dpx"
    )
    assert "Imported 2 still(s)" in result


def test_export_stills(tools):
    result = tools["resolve_export_stills"](
        still_indices="1,2", path="/tmp/export",
        file_prefix="grade_", format="jpg"
    )
    assert "Exported 2 still(s) to /tmp/export" in result


def test_export_stills_out_of_range(tools):
    result = tools["resolve_export_stills"](
        still_indices="99", path="/tmp/export"
    )
    assert "out of range" in result


def test_delete_stills(tools):
    result = tools["resolve_delete_stills"](still_indices="1")
    assert "Deleted 1 still(s)" in result


def test_delete_stills_out_of_range(tools):
    result = tools["resolve_delete_stills"](still_indices="99")
    assert "out of range" in result
