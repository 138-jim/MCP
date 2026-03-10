"""MCP tools for timeline operations."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from resolve_mcp.helpers import resolve_tool, format_list, get_pool, get_project, get_timeline
from resolve_mcp.state import ServerState


def _parse_timeline_rate(value: object) -> tuple[float, bool]:
    """Parse timeline frame rate and drop-frame flag from project settings."""
    raw = str(value).strip().upper()
    is_drop_frame = raw.endswith("DF")
    fps_text = raw.replace(" DF", "").replace("DF", "").strip()
    try:
        fps = float(fps_text)
    except (TypeError, ValueError):
        return 24.0, False
    return (fps if fps > 0 else 24.0), is_drop_frame


def _nominal_timecode_fps(fps: float) -> int:
    """Map timeline fps to nominal SMPTE timecode base."""
    known = (
        (23.976, 24),
        (24.0, 24),
        (25.0, 25),
        (29.97, 30),
        (30.0, 30),
        (47.952, 48),
        (48.0, 48),
        (50.0, 50),
        (59.94, 60),
        (60.0, 60),
    )
    for known_fps, nominal in known:
        if abs(fps - known_fps) < 0.01:
            return nominal
    return max(1, int(round(fps)))


def _frame_to_timecode(frame: int, fps: float, drop_frame: bool = False) -> str:
    """Convert a timeline frame position to HH:MM:SS:FF timecode."""
    total_frames = max(0, int(frame))
    nominal_fps = _nominal_timecode_fps(fps)

    # For 29.97/59.94 DF timelines, skip frame numbers at each minute
    # except every 10th minute so frame->timecode mapping stays exact.
    if drop_frame and nominal_fps in (30, 60):
        drop_frames = 2 if nominal_fps == 30 else 4
        frames_per_hour = nominal_fps * 60 * 60
        frames_per_24h = frames_per_hour * 24
        frames_per_10_minutes = nominal_fps * 60 * 10 - drop_frames * 9
        frames_per_minute = nominal_fps * 60 - drop_frames

        total_frames %= frames_per_24h
        ten_min_chunks = total_frames // frames_per_10_minutes
        remaining = total_frames % frames_per_10_minutes

        dropped = drop_frames * 9 * ten_min_chunks
        if remaining >= drop_frames:
            dropped += drop_frames * ((remaining - drop_frames) // frames_per_minute)
        tc_frames = total_frames + dropped
    else:
        tc_frames = total_frames

    total_seconds, ff = divmod(tc_frames, nominal_fps)
    hh, rem = divmod(total_seconds, 3600)
    mm, ss = divmod(rem, 60)
    return f"{hh:02d}:{mm:02d}:{ss:02d}:{ff:02d}"


def _timecode_to_frame(timecode: str, fps: float, drop_frame: bool = False) -> int:
    """Convert HH:MM:SS:FF timecode to a frame count."""
    parts = str(timecode).split(":")
    if len(parts) != 4:
        return 0
    try:
        hh, mm, ss, ff = [int(part) for part in parts]
    except ValueError:
        return 0

    nominal_fps = _nominal_timecode_fps(fps)
    total_minutes = hh * 60 + mm
    total_frames = ((hh * 3600) + (mm * 60) + ss) * nominal_fps + ff

    if drop_frame and nominal_fps in (30, 60):
        drop_frames = 2 if nominal_fps == 30 else 4
        total_frames -= drop_frames * (total_minutes - total_minutes // 10)

    return max(0, total_frames)


def _find_first_media_pool_item_from_timeline(tl):
    """Return the first timeline clip backed by media pool item, or None."""
    track_count = tl.get_track_count("video")
    for track_index in range(1, track_count + 1):
        for item in tl.get_item_list_in_track("video", track_index):
            media_item = item.get_media_pool_item()
            if media_item is not None:
                return media_item
    return None


def _find_item_location(tl, unique_id: str) -> tuple[int, int] | None:
    """Find a timeline item's (track_index, item_index) by unique ID."""
    track_count = tl.get_track_count("video")
    for track_index in range(1, track_count + 1):
        items = tl.get_item_list_in_track("video", track_index)
        for item_index, item in enumerate(items):
            if item.get_unique_id() == unique_id:
                return track_index, item_index
    return None


def register_timeline_tools(mcp: FastMCP, state: ServerState):

    @mcp.tool()
    @resolve_tool
    def resolve_get_current_timeline() -> str:
        """Get the name and info of the current timeline."""
        tl = get_timeline(state)
        name = tl.get_name()
        start = tl.get_start_frame()
        end = tl.get_end_frame()
        tc = tl.get_start_timecode()
        return f"Timeline: {name}\nFrames: {start}-{end}\nStart TC: {tc}"

    @mcp.tool()
    @resolve_tool
    def resolve_list_timelines() -> str:
        """List all timelines in the current project."""
        proj = get_project(state)
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
        proj = get_project(state)
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
        tl = get_timeline(state)
        old = tl.get_name()
        if tl.set_name(name):
            return f"Renamed timeline from '{old}' to '{name}'"
        return "Failed to rename timeline"

    @mcp.tool()
    @resolve_tool
    def resolve_get_track_count(track_type: str) -> str:
        """Get the number of tracks of a given type (video, audio, subtitle)."""
        tl = get_timeline(state)
        count = tl.get_track_count(track_type)
        return f"{track_type} tracks: {count}"

    @mcp.tool()
    @resolve_tool
    def resolve_add_track(track_type: str) -> str:
        """Add a new track of the given type (video, audio, subtitle)."""
        tl = get_timeline(state)
        if tl.add_track(track_type):
            return f"Added {track_type} track"
        return f"Failed to add {track_type} track"

    @mcp.tool()
    @resolve_tool
    def resolve_get_track_name(track_type: str, index: int) -> str:
        """Get the name of a track (1-based index)."""
        tl = get_timeline(state)
        return tl.get_track_name(track_type, index)

    @mcp.tool()
    @resolve_tool
    def resolve_set_track_name(track_type: str, index: int, name: str) -> str:
        """Set the name of a track (1-based index)."""
        tl = get_timeline(state)
        if tl.set_track_name(track_type, index, name):
            return f"Renamed {track_type} track {index} to '{name}'"
        return "Failed to rename track"

    @mcp.tool()
    @resolve_tool
    def resolve_list_items_in_track(track_type: str, index: int) -> str:
        """List all clips/items in a specific track (1-based index)."""
        tl = get_timeline(state)
        items = tl.get_item_list_in_track(track_type, index)
        names = [item.get_name() for item in items]
        return format_list(names, f"items in {track_type} track {index}")

    @mcp.tool()
    @resolve_tool
    def resolve_get_current_timecode() -> str:
        """Get the current playhead timecode."""
        tl = get_timeline(state)
        return f"Playhead: {tl.get_current_timecode()}"

    @mcp.tool()
    @resolve_tool
    def resolve_set_current_timecode(timecode: str) -> str:
        """Set the playhead to a specific timecode (e.g. '01:00:05:00')."""
        tl = get_timeline(state)
        if tl.set_current_timecode(timecode):
            return f"Playhead set to {timecode}"
        return f"Failed to set timecode to {timecode}"

    @mcp.tool()
    @resolve_tool
    def resolve_get_timeline_markers() -> str:
        """Get all markers on the current timeline."""
        tl = get_timeline(state)
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
        tl = get_timeline(state)
        if tl.add_marker(frame, color, name, note, duration):
            return f"Added {color} marker at frame {frame}"
        return "Failed to add marker"

    @mcp.tool()
    @resolve_tool
    def resolve_delete_timeline_marker(frame: int) -> str:
        """Delete a marker at a specific frame on the current timeline."""
        tl = get_timeline(state)
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
        tl = get_timeline(state)
        # Resolve API expects numeric constants (resolve.EXPORT_EDL etc.).
        export_const = state.session.get_export_constant(export_type)
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
            subtype_const = state.session.get_export_constant(f"TEXT_{export_subtype}")
            sub = subtype_const if subtype_const is not None else export_subtype
        if tl.export(path, export_const, sub):
            return f"Exported timeline to {path}"
        return "Failed to export timeline"

    @mcp.tool()
    @resolve_tool
    def resolve_duplicate_timeline(name: str = "") -> str:
        """Duplicate the current timeline, optionally with a new name."""
        tl = get_timeline(state)
        new_tl = tl.duplicate_timeline(name if name else None)
        return f"Duplicated timeline as: {new_tl.get_name()}"

    # Disabled: GetAvailableGenerators does not exist on Resolve 20.3 proxy
    @resolve_tool
    def resolve_list_generators() -> str:
        """List available generators (solid colors, etc.)."""
        tl = get_timeline(state)
        gens = tl.get_available_generators()
        names = [g.get("Name", str(g)) for g in gens] if gens else []
        return format_list(names, "generators")

    @mcp.tool()
    @resolve_tool
    def resolve_insert_generator(name: str) -> str:
        """Insert a generator into the timeline by name."""
        tl = get_timeline(state)
        tl.insert_generator_in_timeline(name)
        return f"Inserted generator: {name}"

    # Disabled: GetAvailableTitles does not exist on Resolve 20.3 proxy
    @resolve_tool
    def resolve_list_titles() -> str:
        """List available title/text templates."""
        tl = get_timeline(state)
        titles = tl.get_available_titles()
        names = [t.get("Name", str(t)) for t in titles] if titles else []
        return format_list(names, "titles")

    @mcp.tool()
    @resolve_tool
    def resolve_insert_title(name: str) -> str:
        """Insert a title/text template into the timeline."""
        tl = get_timeline(state)
        tl.insert_title_in_timeline(name)
        return f"Inserted title: {name}"

    @mcp.tool()
    @resolve_tool
    def resolve_insert_fusion_generator(name: str) -> str:
        """Insert a Fusion generator into the timeline by name."""
        tl = get_timeline(state)
        tl.insert_fusion_generator_in_timeline(name)
        return f"Inserted Fusion generator: {name}"

    @mcp.tool()
    @resolve_tool
    def resolve_insert_fusion_title(name: str) -> str:
        """Insert a Fusion title into the timeline by name."""
        tl = get_timeline(state)
        tl.insert_fusion_title_in_timeline(name)
        return f"Inserted Fusion title: {name}"

    @mcp.tool()
    @resolve_tool
    def resolve_add_text_overlay(
        text: str,
        start_timecode: str = "",
        overlay_track: int = 2,
        size: str = "0.08",
        font: str = "",
        title_name: str = "Text+",
    ) -> str:
        """Insert and configure a Fusion Text+ overlay in one call.

        This convenience tool:
        1. Ensures the requested video overlay track exists.
        2. Targets that track for insertion.
        3. Inserts a Fusion title at the playhead (or start_timecode).
        4. Sets TextPlus.StyledText, and optionally Size/Font.

        Args:
            text: Title text for TextPlus.StyledText.
            start_timecode: Optional target timecode (e.g. '00:00:10:00').
            overlay_track: Target video track index for the title (1-based).
            size: Optional TextPlus.Size value (default '0.08').
            font: Optional TextPlus.Font value.
            title_name: Fusion title template name (default 'Text+').
        """
        if overlay_track < 1:
            return "overlay_track must be >= 1"

        tl = get_timeline(state)
        pool = get_pool(state)
        target_timecode = start_timecode
        derived_from_clip_start = False
        if not target_timecode:
            base_items = tl.get_item_list_in_track("video", 1)
            if base_items:
                first_item = min(base_items, key=lambda item: item.get_start())
                fps, drop_frame = _parse_timeline_rate(
                    get_project(state).get_setting("timelineFrameRate")
                )
                timeline_start_frame = _timecode_to_frame(
                    tl.get_start_timecode(), fps, drop_frame=drop_frame
                )
                target_timecode = _frame_to_timecode(
                    timeline_start_frame + first_item.get_start(),
                    fps,
                    drop_frame=drop_frame,
                )
                derived_from_clip_start = True
            else:
                target_timecode = tl.get_current_timecode()

        # Ensure requested overlay track exists.
        while tl.get_track_count("video") < overlay_track:
            if not tl.add_track("video"):
                return f"Failed to add video track V{tl.get_track_count('video') + 1}"

        if not tl.set_current_timecode(target_timecode):
            return f"Failed to set playhead to {target_timecode}"

        dummy_uid: str | None = None
        try:
            # Resolve inserts titles on the currently targeted video track.
            # To target a specific track, insert a temporary clip on that track first.
            if overlay_track > 1:
                folder = pool.get_current_folder()
                bin_clips = folder.get_clips()
                source_clip = (
                    bin_clips[0] if bin_clips else _find_first_media_pool_item_from_timeline(tl)
                )
                if source_clip is None:
                    return (
                        "Cannot target overlay track: no media clip available in current bin "
                        "or timeline. Import at least one media clip and retry."
                    )

                dummy_frame = max(tl.get_end_frame() + 1000, 1000)
                before_ids = {
                    item.get_unique_id()
                    for item in tl.get_item_list_in_track("video", overlay_track)
                }
                clip_info = {
                    "mediaPoolItem": source_clip.raw,
                    "recordFrame": dummy_frame,
                    "trackIndex": overlay_track,
                }
                pool.append_to_timeline([clip_info])
                after_items = tl.get_item_list_in_track("video", overlay_track)
                for item in after_items:
                    uid = item.get_unique_id()
                    if uid not in before_ids:
                        dummy_uid = uid
                        break
                if dummy_uid is None:
                    return f"Failed to target overlay track V{overlay_track}"

            # Dummy track-targeting inserts can move the playhead; restore target.
            if not tl.set_current_timecode(target_timecode):
                return f"Failed to set playhead to {target_timecode}"
            # Guard against Resolve jumping playhead during track-targeting operations.
            if tl.get_current_timecode() != target_timecode:
                if not tl.set_current_timecode(target_timecode):
                    return f"Failed to restore playhead to {target_timecode}"
                if tl.get_current_timecode() != target_timecode:
                    return (
                        f"Could not keep playhead at {target_timecode} "
                        f"(current: {tl.get_current_timecode()})"
                    )

            title_item = tl.insert_fusion_title_in_timeline(title_name)
            location = _find_item_location(tl, title_item.get_unique_id())
            if location is None:
                return f"Inserted {title_name}, but could not locate it on the timeline"
            title_track, title_index = location
            title_start = title_item.get_start()

            ok_text = title_item.set_fusion_tool_input("TextPlus", "StyledText", text)

            ok_size = True
            if size:
                size_value: object = size
                try:
                    size_value = float(size)
                except ValueError:
                    pass
                ok_size = title_item.set_fusion_tool_input("TextPlus", "Size", size_value)

            ok_font = True
            if font:
                ok_font = title_item.set_fusion_tool_input("TextPlus", "Font", font)

            lines = [f"Inserted {title_name} overlay on V{title_track}:{title_index}"]
            lines.append(f"At timecode {target_timecode}")
            if derived_from_clip_start:
                lines.append("Auto-aligned to first V1 clip start")
            if not ok_text:
                lines.append("WARNING: Failed to set TextPlus.StyledText")
            if size and not ok_size:
                lines.append("WARNING: Failed to set TextPlus.Size")
            if font and not ok_font:
                lines.append("WARNING: Failed to set TextPlus.Font")
            if title_track != overlay_track:
                lines.append(
                    f"WARNING: Requested overlay_track=V{overlay_track}, but title landed on V{title_track}"
                )
            if ok_text and (not size or ok_size) and (not font or ok_font):
                lines.append(f"Text overlay set to {text!r}")
            lines.append(f"Title start frame: {title_start}")
            return "\n".join(lines)
        finally:
            if dummy_uid is not None:
                items = tl.get_item_list_in_track("video", overlay_track)
                dummy_items = [item for item in items if item.get_unique_id() == dummy_uid]
                if dummy_items:
                    tl.delete_clips(dummy_items, False)

    # Disabled: DetectSceneCuts runs but returns bool, not frame list
    @resolve_tool
    def resolve_detect_scene_cuts() -> str:
        """Run scene cut detection on the current timeline."""
        tl = get_timeline(state)
        cuts = tl.detect_scene_cuts()
        if not cuts:
            return "No scene cuts detected"
        return f"Detected {len(cuts)} scene cuts at frames: {cuts[:20]}{'...' if len(cuts) > 20 else ''}"

    # Disabled: CreateSubtitlesFromAudio always returns False (may need Studio)
    @resolve_tool
    def resolve_create_subtitle_from_audio() -> str:
        """Create subtitles from audio in the current timeline."""
        tl = get_timeline(state)
        if tl.create_subtitle_from_audio():
            return "Subtitle creation from audio started"
        return "Failed to create subtitles from audio"

    @mcp.tool()
    @resolve_tool
    def resolve_delete_items(
        track_type: str, track_index: int, item_indices: list[int], ripple: bool = False
    ) -> str:
        """Delete one or more clips from the timeline by track and index.

        Args:
            track_type: Track type (video or audio).
            track_index: Track index (1-based).
            item_indices: List of item indices (0-based) to delete.
            ripple: If true, close the gap left by removed clips.
        """
        tl = get_timeline(state)
        items = tl.get_item_list_in_track(track_type, track_index)
        to_delete = []
        missing = []
        for idx in item_indices:
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
