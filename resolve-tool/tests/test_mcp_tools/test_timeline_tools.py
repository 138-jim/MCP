"""Tests for MCP timeline tools."""

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
    from resolve_mcp.tools.timeline_tools import register_timeline_tools

    mcp = FastMCP("test")
    register_timeline_tools(mcp, state)
    funcs = {}
    for tool in mcp._tool_manager.list_tools():
        funcs[tool.name] = mcp._tool_manager.get_tool(tool.name).fn
    return funcs


def test_export_timeline_preserves_zero_subtype_constant(state, tools):
    constants = {
        "TEXT_CSV": 11,
        "TEXT_TAB": 0,
    }
    state._session.get_export_constant = lambda name: constants.get(name)  # type: ignore[assignment]

    result = tools["resolve_export_timeline"](
        path="/tmp/out.csv",
        export_type="TEXT_CSV",
        export_subtype="TAB",
    )

    assert "Exported timeline to /tmp/out.csv" in result

    tl = state.session.get_project_manager().get_current_project().get_current_timeline()
    tl._obj.Export.assert_called_once_with("/tmp/out.csv", 11, 0)


def test_frame_to_timecode_handles_2997_drop_frame():
    from resolve_mcp.tools.timeline_tools import _frame_to_timecode

    # 17,982 frames is exactly ten minutes at 29.97 fps.
    assert _frame_to_timecode(17982, 29.97, drop_frame=True) == "00:10:00:00"


def test_add_text_overlay_uses_drop_frame_for_auto_timecode(state, tools):
    project = state.session.get_project_manager().get_current_project()
    project._obj.GetSetting.side_effect = (
        lambda key="": "29.97 DF" if key == "timelineFrameRate" else ""
    )

    tl = project.get_current_timeline()
    tl._obj.GetStartTimecode.return_value = "00:00:00:00"
    items = tl.get_item_list_in_track("video", 1)
    items[0]._obj.GetStart.return_value = 17982
    items[1]._obj.GetStart.return_value = 18082

    tools["resolve_add_text_overlay"](
        text="Drop-frame test",
        overlay_track=1,
    )

    tl._obj.SetCurrentTimecode.assert_any_call("00:10:00:00")


def test_add_text_overlay_offsets_auto_timecode_by_timeline_start(state, tools):
    project = state.session.get_project_manager().get_current_project()
    project._obj.GetSetting.side_effect = (
        lambda key="": "24" if key == "timelineFrameRate" else ""
    )

    tl = project.get_current_timeline()
    tl._obj.GetStartTimecode.return_value = "01:00:00:00"
    items = tl.get_item_list_in_track("video", 1)
    items[0]._obj.GetStart.return_value = 240
    items[1]._obj.GetStart.return_value = 340

    tools["resolve_add_text_overlay"](
        text="Start timecode test",
        overlay_track=1,
    )

    tl._obj.SetCurrentTimecode.assert_any_call("01:00:10:00")
