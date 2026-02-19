# DaVinci Resolve MCP Server — Tool Reference

115 tools for controlling DaVinci Resolve via the Model Context Protocol.
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
| `resolve_save_project` | — | Save the current project |
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

### Color Versions

| Tool | Parameters | Description |
|------|-----------|-------------|
| `resolve_list_color_versions` | `track_type`, `track_index`, `item_index`, `version_type?` | List color versions (local/remote) |
| `resolve_load_color_version` | `track_type`, `track_index`, `item_index`, `name`, `version_type?` | Load a color version by name |

### AI Operations

| Tool | Parameters | Description |
|------|-----------|-------------|
| `resolve_stabilize_clip` | `track_type`, `track_index`, `item_index` | Apply AI stabilization |
| `resolve_smart_reframe` | `track_type`, `track_index`, `item_index` | Apply AI smart reframe |

---

## Color Grading

Color page node graph operations. Requires switching to the Color page first.

| Tool | Parameters | Description |
|------|-----------|-------------|
| `resolve_get_node_count` | `track_type`, `track_index`, `item_index` | Get number of color nodes |
| `resolve_get_node_lut` | `track_type`, `track_index`, `item_index`, `node_index` | Get LUT path on a node (1-based) |
| `resolve_set_node_lut` | `track_type`, `track_index`, `item_index`, `node_index`, `lut_path` | Apply a LUT to a node |
| `resolve_reset_grades` | `track_type`, `track_index`, `item_index` | Reset all grading |
| `resolve_apply_grade_from_drx` | `track_type`, `track_index`, `item_index`, `drx_path`, `grade_mode?` | Apply grade from a .drx still (0=No keyframes, 1=Source TC, 2=Start TC) |
| `resolve_list_color_groups` | — | List all color groups in the project |
| `resolve_add_color_group` | `name` | Create a new color group |
| `resolve_list_gallery_albums` | — | List all still albums in the gallery |
| `resolve_export_still` | `path` | Export the current frame as a still image |

---

## Audio

Audio-related operations on the Fairlight page.

| Tool | Parameters | Description |
|------|-----------|-------------|
| `resolve_insert_audio_at_playhead` | `file_path`, `start_offset?`, `duration?` | Insert an audio file at the playhead |
| `resolve_load_burn_in_preset` | `name` | Load a burn-in preset by name |

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
