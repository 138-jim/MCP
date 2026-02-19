"""Wrapper for DaVinci Resolve ColorGroup object."""

from __future__ import annotations


class ColorGroup:
    """Wraps a Resolve ColorGroup object."""

    def __init__(self, obj):
        self._obj = obj

    def get_name(self) -> str:
        """Get the name of this color group."""
        return self._obj.GetName() or ""

    def set_name(self, name: str) -> bool:
        """Set the name of this color group."""
        return bool(self._obj.SetName(name))

    def get_clips_in_timeline(self, timeline=None) -> list:
        """Get clips belonging to this color group in the given timeline.

        Args:
            timeline: A Timeline wrapper object. If None, uses current timeline.

        Returns:
            List of TimelineItem wrappers.
        """
        from resolve_lib.timeline_item import TimelineItem

        raw_tl = timeline._obj if timeline and hasattr(timeline, "_obj") else timeline
        fn = getattr(self._obj, "GetClipsInTimeline", None)
        if fn is None:
            return []
        if raw_tl is not None:
            result = fn(raw_tl)
        else:
            result = fn()
        return [TimelineItem(c) for c in result] if result else []

    def get_pre_clip_node_graph(self) -> object | None:
        """Get the pre-clip node graph for this color group."""
        from resolve_lib.graph import Graph

        fn = getattr(self._obj, "GetPreClipNodeGraph", None)
        if fn is None:
            return None
        obj = fn()
        return Graph(obj) if obj else None

    def get_post_clip_node_graph(self) -> object | None:
        """Get the post-clip node graph for this color group."""
        from resolve_lib.graph import Graph

        fn = getattr(self._obj, "GetPostClipNodeGraph", None)
        if fn is None:
            return None
        obj = fn()
        return Graph(obj) if obj else None
