"""Tests for MCP transition tools."""

import pytest
from unittest.mock import MagicMock

from tests.mocks.mock_resolve import create_mock_resolve
from resolve_lib.session import Session
from resolve_mcp.state import ServerState
from resolve_mcp.tools.transition_tools import PRESETS_DIR


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


def test_list_available_transitions(tools):
    result = tools["resolve_list_available_transitions"]()
    assert "transition presets" in result
    assert "fade_in" in result
    assert "fade_out" in result
    assert "dip_to_black" in result
    assert "dip_to_white" in result
    # cross_dissolve is no longer a preset file — it's generated from a template
    assert "cross_dissolve" not in result


def test_presets_directory_exists():
    assert PRESETS_DIR.is_dir()
    comp_files = list(PRESETS_DIR.glob("*.comp"))
    assert len(comp_files) == 4


def test_apply_transition_success(tools, state):
    result = tools["resolve_apply_transition"](
        track_type="video", track_index=1, item_index=0,
        transition_name="fade_in",
    )
    assert "Applied 'fade_in' transition to Shot_001" in result

    # Verify ImportFusionComp was called with the right path
    tl = state.session.get_project_manager().get_current_project().get_current_timeline()
    item = tl.get_item_list_in_track("video", 1)[0]
    item._obj.ImportFusionComp.assert_called_once()
    call_path = item._obj.ImportFusionComp.call_args[0][0]
    assert "fade_in.comp" in call_path


def test_apply_transition_invalid_name(tools):
    result = tools["resolve_apply_transition"](
        track_type="video", track_index=1, item_index=0,
        transition_name="nonexistent",
    )
    assert "not found" in result
    assert "Available:" in result


def test_apply_transition_item_not_found(tools):
    result = tools["resolve_apply_transition"](
        track_type="video", track_index=1, item_index=99,
        transition_name="fade_in",
    )
    assert "Item not found" in result


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


# --- Cross dissolve / blur transition helpers ---


def _make_adjacent_clips_state():
    """Create a state with two adjacent clips suitable for transition tests.

    Returns (state, tl, item_a, item_b_v2) — no Fusion clip is created.
    """
    mock_resolve = create_mock_resolve()
    tl = mock_resolve.GetProjectManager().GetCurrentProject().GetCurrentTimeline()

    # Set up two adjacent clips: A (0-120) and B (120-240)
    item_a = MagicMock(name="TimelineItem(Shot_001)")
    item_a.GetName.return_value = "Shot_001"
    item_a.GetStart.return_value = 0
    item_a.GetEnd.return_value = 120
    item_a.GetLeftOffset.return_value = 0
    item_a.GetRightOffset.return_value = 100
    item_a.GetSourceStartFrame.return_value = 0
    item_a.GetSourceEndFrame.return_value = 120
    item_a.ImportFusionComp.return_value = MagicMock()
    item_a.GetFusionCompCount.return_value = 1

    item_b = MagicMock(name="TimelineItem(Shot_002)")
    item_b.GetName.return_value = "Shot_002"
    item_b.GetStart.return_value = 120
    item_b.GetEnd.return_value = 240
    item_b.GetLeftOffset.return_value = 50
    item_b.GetRightOffset.return_value = 100
    item_b.GetSourceStartFrame.return_value = 50
    item_b.GetSourceEndFrame.return_value = 170

    mpi_b = MagicMock(name="MediaPoolItem(Shot_002)")
    item_b.GetMediaPoolItem.return_value = mpi_b

    # V2 clip B after move (starts 30 frames earlier)
    item_b_v2 = MagicMock(name="TimelineItem(Shot_002_V2)")
    item_b_v2.GetName.return_value = "Shot_002"
    item_b_v2.GetStart.return_value = 90  # 120 - 30 dissolve
    item_b_v2.GetEnd.return_value = 240
    item_b_v2.ImportFusionComp.return_value = MagicMock()
    item_b_v2.GetFusionCompCount.return_value = 1

    # Track 1 returns both initially, then just A after delete;
    # Track 2 returns the moved clip B.
    call_count = {"n": 0}

    def get_items_by_track(track_type, track_index):
        call_count["n"] += 1
        if call_count["n"] <= 1:
            # First call: initial state with both clips on V1
            return [item_a, item_b]
        if track_index == 1:
            return [item_a]
        if track_index == 2:
            return [item_b_v2]
        return []

    tl.GetItemListInTrack.side_effect = get_items_by_track
    tl.GetTrackCount.return_value = 1
    tl.AddTrack.return_value = True
    tl.DeleteClips.return_value = True

    pool = mock_resolve.GetProjectManager().GetCurrentProject().GetMediaPool()
    pool.AppendToTimeline.return_value = [mpi_b]

    s = ServerState()
    s._session = Session(mock_resolve)
    return s, tl, item_a, item_b_v2


def _make_transition_tools(state):
    from mcp.server.fastmcp import FastMCP
    from resolve_mcp.tools.transition_tools import register_transition_tools

    mcp = FastMCP("test")
    register_transition_tools(mcp, state)
    funcs = {}
    for tool in mcp._tool_manager.list_tools():
        funcs[tool.name] = mcp._tool_manager.get_tool(tool.name).fn
    return funcs


def test_cross_dissolve_success():
    state, tl, item_a, item_b_v2 = _make_adjacent_clips_state()
    tools = _make_transition_tools(state)

    result = tools["resolve_apply_cross_dissolve"](
        track_index=1, item_index_a=0, item_index_b=1,
        dissolve_duration=30,
    )
    assert "cross dissolve" in result.lower()
    assert "Shot_001" in result
    assert "Shot_002" in result

    # No Fusion clip should be created
    tl.CreateFusionClip.assert_not_called()

    # ImportFusionComp should be called on clip B only
    item_b_v2.ImportFusionComp.assert_called_once()
    call_path = item_b_v2.ImportFusionComp.call_args[0][0]
    assert call_path.endswith(".comp")

    # Clip A should NOT have ImportFusionComp called
    item_a.ImportFusionComp.assert_not_called()


def test_cross_dissolve_not_adjacent():
    state, tl, _, _ = _make_adjacent_clips_state()
    # Override side_effect with non-adjacent clips
    items = tl.GetItemListInTrack.side_effect("video", 1)  # get first-call items
    items[1].GetStart.return_value = 200  # gap between 120 and 200
    tl.GetItemListInTrack.side_effect = None
    tl.GetItemListInTrack.return_value = items
    tools = _make_transition_tools(state)

    result = tools["resolve_apply_cross_dissolve"](
        track_index=1, item_index_a=0, item_index_b=1,
    )
    assert "not adjacent" in result.lower()


def test_cross_dissolve_insufficient_left_offset():
    state, tl, _, _ = _make_adjacent_clips_state()
    # Override side_effect with low left_offset
    items = tl.GetItemListInTrack.side_effect("video", 1)
    items[1].GetLeftOffset.return_value = 10
    tl.GetItemListInTrack.side_effect = None
    tl.GetItemListInTrack.return_value = items
    tools = _make_transition_tools(state)

    result = tools["resolve_apply_cross_dissolve"](
        track_index=1, item_index_a=0, item_index_b=1,
        dissolve_duration=30,
    )
    assert "not have enough source material" in result.lower()


def test_cross_dissolve_clip_b_without_media_pool_item():
    state, tl, _, _ = _make_adjacent_clips_state()
    items = tl.GetItemListInTrack.side_effect("video", 1)
    items[1].GetMediaPoolItem.return_value = None
    tl.GetItemListInTrack.side_effect = None
    tl.GetItemListInTrack.return_value = items
    tools = _make_transition_tools(state)

    result = tools["resolve_apply_cross_dissolve"](
        track_index=1, item_index_a=0, item_index_b=1,
        dissolve_duration=30,
    )
    assert "not backed by a media pool item" in result.lower()
    tl.DeleteClips.assert_not_called()


# --- Blur transition tests ---


def test_blur_transition_success():
    state, tl, item_a, item_b_v2 = _make_adjacent_clips_state()
    tools = _make_transition_tools(state)

    result = tools["resolve_apply_blur_transition"](
        track_index=1, item_index_a=0, item_index_b=1,
        dissolve_duration=30, blur_size=15.0,
    )
    assert "blur transition" in result.lower()
    assert "Shot_001" in result
    assert "Shot_002" in result

    # No Fusion clip should be created
    tl.CreateFusionClip.assert_not_called()

    # ImportFusionComp should be called on BOTH clips
    item_a.ImportFusionComp.assert_called_once()
    item_b_v2.ImportFusionComp.assert_called_once()

    # Both should receive .comp files
    call_path_a = item_a.ImportFusionComp.call_args[0][0]
    call_path_b = item_b_v2.ImportFusionComp.call_args[0][0]
    assert call_path_a.endswith(".comp")
    assert call_path_b.endswith(".comp")


def test_blur_transition_not_adjacent():
    state, tl, _, _ = _make_adjacent_clips_state()
    items = tl.GetItemListInTrack.side_effect("video", 1)
    items[1].GetStart.return_value = 200
    tl.GetItemListInTrack.side_effect = None
    tl.GetItemListInTrack.return_value = items
    tools = _make_transition_tools(state)

    result = tools["resolve_apply_blur_transition"](
        track_index=1, item_index_a=0, item_index_b=1,
    )
    assert "not adjacent" in result.lower()


def test_blur_transition_insufficient_left_offset():
    state, tl, _, _ = _make_adjacent_clips_state()
    items = tl.GetItemListInTrack.side_effect("video", 1)
    items[1].GetLeftOffset.return_value = 10
    tl.GetItemListInTrack.side_effect = None
    tl.GetItemListInTrack.return_value = items
    tools = _make_transition_tools(state)

    result = tools["resolve_apply_blur_transition"](
        track_index=1, item_index_a=0, item_index_b=1,
        dissolve_duration=30,
    )
    assert "not have enough source material" in result.lower()
