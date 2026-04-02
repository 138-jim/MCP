# DaVinci Resolve MCP — AI Usage Guide

This guide helps AI assistants use the Resolve MCP tools effectively. It covers workflows, parameter conventions, and common pitfalls.

## Getting Started

1. **Connect** — The server connects to a running DaVinci Resolve instance automatically on first tool call. Resolve must already be open.
2. **Check version** — Call `resolve_get_version` to confirm the connection is working.
3. **Check current page** — `resolve_get_current_page` returns which Resolve page is active (media, cut, edit, fusion, color, fairlight, deliver). Some operations require being on a specific page.
4. **Switch pages** — `resolve_set_page` with one of: `media`, `cut`, `edit`, `fusion`, `color`, `fairlight`, `deliver`.

## Project & Timeline Workflow

### Opening a project
```
resolve_list_projects          → see available projects
resolve_load_project(name)     → open one
resolve_get_current_project    → confirm what's open
```

### Switching timelines
```
resolve_list_timelines                → list all timelines in the project
resolve_set_current_timeline(name)    → switch to one by name
resolve_get_current_timeline          → get name, frame range, start timecode
```

### Project settings
```
resolve_get_project_setting("")                            → all settings
resolve_get_project_setting("timelineFrameRate")           → e.g. "24"
resolve_set_project_setting("timelineFrameRate", "29.97")  → set frame rate for new timelines
```
Frame rate applies to **new timelines only** — you cannot change an existing timeline's frame rate.
Drop frame: append "DF", e.g. `"29.97 DF"`.

Other useful keys: `timelineResolutionWidth`, `timelineResolutionHeight`, `superScale`.

### Creating timelines
```
resolve_create_timeline(name)                        → empty timeline
resolve_create_timeline_from_clips(name, clip_names)  → from media pool clips
```

## Track & Item Addressing

- **track_type**: Always a string — `"video"`, `"audio"`, or `"subtitle"`.
- **track_index**: **1-based** integer. Track 1 is the bottom/first track.
- **item_index**: **0-based** integer. The first clip in a track is index 0.

Example: The second clip on video track 1 → `track_type="video", track_index=1, item_index=1`.

### Listing items in a track
```
resolve_get_track_count("video")          → number of video tracks
resolve_list_items_in_track("video", 1)   → clip names on V1
```

## Editing Philosophy: Build a Cut List, Then Assemble

The Resolve scripting API does not support "trim like a human" — there are no setters for LeftOffset/RightOffset, and no general ripple-trim tool. Instead, the API excels at **assembling timelines from explicit clip placements**.

The recommended approach for automated editing is:

1. **Build a cut list** — a list of segments, each with a clip name, source in/out, track, and timeline position.
2. **Create a fresh timeline** and assemble it from the cut list using `AppendToTimeline` with clipInfo dicts.
3. **To "trim"** — change `start_frame`/`end_frame` in the cut list and reassemble.
4. **To "split"** — turn one segment into two entries in the cut list.
5. **To "ripple"** — recompute `record_frame` for all downstream segments.

This gives you repeatable, deterministic edits. If you need interchange, Resolve can export a real EDL from any assembled timeline.

### Assembling a timeline from a cut list
```
# 1. Import media
resolve_import_media("/path/to/clip_a.mp4,/path/to/clip_b.mp4")

# 2. Create an empty timeline
resolve_create_timeline("My Edit v1")

# 3. Place clips with precise source ranges and timeline positions
resolve_insert_clip_at_frame(
    clip_name="clip_a.mp4",
    record_frame=0,          # timeline starts at frame 0
    start_frame=100,         # source in
    end_frame=500,           # source out
    track_index=1
)
resolve_insert_clip_at_frame(
    clip_name="clip_b.mp4",
    record_frame=400,        # next position (0 + 400 frames)
    start_frame=0,
    end_frame=300,
    track_index=1
)
```

### Quick append (no precise positioning needed)
```
resolve_import_media("/path/to/clip.mp4")
resolve_append_clips_to_timeline("clip.mp4")     → append full clip to end
```

### Inspecting existing clips
```
resolve_get_item_offsets("video", 1, 0)   → LeftOffset, RightOffset, source range, duration
resolve_get_item_info("video", 1, 0)      → name, start/end frame, duration
```
Use `resolve_get_item_offsets` to read current trim state. Offsets are **read-only** — to change a clip's range, rebuild the segment.

### Deleting clips
```
resolve_delete_items(
    track_type="video",
    track_index=1,
    item_indices="0,2",    # comma-separated, 0-based
    ripple=True             # close gaps
)
```

### Clip properties
```
resolve_get_item_properties("video", 1, 0)              → all properties
resolve_get_item_property("video", 1, 0, "ZoomX")       → single property
resolve_set_item_property("video", 1, 0, "Opacity", "50")
```
Common property keys: `Pan`, `Tilt`, `ZoomX`, `ZoomY`, `Opacity`, `CompositeMode`.

## AI Clip Operations

### Smart Reframe

```
resolve_list_items_in_track("video", 1)         → find target clip index
resolve_smart_reframe("video", 1, 0)            → apply to first clip on V1
```

- Works on timeline items addressed by `track_type`, `track_index`, and `item_index`.
- Use `track_type="video"` for normal reframing workflows.
- Returns `Smart Reframe applied` on success.
- Returns `Failed to apply Smart Reframe` if Resolve rejects the operation.
- Returns `Item not found at ...` if indexing is wrong.

### Stabilization (related)

```
resolve_stabilize_clip("video", 1, 0)
```

- Uses the same item-addressing pattern as Smart Reframe.

## Media Pool

### Navigating bins
```
resolve_get_current_bin      → current bin name
resolve_list_bins            → subfolders of current bin
resolve_set_current_bin(name) → switch bin (searches from root)
resolve_create_bin(name)     → create new subfolder
```

### Clip metadata
```
resolve_get_clip_metadata("clip.mp4")            → all metadata
resolve_set_clip_metadata("clip.mp4", "Comments", "Hero shot")
```

## Media Storage

Browse the filesystem for files to import:
```
resolve_get_mounted_volumes       → list storage volumes
resolve_browse_volume("/path")    → list subfolders
resolve_list_files("/path")       → list files
resolve_import_files_to_pool("/path/to/file1.mp4, /path/to/file2.mp4")
```

## Generators and Titles

Insert by name — there is no tool to list available generators/titles at runtime:
```
resolve_insert_generator("Solid Color")
resolve_insert_title("Text+")
resolve_insert_fusion_title("Scroll Title")
resolve_insert_fusion_generator("Noise")
```
You must know the exact generator/title name. Common names:
- Generators: `"Solid Color"`, `"10 Step"`, `"Grey Scale"`, `"Window"`, `"YCbCr Ramp"`
- Titles: `"Text+"`, `"Fusion Title"`, `"Left Lower Third"`, `"Middle Lower Third"`, `"Scroll Title"`

### Editing Text+ content via Fusion
After inserting a title, edit its text through Fusion tool inputs:
```
resolve_set_fusion_tool_input(
    track_type="video", track_index=1, item_index=0,
    tool_id="TextPlus", input_name="StyledText", value="Hello World"
)
```
Common TextPlus inputs: `StyledText`, `Size`, `Font`, `ColorRed`, `ColorGreen`, `ColorBlue`.

### Easy Text+ overlays (single tool)
For common "title over video" workflows, use:
```
resolve_add_text_overlay(
    text="My Title",
    overlay_track=2,
    size="0.10",
    font="Open Sans"
)
```
This tool inserts a Fusion `Text+` title and sets `StyledText` (and optional size/font) in one call.
If `start_timecode` is omitted, it auto-aligns to the first clip start on V1.

## Transitions (Fusion-Based)

Import a Fusion composition (.comp) file onto a clip to use as a transition:
```
resolve_import_transition_preset("video", 1, 0, "/path/to/my_wipe.comp")
```

## Markers

Markers exist on both timelines and individual clips:
```
# Timeline markers
resolve_add_timeline_marker(frame=100, color="Blue", name="Review", note="Check audio")
resolve_get_timeline_markers
resolve_delete_timeline_marker(frame=100)

# Clip markers (on timeline items)
resolve_add_item_marker("video", 1, 0, frame=10, color="Red", name="Fix")
resolve_get_item_markers("video", 1, 0)
```
Marker colors: `Blue`, `Cyan`, `Green`, `Yellow`, `Red`, `Pink`, `Purple`, `Fuchsia`, `Rose`, `Lavender`, `Sky`, `Mint`, `Lemon`, `Sand`, `Cocoa`, `Cream`.

## Color Grading

**Important**: Switch to the Color page first with `resolve_set_page("color")`.

### Node operations
```
resolve_get_node_count("video", 1, 0)                    → number of nodes
resolve_set_node_lut("video", 1, 0, node_index=1, lut_path="/path/to/lut.cube")
resolve_get_node_lut("video", 1, 0, node_index=1)
resolve_reset_grades("video", 1, 0)                      → reset all grading
```
- **node_index is 1-based**.

### Grades from stills
```
resolve_apply_grade_from_drx("video", 1, 0, drx_path="/path/to/grade.drx", grade_mode=0)
```
Grade modes: `0` = No keyframes, `1` = Source timecode aligned, `2` = Start timecode aligned.

### Color groups and gallery
```
resolve_list_color_groups
resolve_add_color_group("Interview Grades")
resolve_list_gallery_albums
resolve_export_still("/path/to/still.png")
```

### Color versions
```
resolve_list_color_versions("video", 1, 0, version_type="local")
resolve_load_color_version("video", 1, 0, name="Version 2", version_type="local")
```

## Color Nodes (Detailed)

### Browsing and applying LUTs

```
resolve_list_lut_folders                          → browse LUT categories
resolve_list_lut_folders(subfolder="Arri")        → drill into a category
resolve_search_luts(search="rec709")              → find LUTs by name
resolve_apply_lut_by_name("video", 1, 0, node_index=1, search="rec709")  → search + apply in one step
resolve_set_node_lut("video", 1, 0, node_index=1, lut_path="/path/to/lut.cube")  → apply by exact path
resolve_refresh_lut_list                          → refresh after adding new LUT files
```

### CDL values

```
resolve_get_cdl("video", 1, 0)
resolve_set_cdl("video", 1, 0, slope="1.1 1.0 0.9", offset="0.01 0 -0.01", saturation="1.2")
```

Slope, offset, and power are RGB triplets as space-separated strings. Node index defaults to 1.

### Node control

```
resolve_get_node_count("video", 1, 0)
resolve_get_node_label("video", 1, 0, node_index=1)
resolve_set_node_enabled("video", 1, 0, node_index=1, enabled=False)
resolve_get_node_cache_mode("video", 1, 0, node_index=1)     → 0=None, 1=Smart, 2=On
resolve_set_node_cache_mode("video", 1, 0, node_index=1, mode=2)  → cache on
resolve_get_tools_in_node("video", 1, 0, node_index=1)
```

### Copying and exporting grades

```
resolve_copy_grades("video", 1, source_item_index=0, target_item_indices="1,2,3")
resolve_export_lut("video", 1, 0, export_type="LUT_33PTCUBE", path="/path/output.cube")
```

Export types: `LUT_17PTCUBE`, `LUT_33PTCUBE`, `LUT_65PTCUBE`, `LUT_PANASONICVLUT`.

## Color Groups

Color groups let you organize clips that share grading characteristics (e.g., all A-cam shots, all interviews).

```
resolve_list_color_groups
resolve_add_color_group("A-Cam")
resolve_set_color_group_name(current_name="A-Cam", new_name="Main Camera")
resolve_get_clips_in_color_group("A-Cam")           → clips in current timeline
```

### Assigning clips to groups

```
resolve_assign_to_color_group("video", 1, 0, group_name="A-Cam")
resolve_get_item_color_group("video", 1, 0)          → check assignment
resolve_remove_from_color_group("video", 1, 0)       → unassign
```

### Group node graphs

Color groups have pre-clip and post-clip node graphs that affect all clips in the group:

```
resolve_get_color_group_pre_node_graph("A-Cam")
resolve_get_color_group_post_node_graph("A-Cam")
```

## Gallery & Stills

### Grabbing stills

```
resolve_set_page("color")
resolve_grab_still                                    → grab current frame
resolve_grab_all_stills(still_frame_source=1)         → grab from all clips (1=first, 2=middle)
```

### Album management

```
resolve_list_gallery_albums                           → list still albums
resolve_get_current_still_album
resolve_set_current_still_album(album_index=2)        → 1-based index
resolve_create_still_album                            → new album
resolve_create_powergrade_album                       → new PowerGrade album
resolve_set_album_name(album_index=1, name="Selects")
resolve_list_powergrade_albums
```

### Working with stills

```
resolve_list_stills                                   → list stills in current album
resolve_get_still_label(still_index=1)                → 1-based index
resolve_set_still_label(still_index=1, label="Hero")
resolve_import_stills(paths="/path/to/ref1.dpx,/path/to/ref2.dpx")
resolve_export_stills(still_indices="1,2", path="/exports/", format="png")
resolve_delete_stills(still_indices="3,4")
```

## Color Versions

Color versions let you save multiple grade iterations on the same clip.

```
resolve_list_color_versions("video", 1, 0, version_type="local")
resolve_get_current_color_version("video", 1, 0)
resolve_add_color_version("video", 1, 0, name="Warm Look", version_type="local")
resolve_load_color_version("video", 1, 0, name="Warm Look", version_type="local")
resolve_rename_color_version("video", 1, 0, old_name="Version 1", new_name="Original")
resolve_delete_color_version("video", 1, 0, name="Old Version", version_type="local")
```

Version types: `"local"` (default) or `"remote"` (for shared/collaborative grading).

---

## Rendering / Deliver

### Typical render workflow
```
resolve_set_page("deliver")
resolve_set_render_format_and_codec(format="mp4", codec="H265")
resolve_set_render_settings(target_dir="/output/path", custom_name="final_export")
resolve_add_render_job
resolve_start_render
```

### Using presets
```
resolve_list_render_presets
resolve_load_render_preset("YouTube 1080p")
resolve_set_render_settings(target_dir="/output/path")
resolve_add_render_job
resolve_start_render
```

### Monitoring render progress
```
resolve_is_rendering         → check if still rendering
resolve_get_render_status(job_id)
resolve_list_render_jobs     → see all queued jobs
```

## Audio / Fairlight

### Insert external audio at playhead

```
resolve_set_page("fairlight")
resolve_set_current_timecode("00:00:10:00")
resolve_insert_audio_at_playhead(
    file_path="/path/audio.wav",
    start_offset_samples=0,
    duration_samples=0
)
```

- **Requires the Fairlight page** with an audio track selected.
- `file_path` must be an absolute path to an audio file.
- `start_offset_samples` and `duration_samples` are in **samples** (e.g. 44100 = 1 second at 44.1 kHz).
- `duration_samples=0` means "use full clip length".
- Audio is inserted to the **currently targeted audio track** at the playhead.

### Load a burn-in preset

```
resolve_load_burn_in_preset("Timecode")
```

- Loads a project burn-in preset (useful before render export).
- Fails if the preset name does not exist in the current project.

### Related tools for audio tracks

These are generic timeline tools, but they support `track_type="audio"`:

```
resolve_get_track_count("audio")
resolve_add_track("audio")
resolve_get_track_name("audio", 1)
resolve_set_track_name("audio", 1, "Dialog")
resolve_list_items_in_track("audio", 1)
resolve_delete_items(track_type="audio", track_index=1, item_indices=[0], ripple=False)
```

For clip-level info/operations on audio clips, use timeline-item tools with
`track_type="audio"` (for example `resolve_get_item_info`, `resolve_get_item_properties`, and markers).

### Current limitations

- Voice isolation tools are disabled in this server (`resolve_voice_isolation_timeline`, `resolve_voice_isolation_clip`).
- Subtitle-from-audio is also disabled (`resolve_create_subtitle_from_audio`).

## Timecodes and Frames

- **Timelines start at frame 0** (timecode `00:00:00:00`), not `01:00:00:00`.
- **Timecode format**: `"HH:MM:SS:FF"` (e.g., `"00:00:05:00"`).
- **Frames**: Integer values. Use `resolve_get_current_timeline` to see the frame range.
- Move the playhead: `resolve_set_current_timecode("00:00:10:00")`.

## Tips and Pitfalls

1. **Assemble, don't trim** — The Resolve scripting API has no way to modify a clip's trim offsets in place. Build a cut list of segments (clip, sourceIn, sourceOut, recordFrame, trackIndex) and assemble the timeline from scratch. To change a cut, update the cut list and reassemble.

2. **Generators/titles cannot be listed** — The tools to list available generators and titles are disabled because the API methods don't exist in all Resolve versions. Insert by name using known names.

3. **Some features need Resolve Studio** — Magic Mask, voice isolation, and subtitle-from-audio require the paid Studio version. These tools are disabled in the free version.

4. **Always check the current page** — Color operations need the Color page. Render operations work best from the Deliver page. Timeline editing works from Edit or Cut.

5. **Track indices are 1-based, item indices are 0-based** — This is the most common source of off-by-one errors.

6. **Clip names must match exactly** — When referencing clips by name (for media pool operations), the name must be an exact match. Use `resolve_list_clips_in_bin` to get the correct names.

7. **Comma-separated inputs** — Several tools accept comma-separated strings instead of arrays: `resolve_import_media`, `resolve_append_clips_to_timeline`, `resolve_delete_items` (item_indices), and `resolve_insert_clip_at_frame`.

8. **Export type constants** — For `resolve_export_timeline`, use the format name string (e.g., `"EDL"`, `"AAF"`, `"FCP_7_XML"`), not a numeric constant.

9. **The connection is lazy** — The first tool call triggers connection to Resolve. If Resolve isn't running, you'll get a connection error. No explicit connect step needed.

10. **Export EDLs for interchange** — After assembling a timeline, use `resolve_export_timeline` to export a real EDL if you need the cut list in a standard format.

## Fusion Scripting Tools

These tools provide direct access to the Fusion scripting API within a timeline item's composition. They complement the basic Fusion tools (`resolve_add_fusion_comp`, `resolve_set_fusion_tool_input`, `resolve_get_fusion_tool_input`) with advanced capabilities like node creation, connections, keyframes, Lua scripting, and performance controls.

All Fusion scripting tools share the same item-addressing pattern: `track_type`, `track_index`, `item_index`, plus an optional `comp_index` (1-based, default 1).

### Lock / Unlock (Batch Performance)

Use `Lock` before making multiple changes to prevent Resolve from re-rendering after every single operation. Always `Unlock` when done.

```
resolve_fusion_lock("video", 1, 0)
# ... make many changes ...
resolve_fusion_unlock("video", 1, 0)
```

**When to use**: Any time you are making 3+ changes to a composition in a row. Locking can reduce execution time by 10x or more for batch operations.

### Start Undo / End Undo (Atomic Changes)

Group multiple operations into a single undoable action. The user sees one "Undo" entry instead of many.

```
resolve_fusion_start_undo("video", 1, 0, name="Add colour grade chain")
# ... multiple add_tool / connect / set_input calls ...
resolve_fusion_end_undo("video", 1, 0, keep=True)
```

Set `keep=False` to discard all changes made since `start_undo` (useful for error recovery).

### Adding Tools

```
resolve_fusion_add_tool("video", 1, 0, tool_type="ColorCorrector")
resolve_fusion_add_tool("video", 1, 0, tool_type="Merge")
resolve_fusion_add_tool("video", 1, 0, tool_type="Transform")
```

Common tool types: `Background`, `Merge`, `Transform`, `ColorCorrector`, `Blur`, `Glow`, `BrightnessContrast`, `ChannelBooleans`, `FastNoise`, `Polygon`, `BSpline`, `Ellipse`, `Rectangle`, `Plasma`, `Text+`.

Returns the instance name (e.g. `"ColorCorrector1"`) which you use in subsequent calls.

### Connecting Tools

```
resolve_fusion_connect("video", 1, 0,
    tool_name="Merge1", input_name="Background", target_tool="Background1")
resolve_fusion_connect("video", 1, 0,
    tool_name="Merge1", input_name="Foreground", target_tool="Text1")
```

Common input names on Merge: `Background`, `Foreground`. On most tools: `Input`.

### Setting and Getting Inputs (by Tool Name)

```
resolve_fusion_set_input("video", 1, 0,
    tool_name="ColorCorrector1", input_name="Gain", value="1.2")
resolve_fusion_get_input("video", 1, 0,
    tool_name="ColorCorrector1", input_name="Gain")
```

These tools look up tools by their instance name (e.g. `"Background1"`, `"Merge1"`) rather than by type ID. Values are auto-converted: numeric strings become float/int.

### Listing Tools

```
resolve_fusion_get_tool_list("video", 1, 0)
```

Returns all tool names and their types in the composition. Useful for discovering what nodes exist before modifying them.

### Keyframes (Animation)

```
resolve_fusion_add_keyframe("video", 1, 0,
    tool_name="Transform1", input_name="Size", time=0, value="1.0")
resolve_fusion_add_keyframe("video", 1, 0,
    tool_name="Transform1", input_name="Size", time=30, value="1.5")
```

You can also pass `time` to `resolve_fusion_set_input` for the same effect.

### Lua Script Execution

For complex multi-step operations, use `resolve_fusion_execute` to run a Lua script directly in the composition context. The `comp` variable is available automatically.

```
resolve_fusion_execute("video", 1, 0, script="""
    local bg = comp:AddTool("Background", -32768, -32768)
    bg.TopLeftRed = 0.2
    bg.TopLeftGreen = 0.1
    bg.TopLeftBlue = 0.3
    local mg = comp:AddTool("Merge", -32768, -32768)
    mg.Background = bg
    mg.Foreground = comp.MediaIn1
""")
```

**Performance tip**: Use `execute()` for multi-step operations (5+ calls) to avoid per-call round-trip overhead. A single Lua script is faster than multiple individual tool calls.

### Example: Building a Colour Grade Node Chain

```
# Lock for batch performance
resolve_fusion_lock("video", 1, 0)
resolve_fusion_start_undo("video", 1, 0, name="Add colour grade")

# Add nodes
resolve_fusion_add_tool("video", 1, 0, tool_type="ColorCorrector")
resolve_fusion_add_tool("video", 1, 0, tool_type="Merge")

# Connect: MediaIn -> ColorCorrector -> Merge -> MediaOut
resolve_fusion_connect("video", 1, 0,
    tool_name="ColorCorrector1", input_name="Input", target_tool="MediaIn1")
resolve_fusion_connect("video", 1, 0,
    tool_name="Merge1", input_name="Background", target_tool="ColorCorrector1")
resolve_fusion_connect("video", 1, 0,
    tool_name="MediaOut1", input_name="Input", target_tool="Merge1")

# Set grade values
resolve_fusion_set_input("video", 1, 0,
    tool_name="ColorCorrector1", input_name="MasterGain", value="1.15")
resolve_fusion_set_input("video", 1, 0,
    tool_name="ColorCorrector1", input_name="MasterSaturation", value="1.1")

resolve_fusion_end_undo("video", 1, 0, keep=True)
resolve_fusion_unlock("video", 1, 0)
```

### Example: Complex Effect via Lua Script

```
resolve_fusion_execute("video", 1, 0, script="""
    comp:Lock()
    comp:StartUndo("Vignette effect")

    local ell = comp:AddTool("EllipseMask", -32768, -32768)
    ell.Width = 1.8
    ell.Height = 1.8
    ell.SoftEdge = 0.3

    local bc = comp:AddTool("BrightnessContrast", -32768, -32768)
    bc.Gain = 0.6
    bc.EffectMask = ell

    local mg = comp:AddTool("Merge", -32768, -32768)
    mg.Background = comp.MediaIn1
    mg.Foreground = bc
    comp.MediaOut1.Input = mg

    comp:EndUndo(true)
    comp:Unlock()
""")
```

### Tool Parameter Reference

| Tool | Parameter | Description |
|------|-----------|-------------|
| `resolve_fusion_lock` | `track_type`, `track_index`, `item_index`, `comp_index` | Lock comp (prevent rendering) |
| `resolve_fusion_unlock` | `track_type`, `track_index`, `item_index`, `comp_index` | Unlock comp (resume rendering) |
| `resolve_fusion_start_undo` | + `name` | Start undo group |
| `resolve_fusion_end_undo` | + `keep` (bool) | End undo group |
| `resolve_fusion_add_tool` | + `tool_type` | Add a tool node |
| `resolve_fusion_connect` | + `tool_name`, `input_name`, `target_tool` | Connect tool output to input |
| `resolve_fusion_set_input` | + `tool_name`, `input_name`, `value`, `time` | Set input value |
| `resolve_fusion_get_input` | + `tool_name`, `input_name`, `time` | Get input value |
| `resolve_fusion_get_tool_list` | (base params only) | List all tools |
| `resolve_fusion_execute` | + `script` | Run Lua script |
| `resolve_fusion_add_keyframe` | + `tool_name`, `input_name`, `time`, `value` | Add keyframe |
