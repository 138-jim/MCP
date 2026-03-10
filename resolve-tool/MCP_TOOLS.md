# DaVinci Resolve MCP Server — Tool Reference

162 tools for controlling DaVinci Resolve via the Model Context Protocol.
Tested against DaVinci Resolve 20.3 (Free).

---

## Session & Application

Control the Resolve application, pages, and UI layout.

| Tool | Parameters | Description |
|------|-----------|-------------|
| `resolve_get_version` | — | Get the DaVinci Resolve version string |
| `resolve_get_current_page` | — | Get the currently open page (media, cut, edit, fusion, color, fairlight, deliver) |
| `resolve_set_page` | `page` | Switch to a Resolve page |
| `resolve_get_keyframe_mode` | — | Get keyframe mode (0=All, 1=Color, 2=Sizing) |
| `resolve_set_keyframe_mode` | `mode` | Set keyframe mode |
| `resolve_load_layout_preset` | `name` | Load a saved UI layout preset |
| `resolve_import_layout_preset` | `name`, `path` | Import a UI layout preset from a file |
| `resolve_reconnect` | — | Force reconnection to Resolve (use if Resolve was restarted) |
| `resolve_quit` | — | Quit DaVinci Resolve |

---

## Database & Project Management

Manage databases, project folders, and projects.

| Tool | Parameters | Description |
|------|-----------|-------------|
| `resolve_list_databases` | — | List all available databases |
| `resolve_get_current_database` | — | Get info about the active database |
| `resolve_switch_database` | `db_name`, `db_type?`, `ip_address?` | Switch to a different database |
| `resolve_list_project_folders` | — | List folders in the current database location |
| `resolve_open_project_folder` | `path` | Open a project folder by path |
| `resolve_create_project_folder` | `name` | Create a new folder in the database |
| `resolve_goto_root_folder` | — | Navigate to root project folder |
| `resolve_goto_parent_folder` | — | Navigate to parent project folder |
| `resolve_delete_project_folder` | `name` | Delete a project folder |
| `resolve_list_projects` | — | List all projects in the current folder |
| `resolve_create_project` | `name` | Create and open a new project |
| `resolve_load_project` | `name` | Load an existing project |
| `resolve_get_current_project` | — | Get name of the current project |
| `resolve_get_project_setting` | `key` | Get a project setting (empty key = all settings) |
| `resolve_set_project_setting` | `key`, `value` | Set a project setting (e.g. timelineFrameRate) |
| `resolve_export_project` | `name`, `path`, `with_stills_and_luts?` | Export a project to a file |
| `resolve_import_project` | `path`, `name?` | Import a project from a file |

---

## Media Storage

Browse and import from mounted storage volumes.

| Tool | Parameters | Description |
|------|-----------|-------------|
| `resolve_get_mounted_volumes` | — | List all mounted media storage volumes |
| `resolve_browse_volume` | `path` | List subfolders at a media storage path |
| `resolve_list_files` | `path` | List files at a media storage path |
| `resolve_import_files_to_pool` | `paths` (comma-separated) | Import files from storage into the media pool |

---

## Media Pool

Manage bins, clips, metadata, markers, and timelines in the media pool.

### Bins & Folders

| Tool | Parameters | Description |
|------|-----------|-------------|
| `resolve_get_current_bin` | — | Get the name of the current media pool bin |
| `resolve_list_bins` | — | List subfolders (bins) in the current folder |
| `resolve_create_bin` | `name` | Create a new bin in the current folder |
| `resolve_set_current_bin` | `bin_name` | Set the current bin by name (searches subfolders) |
| `resolve_list_clips_in_bin` | — | List all clips in the current bin |
| `resolve_import_media` | `paths` (comma-separated) | Import media files into the current bin |

### Clip Operations

| Tool | Parameters | Description |
|------|-----------|-------------|
| `resolve_get_clip_metadata` | `clip_name`, `key?` | Get metadata for a clip (empty key = all metadata) |
| `resolve_set_clip_metadata` | `clip_name`, `key`, `value` | Set a metadata field on a clip |
| `resolve_get_clip_markers` | `clip_name` | Get all markers on a clip |
| `resolve_add_clip_marker` | `clip_name`, `frame`, `color`, `name`, `note?`, `duration?` | Add a marker to a clip |
| `resolve_set_clip_color` | `clip_name`, `color` | Set the clip color label |
| `resolve_add_clip_flag` | `clip_name`, `color` | Add a flag to a clip |
| `resolve_add_clip_mattes` | `clip_name`, `matte_paths` | Add mattes to a clip via media storage |
| `resolve_transcribe_bin` | — | Transcribe audio for all clips in the current bin |

---

## Timeline Management

Create, navigate, and configure timelines.

### Timelines

| Tool | Parameters | Description |
|------|-----------|-------------|
| `resolve_list_timelines` | — | List all timelines in the current project |
| `resolve_get_current_timeline` | — | Get name, frame range, and start timecode of current timeline |
| `resolve_set_current_timeline` | `name` | Switch to a timeline by name |
| `resolve_create_timeline` | `name` | Create an empty timeline |
| `resolve_create_timeline_from_clips` | `name`, `clip_names` (comma-separated) | Create a timeline from media pool clips |
| `resolve_import_timeline` | `path` | Import a timeline from AAF, EDL, XML, FCPXML, OTIO, etc. |
| `resolve_set_timeline_name` | `name` | Rename the current timeline |
| `resolve_duplicate_timeline` | `name?` | Duplicate the current timeline |
| `resolve_export_timeline` | `path`, `export_type`, `export_subtype?` | Export the timeline (AAF, DRT, EDL, FCP_7_XML, FCPXML_1_8, etc.) |

### Tracks

| Tool | Parameters | Description |
|------|-----------|-------------|
| `resolve_get_track_count` | `track_type` | Get number of tracks (video, audio, subtitle) |
| `resolve_add_track` | `track_type` | Add a new track |
| `resolve_get_track_name` | `track_type`, `index` | Get track name (1-based index) |
| `resolve_set_track_name` | `track_type`, `index`, `name` | Set track name |
| `resolve_list_items_in_track` | `track_type`, `index` | List all clips in a track |

### Playhead & Markers

| Tool | Parameters | Description |
|------|-----------|-------------|
| `resolve_get_current_timecode` | — | Get the current playhead timecode |
| `resolve_set_current_timecode` | `timecode` (e.g. `01:00:05:00`) | Set the playhead position |
| `resolve_get_timeline_markers` | — | Get all markers on the timeline |
| `resolve_add_timeline_marker` | `frame`, `color`, `name`, `note?`, `duration?` | Add a marker at a frame |
| `resolve_delete_timeline_marker` | `frame` | Delete a marker at a frame |

### Generators & Titles

| Tool | Parameters | Description |
|------|-----------|-------------|
| `resolve_insert_generator` | `name` | Insert a generator (e.g. `Solid Color`) at the playhead |
| `resolve_insert_title` | `name` | Insert a title template at the playhead |
| `resolve_insert_fusion_generator` | `name` | Insert a Fusion generator (e.g. `Contours`) |
| `resolve_insert_fusion_title` | `name` | Insert a Fusion title (e.g. `Text+`) |
| `resolve_add_text_overlay` | `text`, `start_timecode?`, `overlay_track?`, `size?`, `font?`, `title_name?` | Insert/configure a Fusion Text+ overlay in one call |

### Clips

| Tool | Parameters | Description |
|------|-----------|-------------|
| `resolve_append_clips_to_timeline` | `clip_names` (comma-separated) | Append clips to the end of the timeline |
| `resolve_insert_clip_at_frame` | `clip_name`, `record_frame`, `start_frame?`, `end_frame?`, `track_index?` | Insert a media pool clip at a specific timeline frame |
| `resolve_delete_items` | `track_type`, `track_index`, `item_indices` (comma-separated), `ripple?` | Delete clips from the timeline by index |

---

## Timeline Items (Clips on Timeline)

Inspect and modify clips placed on the timeline. Items are addressed by `track_type` (video/audio), `track_index` (1-based), and `item_index` (0-based within the track).

### Info & Properties

| Tool | Parameters | Description |
|------|-----------|-------------|
| `resolve_get_item_info` | `track_type`, `track_index`, `item_index` | Get name, start/end frame, duration |
| `resolve_get_item_properties` | `track_type`, `track_index`, `item_index` | Get all Inspector properties (Pan, Tilt, Zoom, Opacity, etc.) |
| `resolve_get_item_property` | `track_type`, `track_index`, `item_index`, `key` | Get a single property value |
| `resolve_set_item_property` | `track_type`, `track_index`, `item_index`, `key`, `value` | Set a property (Pan, Tilt, ZoomX, Opacity, CompositeMode, etc.) |
| `resolve_get_item_offsets` | `track_type`, `track_index`, `item_index` | Get trim offsets, source start/end, and timeline position |
| `resolve_set_item_clip_color` | `track_type`, `track_index`, `item_index`, `color` | Set the clip color label |

### Markers

| Tool | Parameters | Description |
|------|-----------|-------------|
| `resolve_get_item_markers` | `track_type`, `track_index`, `item_index` | Get all markers on a clip |
| `resolve_add_item_marker` | `track_type`, `track_index`, `item_index`, `frame`, `color`, `name`, `note?`, `duration?` | Add a marker to a clip |

### Fusion Compositions

| Tool | Parameters | Description |
|------|-----------|-------------|
| `resolve_list_fusion_comps` | `track_type`, `track_index`, `item_index` | List Fusion compositions on a clip |
| `resolve_add_fusion_comp` | `track_type`, `track_index`, `item_index` | Add a new Fusion composition |
| `resolve_set_fusion_tool_input` | `track_type`, `track_index`, `item_index`, `tool_id`, `input_name`, `value`, `comp_index?` | Set a Fusion tool input (e.g. Text+ text, size, font) |
| `resolve_get_fusion_tool_input` | `track_type`, `track_index`, `item_index`, `tool_id`, `input_name`, `comp_index?` | Get a Fusion tool input value |

**Common Fusion tool inputs:**

| tool_id | input_name | Example value | Description |
|---------|-----------|---------------|-------------|
| `TextPlus` | `StyledText` | `Hello World` | The text content |
| `TextPlus` | `Size` | `0.08` | Font size (0.0–1.0) |
| `TextPlus` | `Font` | `Open Sans` | Font family |
| `Background` | `TopLeftRed` | `0.5` | Red channel (0.0–1.0) |
| `Background` | `TopLeftGreen` | `0.5` | Green channel |
| `Background` | `TopLeftBlue` | `0.5` | Blue channel |

### AI Operations

| Tool | Parameters | Description |
|------|-----------|-------------|
| `resolve_stabilize_clip` | `track_type`, `track_index`, `item_index` | Apply AI stabilization |
| `resolve_smart_reframe` | `track_type`, `track_index`, `item_index` | Apply AI smart reframe |

Notes:
- `track_index` is 1-based and `item_index` is 0-based.
- Smart Reframe is typically used on video timeline items.

---

## Transitions (Fusion-Based)

Apply transition effects to timeline clips. There are two categories:

**Single-clip presets** — replace a clip's Fusion composition with a preset effect (fade in/out, dip to black/white). These are non-destructive and only affect one clip.

**Two-clip overlay transitions** — rearrange two adjacent clips onto separate tracks with an overlap, then apply Fusion `.comp` presets to individual clips for the transition effect (cross dissolve, blur transition). The original clips remain as regular media clips — no Fusion clips are created.

### Single-Clip Preset Transitions

**Built-in presets:** `fade_in`, `fade_out`, `dip_to_black`, `dip_to_white`

| Tool | Parameters | Description |
|------|-----------|-------------|
| `resolve_list_available_transitions` | — | List available Fusion transition preset names |
| `resolve_apply_transition` | `track_type`, `track_index`, `item_index`, `transition_name` | Apply a built-in transition preset to a clip |
| `resolve_import_transition_preset` | `track_type`, `track_index`, `item_index`, `preset_path` | Import a custom .comp file as a transition on a clip |

Notes:
- These replace the clip's Fusion composition with the preset's node graph.
- Each preset uses Fusion expressions referencing `comp.RenderEnd` so the transition timing adapts to the trimmed clip duration on the timeline.
- Default transition duration is ~30 frames from clip start/end.
- Custom presets can be added by placing `.comp` files in the `presets/transitions/` directory within the server package.

### Two-Clip Overlay Transitions

| Tool | Parameters | Description |
|------|-----------|-------------|
| `resolve_apply_cross_dissolve` | `track_index`, `item_index_a`, `item_index_b`, `dissolve_duration?` | Cross dissolve: clip B fades in over clip A during the overlap |
| `resolve_apply_blur_transition` | `track_index`, `item_index_a`, `item_index_b`, `dissolve_duration?`, `blur_size?` | Blur transition: clip A blurs out while clip B blurs in and fades in |

**How the overlay approach works:**

```
V2: |---- Clip B (Fusion comp applied) ----|
V1: |--- Clip A ---|
    ^              ^                        ^
    A_start     cut point               B_end
               (overlap region)
```

1. Clip B is deleted from the original track and re-inserted on a higher video track, shifted back by `dissolve_duration` frames. This creates an overlap region where both clips exist on separate tracks.
2. Fusion `.comp` presets are applied to individual clips (not a merged Fusion clip). The clips remain as regular media clips with Fusion compositions.
3. Clip B's comp uses a transparent background with a `Merge.Blend` ramp — at Blend=0, the background is transparent so clip A on the lower track shows through; at Blend=1, clip B is fully opaque.

**Effect on timeline length:** Clip B is extended backwards using `dissolve_duration` frames of earlier source material to fill the overlap — the total timeline duration does not change. Clip B must have enough unused source material before its in-point (`left_offset >= dissolve_duration`). Use `resolve_get_item_offsets` to check.

**Cross dissolve** applies a Fusion comp to clip B only. The comp ramps `Merge.Blend` from 0→1 over the first `dissolve_duration` frames — clip A remains untouched on the lower track and shows through during the ramp.

**Blur transition** applies Fusion comps to both clips:
- **Clip A** gets a blur that ramps from 0 to `blur_size` over the last `dissolve_duration` frames (clip A stays fully opaque, just blurs)
- **Clip B** gets both a blur ramp (from `blur_size` down to 0) and an opacity ramp (transparent to opaque) over the first `dissolve_duration` frames
- `blur_size` controls the maximum blur amount (default 15.0)

**Render cache:** After applying either transition, clips with Fusion comps may need caching. Right-click the clip → **Render Cache Fusion Output** → **On**, or enable **Playback → Render Cache → Smart**.

---

## Color Nodes

Color page node graph operations. Requires the Color page (`resolve_set_page("color")`).

| Tool | Parameters | Description |
|------|-----------|-------------|
| `resolve_get_node_count` | `track_type`, `track_index`, `item_index` | Get number of color nodes |
| `resolve_get_node_label` | `track_type`, `track_index`, `item_index`, `node_index` | Get the label of a color node (1-based) |
| `resolve_get_tools_in_node` | `track_type`, `track_index`, `item_index`, `node_index` | Get tool names in a color node |
| `resolve_set_node_enabled` | `track_type`, `track_index`, `item_index`, `node_index`, `enabled` | Enable or disable a color node |
| `resolve_get_node_lut` | `track_type`, `track_index`, `item_index`, `node_index` | Get LUT path on a node (1-based) |
| `resolve_set_node_lut` | `track_type`, `track_index`, `item_index`, `node_index`, `lut_path` | Apply a LUT file to a node |
| `resolve_get_node_cache_mode` | `track_type`, `track_index`, `item_index`, `node_index` | Get node cache mode (0=None, 1=Smart, 2=On) |
| `resolve_set_node_cache_mode` | `track_type`, `track_index`, `item_index`, `node_index`, `mode` | Set node cache mode (0=None, 1=Smart, 2=On) |
| `resolve_apply_arri_cdl_lut` | `track_type`, `track_index`, `item_index` | Apply ARRI CDL and LUT to a node graph |
| `resolve_reset_all_node_colors` | `track_type`, `track_index`, `item_index` | Reset all node label colours |
| `resolve_reset_grades` | `track_type`, `track_index`, `item_index` | Reset all grading on a clip |
| `resolve_apply_grade_from_drx` | `track_type`, `track_index`, `item_index`, `drx_path`, `grade_mode?` | Apply grade from a .drx still (0=No keyframes, 1=Source TC, 2=Start TC) |

### CDL (Color Decision List)

| Tool | Parameters | Description |
|------|-----------|-------------|
| `resolve_get_cdl` | `track_type`, `track_index`, `item_index` | Get CDL values (slope, offset, power, saturation) |
| `resolve_set_cdl` | `track_type`, `track_index`, `item_index`, `slope?`, `offset?`, `power?`, `saturation?`, `node_index?` | Set CDL values on a node (RGB as space-separated strings) |

### LUT Discovery

| Tool | Parameters | Description |
|------|-----------|-------------|
| `resolve_list_lut_folders` | `subfolder?` | Browse LUT folders/categories in Resolve's LUT directories |
| `resolve_search_luts` | `search`, `subfolder?` | Search for LUT files by name (case-insensitive) |
| `resolve_apply_lut_by_name` | `track_type`, `track_index`, `item_index`, `node_index`, `search` | Search for a LUT by name and apply it to a node |
| `resolve_refresh_lut_list` | — | Refresh the LUT list for the current project |

---

## Color Grades

Copy, export, and cache color grades.

| Tool | Parameters | Description |
|------|-----------|-------------|
| `resolve_copy_grades` | `track_type`, `track_index`, `source_item_index`, `target_item_indices` | Copy grade from source clip to targets (comma-separated 0-based indices) |
| `resolve_export_lut` | `track_type`, `track_index`, `item_index`, `export_type`, `path` | Export a LUT from a clip's grade (LUT_17PTCUBE, LUT_33PTCUBE, LUT_65PTCUBE, LUT_PANASONICVLUT) |
| `resolve_get_color_output_cache` | `track_type`, `track_index`, `item_index` | Check if color output cache is enabled |
| `resolve_set_color_output_cache` | `track_type`, `track_index`, `item_index`, `enabled` | Enable or disable color output cache |

---

## Color Versions

Manage local and remote color versions on timeline items.

| Tool | Parameters | Description |
|------|-----------|-------------|
| `resolve_list_color_versions` | `track_type`, `track_index`, `item_index`, `version_type?` | List color versions (local/remote) |
| `resolve_load_color_version` | `track_type`, `track_index`, `item_index`, `name`, `version_type?` | Load a color version by name |
| `resolve_add_color_version` | `track_type`, `track_index`, `item_index`, `name`, `version_type?` | Create a new color version |
| `resolve_get_current_color_version` | `track_type`, `track_index`, `item_index`, `version_type?` | Get the currently active color version |
| `resolve_delete_color_version` | `track_type`, `track_index`, `item_index`, `name`, `version_type?` | Delete a color version by name |
| `resolve_rename_color_version` | `track_type`, `track_index`, `item_index`, `old_name`, `new_name`, `version_type?` | Rename a color version |

---

## Color Groups

Organize clips into color groups for shared grading.

| Tool | Parameters | Description |
|------|-----------|-------------|
| `resolve_list_color_groups` | — | List all color groups in the project |
| `resolve_add_color_group` | `name` | Create a new color group |
| `resolve_delete_color_group` | `group_name` | Delete a color group |
| `resolve_set_color_group_name` | `current_name`, `new_name` | Rename a color group |
| `resolve_get_clips_in_color_group` | `group_name` | List clips in a color group (current timeline) |
| `resolve_get_color_group_pre_node_graph` | `group_name` | Get pre-clip node graph info for a group |
| `resolve_get_color_group_post_node_graph` | `group_name` | Get post-clip node graph info for a group |
| `resolve_get_item_color_group` | `track_type`, `track_index`, `item_index` | Get which color group a clip belongs to |
| `resolve_assign_to_color_group` | `track_type`, `track_index`, `item_index`, `group_name` | Assign a clip to a color group |
| `resolve_remove_from_color_group` | `track_type`, `track_index`, `item_index` | Remove a clip from its color group |

---

## Gallery & Stills

Manage still albums, PowerGrade albums, and stills.

### Albums

| Tool | Parameters | Description |
|------|-----------|-------------|
| `resolve_list_gallery_albums` | — | List all still albums in the gallery |
| `resolve_get_current_still_album` | — | Get the name of the current still album |
| `resolve_set_current_still_album` | `album_index` | Set current album by index (1-based) |
| `resolve_list_powergrade_albums` | — | List all PowerGrade albums |
| `resolve_create_still_album` | — | Create a new still album |
| `resolve_create_powergrade_album` | — | Create a new PowerGrade album |
| `resolve_set_album_name` | `album_index`, `name` | Rename a still album (1-based index) |

### Stills

| Tool | Parameters | Description |
|------|-----------|-------------|
| `resolve_grab_still` | — | Grab a still from the current frame (Color page) |
| `resolve_grab_all_stills` | `still_frame_source?` | Grab stills from all clips (1=first frame, 2=middle) |
| `resolve_export_still` | `path` | Export the current frame as a still image |
| `resolve_list_stills` | — | List all stills in the current album |
| `resolve_get_still_label` | `still_index` | Get label of a still (1-based index) |
| `resolve_set_still_label` | `still_index`, `label` | Set label of a still (1-based index) |
| `resolve_import_stills` | `paths` | Import stills into current album (comma-separated paths) |
| `resolve_export_stills` | `still_indices`, `path`, `file_prefix?`, `format?` | Export stills (1-based indices, format: dpx/cin/tif/jpg/png/ppm/bmp/xpm) |
| `resolve_delete_stills` | `still_indices` | Delete stills by index (1-based, comma-separated) |

---

## Audio

Audio-related operations on the Fairlight page.

| Tool | Parameters | Description |
|------|-----------|-------------|
| `resolve_insert_audio_at_playhead` | `file_path`, `start_offset?`, `duration?` | Insert an audio file at the playhead |
| `resolve_load_burn_in_preset` | `name` | Load a burn-in preset by name |

Notes:
- `start_offset` and `duration` are frame counts.
- `duration=0` uses the full remaining source audio.
- `resolve_insert_audio_at_playhead` inserts into the currently targeted audio track.
- `resolve_load_burn_in_preset` applies a project burn-in preset (commonly used before rendering).

---

## Deliver (Rendering)

Configure and execute renders from the Deliver page.

### Render Settings

| Tool | Parameters | Description |
|------|-----------|-------------|
| `resolve_list_render_presets` | — | List available render presets |
| `resolve_load_render_preset` | `name` | Load a render preset |
| `resolve_delete_render_preset` | `name` | Delete a render preset |
| `resolve_get_render_format_and_codec` | — | Get the current format and codec |
| `resolve_list_render_formats` | — | List all available render formats |
| `resolve_list_render_codecs` | `format_name` | List codecs for a format |
| `resolve_set_render_format_and_codec` | `format`, `codec` | Set format and codec (e.g. `mp4`, `H265`) |
| `resolve_set_render_settings` | `target_dir`, `custom_name?`, `preset?` | Configure output directory and filename |

### Render Queue

| Tool | Parameters | Description |
|------|-----------|-------------|
| `resolve_add_render_job` | — | Add current settings as a render job |
| `resolve_list_render_jobs` | — | List all jobs in the queue |
| `resolve_start_render` | `job_ids?` (comma-separated) | Start rendering (empty = all jobs) |
| `resolve_stop_render` | — | Stop the current render |
| `resolve_is_rendering` | — | Check if rendering is in progress |
| `resolve_get_render_status` | `job_id` | Get status of a render job |
| `resolve_delete_render_job` | `job_id` | Delete a job from the queue |
| `resolve_clear_render_queue` | — | Delete all render jobs |

---

## Disabled Tools

These tools are disabled because they rely on API methods that don't exist or always fail on DaVinci Resolve 20.3 Free. The code is preserved and can be re-enabled by adding back the `@mcp.tool()` decorator if a future Resolve version or Resolve Studio supports them.

| Tool | Reason |
|------|--------|
| `resolve_list_generators` | `GetAvailableGenerators` does not exist on the Resolve proxy |
| `resolve_list_titles` | `GetAvailableTitles` does not exist on the Resolve proxy |
| `resolve_set_node_label` | `SetNodeLabel` does not exist (labels are read-only) |
| `resolve_detect_scene_cuts` | `DetectSceneCuts` runs but returns `bool`, not a frame list |
| `resolve_create_subtitle_from_audio` | `CreateSubtitlesFromAudio` always returns `False` (likely requires Studio) |
| `resolve_voice_isolation_timeline` | `SetVoiceIsolationState` always returns `False` (likely requires Studio) |
| `resolve_voice_isolation_clip` | `SetVoiceIsolationState` always returns `False` (likely requires Studio) |
| `resolve_apply_magic_mask` | `CreateMagicMask` always returns `False` (likely requires Studio) |

---

## Parameter Conventions

- **`track_type`**: `"video"`, `"audio"`, or `"subtitle"`
- **`track_index`**: 1-based track number
- **`item_index`**: 0-based index of the clip within the track
- **`node_index`**: 1-based color node index
- **`color`** (markers/labels): `Blue`, `Cyan`, `Green`, `Yellow`, `Red`, `Pink`, `Purple`, `Fuchsia`, `Rose`, `Lavender`, `Sky`, `Mint`, `Lemon`, `Sand`, `Cocoa`, `Cream`, `Teal`, `Orange`
- **`paths`** (comma-separated): Absolute file paths separated by commas
- **`timecode`**: Format `HH:MM:SS:FF` (e.g. `01:00:05:00`)
- **`export_type`**: `AAF`, `DRT`, `EDL`, `FCP_7_XML`, `FCPXML_1_8`, etc.
