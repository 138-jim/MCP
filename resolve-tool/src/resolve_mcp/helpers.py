"""Error formatting, connection guard, and shared accessor helpers for MCP tools."""

from __future__ import annotations

import functools
import logging
from typing import Callable, TYPE_CHECKING

from resolve_lib.exceptions import ResolveError

if TYPE_CHECKING:
    from resolve_lib.media_pool import MediaPool
    from resolve_lib.media_pool_item import MediaPoolItem
    from resolve_lib.project import Project
    from resolve_lib.timeline import Timeline
    from resolve_lib.timeline_item import TimelineItem
    from resolve_mcp.state import ServerState

logger = logging.getLogger("resolve_mcp")


# ---------------------------------------------------------------------------
# Shared accessors — used by every tool module
# ---------------------------------------------------------------------------

def get_project(state: ServerState) -> Project:
    """Return the current project from the session."""
    return state.session.get_project_manager().get_current_project()


def get_timeline(state: ServerState) -> Timeline:
    """Return the current timeline from the current project."""
    return get_project(state).get_current_timeline()


def get_pool(state: ServerState) -> MediaPool:
    """Return the media pool from the current project."""
    return get_project(state).get_media_pool()


def get_item(
    state: ServerState, track_type: str, track_index: int, item_index: int
) -> TimelineItem | None:
    """Return a timeline item by track and index, or None if out of range.

    *item_index* is 0-based.
    """
    tl = get_timeline(state)
    items = tl.get_item_list_in_track(track_type, track_index)
    if item_index >= len(items):
        return None
    return items[item_index]


def find_clip_by_name(state: ServerState, name: str) -> MediaPoolItem | None:
    """Find a clip by name in the current media pool bin."""
    pool = get_pool(state)
    folder = pool.get_current_folder()
    for clip in folder.get_clips():
        if clip.get_name() == name:
            return clip
    return None


def auto_scale_to_timeline(state: ServerState, items: list[TimelineItem]) -> int:
    """Set ZoomX/ZoomY on timeline items so they fill the timeline resolution.

    Compares each item's source resolution (from its media pool clip) against
    the project timeline resolution and applies a uniform scale factor.

    Returns the number of items scaled.
    """
    proj = get_project(state)
    tl_width = proj.get_setting("timelineResolutionWidth")
    tl_height = proj.get_setting("timelineResolutionHeight")
    if not tl_width or not tl_height:
        return 0
    tl_w, tl_h = int(tl_width), int(tl_height)
    scaled = 0
    for item in items:
        pool_clip = item.get_media_pool_item()
        if pool_clip is None:
            continue
        clip_res = pool_clip.get_clip_property("Resolution")
        if not clip_res or "x" not in str(clip_res):
            continue
        parts = str(clip_res).split("x")
        try:
            clip_w, clip_h = int(parts[0]), int(parts[1])
        except (ValueError, IndexError):
            continue
        if clip_w == tl_w and clip_h == tl_h:
            continue  # no mismatch
        if clip_w == 0 or clip_h == 0:
            continue
        # Scale to fill: use the larger ratio so the frame is fully covered
        scale = max(tl_w / clip_w, tl_h / clip_h)
        if abs(scale - 1.0) < 0.001:
            continue
        item.set_property("ZoomX", scale)
        item.set_property("ZoomY", scale)
        scaled += 1
    return scaled


def resolve_tool(fn: Callable) -> Callable:
    """Decorator that catches ResolveError and returns a human-readable error string.

    Also ensures all tools return strings (MCP requirement).
    """

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            result = fn(*args, **kwargs)
            if result is None:
                return "OK"
            return str(result)
        except ResolveError as exc:
            logger.error("%s: %s", type(exc).__name__, exc)
            return f"Error: {exc}"
        except Exception as exc:
            logger.exception("Unexpected error in %s", fn.__name__)
            return f"Unexpected error: {type(exc).__name__}: {exc}"

    return wrapper


def format_list(items: list, label: str = "items") -> str:
    """Format a list for MCP tool output."""
    if not items:
        return f"No {label} found."
    lines = [f"Found {len(items)} {label}:"]
    for i, item in enumerate(items, 1):
        lines.append(f"  {i}. {item}")
    return "\n".join(lines)


def format_dict(d: dict, label: str = "result") -> str:
    """Format a dict for MCP tool output."""
    if not d:
        return f"No {label} data."
    lines = [f"{label}:"]
    for k, v in d.items():
        lines.append(f"  {k}: {v}")
    return "\n".join(lines)
