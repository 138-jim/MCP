"""MCP tools for session-level operations."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from resolve_mcp.helpers import resolve_tool
from resolve_mcp.state import ServerState


def register_session_tools(mcp: FastMCP, state: ServerState):

    @mcp.tool()
    @resolve_tool
    def resolve_get_version() -> str:
        """Get the DaVinci Resolve version string."""
        return state.session.get_version()

    @mcp.tool()
    @resolve_tool
    def resolve_get_current_page() -> str:
        """Get the currently open page in Resolve."""
        return state.session.get_current_page()

    @mcp.tool()
    @resolve_tool
    def resolve_set_page(page: str) -> str:
        """Switch to a Resolve page (media, cut, edit, fusion, color, fairlight, deliver)."""
        state.session.set_current_page(page)
        return f"Switched to {page} page"

    @mcp.tool()
    @resolve_tool
    def resolve_get_keyframe_mode() -> str:
        """Get the current keyframe mode (0=All, 1=Color, 2=Sizing)."""
        mode = state.session.get_keyframe_mode()
        names = {0: "All", 1: "Color", 2: "Sizing"}
        return f"Keyframe mode: {names.get(mode, str(mode))}"

    @mcp.tool()
    @resolve_tool
    def resolve_set_keyframe_mode(mode: int) -> str:
        """Set keyframe mode: 0=All, 1=Color, 2=Sizing."""
        state.session.set_keyframe_mode(mode)
        return f"Keyframe mode set to {mode}"

    @mcp.tool()
    @resolve_tool
    def resolve_load_layout_preset(name: str) -> str:
        """Load a UI layout preset by name."""
        if state.session.load_layout_preset(name):
            return f"Loaded layout preset: {name}"
        return f"Failed to load layout preset: {name}"

    @mcp.tool()
    @resolve_tool
    def resolve_import_layout_preset(name: str, path: str) -> str:
        """Import a UI layout preset from file.

        Args:
            name: Name to assign to the imported preset.
            path: File path of the preset to import.
        """
        if state.session.import_layout_preset(name, path):
            return f"Imported layout preset '{name}' from {path}"
        return f"Failed to import layout preset '{name}'"

    @mcp.tool()
    @resolve_tool
    def resolve_reconnect() -> str:
        """Force reconnection to DaVinci Resolve. Use if Resolve was restarted."""
        state.disconnect()
        state.connect()
        return f"Reconnected to DaVinci Resolve {state.session.get_version()}"

    @mcp.tool()
    @resolve_tool
    def resolve_quit() -> str:
        """Quit DaVinci Resolve."""
        state.session.quit()
        state.disconnect()
        return "Resolve is quitting"
