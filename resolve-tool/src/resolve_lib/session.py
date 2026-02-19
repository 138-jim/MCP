"""Wrapper around the root DaVinci Resolve scripting API object."""

from __future__ import annotations

from resolve_lib.exceptions import ResolveOperationError
from resolve_lib.validators import validate_page


class Session:
    """Wrapper around the root Resolve API object.

    Provides clean Python methods for every top-level operation exposed
    by ``scriptapp('Resolve')``.
    """

    def __init__(self, obj) -> None:
        """Initialise with the raw Resolve object.

        Parameters
        ----------
        obj:
            The raw object returned by ``scriptapp('Resolve')``.
        """
        self._obj = obj

    # ------------------------------------------------------------------
    # Info / navigation
    # ------------------------------------------------------------------

    def get_version(self) -> str:
        """Return the DaVinci Resolve version string."""
        # Try GetVersionString first, fall back to GetVersion (returns list)
        fn = getattr(self._obj, "GetVersionString", None)
        if callable(fn):
            result = fn()
            if result is not None:
                return str(result)
        fn = getattr(self._obj, "GetVersion", None)
        if callable(fn):
            result = fn()
            if result is not None:
                if isinstance(result, (list, tuple)):
                    return ".".join(str(x) for x in result)
                return str(result)
        return "unknown"

    def get_product_name(self) -> str:
        """Return the product name (e.g. 'DaVinci Resolve')."""
        return self._obj.GetProductName()

    def get_current_page(self) -> str:
        """Return the name of the currently active page."""
        return self._obj.GetCurrentPage()

    def set_current_page(self, page: str) -> None:
        """Switch to the specified page.

        Parameters
        ----------
        page:
            Page name (media, cut, edit, fusion, color, fairlight, deliver).

        Raises
        ------
        ResolveValidationError
            If *page* is not a recognised page name.
        """
        validated = validate_page(page)
        self._obj.OpenPage(validated)

    # ------------------------------------------------------------------
    # Sub-object accessors
    # ------------------------------------------------------------------

    def get_project_manager(self) -> ProjectManager:
        """Return the :class:`ProjectManager` for the current session.

        Raises
        ------
        ResolveOperationError
            If the project manager could not be obtained.
        """
        from resolve_lib.project_manager import ProjectManager

        result = self._obj.GetProjectManager()
        if result is None:
            raise ResolveOperationError("Failed to get project manager")
        return ProjectManager(result)

    def get_media_storage(self) -> MediaStorage:
        """Return the :class:`MediaStorage` for the current session.

        Raises
        ------
        ResolveOperationError
            If the media storage could not be obtained.
        """
        from resolve_lib.media_storage import MediaStorage

        result = self._obj.GetMediaStorage()
        if result is None:
            raise ResolveOperationError("Failed to get media storage")
        return MediaStorage(result)

    # ------------------------------------------------------------------
    # Keyframe mode
    # ------------------------------------------------------------------

    def get_keyframe_mode(self) -> int:
        """Return the current keyframe mode as an integer."""
        return self._obj.GetKeyframeMode()

    def set_keyframe_mode(self, mode: int) -> None:
        """Set the keyframe mode.

        Parameters
        ----------
        mode:
            Keyframe mode value (see :class:`resolve_lib.types.KeyframeMode`).
        """
        self._obj.SetKeyframeMode(mode)

    # ------------------------------------------------------------------
    # Layout presets
    # ------------------------------------------------------------------

    def load_layout_preset(self, name: str) -> bool:
        """Load a UI layout preset by name.

        Returns
        -------
        bool
            ``True`` if the preset was loaded successfully.
        """
        return self._obj.LoadLayoutPreset(name)

    def update_layout_preset(self, name: str) -> bool:
        """Update (overwrite) an existing layout preset with the current layout.

        Returns
        -------
        bool
            ``True`` if the preset was updated successfully.
        """
        return self._obj.UpdateLayoutPreset(name)

    def export_layout_preset(self, name: str, path: str) -> bool:
        """Export a layout preset to a file.

        Parameters
        ----------
        name:
            Name of the preset to export.
        path:
            Destination file path.

        Returns
        -------
        bool
            ``True`` if the preset was exported successfully.
        """
        return self._obj.ExportLayoutPreset(name, path)

    def delete_layout_preset(self, name: str) -> bool:
        """Delete a layout preset by name.

        Returns
        -------
        bool
            ``True`` if the preset was deleted successfully.
        """
        return self._obj.DeleteLayoutPreset(name)

    def import_layout_preset(self, name: str, path: str) -> bool:
        """Import a layout preset from a file.

        Parameters
        ----------
        name:
            Name to assign to the imported preset.
        path:
            File path of the preset to import.

        Returns
        -------
        bool
            ``True`` if the preset was imported successfully.
        """
        return self._obj.ImportLayoutPreset(name, path)

    # ------------------------------------------------------------------
    # Application lifecycle
    # ------------------------------------------------------------------

    def quit(self) -> None:
        """Quit DaVinci Resolve."""
        self._obj.Quit()
