"""MCP tool for executing arbitrary Python against the DaVinci Resolve API.

Provides a single escape-hatch tool — ``resolve_execute_python`` — that
runs a Python script string inside the MCP server process with pre-populated
``resolve``, ``proj``, ``tl``, and ``items`` variables pointing at the raw
Resolve scripting objects.

This gives the creative agent immediate access to any Resolve API method —
including new features added in Resolve updates — without requiring a new
dedicated MCP tool for each one.
"""

from __future__ import annotations

import io
import sys
import traceback

from mcp.server.fastmcp import FastMCP

from resolve_mcp.helpers import resolve_tool
from resolve_mcp.state import ServerState


def register_python_exec_tools(mcp: FastMCP, state: ServerState) -> None:

    @mcp.tool()
    @resolve_tool
    def resolve_execute_python(script: str) -> str:
        """Execute a Python script with full DaVinci Resolve API access.

        The script runs inside the MCP server process, which is already
        connected to a live Resolve instance. The following variables are
        pre-populated in the script's namespace:

        - ``resolve``  — raw ``scriptapp("Resolve")`` object
        - ``proj``     — raw current Project object
        - ``tl``       — raw current Timeline object (may be None)
        - ``items``    — list of raw TimelineItem objects on video track 1
                         (empty list if no timeline is open)
        - ``media_pool`` — raw MediaPool object

        Any output written to ``print()`` / stdout is captured and returned.
        Use this tool to access Resolve 21 features (Stabilize, SmartReframe,
        CreateSubtitlesFromAudio, SetFusionOutputCache, etc.) or any API
        method not covered by dedicated MCP tools.

        Example — enable Fusion cache on all clips::

            for item in items:
                item.SetFusionOutputCache("enable")
            print(f"Cached {len(items)} clips")

        Example — auto-captions for current timeline::

            tl.CreateSubtitlesFromAudio()
            print("Subtitles created")

        Example — stabilise clip 0::

            items[0].Stabilize()
            print("Stabilised")

        Args:
            script: Python source code to execute.

        Returns:
            Captured stdout from the script, or an error message.
        """
        # --- Build execution namespace from live Resolve session ---
        raw_resolve = state.session._obj

        raw_pm = raw_resolve.GetProjectManager()
        raw_proj = raw_pm.GetCurrentProject() if raw_pm else None
        raw_tl = raw_proj.GetCurrentTimeline() if raw_proj else None
        raw_items: list = []
        if raw_tl:
            try:
                raw_items = list(raw_tl.GetItemListInTrack("video", 1) or [])
            except Exception:
                raw_items = []
        raw_pool = raw_proj.GetMediaPool() if raw_proj else None

        namespace: dict = {
            "__builtins__": __builtins__,
            "resolve": raw_resolve,
            "proj": raw_proj,
            "tl": raw_tl,
            "items": raw_items,
            "media_pool": raw_pool,
        }

        # --- Capture stdout ---
        buf = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buf

        try:
            exec(script, namespace)  # noqa: S102
        except Exception:
            sys.stdout = old_stdout
            error = traceback.format_exc()
            output = buf.getvalue()
            parts = []
            if output:
                parts.append(output)
            parts.append(f"Script error:\n{error}")
            return "\n".join(parts)
        finally:
            sys.stdout = old_stdout

        output = buf.getvalue()
        return output if output.strip() else "OK"
