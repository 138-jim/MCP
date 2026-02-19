# resolve-tool

A Python toolkit for DaVinci Resolve with two layers:

- **`resolve_lib`** — Standalone Python library wrapping every Resolve scripting API object
- **`resolve_mcp`** — MCP server exposing 110 tools for LLM-driven control of Resolve

Tested against DaVinci Resolve 20.3 (Free) on macOS. Works on macOS, Windows, and Linux.

---

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [MCP Server Setup](#mcp-server-setup)
  - [Claude Code](#claude-code)
  - [Claude Desktop](#claude-desktop)
  - [Cursor](#cursor)
  - [Running Directly](#running-directly)
- [Python Library Guide](#python-library-guide)
  - [Connecting to Resolve](#connecting-to-resolve)
  - [Object Hierarchy](#object-hierarchy)
  - [Session](#session)
  - [Project Manager](#project-manager)
  - [Projects](#projects)
  - [Media Storage](#media-storage)
  - [Media Pool](#media-pool)
  - [Clips (Media Pool Items)](#clips-media-pool-items)
  - [Timelines](#timelines)
  - [Timeline Items (Clips on Timeline)](#timeline-items-clips-on-timeline)
  - [Fusion Compositions](#fusion-compositions)
  - [Color Grading](#color-grading)
  - [Gallery & Stills](#gallery--stills)
  - [Rendering](#rendering)
- [Examples](#examples)
- [Testing](#testing)
- [MCP Tools Reference](#mcp-tools-reference)

---

## Requirements

- Python 3.10+
- DaVinci Resolve (must be running for API access)
- Resolve's scripting module accessible via one of:
  - `PYTHONPATH` includes the Resolve Scripting/Modules directory
  - `RESOLVE_SCRIPT_LIB` env var pointing to the module
  - Resolve installed in the default location

The library auto-detects the scripting module using platform-specific default paths:

| Platform | Default Path |
|----------|-------------|
| macOS | `/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules` |
| Windows | `%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules` |
| Linux | `/opt/resolve/Developer/Scripting/Modules` |

---

## Installation

```bash
# Library only (no dependencies)
pip install -e .

# With MCP server
pip install -e ".[mcp]"

# With dev tools (pytest, ruff, mypy)
pip install -e ".[dev]"
```

---

## MCP Server Setup

The MCP server lets LLMs (Claude, etc.) control DaVinci Resolve through 110 tools. It runs as a stdio process that any MCP-compatible client can connect to.

### Claude Code

Add a `.mcp.json` file to your project root:

```json
{
  "mcpServers": {
    "resolve": {
      "command": "python3",
      "args": ["-m", "resolve_mcp"],
      "cwd": "/path/to/resolve-tool",
      "env": {
        "PYTHONPATH": "/path/to/resolve-tool/src"
      }
    }
  }
}
```

Or use the CLI:

```bash
claude mcp add resolve -- python3 -m resolve_mcp
```

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "resolve": {
      "command": "python3",
      "args": ["-m", "resolve_mcp"],
      "cwd": "/path/to/resolve-tool",
      "env": {
        "PYTHONPATH": "/path/to/resolve-tool/src"
      }
    }
  }
}
```

### Cursor

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "resolve": {
      "command": "python3",
      "args": ["-m", "resolve_mcp"],
      "env": {
        "PYTHONPATH": "/path/to/resolve-tool/src"
      }
    }
  }
}
```

### Running Directly

```bash
PYTHONPATH=src python -m resolve_mcp
```

The server communicates over stdio. It connects to Resolve on startup and stays connected for the session.

---

## Python Library Guide

`resolve_lib` is a standalone Python library with zero dependencies (beyond the Resolve scripting module). It wraps every Resolve API object with clean, typed methods.

### Connecting to Resolve

```python
from resolve_lib import connect, Session

# connect() finds and loads the Resolve scripting module automatically,
# then connects to the running Resolve instance.
raw_resolve = connect()
session = Session(raw_resolve)

print(session.get_version())       # "20.3.2.9"
print(session.get_current_page())  # "edit"
```

`connect()` uses a 3-tier fallback:
1. Direct import (if `PYTHONPATH` is set)
2. `RESOLVE_SCRIPT_LIB` environment variable
3. Platform-specific default paths

### Object Hierarchy

Resolve's API is a tree of objects. `resolve_lib` mirrors this exactly:

```
Session
├── ProjectManager
│   └── Project
│       ├── MediaPool
│       │   ├── Folder (bins)
│       │   │   └── MediaPoolItem (clips)
│       │   └── Timeline
│       │       └── TimelineItem (clips on timeline)
│       │           ├── Graph (color node graph)
│       │           └── Fusion Composition
│       ├── Gallery
│       │   └── GalleryStillAlbum
│       ├── ColorGroup
│       └── Deliver
└── MediaStorage
```

Every wrapper class takes the raw Resolve proxy object and provides clean methods:

```python
pm = session.get_project_manager()
project = pm.get_current_project()
pool = project.get_media_pool()
timeline = project.get_current_timeline()
```

### Session

Controls the Resolve application itself.

```python
session = Session(connect())

# Application info
session.get_version()       # "20.3.2.9"
session.get_product_name()  # "DaVinci Resolve"
session.get_current_page()  # "edit"

# Switch pages: media, cut, edit, fusion, color, fairlight, deliver
session.set_current_page("color")

# Layout presets
session.load_layout_preset("My Layout")
session.import_layout_preset("New Layout", "/path/to/preset.xml")

# Keyframe mode: 0=All, 1=Color, 2=Sizing
session.get_keyframe_mode()
session.set_keyframe_mode(0)

# Quit Resolve
session.quit()
```

### Project Manager

Manages databases, folders, and projects.

```python
pm = session.get_project_manager()

# Databases
pm.get_database_list()     # [{"DbName": "Local", "DbType": "Disk", ...}]
pm.get_current_database()  # {"DbName": "Local", "DbType": "Disk", ...}
pm.set_current_database({"DbName": "Remote", "DbType": "PostgreSQL", "IpAddress": "192.168.1.100"})

# Folder navigation
pm.get_folder_list_in_current_folder()  # ["Folder A", "Folder B"]
pm.create_folder("New Folder")
pm.open_folder("New Folder")
pm.goto_parent_folder()
pm.goto_root_folder()

# Projects
pm.get_project_list_in_current_folder()  # ["Project 1", "Project 2"]
project = pm.create_project("My Project")
project = pm.load_project("Existing Project")
pm.save_project()

# Import / Export
pm.export_project("My Project", "/path/to/export.drp", with_stills_and_luts=True)
pm.import_project("/path/to/project.drp")
```

### Projects

A project contains timelines, media pool, gallery, and render settings.

```python
project = pm.get_current_project()

project.get_name()      # "My Project"
project.get_unique_id()

# Settings
project.get_setting("timelineResolutionWidth")  # "1920"
project.set_setting("timelineResolutionWidth", "3840")
project.set_setting("timelineResolutionHeight", "2160")
project.set_setting("timelineFrameRate", "24")

# Timelines
project.get_timeline_count()          # 3
tl = project.get_timeline_by_index(1) # 1-based
tl = project.get_current_timeline()
project.set_current_timeline(tl)

# Access sub-objects
pool = project.get_media_pool()
gallery = project.get_gallery()

# Audio
project.insert_audio_to_current_track_at_playhead("/path/to/audio.wav", start_offset=0, duration=0)

# Burn-in presets
project.load_burn_in_preset("My Burn-in")

# Stills
project.export_current_frame_as_still("/path/to/still.png")
```

### Media Storage

Browse and import from mounted storage volumes.

```python
storage = session.get_media_storage()

# List mounted volumes
storage.get_mounted_volumes()  # ["/Volumes/Media", "/Volumes/Backup"]

# Browse
storage.get_subfolder_list("/Volumes/Media")  # ["Footage", "Audio"]
storage.get_file_list("/Volumes/Media/Footage")  # ["clip_001.mov", ...]

# Import directly into media pool
items = storage.add_items_to_media_pool("/Volumes/Media/Footage/clip_001.mov")
```

### Media Pool

Manage bins, import media, and create timelines.

```python
pool = project.get_media_pool()

# Folder (bin) navigation
root = pool.get_root_folder()
current = pool.get_current_folder()
print(root.get_name())  # "Master"

# List contents
clips = root.get_clips()        # [MediaPoolItem, ...]
subs = root.get_subfolders()    # [Folder, ...]

# Create bins
new_bin = pool.add_subfolder("Selects", root)
pool.set_current_folder(new_bin)

# Import media
clips = pool.import_media([
    "/path/to/clip_001.mov",
    "/path/to/clip_002.mov",
    "/path/to/clip_003.mov",
])

# Create timelines
timeline = pool.create_empty_timeline("My Edit")
timeline = pool.create_timeline_from_clips("Assembly", clips)

# Append clips to existing timeline
pool.append_to_timeline(clips)

# Import timeline from file
timeline = pool.import_timeline_from_file("/path/to/edit.fcpxml")

# Move clips between bins
pool.move_clips(clips, new_bin)

# Transcribe audio in a folder
root.transcribe_audio()
```

### Clips (Media Pool Items)

Work with individual clips in the media pool.

```python
clip = clips[0]

clip.get_name()       # "clip_001.mov"
clip.get_unique_id()
clip.get_media_id()

# Metadata
clip.get_metadata()            # {"Resolution": "3840x2160", "FPS": "23.976", ...}
clip.get_metadata("Resolution")  # "3840x2160"
clip.set_metadata("Comments", "Best take")

# Properties
clip.get_clip_property()          # all properties
clip.get_clip_property("FPS")     # "23.976"

# Color labels and flags
clip.get_clip_color()             # ""
clip.set_clip_color("Blue")
clip.add_flag("Green")
clip.get_flag_list()              # ["Green"]

# Markers
clip.add_marker(100, "Red", "Bad Focus", "Soft at start", duration=50)
clip.get_markers()  # {100: {"color": "Red", "name": "Bad Focus", ...}}
clip.delete_marker_at_frame(100)

# Mark in/out
clip.get_mark_in()
clip.get_mark_out()

# Replace media
clip.replace_clip("/path/to/new_clip.mov")

# Proxy media
clip.link_proxy_media("/path/to/proxy.mov")
clip.unlink_proxy_media()
```

### Timelines

Create, navigate, and edit timelines.

```python
timeline = project.get_current_timeline()

timeline.get_name()            # "Main Edit"
timeline.set_name("Final Cut")
timeline.get_start_frame()     # 86400
timeline.get_end_frame()       # 87200
timeline.get_start_timecode()  # "01:00:00:00"

# Playhead
timeline.get_current_timecode()         # "01:00:05:12"
timeline.set_current_timecode("01:00:10:00")

# Tracks
timeline.get_track_count("video")     # 2
timeline.get_track_count("audio")     # 4
timeline.add_track("video")
timeline.get_track_name("video", 1)   # "V1"
timeline.set_track_name("video", 1, "Main")

# Track state
timeline.set_track_enable("video", 2, False)  # disable track
timeline.set_track_lock("audio", 1, True)      # lock track

# Get clips on a track
items = timeline.get_item_list_in_track("video", 1)
for item in items:
    print(f"{item.get_name()} - {item.get_duration()} frames")

# Markers
timeline.add_marker(0, "Blue", "Start", "Beginning of edit")
timeline.get_markers()  # {0: {...}, 150: {...}}
timeline.delete_marker_at_frame(0)

# Insert generators and titles at playhead
timeline.insert_generator_in_timeline("Solid Color")
timeline.insert_fusion_title_in_timeline("Text+")

# Duplicate
new_tl = timeline.duplicate_timeline("Backup Edit")

# Export
timeline.export("/path/to/output.fcpxml", export_type, export_subtype)

# Settings
timeline.get_setting("")  # all settings as dict
timeline.get_setting("timelineResolutionWidth")
timeline.set_setting("timelineResolutionWidth", "3840")

# Mark in/out
timeline.set_mark_in(86400)
timeline.set_mark_out(87000)
```

### Timeline Items (Clips on Timeline)

Inspect and modify clips that are placed on the timeline.

```python
items = timeline.get_item_list_in_track("video", 1)
item = items[0]

# Basic info
item.get_name()        # "clip_001"
item.get_duration()    # 120
item.get_start()       # 86400
item.get_end()         # 86520

# Inspector properties
item.get_property()            # all properties as dict
item.get_property("ZoomX")     # 1.0
item.set_property("ZoomX", 1.5)
item.set_property("Pan", 100)
item.set_property("Tilt", -50)
item.set_property("Opacity", 0.8)

# Enable/disable
item.is_enabled()     # True
item.set_enabled(False)

# Color labels and flags
item.set_clip_color("Teal")
item.add_flag("Red")

# Markers (frame offset relative to clip start)
item.add_marker(10, "Green", "Good part")
item.get_markers()

# Link back to media pool
pool_clip = item.get_media_pool_item()
print(pool_clip.get_name())

# Takes
item.get_takes_count()
item.select_take_by_index(2)

# AI features
item.apply_stabilization()
item.apply_smart_reframe()

# Caching
item.set_clip_cache(True)
item.get_clip_cache()
```

### Fusion Compositions

Control Fusion compositions on timeline items.

```python
item = items[0]

# List existing comps
item.get_fusion_comp_name_list()  # ["Composition 1"]
item.get_fusion_comp_count()      # 1

# Add a new comp
comp = item.add_fusion_comp()

# Read/write Fusion tool inputs
# Works with any tool in the comp (TextPlus, Background, etc.)
item.set_fusion_tool_input("TextPlus", "StyledText", "Hello World")
item.set_fusion_tool_input("TextPlus", "Size", 0.08)
item.set_fusion_tool_input("TextPlus", "Font", "Open Sans")
item.get_fusion_tool_input("TextPlus", "StyledText")  # "Hello World"

# Specify which comp (if multiple)
item.set_fusion_tool_input("TextPlus", "StyledText", "Title", comp_index=2)

# Import/export comps
item.import_fusion_comp("/path/to/comp.setting")
item.export_fusion_comp("/path/to/output.setting", 1)

# Manage comps
item.rename_fusion_comp("Composition 1", "Title Card")
item.delete_fusion_comp_by_name("Old Comp")
```

### Color Grading

Work with color nodes, LUTs, and grades. Best used from the Color page.

```python
session.set_current_page("color")

item = timeline.get_item_list_in_track("video", 1)[0]
graph = item.get_node_graph()

# Nodes
graph.get_num_nodes()           # 1
graph.get_node_label(1)         # "Corrector 1"
graph.get_node_enabled(1)       # True
graph.set_node_enabled(1, False)

# LUTs
graph.set_lut(1, "/path/to/lut.cube")
graph.get_lut(1)  # "/path/to/lut.cube"

# Apply a grade from a .drx still
graph.apply_grade_from_drx("/path/to/grade.drx", grade_mode=0, item=item)

# Reset all grading
graph.reset_grades()

# Color versions
item.get_version_name_list("local")   # ["Version 1", "Version 2"]
item.load_version_by_name("Version 2", "local")
item.add_version("New Grade", "local")

# CDL values
cdl = item.get_cdl()   # {"NodeIndex": 1, "Slope": ..., "Offset": ..., "Power": ..., "Saturation": ...}
item.set_cdl(cdl)

# Copy grades between clips
item.copy_grades([items[1], items[2]])

# Export LUT from grade
item.export_lut("Cube", "/path/to/output.cube")

# Color groups
groups = project.get_color_group_list()
group = project.add_color_group("A-Cam")
item.assign_to_color_group(group)
item.remove_from_color_group()
```

### Gallery & Stills

Manage still albums and power grades.

```python
gallery = project.get_gallery()

# Albums
albums = gallery.get_gallery_still_albums()
for album in albums:
    print(gallery.get_album_name(album))

current = gallery.get_current_still_album()
gallery.set_album_name(current, "Selects")

# Create albums
new_album = gallery.create_gallery_still_album()
pg_album = gallery.create_gallery_powergrade_album()

# Stills within an album
stills = current.get_stills()
current.set_label(stills[0], "Hero shot")
current.import_stills(["/path/to/reference.dpx"])
current.export_stills(stills, "/path/to/exports/", file_prefix="still_", format="dpx")
current.delete_stills([stills[0]])
```

### Rendering

Set up and execute renders.

```python
# Using the Deliver helper
deliver = Deliver(project)

# Quick render with defaults
job_id = deliver.quick_render("/path/to/renders/", preset="YouTube 1080p", start=True)

# Check progress
status = deliver.get_render_progress(job_id)  # {"JobStatus": "Rendering", "CompletionPercentage": 45, ...}

# Wait for completion
result = deliver.wait_for_render(job_id)  # blocks until done

# List available formats and codecs
deliver.list_formats()             # {"mp4": "MP4", "mov": "QuickTime", ...}
deliver.list_codecs("mp4")        # {"H264": "H.264", "H265": "H.265", ...}
deliver.list_presets()             # ["YouTube 1080p", "Vimeo 4K", ...]

# Or use the Project directly for more control
project.set_current_render_format_and_codec("mp4", "H265")
project.set_render_settings({"TargetDir": "/path/to/renders/", "CustomName": "final_output"})
job_id = project.add_render_job()
project.start_rendering(job_id)

# Monitor
project.is_rendering_in_progress()  # True
project.get_render_job_status(job_id)

# Queue management
project.get_render_job_list()
project.delete_render_job(job_id)
project.delete_all_render_jobs()
project.stop_rendering()
```

---

## Examples

See the `examples/` directory:

### basic_connection.py

Connect to Resolve and print version info:

```python
from resolve_lib import connect, Session

raw_resolve = connect()
session = Session(raw_resolve)

print(f"Version: {session.get_version()}")
print(f"Page: {session.get_current_page()}")

pm = session.get_project_manager()
project = pm.get_current_project()
print(f"Project: {project.get_name()}")
```

### create_project.py

Create a project with settings and a timeline:

```python
from resolve_lib import connect, Session

session = Session(connect())
pm = session.get_project_manager()

project = pm.create_project("My New Project")
project.set_setting("timelineResolutionWidth", "1920")
project.set_setting("timelineResolutionHeight", "1080")
project.set_setting("timelineFrameRate", "24")

pool = project.get_media_pool()
timeline = pool.create_empty_timeline("Main Edit")

pm.save_project()
```

### import_and_build_timeline.py

Import media and assemble an edit:

```python
from resolve_lib import connect, Session

session = Session(connect())
project = session.get_project_manager().get_current_project()
pool = project.get_media_pool()

clips = pool.import_media([
    "/path/to/shot_001.mov",
    "/path/to/shot_002.mov",
    "/path/to/shot_003.mov",
])

timeline = pool.create_timeline_from_clips("Assembly Edit", clips)

items = timeline.get_item_list_in_track("video", 1)
for item in items:
    print(f"  {item.get_name()} - {item.get_duration()} frames")

timeline.add_marker(0, "Blue", "Start", "Beginning of edit")
```

---

## Testing

Tests are fully mocked and don't require a running Resolve instance.

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

---

## MCP Tools Reference

See [MCP_TOOLS.md](MCP_TOOLS.md) for a complete reference of all 110 MCP tools with parameters and descriptions.
