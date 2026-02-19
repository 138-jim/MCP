"""MCP tools for media storage operations."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from resolve_mcp.helpers import resolve_tool, format_list
from resolve_mcp.state import ServerState


def register_media_storage_tools(mcp: FastMCP, state: ServerState):

    @mcp.tool()
    @resolve_tool
    def resolve_get_mounted_volumes() -> str:
        """List all currently mounted media storage volumes."""
        ms = state.session.get_media_storage()
        volumes = ms.get_mounted_volumes()
        return format_list(volumes, "volumes")

    @mcp.tool()
    @resolve_tool
    def resolve_browse_volume(path: str) -> str:
        """List subfolders at the given media storage path.

        Args:
            path: Absolute filesystem path to browse.
        """
        ms = state.session.get_media_storage()
        subfolders = ms.get_subfolder_list(path)
        return format_list(subfolders, "subfolders")

    @mcp.tool()
    @resolve_tool
    def resolve_list_files(path: str) -> str:
        """List files at the given media storage path.

        Args:
            path: Absolute filesystem path to list files from.
        """
        ms = state.session.get_media_storage()
        files = ms.get_file_list(path)
        return format_list(files, "files")

    @mcp.tool()
    @resolve_tool
    def resolve_import_files_to_pool(paths: str) -> str:
        """Import files from media storage into the media pool.

        Args:
            paths: Comma-separated list of absolute file paths to import.
        """
        ms = state.session.get_media_storage()
        paths_list = [p.strip() for p in paths.split(",") if p.strip()]
        items = ms.add_items_to_media_pool(*paths_list)
        return f"Imported {len(items)} item(s) to the media pool"

    @mcp.tool()
    @resolve_tool
    def resolve_add_clip_mattes(clip_name: str, matte_paths: str) -> str:
        """Add mattes to a media pool clip via media storage.

        Args:
            clip_name: Name of the clip to add mattes to.
            matte_paths: Comma-separated list of matte file paths.
        """
        ms = state.session.get_media_storage()
        # Find the clip by name in the current media pool folder
        project = state.session.get_project_manager().get_current_project()
        pool = project.get_media_pool()
        folder = pool.get_current_folder()
        clip = None
        for c in folder.get_clips():
            if c.get_name() == clip_name:
                clip = c
                break
        if clip is None:
            return f"Clip not found: {clip_name}"
        paths_list = [p.strip() for p in matte_paths.split(",") if p.strip()]
        if ms.add_clip_mattes_to_media_pool(clip, paths_list):
            return f"Added {len(paths_list)} matte(s) to {clip_name}"
        return f"Failed to add mattes to {clip_name}"
