"""MCP tools for timeline item (clip) operations."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from resolve_mcp.helpers import resolve_tool, format_dict, get_item
from resolve_mcp.state import ServerState


def register_timeline_item_tools(mcp: FastMCP, state: ServerState):

    @mcp.tool()
    @resolve_tool
    def resolve_get_item_properties(
        track_type: str, track_index: int, item_index: int
    ) -> str:
        """Get all properties of a timeline item.

        Args:
            track_type: Track type (video or audio).
            track_index: Track index (1-based).
            item_index: Item index within the track (0-based).
        """
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return f"Item not found at {track_type}:{track_index}:{item_index}"
        props = item.get_property()
        if isinstance(props, dict):
            return format_dict(props, f"Properties of {item.get_name()}")
        return str(props)

    @mcp.tool()
    @resolve_tool
    def resolve_get_item_property(
        track_type: str, track_index: int, item_index: int, key: str
    ) -> str:
        """Get a specific property of a timeline item (e.g. Pan, Tilt, ZoomX, Opacity)."""
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return f"Item not found at {track_type}:{track_index}:{item_index}"
        val = item.get_property(key)
        return f"{key}: {val}"

    @mcp.tool()
    @resolve_tool
    def resolve_set_item_property(
        track_type: str, track_index: int, item_index: int, key: str, value: str
    ) -> str:
        """Set a property on a timeline item (e.g. Pan, Tilt, ZoomX, Opacity, CompositeMode)."""
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return f"Item not found at {track_type}:{track_index}:{item_index}"
        # Try to convert to number if applicable
        try:
            numeric = float(value)
            if numeric == int(numeric):
                numeric = int(numeric)
            result = item.set_property(key, numeric)
        except ValueError:
            result = item.set_property(key, value)
        if result:
            return f"Set {key}={value} on {item.get_name()}"
        return f"Failed to set {key} on {item.get_name()}"

    @mcp.tool()
    @resolve_tool
    def resolve_get_item_info(
        track_type: str, track_index: int, item_index: int
    ) -> str:
        """Get identity/placement info for a timeline item."""
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return f"Item not found at {track_type}:{track_index}:{item_index}"
        lines = [
            f"Name: {item.get_name()}",
            f"Start: {item.get_start()}",
            f"End: {item.get_end()}",
            f"Duration: {item.get_duration()}",
        ]
        return "\n".join(lines)

    @mcp.tool()
    @resolve_tool
    def resolve_get_item_markers(
        track_type: str, track_index: int, item_index: int
    ) -> str:
        """Get all markers on a timeline item."""
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return f"Item not found at {track_type}:{track_index}:{item_index}"
        markers = item.get_markers()
        if not markers:
            return f"No markers on {item.get_name()}"
        lines = [f"Markers on {item.get_name()}:"]
        for frame, info in markers.items():
            lines.append(f"  Frame {frame}: {info}")
        return "\n".join(lines)

    @mcp.tool()
    @resolve_tool
    def resolve_add_item_marker(
        track_type: str, track_index: int, item_index: int,
        frame: int, color: str, name: str, note: str = "", duration: int = 1
    ) -> str:
        """Add a marker to a timeline item at the given frame offset."""
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return f"Item not found at {track_type}:{track_index}:{item_index}"
        if item.add_marker(frame, color, name, note, duration):
            return f"Added {color} marker at frame {frame}"
        return "Failed to add marker"

    @mcp.tool()
    @resolve_tool
    def resolve_set_item_clip_color(
        track_type: str, track_index: int, item_index: int, color: str
    ) -> str:
        """Set the clip color label on a timeline item."""
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return f"Item not found at {track_type}:{track_index}:{item_index}"
        if item.set_clip_color(color):
            return f"Set clip color to {color}"
        return "Failed to set clip color"

    @mcp.tool()
    @resolve_tool
    def resolve_list_fusion_comps(
        track_type: str, track_index: int, item_index: int
    ) -> str:
        """List Fusion compositions on a timeline item."""
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return f"Item not found at {track_type}:{track_index}:{item_index}"
        names = item.get_fusion_comp_name_list()
        if not names:
            return f"No Fusion comps on {item.get_name()}"
        lines = [f"Fusion comps on {item.get_name()}:"]
        for n in names:
            lines.append(f"  - {n}")
        return "\n".join(lines)

    @mcp.tool()
    @resolve_tool
    def resolve_add_fusion_comp(
        track_type: str, track_index: int, item_index: int
    ) -> str:
        """Add a new Fusion composition to a timeline item."""
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return f"Item not found at {track_type}:{track_index}:{item_index}"
        comp = item.add_fusion_comp()
        if comp:
            return f"Added Fusion comp to {item.get_name()}"
        return "Failed to add Fusion comp"

    @mcp.tool()
    @resolve_tool
    def resolve_set_fusion_tool_input(
        track_type: str,
        track_index: int,
        item_index: int,
        tool_id: str,
        input_name: str,
        value: str,
        comp_index: int = 1,
    ) -> str:
        """Set an input on a Fusion tool inside a timeline item's composition.

        Common examples:
        - Text+ text: tool_id='TextPlus', input_name='StyledText', value='Hello'
        - Text+ size: tool_id='TextPlus', input_name='Size', value='0.08'
        - Text+ font: tool_id='TextPlus', input_name='Font', value='Open Sans'
        - Background color: tool_id='Background', input_name='TopLeftRed', value='0.5'

        Args:
            track_type: Track type (video or audio).
            track_index: Track index (1-based).
            item_index: Item index within the track (0-based).
            tool_id: Fusion tool ID (e.g. 'TextPlus', 'Background').
            input_name: Name of the input to set (e.g. 'StyledText').
            value: The value to set (numbers are auto-converted).
            comp_index: Fusion composition index (1-based, default 1).
        """
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return f"Item not found at {track_type}:{track_index}:{item_index}"
        # Auto-convert numeric strings
        converted: object = value
        try:
            converted = float(value)
            if converted == int(converted):
                converted = int(converted)
        except ValueError:
            pass
        ok = item.set_fusion_tool_input(tool_id, input_name, converted, comp_index)
        if ok:
            return f"Set {tool_id}.{input_name} = {value!r}"
        return f"Failed to set {tool_id}.{input_name} (tool or input not found)"

    @mcp.tool()
    @resolve_tool
    def resolve_get_fusion_tool_input(
        track_type: str,
        track_index: int,
        item_index: int,
        tool_id: str,
        input_name: str,
        comp_index: int = 1,
    ) -> str:
        """Get an input value from a Fusion tool inside a timeline item's composition.

        Args:
            track_type: Track type (video or audio).
            track_index: Track index (1-based).
            item_index: Item index within the track (0-based).
            tool_id: Fusion tool ID (e.g. 'TextPlus', 'Background').
            input_name: Name of the input (e.g. 'StyledText', 'Size').
            comp_index: Fusion composition index (1-based, default 1).
        """
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return f"Item not found at {track_type}:{track_index}:{item_index}"
        result = item.get_fusion_tool_input(tool_id, input_name, comp_index)
        if result is None:
            return f"Could not read {tool_id}.{input_name} (tool or input not found)"
        return f"{tool_id}.{input_name} = {result!r}"

    @mcp.tool()
    @resolve_tool
    def resolve_list_color_versions(
        track_type: str, track_index: int, item_index: int, version_type: str = "local"
    ) -> str:
        """List color versions on a timeline item."""
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return f"Item not found at {track_type}:{track_index}:{item_index}"
        versions = item.get_version_name_list(version_type)
        if not versions:
            return f"No {version_type} color versions"
        lines = [f"{version_type.title()} color versions:"]
        for v in versions:
            lines.append(f"  - {v}")
        return "\n".join(lines)

    @mcp.tool()
    @resolve_tool
    def resolve_load_color_version(
        track_type: str, track_index: int, item_index: int,
        name: str, version_type: str = "local"
    ) -> str:
        """Load a color version by name on a timeline item."""
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return f"Item not found at {track_type}:{track_index}:{item_index}"
        if item.load_version_by_name(name, version_type):
            return f"Loaded {version_type} version: {name}"
        return f"Failed to load version: {name}"

    # Disabled: CreateMagicMask always returns False (may need Studio)
    @resolve_tool
    def resolve_apply_magic_mask(
        track_type: str, track_index: int, item_index: int, mode: str = "forward"
    ) -> str:
        """Apply Magic Mask to a timeline item (Resolve 18+)."""
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return f"Item not found at {track_type}:{track_index}:{item_index}"
        if item.apply_magic_mask(mode):
            return f"Applied Magic Mask ({mode})"
        return "Failed to apply Magic Mask"

    @mcp.tool()
    @resolve_tool
    def resolve_get_item_offsets(
        track_type: str, track_index: int, item_index: int
    ) -> str:
        """Get trim offsets and source info for a timeline item.

        Returns the clip name, timeline start/end, duration, left/right trim
        offsets, and source start/end frames in one call. Useful for planning
        trim operations.

        Args:
            track_type: Track type (video or audio).
            track_index: Track index (1-based).
            item_index: Item index within the track (0-based).
        """
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return f"Item not found at {track_type}:{track_index}:{item_index}"
        lines = [
            f"Name: {item.get_name()}",
            f"Start: {item.get_start()}",
            f"End: {item.get_end()}",
            f"Duration: {item.get_duration()}",
            f"LeftOffset: {item.get_left_offset()}",
            f"RightOffset: {item.get_right_offset()}",
            f"SourceStart: {item.get_source_start_frame()}",
            f"SourceEnd: {item.get_source_end_frame()}",
        ]
        return "\n".join(lines)

    @mcp.tool()
    @resolve_tool
    def resolve_stabilize_clip(
        track_type: str, track_index: int, item_index: int
    ) -> str:
        """Apply stabilization to a timeline item."""
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return f"Item not found at {track_type}:{track_index}:{item_index}"
        if item.apply_stabilization():
            return "Stabilization applied"
        return "Failed to apply stabilization"

    @mcp.tool()
    @resolve_tool
    def resolve_smart_reframe(
        track_type: str, track_index: int, item_index: int
    ) -> str:
        """Apply Smart Reframe to a timeline item."""
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return f"Item not found at {track_type}:{track_index}:{item_index}"
        if item.apply_smart_reframe():
            return "Smart Reframe applied"
        return "Failed to apply Smart Reframe"
