"""Wrapper for DaVinci Resolve node graph (Color page)."""

from __future__ import annotations

from resolve_lib.exceptions import ResolveOperationError
from resolve_lib.validators import validate_node_index


class Graph:
    """Wraps a Resolve node graph object for color grading operations."""

    def __init__(self, obj):
        self._obj = obj

    def get_num_nodes(self) -> int:
        """Return the number of nodes in the graph."""
        return self._obj.GetNumNodes() or 0

    def get_lut(self, node_index: int) -> str:
        """Get the LUT file path applied to a node (1-based index)."""
        validate_node_index(node_index)
        return self._obj.GetLUT(node_index) or ""

    def set_lut(self, node_index: int, lut_path: str) -> bool:
        """Apply a LUT file to a node (1-based index)."""
        validate_node_index(node_index)
        return bool(self._obj.SetLUT(node_index, lut_path))

    def get_node_cache_mode(self, node_index: int) -> int:
        """Get cache mode for a node. Returns 0=None, 1=Smart, 2=On."""
        validate_node_index(node_index)
        fn = getattr(self._obj, "GetNodeCacheMode", None)
        if not callable(fn):
            return 0
        result = fn(node_index)
        return result if result is not None else 0

    def set_node_cache_mode(self, node_index: int, mode: int) -> bool:
        """Set cache mode for a node. mode: 0=None, 1=Smart, 2=On."""
        validate_node_index(node_index)
        fn = getattr(self._obj, "SetNodeCacheMode", None)
        if not callable(fn):
            return False
        return bool(fn(node_index, mode))

    def get_node_label(self, node_index: int) -> str:
        """Get the label of a node."""
        validate_node_index(node_index)
        fn = getattr(self._obj, "GetNodeLabel", None)
        if not callable(fn):
            return ""
        return fn(node_index) or ""

    def set_node_label(self, node_index: int, label: str) -> bool:
        """Set the label of a node."""
        validate_node_index(node_index)
        fn = getattr(self._obj, "SetNodeLabel", None)
        if not callable(fn):
            return False
        return bool(fn(node_index, label))

    def get_tools_in_node(self, node_index: int) -> list[str]:
        """Get list of tool names in a node."""
        validate_node_index(node_index)
        fn = getattr(self._obj, "GetToolsInNode", None)
        if not callable(fn):
            return []
        return fn(node_index) or []

    def set_node_enabled(self, node_index: int, enabled: bool) -> bool:
        """Enable or disable a node."""
        validate_node_index(node_index)
        fn = getattr(self._obj, "SetNodeEnabled", None)
        if not callable(fn):
            return False
        return bool(fn(node_index, enabled))

    def get_node_enabled(self, node_index: int) -> bool:
        """Check if a node is enabled."""
        validate_node_index(node_index)
        fn = getattr(self._obj, "GetNodeEnabled", None)
        if not callable(fn):
            return True
        return bool(fn(node_index))

    def apply_grade_from_drx(
        self, path: str, grade_mode: int = 0, item=None
    ) -> bool:
        """Apply a grade from a .drx still file.

        Args:
            path: Path to the .drx file.
            grade_mode: 0=No keyframes, 1=Source timecode, 2=Start timecode.
            item: Optional TimelineItem raw object for targeted apply.
        """
        fn = getattr(self._obj, "ApplyGradeFromDRX", None)
        if not callable(fn):
            return False
        if item is not None:
            raw = item._obj if hasattr(item, "_obj") else item
            return bool(fn(path, grade_mode, raw))
        return bool(fn(path, grade_mode))

    def apply_arri_cdl_lut(self) -> bool:
        """Apply ARRI CDL and LUT."""
        fn = getattr(self._obj, "ApplyArriCdlLut", None)
        if not callable(fn):
            return False
        return bool(fn())

    def refresh_lut_list(self) -> bool:
        """Refresh the LUT list for the node graph.

        Returns
        -------
        bool
            ``True`` if the LUT list was refreshed successfully.
        """
        fn = getattr(self._obj, "RefreshLUTList", None)
        if not callable(fn):
            return False
        return bool(fn())

    def reset_grades(self) -> bool:
        """Reset all grading on the current node graph."""
        fn = getattr(self._obj, "ResetAllGrades", None)
        if not callable(fn):
            return False
        return bool(fn())
