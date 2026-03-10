"""MCP tools for color node and graph control."""

from __future__ import annotations

import platform
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from resolve_mcp.helpers import (
    resolve_tool,
    format_dict,
    format_list,
    get_project,
    get_item,
)
from resolve_mcp.state import ServerState

# LUT file extensions recognised by DaVinci Resolve
LUT_EXTENSIONS = {
    ".cube", ".3dl", ".dat", ".ilut", ".olut",
    ".look", ".xml", ".csp", ".vlt", ".m3d",
}


def _get_lut_dirs() -> list[Path]:
    """Return the standard DaVinci Resolve LUT directories for this platform."""
    dirs: list[Path] = []
    system = platform.system()
    if system == "Darwin":
        dirs.append(
            Path("/Library/Application Support/Blackmagic Design"
                 "/DaVinci Resolve/LUT")
        )
        dirs.append(
            Path.home() / "Library/Application Support/Blackmagic Design"
            "/DaVinci Resolve/LUT"
        )
    elif system == "Windows":
        prog_data = Path(
            "C:/ProgramData/Blackmagic Design/DaVinci Resolve/Support/LUT"
        )
        dirs.append(prog_data)
    else:  # Linux
        dirs.append(Path("/opt/resolve/LUT"))
        dirs.append(Path.home() / ".local/share/DaVinciResolve/LUT")
    return [d for d in dirs if d.is_dir()]


def _find_luts(subfolder: str = "", search: str = "") -> list[tuple[str, str]]:
    """Find LUT files in the standard directories.

    Returns a list of (relative_path, absolute_path) tuples.
    The relative_path is suitable for passing to Graph.set_lut().
    """
    results: list[tuple[str, str]] = []
    search_lower = search.lower()
    for lut_dir in _get_lut_dirs():
        scan_dir = lut_dir / subfolder if subfolder else lut_dir
        if not scan_dir.is_dir():
            continue
        for f in sorted(scan_dir.rglob("*")):
            if not f.is_file():
                continue
            if f.suffix.lower() not in LUT_EXTENSIONS:
                continue
            if search_lower and search_lower not in f.name.lower():
                continue
            try:
                rel = str(f.relative_to(lut_dir))
            except ValueError:
                rel = str(f)
            results.append((rel, str(f)))
    return results


def register_color_node_tools(mcp: FastMCP, state: ServerState):

    @mcp.tool()
    @resolve_tool
    def resolve_get_cdl(
        track_type: str, track_index: int, item_index: int
    ) -> str:
        """Get the CDL (Color Decision List) values for a timeline item.

        Returns slope, offset, power, and saturation values.
        """
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return "Item not found"
        cdl = item.get_cdl()
        if not cdl:
            return "No CDL data available"
        return format_dict(cdl, f"CDL for {item.get_name()}")

    @mcp.tool()
    @resolve_tool
    def resolve_set_cdl(
        track_type: str, track_index: int, item_index: int,
        slope: str = "", offset: str = "", power: str = "",
        saturation: str = "", node_index: int = 1
    ) -> str:
        """Set CDL (Color Decision List) values on a timeline item.

        Args:
            slope: RGB slope as space-separated string (e.g. "1.0 1.0 1.0").
            offset: RGB offset as space-separated string (e.g. "0 0 0").
            power: RGB power as space-separated string (e.g. "1.0 1.0 1.0").
            saturation: Saturation value (e.g. "1.0").
            node_index: 1-based color node index (default 1).
        """
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return "Item not found"
        cdl = {}
        if slope:
            cdl["Slope"] = slope
        if offset:
            cdl["Offset"] = offset
        if power:
            cdl["Power"] = power
        if saturation:
            cdl["Saturation"] = saturation
        if not cdl:
            return "No CDL values provided"
        cdl["NodeIndex"] = str(node_index)
        if item.set_cdl(cdl):
            return f"Set CDL on {item.get_name()}"
        return "Failed to set CDL"

    @mcp.tool()
    @resolve_tool
    def resolve_get_node_label(
        track_type: str, track_index: int, item_index: int,
        node_index: int
    ) -> str:
        """Get the label of a color node (1-based node index)."""
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return "Item not found"
        graph = item.get_node_graph()
        if graph is None:
            return "No node graph available"
        label = graph.get_node_label(node_index)
        if label:
            return f"Node {node_index} label: {label}"
        return f"No label on node {node_index}"

    @mcp.tool()
    @resolve_tool
    def resolve_get_tools_in_node(
        track_type: str, track_index: int, item_index: int,
        node_index: int
    ) -> str:
        """Get the list of tool names in a color node (1-based node index)."""
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return "Item not found"
        graph = item.get_node_graph()
        if graph is None:
            return "No node graph available"
        tools = graph.get_tools_in_node(node_index)
        return format_list(tools, f"tools in node {node_index}")

    @mcp.tool()
    @resolve_tool
    def resolve_set_node_enabled(
        track_type: str, track_index: int, item_index: int,
        node_index: int, enabled: bool
    ) -> str:
        """Enable or disable a color node (1-based node index)."""
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return "Item not found"
        graph = item.get_node_graph()
        if graph is None:
            return "No node graph available"
        if graph.set_node_enabled(node_index, enabled):
            status = "enabled" if enabled else "disabled"
            return f"Node {node_index} {status}"
        return f"Failed to set node {node_index} enabled state"

    @mcp.tool()
    @resolve_tool
    def resolve_get_node_cache_mode(
        track_type: str, track_index: int, item_index: int,
        node_index: int
    ) -> str:
        """Get the cache mode of a color node (1-based index).

        Returns 0=None, 1=Smart, 2=On.
        """
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return "Item not found"
        graph = item.get_node_graph()
        if graph is None:
            return "No node graph available"
        mode = graph.get_node_cache_mode(node_index)
        mode_names = {0: "None", 1: "Smart", 2: "On"}
        return f"Node {node_index} cache mode: {mode} ({mode_names.get(mode, 'Unknown')})"

    @mcp.tool()
    @resolve_tool
    def resolve_set_node_cache_mode(
        track_type: str, track_index: int, item_index: int,
        node_index: int, mode: int
    ) -> str:
        """Set the cache mode of a color node (1-based index).

        Args:
            mode: 0=None, 1=Smart, 2=On.
        """
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return "Item not found"
        graph = item.get_node_graph()
        if graph is None:
            return "No node graph available"
        if graph.set_node_cache_mode(node_index, mode):
            mode_names = {0: "None", 1: "Smart", 2: "On"}
            return f"Set node {node_index} cache mode to {mode} ({mode_names.get(mode, 'Unknown')})"
        return f"Failed to set cache mode on node {node_index}"

    @mcp.tool()
    @resolve_tool
    def resolve_apply_arri_cdl_lut(
        track_type: str, track_index: int, item_index: int
    ) -> str:
        """Apply ARRI CDL and LUT to a timeline item's node graph."""
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return "Item not found"
        graph = item.get_node_graph()
        if graph is None:
            return "No node graph available"
        if graph.apply_arri_cdl_lut():
            return f"Applied ARRI CDL+LUT to {item.get_name()}"
        return "Failed to apply ARRI CDL+LUT"

    @mcp.tool()
    @resolve_tool
    def resolve_reset_all_node_colors(
        track_type: str, track_index: int, item_index: int
    ) -> str:
        """Reset all node label colours on a timeline item."""
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return "Item not found"
        if item.reset_all_node_colors():
            return f"Reset all node colours on {item.get_name()}"
        return "Failed to reset node colours"

    @mcp.tool()
    @resolve_tool
    def resolve_refresh_lut_list() -> str:
        """Refresh the LUT list for the current project."""
        proj = get_project(state)
        if proj.refresh_lut_list():
            return "LUT list refreshed"
        return "Failed to refresh LUT list"

    # ------------------------------------------------------------------
    # LUT discovery
    # ------------------------------------------------------------------

    @mcp.tool()
    @resolve_tool
    def resolve_list_lut_folders(subfolder: str = "") -> str:
        """List LUT folders/categories available in DaVinci Resolve.

        Browse the standard LUT directories. Pass a subfolder to drill
        into a category (e.g. "Blackmagic Design", "ACES", "Arri").

        Args:
            subfolder: Subfolder path to browse (empty for root).
        """
        lut_dirs = _get_lut_dirs()
        if not lut_dirs:
            return "No LUT directories found on this system."
        folders: list[str] = []
        files: list[str] = []
        for lut_dir in lut_dirs:
            scan_dir = lut_dir / subfolder if subfolder else lut_dir
            if not scan_dir.is_dir():
                continue
            for entry in sorted(scan_dir.iterdir()):
                name = entry.name
                if entry.is_dir() and name not in folders:
                    folders.append(name)
                elif entry.is_file() and entry.suffix.lower() in LUT_EXTENSIONS:
                    if name not in files:
                        files.append(name)
        lines: list[str] = []
        if subfolder:
            lines.append(f"Contents of LUT folder '{subfolder}':")
        else:
            lines.append("LUT root folders:")
        if folders:
            lines.append(f"\nFolders ({len(folders)}):")
            for f in folders:
                lines.append(f"  [dir] {f}")
        if files:
            lines.append(f"\nLUT files ({len(files)}):")
            for f in files:
                lines.append(f"  {f}")
        if not folders and not files:
            lines.append("  (empty)")
        return "\n".join(lines)

    @mcp.tool()
    @resolve_tool
    def resolve_search_luts(search: str, subfolder: str = "") -> str:
        """Search for LUT files by name across all DaVinci Resolve LUT directories.

        Args:
            search: Text to search for in LUT file names (case-insensitive).
            subfolder: Optional subfolder to limit search (e.g. "Arri").
        """
        results = _find_luts(subfolder=subfolder, search=search)
        if not results:
            return f"No LUTs found matching '{search}'."
        lines = [f"Found {len(results)} LUT(s) matching '{search}':"]
        for i, (rel, _abs) in enumerate(results, 1):
            lines.append(f"  {i}. {rel}")
            if i >= 50:
                remaining = len(results) - 50
                if remaining > 0:
                    lines.append(f"  ... and {remaining} more")
                break
        return "\n".join(lines)

    @mcp.tool()
    @resolve_tool
    def resolve_apply_lut_by_name(
        track_type: str, track_index: int, item_index: int,
        node_index: int, search: str
    ) -> str:
        """Search for a LUT by name and apply it to a color node.

        Searches DaVinci Resolve's LUT directories for a matching file
        and applies it to the specified node. Use resolve_search_luts
        first if you want to browse available LUTs.

        Args:
            node_index: 1-based color node index.
            search: LUT name or partial name to search for (case-insensitive).
        """
        item = get_item(state, track_type, track_index, item_index)
        if item is None:
            return "Item not found"
        graph = item.get_node_graph()
        if graph is None:
            return "No node graph available"
        results = _find_luts(search=search)
        if not results:
            return f"No LUT found matching '{search}'."
        if len(results) > 1:
            # Try exact stem match first
            exact = [r for r in results if Path(r[1]).stem.lower() == search.lower()]
            if len(exact) == 1:
                results = exact
            else:
                lines = [
                    f"Multiple LUTs match '{search}'. Be more specific, "
                    f"or use resolve_search_luts to browse:"
                ]
                for rel, _ in results[:10]:
                    lines.append(f"  - {rel}")
                if len(results) > 10:
                    lines.append(f"  ... and {len(results) - 10} more")
                return "\n".join(lines)
        rel_path, abs_path = results[0]
        if graph.set_lut(node_index, abs_path):
            return f"Applied LUT '{rel_path}' to node {node_index} on {item.get_name()}"
        return f"Failed to apply LUT '{rel_path}'. Try resolve_refresh_lut_list first."
