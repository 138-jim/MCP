"""MCP tools for timeline operations."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from resolve_mcp.helpers import resolve_tool, format_list, format_dict
from resolve_mcp.state import ServerState


def _get_project(state: ServerState):
    return state.session.get_project_manager().get_current_project()


def _get_timeline(state: ServerState):
    return _get_project(state).get_current_timeline()


def register_timeline_tools(mcp: FastMCP, state: ServerState):

    @mcp.tool()
    @resolve_tool
    def resolve_get_current_timeline() -> str:
        """Get the name and info of the current timeline."""
        tl = _get_timeline(state)
        name = tl.get_name()
        start = tl.get_start_frame()
        end = tl.get_end_frame()
        tc = tl.get_start_timecode()
        return f"Timeline: {name}\nFrames: {start}-{end}\nStart TC: {tc}"

    @mcp.tool()
    @resolve_tool
    def resolve_list_timelines() -> str:
        """List all timelines in the current project."""
        proj = _get_project(state)
        count = proj.get_timeline_count()
        names = []
        for i in range(1, count + 1):
            tl = proj.get_timeline_by_index(i)
            names.append(tl.get_name())
        return format_list(names, "timelines")

    @mcp.tool()
    @resolve_tool
    def resolve_set_current_timeline(name: str) -> str:
        """Switch to a timeline by name."""
        proj = _get_project(state)
        count = proj.get_timeline_count()
        for i in range(1, count + 1):
            tl = proj.get_timeline_by_index(i)
            if tl.get_name() == name:
                proj.set_current_timeline(tl)
                return f"Switched to timeline: {name}"
        return f"Timeline not found: {name}"

    @mcp.tool()
    @resolve_tool
    def resolve_set_timeline_name(name: str) -> str:
        """Rename the current timeline."""
        tl = _get_timeline(state)
        old = tl.get_name()
        if tl.set_name(name):
            return f"Renamed timeline from '{old}' to '{name}'"
        return "Failed to rename timeline"

    @mcp.tool()
    @resolve_tool
    def resolve_get_track_count(track_type: str) -> str:
        """Get the number of tracks of a given type (video, audio, subtitle)."""
        tl = _get_timeline(state)
        count = tl.get_track_count(track_type)
        return f"{track_type} tracks: {count}"

    @mcp.tool()
    @resolve_tool
    def resolve_add_track(track_type: str) -> str:
        """Add a new track of the given type (video, audio, subtitle)."""
        tl = _get_timeline(state)
        if tl.add_track(track_type):
            return f"Added {track_type} track"
        return f"Failed to add {track_type} track"

    @mcp.tool()
    @resolve_tool
    def resolve_get_track_name(track_type: str, index: int) -> str:
        """Get the name of a track (1-based index)."""
        tl = _get_timeline(state)
        return tl.get_track_name(track_type, index)

    @mcp.tool()
    @resolve_tool
    def resolve_set_track_name(track_type: str, index: int, name: str) -> str:
        """Set the name of a track (1-based index)."""
        tl = _get_timeline(state)
        if tl.set_track_name(track_type, index, name):
            return f"Renamed {track_type} track {index} to '{name}'"
        return "Failed to rename track"

    @mcp.tool()
    @resolve_tool
    def resolve_list_items_in_track(track_type: str, index: int) -> str:
        """List all clips/items in a specific track (1-based index)."""
        tl = _get_timeline(state)
        items = tl.get_item_list_in_track(track_type, index)
        names = [item.get_name() for item in items]
        return format_list(names, f"items in {track_type} track {index}")

    @mcp.tool()
    @resolve_tool
    def resolve_get_current_timecode() -> str:
        """Get the current playhead timecode."""
        tl = _get_timeline(state)
        return f"Playhead: {tl.get_current_timecode()}"

    @mcp.tool()
    @resolve_tool
    def resolve_set_current_timecode(timecode: str) -> str:
        """Set the playhead to a specific timecode (e.g. '01:00:05:00')."""
        tl = _get_timeline(state)
        if tl.set_current_timecode(timecode):
            return f"Playhead set to {timecode}"
        return f"Failed to set timecode to {timecode}"

    @mcp.tool()
    @resolve_tool
    def resolve_get_timeline_markers() -> str:
        """Get all markers on the current timeline."""
        tl = _get_timeline(state)
        markers = tl.get_markers()
        if not markers:
            return "No markers on timeline"
        lines = ["Timeline markers:"]
        for frame, info in markers.items():
            lines.append(f"  Frame {frame}: {info}")
        return "\n".join(lines)

    @mcp.tool()
    @resolve_tool
    def resolve_add_timeline_marker(
        frame: int, color: str, name: str, note: str = "", duration: int = 1
    ) -> str:
        """Add a marker to the current timeline at the given frame."""
        tl = _get_timeline(state)
        if tl.add_marker(frame, color, name, note, duration):
            return f"Added {color} marker at frame {frame}"
        return "Failed to add marker"

    @mcp.tool()
    @resolve_tool
    def resolve_delete_timeline_marker(frame: int) -> str:
        """Delete a marker at a specific frame on the current timeline."""
        tl = _get_timeline(state)
        if tl.delete_marker_at_frame(frame):
            return f"Deleted marker at frame {frame}"
        return f"No marker at frame {frame}"

    @mcp.tool()
    @resolve_tool
    def resolve_export_timeline(path: str, export_type: str, export_subtype: str = "") -> str:
        """Export the current timeline.

        Args:
            path: Output file path.
            export_type: Format (AAF, DRT, EDL, FCP_7_XML, FCPXML_1_8, etc.).
            export_subtype: Optional subtype for the format.
        """
        tl = _get_timeline(state)
        # Resolve API expects numeric constants (resolve.EXPORT_EDL etc.),
        # not raw strings.  Resolve the constant from the session object.
        resolve_obj = state.session._obj
        const_name = f"EXPORT_{export_type}"
        export_const = getattr(resolve_obj, const_name, None)
        if export_const is None:
            return (
                f"Unknown export type: {export_type}. "
                f"Use AAF, DRT, EDL, FCP_7_XML, FCPXML_1_8, FCPXML_1_9, "
                f"FCPXML_1_10, FCPXML_1_11, HDR_10_PROFILE_A, HDR_10_PROFILE_B, "
                f"TEXT_CSV, TEXT_TAB, DOLBY_VISION_VER_2_9, DOLBY_VISION_VER_4_0, "
                f"DOLBY_VISION_VER_5_1, OTIO"
            )
        sub = None
        if export_subtype:
            sub_const_name = f"EXPORT_TEXT_{export_subtype}"
            sub = getattr(resolve_obj, sub_const_name, export_subtype)
        if tl.export(path, export_const, sub):
            return f"Exported timeline to {path}"
        return "Failed to export timeline"

    @mcp.tool()
    @resolve_tool
    def resolve_duplicate_timeline(name: str = "") -> str:
        """Duplicate the current timeline, optionally with a new name."""
        tl = _get_timeline(state)
        new_tl = tl.duplicate_timeline(name if name else None)
        return f"Duplicated timeline as: {new_tl.get_name()}"

    # Disabled: GetAvailableGenerators does not exist on Resolve 20.3 proxy
    @resolve_tool
    def resolve_list_generators() -> str:
        """List available generators (solid colors, etc.)."""
        tl = _get_timeline(state)
        gens = tl.get_available_generators()
        names = [g.get("Name", str(g)) for g in gens] if gens else []
        return format_list(names, "generators")

    @mcp.tool()
    @resolve_tool
    def resolve_insert_generator(name: str) -> str:
        """Insert a generator into the timeline by name."""
        tl = _get_timeline(state)
        tl.insert_generator_in_timeline(name)
        return f"Inserted generator: {name}"

    # Disabled: GetAvailableTitles does not exist on Resolve 20.3 proxy
    @resolve_tool
    def resolve_list_titles() -> str:
        """List available title/text templates."""
        tl = _get_timeline(state)
        titles = tl.get_available_titles()
        names = [t.get("Name", str(t)) for t in titles] if titles else []
        return format_list(names, "titles")

    @mcp.tool()
    @resolve_tool
    def resolve_insert_title(name: str) -> str:
        """Insert a title/text template into the timeline."""
        tl = _get_timeline(state)
        tl.insert_title_in_timeline(name)
        return f"Inserted title: {name}"

    @mcp.tool()
    @resolve_tool
    def resolve_insert_fusion_generator(name: str) -> str:
        """Insert a Fusion generator into the timeline by name."""
        tl = _get_timeline(state)
        tl.insert_fusion_generator_in_timeline(name)
        return f"Inserted Fusion generator: {name}"

    @mcp.tool()
    @resolve_tool
    def resolve_insert_fusion_title(name: str) -> str:
        """Insert a Fusion title into the timeline by name."""
        tl = _get_timeline(state)
        tl.insert_fusion_title_in_timeline(name)
        return f"Inserted Fusion title: {name}"

    # Disabled: DetectSceneCuts runs but returns bool, not frame list
    @resolve_tool
    def resolve_detect_scene_cuts() -> str:
        """Run scene cut detection on the current timeline."""
        tl = _get_timeline(state)
        cuts = tl.detect_scene_cuts()
        if not cuts:
            return "No scene cuts detected"
        return f"Detected {len(cuts)} scene cuts at frames: {cuts[:20]}{'...' if len(cuts) > 20 else ''}"

    # Disabled: CreateSubtitlesFromAudio always returns False (may need Studio)
    @resolve_tool
    def resolve_create_subtitle_from_audio() -> str:
        """Create subtitles from audio in the current timeline."""
        tl = _get_timeline(state)
        if tl.create_subtitle_from_audio():
            return "Subtitle creation from audio started"
        return "Failed to create subtitles from audio"

    @mcp.tool()
    @resolve_tool
    def resolve_delete_items(
        track_type: str, track_index: int, item_indices: str, ripple: bool = False
    ) -> str:
        """Delete one or more clips from the timeline by track and index.

        Args:
            track_type: Track type (video or audio).
            track_index: Track index (1-based).
            item_indices: Comma-separated item indices (0-based) to delete.
            ripple: If true, close the gap left by removed clips.
        """
        tl = _get_timeline(state)
        items = tl.get_item_list_in_track(track_type, track_index)
        indices = [int(i.strip()) for i in item_indices.split(",") if i.strip()]
        to_delete = []
        missing = []
        for idx in indices:
            if idx < len(items):
                to_delete.append(items[idx])
            else:
                missing.append(str(idx))
        if missing:
            return f"Item indices not found: {', '.join(missing)}"
        if not to_delete:
            return "No items specified"
        names = [item.get_name() for item in to_delete]
        if tl.delete_clips(to_delete, ripple):
            mode = " (ripple)" if ripple else ""
            return f"Deleted{mode}: {', '.join(names)}"
        return f"Failed to delete items: {', '.join(names)}"

    # Disabled: Timeline.GetSetting / SetSetting don't exist in Resolve 20.3 Free.
    # Use resolve_get_project_setting / resolve_set_project_setting instead.
