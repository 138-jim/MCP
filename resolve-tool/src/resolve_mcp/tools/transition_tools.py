"""MCP tools for Fusion-based transition presets."""

from __future__ import annotations

import tempfile
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from resolve_mcp.helpers import resolve_tool, format_list, get_item, get_timeline, get_pool
from resolve_mcp.state import ServerState

PRESETS_DIR = Path(__file__).resolve().parent.parent / "presets" / "transitions"

# ---------------------------------------------------------------------------
# Fusion comp templates for overlay-based transitions
# ---------------------------------------------------------------------------

_CROSS_DISSOLVE_TEMPLATE = """\
Composition {{
\tTools = {{
\t\tBackground1 = Background {{
\t\t\tInputs = {{
\t\t\t\tUseFrameFormatSettings = Input {{ Value = 1, }},
\t\t\t\tTopLeftAlpha = Input {{ Value = 0, }},
\t\t\t}},
\t\t\tViewInfo = OperatorInfo {{ Pos = {{ 55, 16.5 }} }},
\t\t}},
\t\tMediaIn1 = Loader {{
\t\t\tInputs = {{
\t\t\t\t["Gamut.SLogVersion"] = Input {{ Value = FuID {{ "SLog2" }}, }},
\t\t\t}},
\t\t\tViewInfo = OperatorInfo {{ Pos = {{ 55, 82.5 }} }},
\t\t}},
\t\tMerge1 = Merge {{
\t\t\tInputs = {{
\t\t\t\tBlend = Input {{ Expression = "iif(time < (comp.RenderStart + {dissolve_duration}), (time - comp.RenderStart) / {dissolve_duration}, 1.0)", }},
\t\t\t\tBackground = Input {{
\t\t\t\t\tSourceOp = "Background1",
\t\t\t\t\tSource = "Output",
\t\t\t\t}},
\t\t\t\tForeground = Input {{
\t\t\t\t\tSourceOp = "MediaIn1",
\t\t\t\t\tSource = "Output",
\t\t\t\t}},
\t\t\t\tPerformDepthMerge = Input {{ Value = 0, }},
\t\t\t}},
\t\t\tViewInfo = OperatorInfo {{ Pos = {{ 165, 82.5 }} }},
\t\t}},
\t\tMediaOut1 = Saver {{
\t\t\tInputs = {{
\t\t\t\tInput = Input {{
\t\t\t\t\tSourceOp = "Merge1",
\t\t\t\t\tSource = "Output",
\t\t\t\t}},
\t\t\t}},
\t\t\tViewInfo = OperatorInfo {{ Pos = {{ 275, 82.5 }} }},
\t\t}},
\t}},
}}
"""

_BLUR_OUT_TEMPLATE = """\
Composition {{
\tTools = {{
\t\tMediaIn1 = Loader {{
\t\t\tInputs = {{
\t\t\t\t["Gamut.SLogVersion"] = Input {{ Value = FuID {{ "SLog2" }}, }},
\t\t\t}},
\t\t\tViewInfo = OperatorInfo {{ Pos = {{ 55, 82.5 }} }},
\t\t}},
\t\tBlur1 = Blur {{
\t\t\tInputs = {{
\t\t\t\tXBlurSize = Input {{ Expression = "iif(time > (comp.RenderEnd - {dissolve_duration}), {blur_size} * (time - (comp.RenderEnd - {dissolve_duration})) / {dissolve_duration}, 0)", }},
\t\t\t\tInput = Input {{
\t\t\t\t\tSourceOp = "MediaIn1",
\t\t\t\t\tSource = "Output",
\t\t\t\t}},
\t\t\t}},
\t\t\tViewInfo = OperatorInfo {{ Pos = {{ 165, 82.5 }} }},
\t\t}},
\t\tMediaOut1 = Saver {{
\t\t\tInputs = {{
\t\t\t\tInput = Input {{
\t\t\t\t\tSourceOp = "Blur1",
\t\t\t\t\tSource = "Output",
\t\t\t\t}},
\t\t\t}},
\t\t\tViewInfo = OperatorInfo {{ Pos = {{ 275, 82.5 }} }},
\t\t}},
\t}},
}}
"""

_BLUR_IN_FADE_TEMPLATE = """\
Composition {{
\tTools = {{
\t\tBackground1 = Background {{
\t\t\tInputs = {{
\t\t\t\tUseFrameFormatSettings = Input {{ Value = 1, }},
\t\t\t\tTopLeftAlpha = Input {{ Value = 0, }},
\t\t\t}},
\t\t\tViewInfo = OperatorInfo {{ Pos = {{ 55, 16.5 }} }},
\t\t}},
\t\tMediaIn1 = Loader {{
\t\t\tInputs = {{
\t\t\t\t["Gamut.SLogVersion"] = Input {{ Value = FuID {{ "SLog2" }}, }},
\t\t\t}},
\t\t\tViewInfo = OperatorInfo {{ Pos = {{ 55, 82.5 }} }},
\t\t}},
\t\tBlur1 = Blur {{
\t\t\tInputs = {{
\t\t\t\tXBlurSize = Input {{ Expression = "iif(time < (comp.RenderStart + {dissolve_duration}), {blur_size} * (1 - (time - comp.RenderStart) / {dissolve_duration}), 0)", }},
\t\t\t\tInput = Input {{
\t\t\t\t\tSourceOp = "MediaIn1",
\t\t\t\t\tSource = "Output",
\t\t\t\t}},
\t\t\t}},
\t\t\tViewInfo = OperatorInfo {{ Pos = {{ 165, 82.5 }} }},
\t\t}},
\t\tMerge1 = Merge {{
\t\t\tInputs = {{
\t\t\t\tBlend = Input {{ Expression = "iif(time < (comp.RenderStart + {dissolve_duration}), (time - comp.RenderStart) / {dissolve_duration}, 1.0)", }},
\t\t\t\tBackground = Input {{
\t\t\t\t\tSourceOp = "Background1",
\t\t\t\t\tSource = "Output",
\t\t\t\t}},
\t\t\t\tForeground = Input {{
\t\t\t\t\tSourceOp = "Blur1",
\t\t\t\t\tSource = "Output",
\t\t\t\t}},
\t\t\t\tPerformDepthMerge = Input {{ Value = 0, }},
\t\t\t}},
\t\t\tViewInfo = OperatorInfo {{ Pos = {{ 275, 82.5 }} }},
\t\t}},
\t\tMediaOut1 = Saver {{
\t\t\tInputs = {{
\t\t\t\tInput = Input {{
\t\t\t\t\tSourceOp = "Merge1",
\t\t\t\t\tSource = "Output",
\t\t\t\t}},
\t\t\t}},
\t\t\tViewInfo = OperatorInfo {{ Pos = {{ 385, 82.5 }} }},
\t\t}},
\t}},
}}
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _apply_comp_from_template(clip, template: str, **kwargs) -> None:
    """Write a Fusion comp template to a temp file and import it onto a clip."""
    comp_text = template.format(**kwargs)
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".comp", delete=False,
    ) as f:
        f.write(comp_text)
        temp_path = f.name
    try:
        clip.import_fusion_comp(temp_path)
    finally:
        Path(temp_path).unlink(missing_ok=True)


def _setup_overlay_transition(state, tl, pool, track_index,
                              item_index_a, item_index_b,
                              dissolve_duration):
    """Rearrange two adjacent clips into an overlap on separate tracks.

    Clip B is moved to a higher video track, shifted back by
    dissolve_duration frames to create an overlap region. No Fusion clip
    is created — callers apply .comp presets to individual clips.

    Returns a dict with keys (clip_a, clip_b, a_name, b_name, overlay_track)
    on success, or an error string on failure.
    """
    items = tl.get_item_list_in_track("video", track_index)
    if item_index_a >= len(items):
        return f"Clip A not found at video:{track_index}:{item_index_a}"
    if item_index_b >= len(items):
        return f"Clip B not found at video:{track_index}:{item_index_b}"

    clip_a = items[item_index_a]
    clip_b = items[item_index_b]

    a_name = clip_a.get_name() or f"clip at index {item_index_a}"
    b_name = clip_b.get_name() or f"clip at index {item_index_b}"

    a_end = clip_a.get_end()
    b_start = clip_b.get_start()
    if b_start != a_end:
        return (
            f"Clips are not adjacent: clip A ends at {a_end}, "
            f"clip B starts at {b_start}"
        )

    b_left_offset = clip_b.get_left_offset()
    if b_left_offset < dissolve_duration:
        return (
            f"Clip B does not have enough source material for a "
            f"{dissolve_duration}-frame dissolve (left_offset={b_left_offset}). "
            f"Try a shorter dissolve_duration or trim clip B's in-point later."
        )

    b_mpi = clip_b.get_media_pool_item()
    if b_mpi is None:
        return (
            f"Clip B ({b_name}) is not backed by a media pool item and "
            "cannot be used for this transition."
        )
    b_source_start = clip_b.get_source_start_frame()
    b_source_end = clip_b.get_source_end_frame()

    overlay_track = track_index + 1
    video_track_count = tl.get_track_count("video")
    if overlay_track > video_track_count:
        tl.add_track("video")

    tl.delete_clips([clip_b], ripple=False)

    new_record_frame = b_start - dissolve_duration
    clip_info = {
        "mediaPoolItem": b_mpi.raw,
        "recordFrame": new_record_frame,
        "trackIndex": overlay_track,
        "mediaType": 1,
        "startFrame": b_source_start - dissolve_duration,
        "endFrame": b_source_end,
    }
    pool.append_to_timeline([clip_info])

    items_v1 = tl.get_item_list_in_track("video", track_index)
    items_v2 = tl.get_item_list_in_track("video", overlay_track)

    found_clip_a = None
    for it in items_v1:
        if it.get_end() == a_end:
            found_clip_a = it
            break
    if found_clip_a is None:
        return "Failed to find clip A after rearranging tracks"

    found_clip_b = None
    for it in items_v2:
        if it.get_start() == new_record_frame:
            found_clip_b = it
            break
    if found_clip_b is None:
        return "Failed to find clip B on overlay track after insertion"

    return {
        "clip_a": found_clip_a,
        "clip_b": found_clip_b,
        "a_name": a_name,
        "b_name": b_name,
        "overlay_track": overlay_track,
    }


def register_transition_tools(mcp: FastMCP, state: ServerState):

    @mcp.tool()
    @resolve_tool
    def resolve_list_available_transitions() -> str:
        """List available Fusion transition presets.

        Returns names of .comp files in the presets/transitions directory.
        Custom presets can be added by placing .comp files in that directory.
        """
        if not PRESETS_DIR.is_dir():
            return "No presets directory found."
        names = sorted(p.stem for p in PRESETS_DIR.glob("*.comp"))
        return format_list(names, "transition presets")

    @mcp.tool()
    @resolve_tool
    def resolve_apply_transition(
        track_type: str, track_index: int, item_index: int,
        transition_name: str,
    ) -> str:
        """Apply a Fusion transition preset to a timeline clip.

        The transition replaces the clip's Fusion composition with the preset.
        Use resolve_list_available_transitions to see available presets.

        Args:
            track_type: Track type (video or audio).
            track_index: Track index (1-based).
            item_index: Item index within the track (0-based).
            transition_name: Name of the transition preset (e.g. 'fade_out').
        """
        preset_path = PRESETS_DIR / f"{transition_name}.comp"
        if not preset_path.is_file():
            available = sorted(p.stem for p in PRESETS_DIR.glob("*.comp"))
            return f"Transition '{transition_name}' not found. Available: {', '.join(available)}"
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return f"Item not found at {track_type}:{track_index}:{item_index}"
        item.import_fusion_comp(str(preset_path))
        return f"Applied '{transition_name}' transition to {item.get_name()}"

    @mcp.tool()
    @resolve_tool
    def resolve_import_transition_preset(
        track_type: str, track_index: int, item_index: int,
        preset_path: str,
    ) -> str:
        """Import a custom Fusion composition (.comp) file as a transition on a clip.

        Args:
            track_type: Track type (video or audio).
            track_index: Track index (1-based).
            item_index: Item index within the track (0-based).
            preset_path: Absolute path to the .comp or .setting file.
        """
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return f"Item not found at {track_type}:{track_index}:{item_index}"
        item.import_fusion_comp(preset_path)
        return f"Imported Fusion comp from {preset_path} onto {item.get_name()}"

    @mcp.tool()
    @resolve_tool
    def resolve_apply_cross_dissolve(
        track_index: int,
        item_index_a: int,
        item_index_b: int,
        dissolve_duration: int = 30,
    ) -> str:
        """Apply a cross dissolve between two adjacent video clips.

        Clip B is moved to a higher video track and shifted back to create
        an overlap region. A Fusion comp is applied to clip B that ramps
        its opacity from 0 to 1 over the overlap, so clip A on the lower
        track shows through during the transition.

        Requires that the second clip has enough source material before its
        current in-point to extend back by dissolve_duration frames
        (i.e. left_offset >= dissolve_duration).

        Args:
            track_index: Video track index (1-based) where both clips live.
            item_index_a: Index of the first clip (0-based).
            item_index_b: Index of the second clip (0-based), must be adjacent.
            dissolve_duration: Overlap duration in frames (default 30).
        """
        tl = get_timeline(state)
        pool = get_pool(state)

        result = _setup_overlay_transition(
            state, tl, pool, track_index,
            item_index_a, item_index_b, dissolve_duration,
        )
        if isinstance(result, str):
            return result

        clip_b = result["clip_b"]
        a_name = result["a_name"]
        b_name = result["b_name"]

        _apply_comp_from_template(
            clip_b, _CROSS_DISSOLVE_TEMPLATE,
            dissolve_duration=dissolve_duration,
        )

        return (
            f"Applied cross dissolve ({dissolve_duration} frames) between "
            f"'{a_name}' and '{b_name}'"
        )

    @mcp.tool()
    @resolve_tool
    def resolve_apply_blur_transition(
        track_index: int,
        item_index_a: int,
        item_index_b: int,
        dissolve_duration: int = 30,
        blur_size: float = 15.0,
    ) -> str:
        """Apply a blur transition between two adjacent video clips.

        Clip A gets a blur that ramps up over the last dissolve_duration
        frames. Clip B is moved to a higher video track with an overlap;
        it gets both a blur ramp (high to zero) and an opacity ramp
        (transparent to opaque) so it fades in while unblurring.

        Requires that the second clip has enough source material before its
        current in-point to extend back by dissolve_duration frames
        (i.e. left_offset >= dissolve_duration).

        Args:
            track_index: Video track index (1-based) where both clips live.
            item_index_a: Index of the first clip (0-based).
            item_index_b: Index of the second clip (0-based), must be adjacent.
            dissolve_duration: Overlap duration in frames (default 30).
            blur_size: Maximum blur amount (default 15.0).
        """
        tl = get_timeline(state)
        pool = get_pool(state)

        result = _setup_overlay_transition(
            state, tl, pool, track_index,
            item_index_a, item_index_b, dissolve_duration,
        )
        if isinstance(result, str):
            return result

        clip_a = result["clip_a"]
        clip_b = result["clip_b"]
        a_name = result["a_name"]
        b_name = result["b_name"]

        _apply_comp_from_template(
            clip_a, _BLUR_OUT_TEMPLATE,
            dissolve_duration=dissolve_duration,
            blur_size=blur_size,
        )
        _apply_comp_from_template(
            clip_b, _BLUR_IN_FADE_TEMPLATE,
            dissolve_duration=dissolve_duration,
            blur_size=blur_size,
        )

        return (
            f"Applied blur transition ({dissolve_duration} frames, "
            f"blur_size={blur_size}) between '{a_name}' and '{b_name}'"
        )
