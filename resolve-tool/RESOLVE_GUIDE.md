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
    record_frame=86400,      # timeline frame (01:00:00:00 at 24fps)
    start_frame=100,         # source in
    end_frame=500,           # source out
    track_index=1
)
resolve_insert_clip_at_frame(
    clip_name="clip_b.mp4",
    record_frame=86800,      # next position (86400 + 400 frames)
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

```
resolve_insert_audio_at_playhead(file_path="/path/audio.wav", start_offset=0, duration=0)
resolve_load_burn_in_preset("Timecode")
```
Set `duration=0` for full clip length.

## Timecodes and Frames

- **Timecode format**: `"HH:MM:SS:FF"` (e.g., `"01:00:05:00"`).
- **Frames**: Integer values. Use `resolve_get_current_timeline` to see the frame range.
- Move the playhead: `resolve_set_current_timecode("01:00:10:00")`.

## Tips and Pitfalls

1. **Assemble, don't trim** — The Resolve scripting API has no way to modify a clip's trim offsets in place. Build a cut list of segments (clip, sourceIn, sourceOut, recordFrame, trackIndex) and assemble the timeline from scratch. To change a cut, update the cut list and reassemble.

2. **Generators/titles cannot be listed** — The tools to list available generators and titles are disabled because the API methods don't exist in all Resolve versions. Insert by name using known names.

3. **Some features need Resolve Studio** — Magic Mask, voice isolation, and subtitle-from-audio require the paid Studio version. These tools are disabled in the free version.

4. **Always check the current page** — Color operations need the Color page. Render operations work best from the Deliver page. Timeline editing works from Edit or Cut.

5. **Track indices are 1-based, item indices are 0-based** — This is the most common source of off-by-one errors.

6. **Clip names must match exactly** — When referencing clips by name (for media pool operations), the name must be an exact match. Use `resolve_list_clips_in_bin` to get the correct names.

7. **Save often** — Call `resolve_save_project` periodically. There is no auto-save through the API.

8. **Comma-separated inputs** — Several tools accept comma-separated strings instead of arrays: `resolve_import_media`, `resolve_append_clips_to_timeline`, `resolve_delete_items` (item_indices), and `resolve_insert_clip_at_frame`.

9. **Export type constants** — For `resolve_export_timeline`, use the format name string (e.g., `"EDL"`, `"AAF"`, `"FCP_7_XML"`), not a numeric constant.

10. **The connection is lazy** — The first tool call triggers connection to Resolve. If Resolve isn't running, you'll get a connection error. No explicit connect step needed.

11. **Export EDLs for interchange** — After assembling a timeline, use `resolve_export_timeline` to export a real EDL if you need the cut list in a standard format.
