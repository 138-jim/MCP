"""MCP tools for Fusion composition import."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from resolve_mcp.helpers import resolve_tool, get_item
from resolve_mcp.state import ServerState


def register_transition_tools(mcp: FastMCP, state: ServerState):

    @mcp.tool()
    @resolve_tool
    def resolve_import_transition_preset(
        track_type: str, track_index: int, item_index: int,
        preset_path: str,
    ) -> str:
        """Import a custom Fusion composition (.comp) file as a transition on a clip.

        Args:
            track_type: Track type (video or audio).
            track_index: Track index (1-based).
            item_index: Item index within the track (0-based).
            preset_path: Absolute path to the .comp or .setting file.
        """
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return f"Item not found at {track_type}:{track_index}:{item_index}"
        item.import_fusion_comp(preset_path)
        return f"Imported Fusion comp from {preset_path} onto {item.get_name()}"
