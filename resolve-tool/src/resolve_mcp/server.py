"""FastMCP server instance and tool registration."""

from __future__ import annotations

import logging
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from resolve_mcp.state import ServerState
from resolve_mcp.tools.session_tools import register_session_tools
from resolve_mcp.tools.project_tools import register_project_tools
from resolve_mcp.tools.media_storage_tools import register_media_storage_tools
from resolve_mcp.tools.media_pool_tools import register_media_pool_tools
from resolve_mcp.tools.timeline_tools import register_timeline_tools
from resolve_mcp.tools.timeline_item_tools import register_timeline_item_tools
from resolve_mcp.tools.color_tools import register_color_tools
from resolve_mcp.tools.audio_tools import register_audio_tools
from resolve_mcp.tools.deliver_tools import register_deliver_tools
from resolve_mcp.tools.transition_tools import register_transition_tools
from resolve_mcp.tools.color_node_tools import register_color_node_tools
from resolve_mcp.tools.color_version_tools import register_color_version_tools
from resolve_mcp.tools.color_grade_tools import register_color_grade_tools
from resolve_mcp.tools.color_group_tools import register_color_group_tools
from resolve_mcp.tools.gallery_tools import register_gallery_tools

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler()],  # stderr only for STDIO transport
)


def create_server() -> FastMCP:
    """Create and configure the MCP server with all tool modules."""
    mcp = FastMCP("DaVinci Resolve")
    state = ServerState()

    register_session_tools(mcp, state)
    register_project_tools(mcp, state)
    register_media_storage_tools(mcp, state)
    register_media_pool_tools(mcp, state)
    register_timeline_tools(mcp, state)
    register_timeline_item_tools(mcp, state)
    register_color_tools(mcp, state)
    register_audio_tools(mcp, state)
    register_deliver_tools(mcp, state)
    register_transition_tools(mcp, state)
    register_color_node_tools(mcp, state)
    register_color_version_tools(mcp, state)
    register_color_grade_tools(mcp, state)
    register_color_group_tools(mcp, state)
    register_gallery_tools(mcp, state)

    _guide_path = Path(__file__).resolve().parent.parent.parent / "RESOLVE_GUIDE.md"
    _fusion_guide_path = Path(__file__).resolve().parent.parent.parent / "FUSION_COMP_GUIDE.md"

    @mcp.resource("resolve://guide")
    def get_resolve_guide() -> str:
        """AI usage guide for the DaVinci Resolve MCP server — covers workflows, parameter conventions, and tips."""
        return _guide_path.read_text(encoding="utf-8")

    @mcp.resource("resolve://fusion-comp-guide")
    def get_fusion_comp_guide() -> str:
        """Comprehensive reference for programmatically authoring Fusion .comp files — covers Lua grammar, tool types, input parameters, expressions, keyframes, and 20 complete templates."""
        return _fusion_guide_path.read_text(encoding="utf-8")

    return mcp
