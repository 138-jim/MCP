"""MCP tools for gallery, still albums, and stills management."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from resolve_mcp.helpers import (
    resolve_tool,
    format_list,
    get_project,
    get_timeline,
)
from resolve_mcp.state import ServerState


def register_gallery_tools(mcp: FastMCP, state: ServerState):

    # ------------------------------------------------------------------
    # Stills capture
    # ------------------------------------------------------------------

    @mcp.tool()
    @resolve_tool
    def resolve_grab_still() -> str:
        """Grab a still from the current frame on the Color page."""
        tl = get_timeline(state)
        tl.grab_still()
        return "Still grabbed from current frame"

    @mcp.tool()
    @resolve_tool
    def resolve_grab_all_stills(still_frame_source: int = 1) -> str:
        """Grab stills from all clips in the timeline.

        Args:
            still_frame_source: 1=first frame, 2=middle frame.
        """
        tl = get_timeline(state)
        stills = tl.grab_all_stills(still_frame_source)
        return f"Grabbed {len(stills)} still(s) from timeline"

    # ------------------------------------------------------------------
    # Album management
    # ------------------------------------------------------------------

    @mcp.tool()
    @resolve_tool
    def resolve_get_current_still_album() -> str:
        """Get the name of the currently selected still album."""
        proj = get_project(state)
        gallery = proj.get_gallery()
        album = gallery.get_current_still_album()
        name = gallery.get_album_name(album)
        return f"Current still album: {name}"

    @mcp.tool()
    @resolve_tool
    def resolve_set_current_still_album(album_index: int) -> str:
        """Set the current still album by index (1-based, from resolve_list_gallery_albums)."""
        proj = get_project(state)
        gallery = proj.get_gallery()
        albums = gallery.get_gallery_still_albums()
        if album_index < 1 or album_index > len(albums):
            return f"Album index {album_index} out of range (1-{len(albums)})"
        album = albums[album_index - 1]
        if gallery.set_current_still_album(album):
            name = gallery.get_album_name(album)
            return f"Set current still album to: {name}"
        return "Failed to set current still album"

    @mcp.tool()
    @resolve_tool
    def resolve_list_powergrade_albums() -> str:
        """List all PowerGrade albums in the gallery."""
        proj = get_project(state)
        gallery = proj.get_gallery()
        albums = gallery.get_gallery_powergrade_albums()
        names = [gallery.get_album_name(a) for a in albums]
        return format_list(names, "PowerGrade albums")

    @mcp.tool()
    @resolve_tool
    def resolve_create_still_album() -> str:
        """Create a new still album in the gallery."""
        proj = get_project(state)
        gallery = proj.get_gallery()
        album = gallery.create_gallery_still_album()
        name = gallery.get_album_name(album)
        return f"Created still album: {name}"

    @mcp.tool()
    @resolve_tool
    def resolve_create_powergrade_album() -> str:
        """Create a new PowerGrade album in the gallery."""
        proj = get_project(state)
        gallery = proj.get_gallery()
        album = gallery.create_gallery_powergrade_album()
        name = gallery.get_album_name(album)
        return f"Created PowerGrade album: {name}"

    @mcp.tool()
    @resolve_tool
    def resolve_set_album_name(album_index: int, name: str) -> str:
        """Rename a still album by index (1-based, from resolve_list_gallery_albums)."""
        proj = get_project(state)
        gallery = proj.get_gallery()
        albums = gallery.get_gallery_still_albums()
        if album_index < 1 or album_index > len(albums):
            return f"Album index {album_index} out of range (1-{len(albums)})"
        album = albums[album_index - 1]
        if gallery.set_album_name(album, name):
            return f"Renamed album {album_index} to: {name}"
        return "Failed to rename album"

    # ------------------------------------------------------------------
    # Stills within albums
    # ------------------------------------------------------------------

    @mcp.tool()
    @resolve_tool
    def resolve_list_stills() -> str:
        """List all stills in the current still album."""
        proj = get_project(state)
        gallery = proj.get_gallery()
        album = gallery.get_current_still_album()
        stills = album.get_stills()
        if not stills:
            return "No stills in current album."
        labels = []
        for still in stills:
            label = album.get_label(still)
            labels.append(label if label else "(unlabeled)")
        return format_list(labels, "stills")

    @mcp.tool()
    @resolve_tool
    def resolve_get_still_label(still_index: int) -> str:
        """Get the label of a still by index (1-based, from resolve_list_stills)."""
        proj = get_project(state)
        gallery = proj.get_gallery()
        album = gallery.get_current_still_album()
        stills = album.get_stills()
        if still_index < 1 or still_index > len(stills):
            return f"Still index {still_index} out of range (1-{len(stills)})"
        still = stills[still_index - 1]
        label = album.get_label(still)
        if label:
            return f"Still {still_index} label: {label}"
        return f"Still {still_index} has no label"

    @mcp.tool()
    @resolve_tool
    def resolve_set_still_label(still_index: int, label: str) -> str:
        """Set the label of a still by index (1-based, from resolve_list_stills)."""
        proj = get_project(state)
        gallery = proj.get_gallery()
        album = gallery.get_current_still_album()
        stills = album.get_stills()
        if still_index < 1 or still_index > len(stills):
            return f"Still index {still_index} out of range (1-{len(stills)})"
        still = stills[still_index - 1]
        if album.set_label(still, label):
            return f"Set still {still_index} label to: {label}"
        return "Failed to set still label"

    @mcp.tool()
    @resolve_tool
    def resolve_import_stills(paths: str) -> str:
        """Import still files into the current album.

        Args:
            paths: Comma-separated file paths.
        """
        proj = get_project(state)
        gallery = proj.get_gallery()
        album = gallery.get_current_still_album()
        path_list = [p.strip() for p in paths.split(",")]
        if album.import_stills(path_list):
            return f"Imported {len(path_list)} still(s) into current album"
        return "Failed to import stills"

    @mcp.tool()
    @resolve_tool
    def resolve_export_stills(
        still_indices: str, path: str,
        file_prefix: str = "", format: str = "dpx"
    ) -> str:
        """Export stills from the current album.

        Args:
            still_indices: Comma-separated 1-based indices (e.g. "1,2,3").
            path: Target directory for exported files.
            file_prefix: Optional prefix for exported file names.
            format: Export format (dpx, cin, tif, jpg, png, ppm, bmp, xpm).
        """
        proj = get_project(state)
        gallery = proj.get_gallery()
        album = gallery.get_current_still_album()
        stills = album.get_stills()
        indices = [int(i.strip()) for i in still_indices.split(",")]
        selected = []
        for idx in indices:
            if idx < 1 or idx > len(stills):
                return f"Still index {idx} out of range (1-{len(stills)})"
            selected.append(stills[idx - 1])
        if album.export_stills(selected, path, file_prefix, format):
            return f"Exported {len(selected)} still(s) to {path}"
        return "Failed to export stills"

    @mcp.tool()
    @resolve_tool
    def resolve_delete_stills(still_indices: str) -> str:
        """Delete stills from the current album by index.

        Args:
            still_indices: Comma-separated 1-based indices (e.g. "1,2,3").
        """
        proj = get_project(state)
        gallery = proj.get_gallery()
        album = gallery.get_current_still_album()
        stills = album.get_stills()
        indices = [int(i.strip()) for i in still_indices.split(",")]
        selected = []
        for idx in indices:
            if idx < 1 or idx > len(stills):
                return f"Still index {idx} out of range (1-{len(stills)})"
            selected.append(stills[idx - 1])
        if album.delete_stills(selected):
            return f"Deleted {len(selected)} still(s)"
        return "Failed to delete stills"
