"""MCP tools for advanced Fusion scripting operations."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from resolve_mcp.helpers import resolve_tool, get_item
from resolve_mcp.state import ServerState


def _get_fusion_comp(
    state: ServerState,
    track_type: str,
    track_index: int,
    item_index: int,
    comp_index: int,
) -> tuple[object | None, str | None]:
    """Return (comp, None) on success or (None, error_message) on failure."""
    item = get_item(state, track_type, track_index, item_index)
    if item is None:
        return None, f"Item not found at {track_type}:{track_index}:{item_index}"
    comp = item.get_fusion_comp_by_index(comp_index)
    if comp is None:
        return None, f"Fusion comp not found at index {comp_index}"
    return comp, None


def _find_tool(comp: object, tool_name: str) -> tuple[object | None, str | None]:
    """Return (tool, None) on success or (None, error_message) on failure."""
    tool = comp.FindTool(tool_name)  # type: ignore[attr-defined]
    if tool is None:
        return None, f"Tool '{tool_name}' not found in composition"
    return tool, None


def _auto_convert(value: str) -> object:
    """Try to convert a string value to float/int, falling back to string."""
    try:
        numeric = float(value)
        if numeric == int(numeric):
            return int(numeric)
        return numeric
    except ValueError:
        return value


def register_fusion_scripting_tools(mcp: FastMCP, state: ServerState) -> None:
    """Register all advanced Fusion scripting tools."""

    @mcp.tool()
    @resolve_tool
    def resolve_fusion_lock(
        track_type: str,
        track_index: int,
        item_index: int,
        comp_index: int = 1,
    ) -> str:
        """Lock a Fusion composition to prevent re-rendering during batch changes.

        Call this before making multiple changes, then unlock when done.
        This significantly improves performance for batch operations.

        Args:
            track_type: Track type (video or audio).
            track_index: Track index (1-based).
            item_index: Item index within the track (0-based).
            comp_index: Fusion composition index (1-based, default 1).
        """
        comp, err = _get_fusion_comp(state, track_type, track_index, item_index, comp_index)
        if err:
            return err
        comp.Lock()  # type: ignore[attr-defined]
        return "Composition locked"

    @mcp.tool()
    @resolve_tool
    def resolve_fusion_unlock(
        track_type: str,
        track_index: int,
        item_index: int,
        comp_index: int = 1,
    ) -> str:
        """Unlock a Fusion composition to resume rendering after batch changes.

        Always call this after resolve_fusion_lock to allow Resolve to render.

        Args:
            track_type: Track type (video or audio).
            track_index: Track index (1-based).
            item_index: Item index within the track (0-based).
            comp_index: Fusion composition index (1-based, default 1).
        """
        comp, err = _get_fusion_comp(state, track_type, track_index, item_index, comp_index)
        if err:
            return err
        comp.Unlock()  # type: ignore[attr-defined]
        return "Composition unlocked"

    @mcp.tool()
    @resolve_tool
    def resolve_fusion_start_undo(
        track_type: str,
        track_index: int,
        item_index: int,
        name: str,
        comp_index: int = 1,
    ) -> str:
        """Start an undo group in a Fusion composition.

        All changes between start_undo and end_undo are grouped as a single
        undoable action. Useful for atomic multi-step changes.

        Args:
            track_type: Track type (video or audio).
            track_index: Track index (1-based).
            item_index: Item index within the track (0-based).
            name: Name for the undo action (shown in Edit > Undo menu).
            comp_index: Fusion composition index (1-based, default 1).
        """
        comp, err = _get_fusion_comp(state, track_type, track_index, item_index, comp_index)
        if err:
            return err
        comp.StartUndo(name)  # type: ignore[attr-defined]
        return f"Started undo group: {name}"

    @mcp.tool()
    @resolve_tool
    def resolve_fusion_end_undo(
        track_type: str,
        track_index: int,
        item_index: int,
        keep: bool = True,
        comp_index: int = 1,
    ) -> str:
        """End an undo group in a Fusion composition.

        Args:
            track_type: Track type (video or audio).
            track_index: Track index (1-based).
            item_index: Item index within the track (0-based).
            keep: If True, keep the changes. If False, discard them.
            comp_index: Fusion composition index (1-based, default 1).
        """
        comp, err = _get_fusion_comp(state, track_type, track_index, item_index, comp_index)
        if err:
            return err
        comp.EndUndo(keep)  # type: ignore[attr-defined]
        action = "kept" if keep else "discarded"
        return f"Ended undo group (changes {action})"

    @mcp.tool()
    @resolve_tool
    def resolve_fusion_add_tool(
        track_type: str,
        track_index: int,
        item_index: int,
        tool_type: str,
        comp_index: int = 1,
    ) -> str:
        """Add a Fusion tool node to a composition.

        Common tool types: Background, Merge, Transform, ColorCorrector,
        Blur, Glow, BrightnessContrast, ChannelBooleans, FastNoise,
        Polygon, BSpline, Ellipse, Rectangle, Plasma, Text+.

        Args:
            track_type: Track type (video or audio).
            track_index: Track index (1-based).
            item_index: Item index within the track (0-based).
            tool_type: Fusion tool type ID (e.g. 'Merge', 'Transform').
            comp_index: Fusion composition index (1-based, default 1).
        """
        comp, err = _get_fusion_comp(state, track_type, track_index, item_index, comp_index)
        if err:
            return err
        tool = comp.AddTool(tool_type, -32768, -32768)  # type: ignore[attr-defined]
        if tool is None:
            return f"Failed to add tool of type '{tool_type}'"
        return f"Added tool: {tool.Name} (type: {tool_type})"

    @mcp.tool()
    @resolve_tool
    def resolve_fusion_connect(
        track_type: str,
        track_index: int,
        item_index: int,
        tool_name: str,
        input_name: str,
        target_tool: str,
        comp_index: int = 1,
    ) -> str:
        """Connect one Fusion tool's output to another tool's input.

        For example, connect a Background tool to a Merge's Background input.

        Args:
            track_type: Track type (video or audio).
            track_index: Track index (1-based).
            item_index: Item index within the track (0-based).
            tool_name: Name of the tool receiving the connection.
            input_name: Input name on tool_name (e.g. 'Background', 'Input').
            target_tool: Name of the tool whose output to connect.
            comp_index: Fusion composition index (1-based, default 1).
        """
        comp, err = _get_fusion_comp(state, track_type, track_index, item_index, comp_index)
        if err:
            return err
        tool, terr = _find_tool(comp, tool_name)
        if terr:
            return terr
        target, terr2 = _find_tool(comp, target_tool)
        if terr2:
            return terr2
        tool.ConnectInput(input_name, target)  # type: ignore[attr-defined]
        return f"Connected {target_tool} -> {tool_name}.{input_name}"

    @mcp.tool()
    @resolve_tool
    def resolve_fusion_set_input(
        track_type: str,
        track_index: int,
        item_index: int,
        tool_name: str,
        input_name: str,
        value: str,
        time: int | None = None,
        comp_index: int = 1,
    ) -> str:
        """Set an input value on a Fusion tool by tool name.

        Unlike resolve_set_fusion_tool_input which looks up tools by type ID,
        this uses the tool's instance name (e.g. 'Background1', 'Merge1').

        Values are auto-converted: numeric strings become float/int.

        Args:
            track_type: Track type (video or audio).
            track_index: Track index (1-based).
            item_index: Item index within the track (0-based).
            tool_name: Instance name of the tool (e.g. 'Background1').
            input_name: Name of the input to set (e.g. 'TopLeftRed').
            value: The value to set (numbers are auto-converted).
            time: Optional frame number for keyframed values.
            comp_index: Fusion composition index (1-based, default 1).
        """
        comp, err = _get_fusion_comp(state, track_type, track_index, item_index, comp_index)
        if err:
            return err
        tool, terr = _find_tool(comp, tool_name)
        if terr:
            return terr
        converted = _auto_convert(value)
        if time is not None:
            tool.SetInput(input_name, converted, time)  # type: ignore[attr-defined]
        else:
            tool.SetInput(input_name, converted)  # type: ignore[attr-defined]
        return f"Set {tool_name}.{input_name} = {value!r}"

    @mcp.tool()
    @resolve_tool
    def resolve_fusion_get_input(
        track_type: str,
        track_index: int,
        item_index: int,
        tool_name: str,
        input_name: str,
        time: int | None = None,
        comp_index: int = 1,
    ) -> str:
        """Get an input value from a Fusion tool by tool name.

        Args:
            track_type: Track type (video or audio).
            track_index: Track index (1-based).
            item_index: Item index within the track (0-based).
            tool_name: Instance name of the tool (e.g. 'Background1').
            input_name: Name of the input to read (e.g. 'TopLeftRed').
            time: Optional frame number for keyframed values.
            comp_index: Fusion composition index (1-based, default 1).
        """
        comp, err = _get_fusion_comp(state, track_type, track_index, item_index, comp_index)
        if err:
            return err
        tool, terr = _find_tool(comp, tool_name)
        if terr:
            return terr
        if time is not None:
            result = tool.GetInput(input_name, time)  # type: ignore[attr-defined]
        else:
            result = tool.GetInput(input_name)  # type: ignore[attr-defined]
        if result is None:
            return f"Could not read {tool_name}.{input_name}"
        return f"{tool_name}.{input_name} = {result!r}"

    @mcp.tool()
    @resolve_tool
    def resolve_fusion_get_tool_list(
        track_type: str,
        track_index: int,
        item_index: int,
        comp_index: int = 1,
    ) -> str:
        """List all tools in a Fusion composition with their names and types.

        Args:
            track_type: Track type (video or audio).
            track_index: Track index (1-based).
            item_index: Item index within the track (0-based).
            comp_index: Fusion composition index (1-based, default 1).
        """
        comp, err = _get_fusion_comp(state, track_type, track_index, item_index, comp_index)
        if err:
            return err
        tools = comp.GetToolList()  # type: ignore[attr-defined]
        if not tools:
            return "No tools in composition"
        lines = [f"Tools in composition ({len(tools)}):"]
        for _idx, tool in tools.items():
            lines.append(f"  {tool.Name}: {tool.ID}")
        return "\n".join(lines)

    @mcp.tool()
    @resolve_tool
    def resolve_fusion_execute(
        track_type: str,
        track_index: int,
        item_index: int,
        script: str,
        comp_index: int = 1,
    ) -> str:
        """Execute a Lua script in the context of a Fusion composition.

        The script has access to the 'comp' variable automatically. Use this
        for complex multi-step operations to avoid per-call round-trip overhead.

        Args:
            track_type: Track type (video or audio).
            track_index: Track index (1-based).
            item_index: Item index within the track (0-based).
            script: Lua script to execute.
            comp_index: Fusion composition index (1-based, default 1).
        """
        comp, err = _get_fusion_comp(state, track_type, track_index, item_index, comp_index)
        if err:
            return err
        comp.Execute(script)  # type: ignore[attr-defined]
        return "Script executed"

    @mcp.tool()
    @resolve_tool
    def resolve_fusion_add_keyframe(
        track_type: str,
        track_index: int,
        item_index: int,
        tool_name: str,
        input_name: str,
        time: int,
        value: str,
        comp_index: int = 1,
    ) -> str:
        """Add a keyframe to animate a Fusion tool input at a specific frame.

        This sets the input value at the given time, creating or updating a
        keyframe. The input must already be animated (use BezierSpline) or
        this will set a static value at that time.

        Values are auto-converted: numeric strings become float/int.

        Args:
            track_type: Track type (video or audio).
            track_index: Track index (1-based).
            item_index: Item index within the track (0-based).
            tool_name: Instance name of the tool (e.g. 'Transform1').
            input_name: Name of the input to keyframe (e.g. 'Size').
            time: Frame number for the keyframe.
            value: The value at this keyframe (numbers are auto-converted).
            comp_index: Fusion composition index (1-based, default 1).
        """
        comp, err = _get_fusion_comp(state, track_type, track_index, item_index, comp_index)
        if err:
            return err
        tool, terr = _find_tool(comp, tool_name)
        if terr:
            return terr
        converted = _auto_convert(value)
        tool.SetInput(input_name, converted, time)  # type: ignore[attr-defined]
        return f"Set keyframe: {tool_name}.{input_name} = {value!r} at frame {time}"
