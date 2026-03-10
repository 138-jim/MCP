"""MCP tools for grade operations (copy, export, caching)."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from resolve_mcp.helpers import resolve_tool, get_item, get_timeline
from resolve_mcp.state import ServerState


def register_color_grade_tools(mcp: FastMCP, state: ServerState):

    @mcp.tool()
    @resolve_tool
    def resolve_copy_grades(
        track_type: str, track_index: int, source_item_index: int,
        target_item_indices: str
    ) -> str:
        """Copy the grade from a source clip to one or more target clips.

        Args:
            source_item_index: 0-based index of the source clip.
            target_item_indices: Comma-separated 0-based item indices (e.g. "1,2,3").
        """
        source = get_item(state, track_type, track_index, source_item_index)
        if source is None:
            return "Source item not found"
        tl = get_timeline(state)
        items = tl.get_item_list_in_track(track_type, track_index)
        indices = [int(i.strip()) for i in target_item_indices.split(",")]
        targets = []
        for idx in indices:
            if idx >= len(items):
                return f"Target item at index {idx} not found"
            targets.append(items[idx])
        if source.copy_grades(targets):
            return f"Copied grade from {source.get_name()} to {len(targets)} clip(s)"
        return "Failed to copy grades"

    @mcp.tool()
    @resolve_tool
    def resolve_export_lut(
        track_type: str, track_index: int, item_index: int,
        export_type: str, path: str
    ) -> str:
        """Export a LUT for a timeline item's grade.

        Args:
            export_type: LUT format constant suffix: LUT_17PTCUBE, LUT_33PTCUBE, LUT_65PTCUBE, or LUT_PANASONICVLUT.
            path: Destination file path.
        """
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return "Item not found"
        export_const = state.session.get_export_constant(export_type)
        if export_const is None:
            return (
                f"Unknown export type: {export_type}. "
                f"Use LUT_17PTCUBE, LUT_33PTCUBE, LUT_65PTCUBE, or LUT_PANASONICVLUT"
            )
        if item.export_lut(export_const, path):
            return f"Exported LUT to {path}"
        return "Failed to export LUT"

    @mcp.tool()
    @resolve_tool
    def resolve_get_color_output_cache(
        track_type: str, track_index: int, item_index: int
    ) -> str:
        """Check if color output cache is enabled on a timeline item."""
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return "Item not found"
        enabled = item.get_color_output_cache()
        status = "enabled" if enabled else "disabled"
        return f"Color output cache on {item.get_name()}: {status}"

    @mcp.tool()
    @resolve_tool
    def resolve_set_color_output_cache(
        track_type: str, track_index: int, item_index: int,
        enabled: bool
    ) -> str:
        """Enable or disable color output cache on a timeline item."""
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return "Item not found"
        if item.set_color_output_cache(enabled):
            status = "enabled" if enabled else "disabled"
            return f"Color output cache {status} on {item.get_name()}"
        return "Failed to set color output cache"
