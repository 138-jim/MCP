# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install
pip install -e ".[mcp,dev]"

# Test (fully mocked, no Resolve needed)
pytest tests/ -v
pytest tests/test_session.py -v              # single file
pytest tests/test_timeline.py::test_markers  # single test

# Lint & format
ruff check src/ tests/
ruff format src/ tests/

# Type check
mypy src/

# Run MCP server (STDIO transport)
python -m resolve_mcp
```

## Architecture

Two packages in `src/`:

**`resolve_lib`** — Standalone Python wrapper over the DaVinci Resolve Scripting API. Zero runtime dependencies. Each Resolve API object gets a Python class holding `_obj` (the raw API object). The class hierarchy mirrors Resolve's own: `Session` → `ProjectManager` → `Project` → `MediaPool`/`Timeline` → etc.

**`resolve_mcp`** — MCP server that exposes ~160 tools as a thin layer over `resolve_lib`. Uses `FastMCP` from the `mcp` package. Tools return strings only.

### Connection flow

`connect.py` uses a 3-tier fallback to find the `DaVinciResolveScript` module: (1) direct import via PYTHONPATH, (2) `RESOLVE_SCRIPT_LIB` env var, (3) platform default paths. Returns the raw Resolve object. Resolve must already be running.

### MCP tool pattern

Every tool module exports `register_*_tools(mcp, state)`. `state` is a `ServerState` singleton that lazily connects on first use. Each tool function uses the `@mcp.tool()` decorator (generates JSON schema from type hints) and `@resolve_tool` (catches `ResolveError` and returns error strings instead of tracebacks).

```python
def register_foo_tools(mcp: FastMCP, state: ServerState):
    @mcp.tool()
    @resolve_tool
    def resolve_do_thing(param: str) -> str:
        """Docstring becomes the tool description for LLMs."""
        result = state.session.get_project_manager()...
        return f"Done: {result}"
```

New tool modules must be imported and registered in `server.py`.

### Tool modules (15 files in `tools/`)

`session_tools`, `project_tools`, `media_storage_tools`, `media_pool_tools`, `timeline_tools`, `timeline_item_tools`, `color_tools`, `audio_tools`, `deliver_tools`, `transition_tools`, `color_node_tools`, `color_version_tools`, `color_grade_tools`, `color_group_tools`, `gallery_tools`

### Resources

The server exposes a `resolve://guide` resource (serves `RESOLVE_GUIDE.md`) and stores Fusion transition presets in `presets/transitions/`.

### Error hierarchy

`ResolveError` → `ResolveConnectionError`, `ResolveOperationError`, `ResolveNotFoundError`, `ResolveValidationError`. The library raises these; the MCP layer catches them via `@resolve_tool` and converts to strings.

### Circular import avoidance

Wrapper classes reference each other (e.g., `Project.get_media_pool()` returns `MediaPool`). Local imports inside methods prevent circular dependencies:

```python
def get_media_pool(self):
    from resolve_lib.media_pool import MediaPool
    return MediaPool(self._obj.GetMediaPool())
```

### Testing

Tests use a full mock hierarchy in `tests/mocks/mock_resolve.py` — `MagicMock` objects simulating the entire Resolve API chain. Fixtures in `conftest.py` chain: `mock_resolve` → `session` → `project_manager` → `project` → `media_pool` / `timeline`. No Resolve installation needed.

### Conventions

- All wrapper methods that return API objects raise `ResolveOperationError` when the raw API returns `None`
- All wrapper methods that return lists return `[]` when the raw API returns `None`
- Node indices and track indices are **1-based** (matching Resolve's API)
- `getattr` with lambda fallbacks for methods that may not exist in all Resolve versions
- Validators in `validators.py` for track type, track index, node index, page name, frame number
