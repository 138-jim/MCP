# resolve-tool

High-level Python wrapper for the DaVinci Resolve Scripting API, plus an MCP server for LLM-driven control.

## Structure

- **`resolve_lib`** — Standalone Python library wrapping every Resolve API object with clean methods
- **`resolve_mcp`** — MCP server (thin layer over resolve_lib) exposing ~80 tools for LLMs

## Installation

```bash
# Library only
pip install -e .

# With MCP server
pip install -e ".[mcp]"

# With dev tools
pip install -e ".[dev]"
```

## Requirements

- Python 3.10+
- DaVinci Resolve (must be running for API access)
- Resolve's scripting module accessible via one of:
  - `PYTHONPATH` includes the Resolve Scripting/Modules directory
  - `RESOLVE_SCRIPT_LIB` env var pointing to the module
  - Resolve installed in the default location

## Library Usage

```python
from resolve_lib import connect, Session

# Connect to running Resolve
raw = connect()
session = Session(raw)

print(session.get_version())
print(session.get_current_page())

# Navigate the object hierarchy
pm = session.get_project_manager()
project = pm.get_current_project()
pool = project.get_media_pool()
timeline = project.get_current_timeline()

# Work with timelines
for i in range(1, timeline.get_track_count("video") + 1):
    items = timeline.get_item_list_in_track("video", i)
    for item in items:
        print(f"  {item.get_name()} - {item.get_duration()} frames")
```

## MCP Server

### Run directly

```bash
python -m resolve_mcp
```

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "resolve": {
      "command": "python",
      "args": ["-m", "resolve_mcp"],
      "cwd": "/path/to/resolve-tool",
      "env": {
        "PYTHONPATH": "/path/to/resolve-tool/src"
      }
    }
  }
}
```

### Claude Code

Add to `.claude/settings.json` or run:

```bash
claude mcp add resolve -- python -m resolve_mcp
```

### Cursor

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "resolve": {
      "command": "python",
      "args": ["-m", "resolve_mcp"],
      "env": {
        "PYTHONPATH": "/path/to/resolve-tool/src"
      }
    }
  }
}
```

## Available MCP Tools

| Domain | Tools | Examples |
|--------|-------|---------|
| Session | 8 | `resolve_connect`, `resolve_set_page`, `resolve_get_version` |
| Projects | 13 | `resolve_list_projects`, `resolve_create_project`, `resolve_load_project` |
| Media Storage | 5 | `resolve_get_mounted_volumes`, `resolve_import_files_to_pool` |
| Media Pool | 15 | `resolve_list_clips_in_bin`, `resolve_import_media`, `resolve_create_timeline` |
| Timeline | 22 | `resolve_list_timelines`, `resolve_add_track`, `resolve_detect_scene_cuts` |
| Timeline Items | 15 | `resolve_get_item_properties`, `resolve_set_item_property` |
| Color | 10 | `resolve_set_node_lut`, `resolve_list_color_groups`, `resolve_reset_grades` |
| Audio | 4 | `resolve_insert_audio_at_playhead`, `resolve_voice_isolation_clip` |
| Deliver | 12 | `resolve_start_render`, `resolve_list_render_presets`, `resolve_get_render_status` |

## Testing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests (no Resolve needed — fully mocked)
pytest tests/ -v
```

## Examples

See the `examples/` directory:

- `basic_connection.py` — Connect and print version info
- `create_project.py` — Create a project with settings and a timeline
- `import_and_build_timeline.py` — Import media and assemble an edit
