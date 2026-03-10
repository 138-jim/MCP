"""Tests for MCP color node tools."""

import pytest
from unittest.mock import patch
from pathlib import Path

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
    from resolve_mcp.tools.color_node_tools import register_color_node_tools

    mcp = FastMCP("test")
    register_color_node_tools(mcp, state)
    funcs = {}
    for tool in mcp._tool_manager.list_tools():
        funcs[tool.name] = mcp._tool_manager.get_tool(tool.name).fn
    return funcs


# --- CDL ---


def test_get_cdl(tools):
    result = tools["resolve_get_cdl"](
        track_type="video", track_index=1, item_index=0
    )
    assert "CDL for Shot_001" in result
    assert "slope" in result


def test_get_cdl_item_not_found(tools):
    result = tools["resolve_get_cdl"](
        track_type="video", track_index=1, item_index=99
    )
    assert "Item not found" in result


def test_set_cdl(tools):
    result = tools["resolve_set_cdl"](
        track_type="video", track_index=1, item_index=0,
        slope="1.1 1.0 1.0", saturation="1.2"
    )
    assert "Set CDL on Shot_001" in result


def test_set_cdl_includes_node_index(tools, state):
    """SetCDL dict must include NodeIndex as a string."""
    tools["resolve_set_cdl"](
        track_type="video", track_index=1, item_index=0,
        slope="1.0 1.0 1.0", node_index=2
    )
    tl = state._session.get_project_manager().get_current_project().get_current_timeline()
    item = tl.get_item_list_in_track("video", 1)[0]
    cdl_arg = item._obj.SetCDL.call_args[0][0]
    assert cdl_arg["NodeIndex"] == "2"
    assert "Slope" in cdl_arg


def test_set_cdl_no_values(tools):
    result = tools["resolve_set_cdl"](
        track_type="video", track_index=1, item_index=0
    )
    assert "No CDL values provided" in result


# --- Node label ---


def test_get_node_label(tools):
    result = tools["resolve_get_node_label"](
        track_type="video", track_index=1, item_index=0, node_index=1
    )
    assert "Node 1 label:" in result
    assert "Corrector 1" in result


def test_get_node_label_item_not_found(tools):
    result = tools["resolve_get_node_label"](
        track_type="video", track_index=1, item_index=99, node_index=1
    )
    assert "Item not found" in result


# --- Tools in node ---


def test_get_tools_in_node(tools):
    result = tools["resolve_get_tools_in_node"](
        track_type="video", track_index=1, item_index=0, node_index=1
    )
    assert "tools in node 1" in result
    assert "ColorCorrector" in result


# --- Node enabled ---


def test_set_node_enabled(tools):
    result = tools["resolve_set_node_enabled"](
        track_type="video", track_index=1, item_index=0,
        node_index=1, enabled=False
    )
    assert "Node 1 disabled" in result


def test_set_node_enabled_true(tools):
    result = tools["resolve_set_node_enabled"](
        track_type="video", track_index=1, item_index=0,
        node_index=1, enabled=True
    )
    assert "Node 1 enabled" in result


# --- Node cache mode ---


def test_get_node_cache_mode(tools):
    result = tools["resolve_get_node_cache_mode"](
        track_type="video", track_index=1, item_index=0, node_index=1
    )
    assert "Node 1 cache mode: 0 (None)" in result


def test_set_node_cache_mode(tools):
    result = tools["resolve_set_node_cache_mode"](
        track_type="video", track_index=1, item_index=0,
        node_index=1, mode=2
    )
    assert "Set node 1 cache mode to 2 (On)" in result


# --- ARRI CDL LUT ---


def test_apply_arri_cdl_lut(tools):
    result = tools["resolve_apply_arri_cdl_lut"](
        track_type="video", track_index=1, item_index=0
    )
    assert "Applied ARRI CDL+LUT to Shot_001" in result


def test_apply_arri_cdl_lut_item_not_found(tools):
    result = tools["resolve_apply_arri_cdl_lut"](
        track_type="video", track_index=1, item_index=99
    )
    assert "Item not found" in result


# --- Reset all node colours ---


def test_reset_all_node_colors(tools):
    result = tools["resolve_reset_all_node_colors"](
        track_type="video", track_index=1, item_index=0
    )
    assert "Reset all node colours on Shot_001" in result


# --- Refresh LUT list ---


def test_refresh_lut_list(tools):
    result = tools["resolve_refresh_lut_list"]()
    assert "LUT list refreshed" in result


# --- LUT discovery tools ---


def _fake_lut_dir(tmp_path):
    """Create a fake LUT directory structure for testing."""
    lut_root = tmp_path / "LUT"
    lut_root.mkdir()

    # Create subfolder structure
    arri = lut_root / "Arri"
    arri.mkdir()
    (arri / "LogC_to_Rec709.cube").write_text("# LUT")
    (arri / "LogC_to_ACEScct.cube").write_text("# LUT")

    bmd = lut_root / "Blackmagic Design"
    bmd.mkdir()
    (bmd / "BMDFilm_to_Rec709.cube").write_text("# LUT")

    # A LUT in the root
    (lut_root / "Custom_Grade.cube").write_text("# LUT")

    return lut_root


@patch("resolve_mcp.tools.color_node_tools._get_lut_dirs")
def test_list_lut_folders(mock_dirs, tools, tmp_path):
    lut_root = _fake_lut_dir(tmp_path)
    mock_dirs.return_value = [lut_root]

    result = tools["resolve_list_lut_folders"]()
    assert "LUT root folders" in result
    assert "Arri" in result
    assert "Blackmagic Design" in result
    assert "Custom_Grade.cube" in result


@patch("resolve_mcp.tools.color_node_tools._get_lut_dirs")
def test_list_lut_folders_subfolder(mock_dirs, tools, tmp_path):
    lut_root = _fake_lut_dir(tmp_path)
    mock_dirs.return_value = [lut_root]

    result = tools["resolve_list_lut_folders"](subfolder="Arri")
    assert "Contents of LUT folder 'Arri'" in result
    assert "LogC_to_Rec709.cube" in result


@patch("resolve_mcp.tools.color_node_tools._get_lut_dirs")
def test_list_lut_folders_no_dirs(mock_dirs, tools):
    mock_dirs.return_value = []

    result = tools["resolve_list_lut_folders"]()
    assert "No LUT directories found" in result


@patch("resolve_mcp.tools.color_node_tools._get_lut_dirs")
def test_search_luts(mock_dirs, tools, tmp_path):
    lut_root = _fake_lut_dir(tmp_path)
    mock_dirs.return_value = [lut_root]

    result = tools["resolve_search_luts"](search="LogC")
    assert "Found 2 LUT(s) matching 'LogC'" in result
    assert "LogC_to_Rec709.cube" in result
    assert "LogC_to_ACEScct.cube" in result


@patch("resolve_mcp.tools.color_node_tools._get_lut_dirs")
def test_search_luts_no_results(mock_dirs, tools, tmp_path):
    lut_root = _fake_lut_dir(tmp_path)
    mock_dirs.return_value = [lut_root]

    result = tools["resolve_search_luts"](search="nonexistent_lut_xyz")
    assert "No LUTs found matching" in result


@patch("resolve_mcp.tools.color_node_tools._get_lut_dirs")
def test_search_luts_subfolder(mock_dirs, tools, tmp_path):
    lut_root = _fake_lut_dir(tmp_path)
    mock_dirs.return_value = [lut_root]

    result = tools["resolve_search_luts"](search="BMD", subfolder="Blackmagic Design")
    assert "Found 1 LUT(s)" in result
    assert "BMDFilm_to_Rec709.cube" in result


@patch("resolve_mcp.tools.color_node_tools._find_luts")
def test_apply_lut_by_name_single_match(mock_find, tools):
    mock_find.return_value = [
        ("Arri/LogC_to_Rec709.cube", "/fake/LUT/Arri/LogC_to_Rec709.cube")
    ]

    result = tools["resolve_apply_lut_by_name"](
        track_type="video", track_index=1, item_index=0,
        node_index=1, search="LogC_to_Rec709"
    )
    assert "Applied LUT 'Arri/LogC_to_Rec709.cube'" in result
    assert "node 1" in result


@patch("resolve_mcp.tools.color_node_tools._find_luts")
def test_apply_lut_by_name_no_match(mock_find, tools):
    mock_find.return_value = []

    result = tools["resolve_apply_lut_by_name"](
        track_type="video", track_index=1, item_index=0,
        node_index=1, search="nonexistent"
    )
    assert "No LUT found matching 'nonexistent'" in result


@patch("resolve_mcp.tools.color_node_tools._find_luts")
def test_apply_lut_by_name_multiple_matches(mock_find, tools):
    mock_find.return_value = [
        ("Arri/LogC_to_Rec709.cube", "/fake/LUT/Arri/LogC_to_Rec709.cube"),
        ("Arri/LogC_to_ACEScct.cube", "/fake/LUT/Arri/LogC_to_ACEScct.cube"),
    ]

    result = tools["resolve_apply_lut_by_name"](
        track_type="video", track_index=1, item_index=0,
        node_index=1, search="LogC"
    )
    assert "Multiple LUTs match" in result
    assert "LogC_to_Rec709" in result
    assert "LogC_to_ACEScct" in result


@patch("resolve_mcp.tools.color_node_tools._find_luts")
def test_apply_lut_by_name_exact_stem(mock_find, tools):
    """When multiple matches exist but one is an exact stem match, use it."""
    mock_find.return_value = [
        ("Arri/LogC_to_Rec709.cube", "/fake/LUT/Arri/LogC_to_Rec709.cube"),
        ("Custom/LogC_to_Rec709_v2.cube", "/fake/LUT/Custom/LogC_to_Rec709_v2.cube"),
    ]

    result = tools["resolve_apply_lut_by_name"](
        track_type="video", track_index=1, item_index=0,
        node_index=1, search="LogC_to_Rec709"
    )
    assert "Applied LUT" in result


def test_apply_lut_by_name_item_not_found(tools):
    result = tools["resolve_apply_lut_by_name"](
        track_type="video", track_index=1, item_index=99,
        node_index=1, search="anything"
    )
    assert "Item not found" in result
