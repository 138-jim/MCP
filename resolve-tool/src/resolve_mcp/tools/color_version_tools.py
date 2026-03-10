"""MCP tools for color version management."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from resolve_mcp.helpers import resolve_tool, format_dict, get_item
from resolve_mcp.state import ServerState


def _normalize_version_type(version_type: str) -> str:
    """Normalize user-provided version type labels."""
    normalized = str(version_type).strip().lower()
    if normalized in {"local", "remote"}:
        return normalized
    return "local"


def _infer_current_version_type(version: dict, fallback: str) -> str:
    """Infer local/remote from Resolve current-version payload when present."""
    raw_type = version.get("versionType")
    if raw_type in (0, "0", "local", "LOCAL", "Local"):
        return "local"
    if raw_type in (1, "1", "remote", "REMOTE", "Remote"):
        return "remote"
    return fallback


def register_color_version_tools(mcp: FastMCP, state: ServerState):

    @mcp.tool()
    @resolve_tool
    def resolve_add_color_version(
        track_type: str, track_index: int, item_index: int,
        name: str, version_type: str = "local"
    ) -> str:
        """Create a new color version on a timeline item.

        Args:
            version_type: "local" or "remote".
        """
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return "Item not found"
        if item.add_version(name, version_type):
            return f"Added {version_type} color version '{name}' to {item.get_name()}"
        return "Failed to add color version"

    @mcp.tool()
    @resolve_tool
    def resolve_get_current_color_version(
        track_type: str, track_index: int, item_index: int,
        version_type: str = "local"
    ) -> str:
        """Get the current color version of a timeline item.

        Args:
            version_type: "local" or "remote".
        """
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return "Item not found"
        requested_type = _normalize_version_type(version_type)
        version = item.get_current_version(requested_type)
        if not version:
            return "No version info available"
        actual_type = _infer_current_version_type(version, requested_type)
        label = f"Current {actual_type} version of {item.get_name()}"
        if actual_type != requested_type:
            label += f" (requested {requested_type})"
        return format_dict(version, label)

    @mcp.tool()
    @resolve_tool
    def resolve_delete_color_version(
        track_type: str, track_index: int, item_index: int,
        name: str, version_type: str = "local"
    ) -> str:
        """Delete a color version by name.

        Args:
            version_type: "local" or "remote".
        """
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return "Item not found"
        if item.delete_version_by_name(name, version_type):
            return f"Deleted {version_type} version '{name}' from {item.get_name()}"
        return f"Failed to delete version '{name}'"

    @mcp.tool()
    @resolve_tool
    def resolve_rename_color_version(
        track_type: str, track_index: int, item_index: int,
        old_name: str, new_name: str, version_type: str = "local"
    ) -> str:
        """Rename a color version.

        Args:
            version_type: "local" or "remote".
        """
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return "Item not found"
        if item.rename_version_by_name(old_name, new_name, version_type):
            return f"Renamed {version_type} version '{old_name}' to '{new_name}'"
        return f"Failed to rename version '{old_name}'"
