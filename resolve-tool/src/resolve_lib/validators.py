"""Validation helpers for resolve_lib."""

from __future__ import annotations

from resolve_lib.exceptions import ResolveValidationError
from resolve_lib.types import Page, TrackType


def validate_track_index(index: int, *, min_val: int = 1) -> None:
    """Ensure track index is a positive integer (1-based)."""
    if not isinstance(index, int) or index < min_val:
        raise ResolveValidationError(
            f"Track index must be an integer >= {min_val}, got {index!r}"
        )


def validate_node_index(index: int) -> None:
    """Ensure node index is a positive integer (1-based)."""
    if not isinstance(index, int) or index < 1:
        raise ResolveValidationError(
            f"Node index must be an integer >= 1, got {index!r}"
        )


def validate_page(page: str) -> str:
    """Validate and normalize a page name."""
    try:
        return Page(page.lower()).value
    except ValueError:
        valid = ", ".join(p.value for p in Page)
        raise ResolveValidationError(
            f"Invalid page {page!r}. Must be one of: {valid}"
        )


def validate_track_type(track_type: str) -> str:
    """Validate and normalize a track type string."""
    try:
        return TrackType(track_type.lower()).value
    except ValueError:
        valid = ", ".join(t.value for t in TrackType)
        raise ResolveValidationError(
            f"Invalid track type {track_type!r}. Must be one of: {valid}"
        )


def validate_frame(frame: int, name: str = "frame") -> None:
    """Ensure a frame number is a non-negative integer."""
    if not isinstance(frame, int) or frame < 0:
        raise ResolveValidationError(
            f"{name} must be a non-negative integer, got {frame!r}"
        )
