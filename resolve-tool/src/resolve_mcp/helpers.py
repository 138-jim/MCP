"""Error formatting and connection guard helpers for MCP tools."""

from __future__ import annotations

import functools
import logging
from typing import Callable

from resolve_lib.exceptions import ResolveError

logger = logging.getLogger("resolve_mcp")


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
