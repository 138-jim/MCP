"""MCP tools for media pool operations."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from resolve_mcp.helpers import resolve_tool, format_list, format_dict, get_project, get_pool, get_timeline, find_clip_by_name, auto_scale_to_timeline
from resolve_mcp.state import ServerState


def _timeline_info(state: ServerState, tl) -> str:
    """Return a summary string of timeline properties."""
    proj = get_project(state)
    fps = proj.get_setting("timelineFrameRate")
    width = proj.get_setting("timelineResolutionWidth")
    height = proj.get_setting("timelineResolutionHeight")
    lines = [
        f"Name: {tl.get_name()}",
        f"Frames: {tl.get_start_frame()}-{tl.get_end_frame()}",
        f"Start TC: {tl.get_start_timecode()}",
        f"Frame Rate: {fps}",
        f"Resolution: {width}x{height}",
    ]
    return "\n".join(lines)


def register_media_pool_tools(mcp: FastMCP, state: ServerState):

    @mcp.tool()
    @resolve_tool
    def resolve_get_current_bin() -> str:
        """Get the name of the currently selected media pool bin/folder."""
        pool = get_pool(state)
        folder = pool.get_current_folder()
        return f"Current bin: {folder.get_name()}"

    @mcp.tool()
    @resolve_tool
    def resolve_list_bins() -> str:
        """List subfolders (bins) in the current media pool folder."""
        pool = get_pool(state)
        folder = pool.get_current_folder()
        subs = folder.get_subfolders()
        names = [s.get_name() for s in subs]
        return format_list(names, "bins")

    @mcp.tool()
    @resolve_tool
    def resolve_create_bin(name: str) -> str:
        """Create a new bin (subfolder) in the current media pool folder."""
        pool = get_pool(state)
        parent = pool.get_current_folder()
        new_folder = pool.add_subfolder(name, parent)
        return f"Created bin: {new_folder.get_name()}"

    @mcp.tool()
    @resolve_tool
    def resolve_set_current_bin(bin_name: str) -> str:
        """Set the current media pool bin by name. Searches subfolders of root."""
        pool = get_pool(state)
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
        pool = get_pool(state)
        folder = pool.get_current_folder()
        clips = folder.get_clips()
        names = [c.get_name() for c in clips]
        return format_list(names, "clips")

    @mcp.tool()
    @resolve_tool
    def resolve_import_media(paths: list[str]) -> str:
        """Import media files into the current bin.

        Args:
            paths: List of file paths to import.
        """
        pool = get_pool(state)
        items = pool.import_media(paths)
        return f"Imported {len(items)} clip(s)"

    @mcp.tool()
    @resolve_tool
    def resolve_get_clip_metadata(clip_name: str, key: str = "") -> str:
        """Get metadata for a clip by name. If key is empty, returns all metadata."""
        clip = find_clip_by_name(state, clip_name)
        if clip is None:
            return f"Clip not found: {clip_name}"
        if key:
            return f"{key}: {clip.get_metadata(key)}"
        return format_dict(clip.get_metadata(), f"Metadata for {clip_name}")

    @mcp.tool()
    @resolve_tool
    def resolve_set_clip_metadata(clip_name: str, key: str, value: str) -> str:
        """Set a metadata field on a clip."""
        clip = find_clip_by_name(state, clip_name)
        if clip is None:
            return f"Clip not found: {clip_name}"
        if clip.set_metadata(key, value):
            return f"Set {key}={value} on {clip_name}"
        return f"Failed to set metadata on {clip_name}"

    @mcp.tool()
    @resolve_tool
    def resolve_get_clip_markers(clip_name: str) -> str:
        """Get all markers on a media pool clip."""
        clip = find_clip_by_name(state, clip_name)
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
        clip = find_clip_by_name(state, clip_name)
        if clip is None:
            return f"Clip not found: {clip_name}"
        if clip.add_marker(frame, color, name, note, duration):
            return f"Added {color} marker at frame {frame}"
        return "Failed to add marker"

    @mcp.tool()
    @resolve_tool
    def resolve_set_clip_color(clip_name: str, color: str) -> str:
        """Set the clip color label on a media pool clip."""
        clip = find_clip_by_name(state, clip_name)
        if clip is None:
            return f"Clip not found: {clip_name}"
        if clip.set_clip_color(color):
            return f"Set clip color to {color}"
        return "Failed to set clip color"

    @mcp.tool()
    @resolve_tool
    def resolve_add_clip_flag(clip_name: str, color: str) -> str:
        """Add a flag to a media pool clip."""
        clip = find_clip_by_name(state, clip_name)
        if clip is None:
            return f"Clip not found: {clip_name}"
        if clip.add_flag(color):
            return f"Added {color} flag"
        return "Failed to add flag"

    @mcp.tool()
    @resolve_tool
    def resolve_create_timeline(name: str) -> str:
        """Create an empty timeline."""
        pool = get_pool(state)
        tl = pool.create_empty_timeline(name)
        return f"Created timeline\n{_timeline_info(state, tl)}"

    @mcp.tool()
    @resolve_tool
    def resolve_create_timeline_from_clips(name: str, clip_names: list[str]) -> str:
        """Create a new timeline from media pool clips.

        Args:
            name: Name for the new timeline.
            clip_names: List of clip names from the current bin.
        """
        pool = get_pool(state)
        folder = pool.get_current_folder()
        all_clips = {c.get_name(): c for c in folder.get_clips()}
        selected = []
        missing = []
        for n in clip_names:
            if n in all_clips:
                selected.append(all_clips[n])
            else:
                missing.append(n)
        if missing:
            return f"Clips not found: {', '.join(missing)}"
        if not selected:
            return "No clips specified"
        tl = pool.create_timeline_from_clips(name, selected)
        msg = f"Created timeline with {len(selected)} clip(s)\n{_timeline_info(state, tl)}"
        proj = get_project(state)
        timeline_fps = proj.get_setting("timelineFrameRate")
        if timeline_fps:
            mismatched = []
            for c in selected:
                clip_fps = c.get_clip_property("FPS")
                if clip_fps and str(clip_fps) != str(timeline_fps):
                    mismatched.append(f"{c.get_name()} ({clip_fps})")
            if mismatched:
                msg += f"\n  WARNING: timeline fps is {timeline_fps} but these clips differ: {', '.join(mismatched)}"
        tl_width = proj.get_setting("timelineResolutionWidth")
        tl_height = proj.get_setting("timelineResolutionHeight")
        if tl_width and tl_height:
            tl_res = f"{tl_width}x{tl_height}"
            res_mismatched = []
            for c in selected:
                clip_res = c.get_clip_property("Resolution")
                if clip_res and str(clip_res) != tl_res:
                    res_mismatched.append(f"{c.get_name()} ({clip_res})")
            if res_mismatched:
                msg += f"\n  WARNING: timeline resolution is {tl_res} but these clips differ: {', '.join(res_mismatched)}"
        return msg

    @mcp.tool()
    @resolve_tool
    def resolve_append_clips_to_timeline(clip_names: list[str]) -> str:
        """Append media pool clips to the end of the current timeline.

        Args:
            clip_names: List of clip names from the current bin.
        """
        pool = get_pool(state)
        folder = pool.get_current_folder()
        all_clips = {c.get_name(): c for c in folder.get_clips()}
        selected = []
        missing = []
        for n in clip_names:
            if n in all_clips:
                selected.append(all_clips[n])
            else:
                missing.append(n)
        if missing:
            return f"Clips not found: {', '.join(missing)}"
        if not selected:
            return "No clips specified"
        tl = get_timeline(state)
        video_before = len(tl.get_item_list_in_track("video", 1))
        result = pool.append_to_timeline(selected)
        msg = f"Appended {len(result)} clip(s) to timeline"
        # Auto-scale newly added timeline items
        video_after = tl.get_item_list_in_track("video", 1)
        new_items = video_after[video_before:]
        if new_items:
            scaled = auto_scale_to_timeline(state, new_items)
            if scaled:
                msg += f"\n  Auto-scaled {scaled} clip(s) to match timeline resolution"
        return msg

    @mcp.tool()
    @resolve_tool
    def resolve_insert_clip_at_frame(
        clip_name: str,
        record_frame: int,
        start_frame: int = -1,
        end_frame: int = -1,
        track_index: int = 1,
        media_type: int = 1,
        track_type: str = "",
    ) -> str:
        """Insert a media pool clip at a specific timeline frame position.

        Places a clip from the current bin onto the timeline at the given
        record frame. Optionally specify source in/out points and target
        track.

        Args:
            clip_name: Name of the clip in the current media pool bin.
            record_frame: Timeline frame where the clip should be placed.
            start_frame: Source start frame (-1 to use clip default).
            end_frame: Source end frame (-1 to use clip default).
            track_index: Track index (1-based, default 1).
            media_type: 1 for video (default), 2 for audio-only.
                Prefer using track_type instead.
            track_type: "audio" or "video" (default "video").  When set,
                this overrides media_type for convenience.
        """
        # Allow callers to use the friendlier track_type string
        if track_type.lower() == "audio":
            media_type = 2
        elif track_type.lower() == "video":
            media_type = 1
        clip = find_clip_by_name(state, clip_name)
        if clip is None:
            return f"Clip not found: {clip_name}"
        clip_info: dict = {
            "mediaPoolItem": clip.raw,
            "recordFrame": record_frame,
            "trackIndex": track_index,
            "mediaType": media_type,
        }
        if start_frame >= 0:
            clip_info["startFrame"] = start_frame
        if end_frame >= 0:
            clip_info["endFrame"] = end_frame
        pool = get_pool(state)
        proj = get_project(state)
        tl = proj.get_current_timeline()
        track_type = "audio" if media_type == 2 else "video"
        before = len(tl.get_item_list_in_track(track_type, track_index))
        pool.append_to_timeline([clip_info])
        items = tl.get_item_list_in_track(track_type, track_index)
        if len(items) <= before:
            return f"Failed to insert '{clip_name}' at frame {record_frame} -- track may have existing content at that position"
        # Auto-scale new items to match timeline resolution
        new_items = items[before:]
        scaled = auto_scale_to_timeline(state, new_items)
        # Check for frame rate mismatch
        track_label = f"A{track_index}" if media_type == 2 else f"V{track_index}"
        msg = f"Inserted '{clip_name}' at frame {record_frame} on track {track_label}"
        if scaled:
            msg += f"\n  Auto-scaled to match timeline resolution"
        timeline_fps = proj.get_setting("timelineFrameRate")
        clip_fps = clip.get_clip_property("FPS")
        if clip_fps and timeline_fps and str(clip_fps) != str(timeline_fps):
            msg += f"\n  WARNING: clip fps ({clip_fps}) does not match timeline fps ({timeline_fps})"
        tl_width = proj.get_setting("timelineResolutionWidth")
        tl_height = proj.get_setting("timelineResolutionHeight")
        if tl_width and tl_height:
            tl_res = f"{tl_width}x{tl_height}"
            clip_res = clip.get_clip_property("Resolution")
            if clip_res and str(clip_res) != tl_res:
                msg += f"\n  WARNING: clip resolution ({clip_res}) does not match timeline resolution ({tl_res})"
        # Check for gaps with neighbors
        if len(items) >= 2:
            # Sort items by timeline start position
            sorted_items = sorted(items, key=lambda it: it.get_start())
            for i, it in enumerate(sorted_items):
                if it.get_start() == record_frame or (
                    i > 0 and sorted_items[i - 1].get_end() != it.get_start()
                    and it.get_name() == clip_name
                ):
                    # Check gap before this clip
                    if i > 0:
                        prev_end = sorted_items[i - 1].get_end()
                        this_start = it.get_start()
                        if this_start > prev_end:
                            gap = this_start - prev_end
                            msg += f"\n  WARNING: {gap}-frame gap before this clip (prev clip ends at {prev_end}, this starts at {this_start})"
                            msg += "\n  TIP: Often this is caused by mismatched framerates between your timeline and footage — check that first."
                    # Check gap after this clip
                    if i < len(sorted_items) - 1:
                        this_end = it.get_end()
                        next_start = sorted_items[i + 1].get_start()
                        if next_start > this_end:
                            gap = next_start - this_end
                            msg += f"\n  WARNING: {gap}-frame gap after this clip (this ends at {this_end}, next starts at {next_start})"
                            msg += "\n  TIP: Often this is caused by mismatched framerates between your timeline and footage — check that first."
                    break
        return msg

    @mcp.tool()
    @resolve_tool
    def resolve_import_timeline(path: str) -> str:
        """Import a timeline from a file (AAF, EDL, XML, FCPXML, OTIO, etc.)."""
        pool = get_pool(state)
        tl = pool.import_timeline_from_file(path)
        return f"Imported timeline: {tl.get_name()}"

    @mcp.tool()
    @resolve_tool
    def resolve_transcribe_bin() -> str:
        """Transcribe audio for all clips in the current bin."""
        pool = get_pool(state)
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
