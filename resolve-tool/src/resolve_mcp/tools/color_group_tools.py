"""MCP tools for color group management."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from resolve_mcp.helpers import (
    resolve_tool,
    format_list,
    get_project,
    get_item,
    get_timeline,
)
from resolve_mcp.state import ServerState


def _find_color_group(state, group_name):
    """Find a color group by name. Returns (group, error_string)."""
    proj = get_project(state)
    groups = proj.get_color_group_list()
    for g in groups:
        if g.get_name() == group_name:
            return g, None
    return None, f"Color group '{group_name}' not found"


def register_color_group_tools(mcp: FastMCP, state: ServerState):

    @mcp.tool()
    @resolve_tool
    def resolve_delete_color_group(group_name: str) -> str:
        """Delete a color group by name."""
        group, err = _find_color_group(state, group_name)
        if err:
            return err
        proj = get_project(state)
        if proj.delete_color_group(group):
            return f"Deleted color group: {group_name}"
        return f"Failed to delete color group: {group_name}"

    @mcp.tool()
    @resolve_tool
    def resolve_set_color_group_name(
        current_name: str, new_name: str
    ) -> str:
        """Rename a color group."""
        group, err = _find_color_group(state, current_name)
        if err:
            return err
        if group.set_name(new_name):
            return f"Renamed color group '{current_name}' to '{new_name}'"
        return "Failed to rename color group"

    @mcp.tool()
    @resolve_tool
    def resolve_get_clips_in_color_group(group_name: str) -> str:
        """List clips belonging to a color group in the current timeline."""
        group, err = _find_color_group(state, group_name)
        if err:
            return err
        tl = get_timeline(state)
        clips = group.get_clips_in_timeline(tl)
        names = [c.get_name() for c in clips]
        return format_list(names, f"clips in '{group_name}'")

    @mcp.tool()
    @resolve_tool
    def resolve_get_color_group_pre_node_graph(group_name: str) -> str:
        """Get the pre-clip node graph info for a color group."""
        group, err = _find_color_group(state, group_name)
        if err:
            return err
        graph = group.get_pre_clip_node_graph()
        if graph is None:
            return "No pre-clip node graph available"
        num_nodes = graph.get_num_nodes()
        lines = [f"Pre-clip node graph for '{group_name}': {num_nodes} node(s)"]
        for i in range(1, num_nodes + 1):
            label = graph.get_node_label(i)
            lines.append(f"  Node {i}: {label}" if label else f"  Node {i}: (no label)")
        return "\n".join(lines)

    @mcp.tool()
    @resolve_tool
    def resolve_get_color_group_post_node_graph(group_name: str) -> str:
        """Get the post-clip node graph info for a color group."""
        group, err = _find_color_group(state, group_name)
        if err:
            return err
        graph = group.get_post_clip_node_graph()
        if graph is None:
            return "No post-clip node graph available"
        num_nodes = graph.get_num_nodes()
        lines = [f"Post-clip node graph for '{group_name}': {num_nodes} node(s)"]
        for i in range(1, num_nodes + 1):
            label = graph.get_node_label(i)
            lines.append(f"  Node {i}: {label}" if label else f"  Node {i}: (no label)")
        return "\n".join(lines)

    @mcp.tool()
    @resolve_tool
    def resolve_get_item_color_group(
        track_type: str, track_index: int, item_index: int
    ) -> str:
        """Get which color group a timeline item belongs to."""
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return "Item not found"
        group = item.get_color_group()
        if group is None:
            return f"{item.get_name()} is not assigned to any color group"
        return f"{item.get_name()} is in color group: {group.get_name()}"

    @mcp.tool()
    @resolve_tool
    def resolve_assign_to_color_group(
        track_type: str, track_index: int, item_index: int,
        group_name: str
    ) -> str:
        """Assign a timeline item to a color group by name."""
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return "Item not found"
        group, err = _find_color_group(state, group_name)
        if err:
            return err
        if item.assign_to_color_group(group):
            return f"Assigned {item.get_name()} to color group '{group_name}'"
        return "Failed to assign to color group"

    @mcp.tool()
    @resolve_tool
    def resolve_remove_from_color_group(
        track_type: str, track_index: int, item_index: int
    ) -> str:
        """Remove a timeline item from its current color group."""
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return "Item not found"
        if item.remove_from_color_group():
            return f"Removed {item.get_name()} from its color group"
        return "Failed to remove from color group"
