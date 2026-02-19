"""MCP tools for media pool operations."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from resolve_mcp.helpers import resolve_tool, format_list, format_dict
from resolve_mcp.state import ServerState


def _get_pool(state: ServerState):
    return state.session.get_project_manager().get_current_project().get_media_pool()


def register_media_pool_tools(mcp: FastMCP, state: ServerState):

    @mcp.tool()
    @resolve_tool
    def resolve_get_current_bin() -> str:
        """Get the name of the currently selected media pool bin/folder."""
        pool = _get_pool(state)
        folder = pool.get_current_folder()
        return f"Current bin: {folder.get_name()}"

    @mcp.tool()
    @resolve_tool
    def resolve_list_bins() -> str:
        """List subfolders (bins) in the current media pool folder."""
        pool = _get_pool(state)
        folder = pool.get_current_folder()
        subs = folder.get_subfolders()
        names = [s.get_name() for s in subs]
        return format_list(names, "bins")

    @mcp.tool()
    @resolve_tool
    def resolve_create_bin(name: str) -> str:
        """Create a new bin (subfolder) in the current media pool folder."""
        pool = _get_pool(state)
        parent = pool.get_current_folder()
        new_folder = pool.add_subfolder(name, parent)
        return f"Created bin: {new_folder.get_name()}"

    @mcp.tool()
    @resolve_tool
    def resolve_set_current_bin(bin_name: str) -> str:
        """Set the current media pool bin by name. Searches subfolders of root."""
        pool = _get_pool(state)
        root = pool.get_root_folder()
        target = _find_folder(root, bin_name)
        if target is None:
            return f"Bin not found: {bin_name}"
        pool.set_current_folder(target)
        return f"Switched to bin: {bin_name}"

    @mcp.tool()
    @resolve_tool
    def resolve_list_clips_in_bin() -> str:
        """List all clips in the current media pool bin."""
        pool = _get_pool(state)
        folder = pool.get_current_folder()
        clips = folder.get_clips()
        names = [c.get_name() for c in clips]
        return format_list(names, "clips")

    @mcp.tool()
    @resolve_tool
    def resolve_import_media(paths: str) -> str:
        """Import media files into the current bin. Paths are comma-separated."""
        pool = _get_pool(state)
        path_list = [p.strip() for p in paths.split(",") if p.strip()]
        items = pool.import_media(path_list)
        return f"Imported {len(items)} clip(s)"

    @mcp.tool()
    @resolve_tool
    def resolve_get_clip_metadata(clip_name: str, key: str = "") -> str:
        """Get metadata for a clip by name. If key is empty, returns all metadata."""
        clip = _find_clip_by_name(state, clip_name)
        if clip is None:
            return f"Clip not found: {clip_name}"
        if key:
            return f"{key}: {clip.get_metadata(key)}"
        return format_dict(clip.get_metadata(), f"Metadata for {clip_name}")

    @mcp.tool()
    @resolve_tool
    def resolve_set_clip_metadata(clip_name: str, key: str, value: str) -> str:
        """Set a metadata field on a clip."""
        clip = _find_clip_by_name(state, clip_name)
        if clip is None:
            return f"Clip not found: {clip_name}"
        if clip.set_metadata(key, value):
            return f"Set {key}={value} on {clip_name}"
        return f"Failed to set metadata on {clip_name}"

    @mcp.tool()
    @resolve_tool
    def resolve_get_clip_markers(clip_name: str) -> str:
        """Get all markers on a media pool clip."""
        clip = _find_clip_by_name(state, clip_name)
        if clip is None:
            return f"Clip not found: {clip_name}"
        markers = clip.get_markers()
        if not markers:
            return f"No markers on {clip_name}"
        lines = [f"Markers on {clip_name}:"]
        for frame, info in markers.items():
            lines.append(f"  Frame {frame}: {info}")
        return "\n".join(lines)

    @mcp.tool()
    @resolve_tool
    def resolve_add_clip_marker(
        clip_name: str, frame: int, color: str, name: str, note: str = "", duration: int = 1
    ) -> str:
        """Add a marker to a media pool clip."""
        clip = _find_clip_by_name(state, clip_name)
        if clip is None:
            return f"Clip not found: {clip_name}"
        if clip.add_marker(frame, color, name, note, duration):
            return f"Added {color} marker at frame {frame}"
        return "Failed to add marker"

    @mcp.tool()
    @resolve_tool
    def resolve_set_clip_color(clip_name: str, color: str) -> str:
        """Set the clip color label on a media pool clip."""
        clip = _find_clip_by_name(state, clip_name)
        if clip is None:
            return f"Clip not found: {clip_name}"
        if clip.set_clip_color(color):
            return f"Set clip color to {color}"
        return "Failed to set clip color"

    @mcp.tool()
    @resolve_tool
    def resolve_add_clip_flag(clip_name: str, color: str) -> str:
        """Add a flag to a media pool clip."""
        clip = _find_clip_by_name(state, clip_name)
        if clip is None:
            return f"Clip not found: {clip_name}"
        if clip.add_flag(color):
            return f"Added {color} flag"
        return "Failed to add flag"

    @mcp.tool()
    @resolve_tool
    def resolve_create_timeline(name: str) -> str:
        """Create an empty timeline."""
        pool = _get_pool(state)
        tl = pool.create_empty_timeline(name)
        return f"Created timeline: {tl.get_name()}"

    @mcp.tool()
    @resolve_tool
    def resolve_create_timeline_from_clips(name: str, clip_names: str) -> str:
        """Create a new timeline from media pool clips.

        Args:
            name: Name for the new timeline.
            clip_names: Comma-separated clip names from the current bin.
        """
        pool = _get_pool(state)
        folder = pool.get_current_folder()
        all_clips = {c.get_name(): c for c in folder.get_clips()}
        names = [n.strip() for n in clip_names.split(",") if n.strip()]
        selected = []
        missing = []
        for n in names:
            if n in all_clips:
                selected.append(all_clips[n])
            else:
                missing.append(n)
        if missing:
            return f"Clips not found: {', '.join(missing)}"
        if not selected:
            return "No clips specified"
        tl = pool.create_timeline_from_clips(name, selected)
        return f"Created timeline '{tl.get_name()}' with {len(selected)} clip(s)"

    @mcp.tool()
    @resolve_tool
    def resolve_append_clips_to_timeline(clip_names: str) -> str:
        """Append media pool clips to the end of the current timeline.

        Args:
            clip_names: Comma-separated clip names from the current bin.
        """
        pool = _get_pool(state)
        folder = pool.get_current_folder()
        all_clips = {c.get_name(): c for c in folder.get_clips()}
        names = [n.strip() for n in clip_names.split(",") if n.strip()]
        selected = []
        missing = []
        for n in names:
            if n in all_clips:
                selected.append(all_clips[n])
            else:
                missing.append(n)
        if missing:
            return f"Clips not found: {', '.join(missing)}"
        if not selected:
            return "No clips specified"
        result = pool.append_to_timeline(selected)
        return f"Appended {len(result)} clip(s) to timeline"

    @mcp.tool()
    @resolve_tool
    def resolve_import_timeline(path: str) -> str:
        """Import a timeline from a file (AAF, EDL, XML, FCPXML, OTIO, etc.)."""
        pool = _get_pool(state)
        tl = pool.import_timeline_from_file(path)
        return f"Imported timeline: {tl.get_name()}"

    @mcp.tool()
    @resolve_tool
    def resolve_transcribe_bin() -> str:
        """Transcribe audio for all clips in the current bin."""
        pool = _get_pool(state)
        folder = pool.get_current_folder()
        if folder.transcribe_audio():
            return "Transcription started"
        return "Failed to start transcription"


def _find_folder(root, name: str):
    """Recursively find a folder by name."""
    if root.get_name() == name:
        return root
    for sub in root.get_subfolders():
        found = _find_folder(sub, name)
        if found is not None:
            return found
    return None


def _find_clip_by_name(state: ServerState, name: str):
    """Find a clip by name in the current bin."""
    pool = _get_pool(state)
    folder = pool.get_current_folder()
    for clip in folder.get_clips():
        if clip.get_name() == name:
            return clip
    return None
