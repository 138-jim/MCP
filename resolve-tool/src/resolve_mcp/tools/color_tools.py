"""MCP tools for color grading, nodes, gallery, and stills."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from resolve_mcp.helpers import resolve_tool, format_list, get_project, get_item
from resolve_mcp.state import ServerState


def register_color_tools(mcp: FastMCP, state: ServerState):

    @mcp.tool()
    @resolve_tool
    def resolve_get_node_count(
        track_type: str, track_index: int, item_index: int
    ) -> str:
        """Get the number of color nodes on a timeline item."""
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return "Item not found"
        graph = item.get_node_graph()
        if graph is None:
            return "No node graph available"
        return f"Node count: {graph.get_num_nodes()}"

    @mcp.tool()
    @resolve_tool
    def resolve_get_node_lut(
        track_type: str, track_index: int, item_index: int, node_index: int
    ) -> str:
        """Get the LUT applied to a specific node (1-based index)."""
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return "Item not found"
        graph = item.get_node_graph()
        if graph is None:
            return "No node graph available"
        lut = graph.get_lut(node_index)
        return f"Node {node_index} LUT: {lut}" if lut else f"No LUT on node {node_index}"

    @mcp.tool()
    @resolve_tool
    def resolve_set_node_lut(
        track_type: str, track_index: int, item_index: int,
        node_index: int, lut_path: str
    ) -> str:
        """Apply a LUT to a specific node (1-based index)."""
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return "Item not found"
        graph = item.get_node_graph()
        if graph is None:
            return "No node graph available"
        if graph.set_lut(node_index, lut_path):
            return f"Applied LUT to node {node_index}"
        return "Failed to apply LUT"

    # Disabled: SetNodeLabel does not exist on Resolve 20.3 proxy (read-only)
    @resolve_tool
    def resolve_set_node_label(
        track_type: str, track_index: int, item_index: int,
        node_index: int, label: str
    ) -> str:
        """Set the label of a color node."""
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return "Item not found"
        graph = item.get_node_graph()
        if graph is None:
            return "No node graph available"
        if graph.set_node_label(node_index, label):
            return f"Set node {node_index} label to '{label}'"
        return "Failed to set node label"

    @mcp.tool()
    @resolve_tool
    def resolve_reset_grades(
        track_type: str, track_index: int, item_index: int
    ) -> str:
        """Reset all color grading on a timeline item."""
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return "Item not found"
        graph = item.get_node_graph()
        if graph is None:
            return "No node graph available"
        if graph.reset_grades():
            return "Grades reset"
        return "Failed to reset grades"

    @mcp.tool()
    @resolve_tool
    def resolve_list_color_groups() -> str:
        """List all color groups in the current project."""
        proj = get_project(state)
        groups = proj.get_color_group_list()
        names = [g.get_name() for g in groups]
        return format_list(names, "color groups")

    @mcp.tool()
    @resolve_tool
    def resolve_add_color_group(name: str) -> str:
        """Create a new color group."""
        proj = get_project(state)
        group = proj.add_color_group(name)
        return f"Created color group: {group.get_name()}"

    @mcp.tool()
    @resolve_tool
    def resolve_list_gallery_albums() -> str:
        """List all still albums in the gallery."""
        proj = get_project(state)
        gallery = proj.get_gallery()
        albums = gallery.get_gallery_still_albums()
        names = [gallery.get_album_name(a) for a in albums]
        return format_list(names, "still albums")

    @mcp.tool()
    @resolve_tool
    def resolve_export_still(path: str) -> str:
        """Export the current frame as a still image."""
        proj = get_project(state)
        if proj.export_current_frame_as_still(path):
            return f"Exported still to {path}"
        return "Failed to export still"

    @mcp.tool()
    @resolve_tool
    def resolve_apply_grade_from_drx(
        track_type: str, track_index: int, item_index: int,
        drx_path: str, grade_mode: int = 0
    ) -> str:
        """Apply a grade from a .drx still file to a timeline item.

        Args:
            grade_mode: 0=No keyframes, 1=Source timecode, 2=Start timecode.
        """
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return "Item not found"
        graph = item.get_node_graph()
        if graph is None:
            return "No node graph available"
        if graph.apply_grade_from_drx(drx_path, grade_mode, item):
            return f"Applied grade from {drx_path}"
        return "Failed to apply grade"
