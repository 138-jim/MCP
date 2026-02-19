"""Connect to a running DaVinci Resolve instance.

3-tier fallback strategy:
1. ``import DaVinciResolveScript`` (works when PYTHONPATH includes the Resolve scripts dir)
2. Dynamic load from ``RESOLVE_SCRIPT_LIB`` environment variable
3. Known default paths per platform (macOS / Windows / Linux)
"""

from __future__ import annotations

import importlib
import importlib.util
import os
import sys
from pathlib import Path

from resolve_lib.exceptions import ResolveConnectionError


def _default_script_paths() -> list[Path]:
    """Return platform-specific default paths for the Resolve scripting module."""
    if sys.platform == "darwin":
        return [
            Path(
                "/Library/Application Support/Blackmagic Design"
                "/DaVinci Resolve/Developer/Scripting/Modules"
            ),
        ]
    elif sys.platform == "win32":
        prog = os.environ.get("PROGRAMDATA", r"C:\ProgramData")
        return [
            Path(prog)
            / "Blackmagic Design"
            / "DaVinci Resolve"
            / "Support"
            / "Developer"
            / "Scripting"
            / "Modules",
        ]
    else:
        # Linux
        return [
            Path("/opt/resolve/Developer/Scripting/Modules"),
            Path("/opt/resolve/libs/Fusion/Modules"),
        ]


def _load_script_module():
    """Load the DaVinciResolveScript module using the 3-tier fallback."""
    # Tier 1: direct import (PYTHONPATH already set)
    try:
        mod = importlib.import_module("DaVinciResolveScript")
        return mod
    except ImportError:
        pass

    # Tier 2: explicit env var
    env_path = os.environ.get("RESOLVE_SCRIPT_LIB")
    if env_path:
        p = Path(env_path)
        if p.is_file():
            spec = importlib.util.spec_from_file_location("DaVinciResolveScript", p)
        elif p.is_dir():
            spec = importlib.util.spec_from_file_location(
                "DaVinciResolveScript", p / "DaVinciResolveScript.py"
            )
        else:
            spec = None
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod

    # Tier 3: platform defaults
    for base in _default_script_paths():
        candidate = base / "DaVinciResolveScript.py"
        if candidate.exists():
            spec = importlib.util.spec_from_file_location("DaVinciResolveScript", candidate)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                return mod

    raise ResolveConnectionError(
        "Could not find DaVinciResolveScript module. "
        "Ensure DaVinci Resolve is installed and either:\n"
        "  - PYTHONPATH includes the Resolve Scripting/Modules directory, or\n"
        "  - RESOLVE_SCRIPT_LIB points to the module file/directory, or\n"
        "  - Resolve is installed in the default location."
    )


def connect():
    """Connect to a running DaVinci Resolve instance.

    Returns the raw Resolve API root object.

    Raises:
        ResolveConnectionError: If the scripting module cannot be found
            or Resolve is not running.
    """
    mod = _load_script_module()

    # DaVinciResolveScript.py replaces itself in sys.modules with the
    # fusionscript module.  When loaded via importlib the original ``mod``
    # reference still points to the stub, so prefer the replaced module.
    replaced = sys.modules.get("DaVinciResolveScript")
    if replaced is not None and replaced is not mod:
        mod = replaced

    resolve = None

    # Strategy 1: scriptapp (traditional)
    scriptapp_fn = getattr(mod, "scriptapp", None)
    if callable(scriptapp_fn):
        try:
            resolve = scriptapp_fn("Resolve")
        except Exception:
            pass

    # Strategy 2: GetResolve (newer Resolve versions)
    if resolve is None:
        get_resolve_fn = getattr(mod, "GetResolve", None)
        if callable(get_resolve_fn):
            try:
                resolve = get_resolve_fn()
            except Exception:
                pass

    if resolve is None:
        raise ResolveConnectionError(
            "DaVinci Resolve is not running or not responding. "
            "Please start Resolve and try again."
        )

    return resolve
