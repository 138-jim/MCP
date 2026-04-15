"""Wrapper for DaVinci Resolve TimelineItem object."""

from __future__ import annotations

from resolve_lib.exceptions import ResolveOperationError
from resolve_lib.validators import validate_node_index

_VER_TYPE = {"local": 0, "remote": 1}


class TimelineItem:
    """Wraps a Resolve TimelineItem API object.

    Provides clean Python methods for Inspector-level operations on a
    single timeline clip, including identity, placement, markers, flags,
    properties, takes, Fusion comps, colour versions, CDL, grading,
    node graphs, and AI-powered operations.
    """

    def __init__(self, obj) -> None:
        """Initialise with the raw TimelineItem object.

        Parameters
        ----------
        obj:
            The raw object returned by the Resolve API for a timeline item.
        """
        self._obj = obj

    # ------------------------------------------------------------------
    # Identity / Placement
    # ------------------------------------------------------------------

    def get_name(self) -> str:
        """Return the clip name."""
        return self._obj.GetName()

    def get_duration(self) -> int:
        """Return the clip duration in frames."""
        return self._obj.GetDuration()

    def get_start(self) -> int:
        """Return the timeline start frame of this clip."""
        return self._obj.GetStart()

    def get_end(self) -> int:
        """Return the timeline end frame of this clip."""
        return self._obj.GetEnd()

    def get_left_offset(self) -> int:
        """Return the left trim offset in frames."""
        return self._obj.GetLeftOffset()

    def get_right_offset(self) -> int:
        """Return the right trim offset in frames."""
        return self._obj.GetRightOffset()

    def get_source_start_frame(self) -> int:
        """Return the source media start frame.

        Returns
        -------
        int
            Source start frame, or ``0`` if the method is unavailable.
        """
        fn = getattr(self._obj, "GetSourceStartFrame", None)
        if not callable(fn):
            return 0
        return fn()

    def get_source_end_frame(self) -> int:
        """Return the source media end frame.

        Returns
        -------
        int
            Source end frame, or ``0`` if the method is unavailable.
        """
        fn = getattr(self._obj, "GetSourceEndFrame", None)
        if not callable(fn):
            return 0
        return fn()

    def get_media_pool_item(self) -> MediaPoolItem | None:
        """Return the media pool item linked to this timeline clip.

        Returns
        -------
        MediaPoolItem | None
            The wrapped media pool item, or ``None`` if there is no
            linked media (e.g. a generated title or adjustment clip).
        """
        from resolve_lib.media_pool_item import MediaPoolItem

        obj = self._obj.GetMediaPoolItem()
        return MediaPoolItem(obj) if obj else None

    # ------------------------------------------------------------------
    # Enable / Disable
    # ------------------------------------------------------------------

    def is_enabled(self) -> bool:
        """Return whether the clip is enabled on the timeline.

        Returns
        -------
        bool
            ``True`` if the clip is enabled, or ``True`` by default if
            the method is unavailable in this Resolve version.
        """
        fn = getattr(self._obj, "GetClipEnabled", None)
        if not callable(fn):
            return True
        return bool(fn())

    def set_enabled(self, enabled: bool) -> bool:
        """Enable or disable the clip on the timeline.

        Parameters
        ----------
        enabled:
            ``True`` to enable, ``False`` to disable.

        Returns
        -------
        bool
            ``True`` if the operation succeeded, or ``False`` if the
            method is unavailable.
        """
        fn = getattr(self._obj, "SetClipEnabled", None)
        if not callable(fn):
            return False
        return bool(fn(enabled))

    # ------------------------------------------------------------------
    # Properties (Inspector)
    # ------------------------------------------------------------------

    def get_property(self, key: str = "") -> str | dict:
        """Return clip properties from the Inspector.

        Parameters
        ----------
        key:
            If provided, return the value for that single property key.
            If empty, return a dict of all available properties.

        Returns
        -------
        str | dict
            A single property value when *key* is given, or a dict of
            all properties when *key* is empty.
        """
        if key:
            return self._obj.GetProperty(key)
        return self._obj.GetProperty()

    def set_property(self, key: str, value) -> bool:
        """Set a clip property in the Inspector.

        Parameters
        ----------
        key:
            Property name (e.g. ``"Pan"``, ``"Tilt"``, ``"ZoomX"``).
        value:
            Property value to set.

        Returns
        -------
        bool
            ``True`` if the property was set successfully.
        """
        return self._obj.SetProperty(key, value)

    # ------------------------------------------------------------------
    # Markers
    # ------------------------------------------------------------------

    def get_markers(self) -> dict:
        """Return all markers on this timeline item.

        Returns
        -------
        dict
            A dict keyed by frame offset, each value being a dict of
            marker information.  Returns an empty dict when there are
            no markers.
        """
        result = self._obj.GetMarkers()
        return result if result is not None else {}

    def add_marker(
        self,
        frame_id: int,
        color: str,
        name: str,
        note: str = "",
        duration: int = 1,
        custom_data: str = "",
    ) -> bool:
        """Add a marker to this timeline item.

        Parameters
        ----------
        frame_id:
            Frame offset relative to the clip start for the marker.
        color:
            Marker colour (e.g. ``"Blue"``, ``"Red"``, ``"Green"``).
        name:
            Display name for the marker.
        note:
            Optional note text.
        duration:
            Duration of the marker in frames (default ``1``).
        custom_data:
            Optional custom data string stored with the marker.

        Returns
        -------
        bool
            ``True`` if the marker was added successfully.
        """
        return self._obj.AddMarker(
            frame_id, color, name, note, duration, custom_data
        )

    def delete_marker_at_frame(self, frame_id: int) -> bool:
        """Delete the marker at the specified frame offset.

        Parameters
        ----------
        frame_id:
            Frame offset of the marker to delete.

        Returns
        -------
        bool
            ``True`` if a marker was deleted.
        """
        return self._obj.DeleteMarkerAtFrame(frame_id)

    def delete_marker_by_custom_data(self, custom_data: str) -> bool:
        """Delete the first marker matching the given custom data.

        Parameters
        ----------
        custom_data:
            Custom data string to match.

        Returns
        -------
        bool
            ``True`` if a marker was deleted.
        """
        return self._obj.DeleteMarkerByCustomData(custom_data)

    def delete_markers_by_color(self, color: str) -> bool:
        """Delete all markers of the specified colour.

        Parameters
        ----------
        color:
            Marker colour to delete (e.g. ``"Blue"``).  Use ``""`` to
            delete all markers regardless of colour.

        Returns
        -------
        bool
            ``True`` if markers were deleted.
        """
        return self._obj.DeleteMarkersByColor(color)

    def update_marker_custom_data(
        self, frame_id: int, custom_data: str
    ) -> bool:
        """Update the custom data on the marker at *frame_id*.

        Parameters
        ----------
        frame_id:
            Frame offset of the marker.
        custom_data:
            New custom data string.

        Returns
        -------
        bool
            ``True`` if the custom data was updated.
        """
        return self._obj.UpdateMarkerCustomData(frame_id, custom_data)

    def get_marker_custom_data(self, frame_id: int) -> str:
        """Return the custom data string for the marker at *frame_id*.

        Parameters
        ----------
        frame_id:
            Frame offset of the marker.

        Returns
        -------
        str
            The custom data string, or ``""`` if none is set.
        """
        return self._obj.GetMarkerCustomData(frame_id)

    # ------------------------------------------------------------------
    # Flags / Clip Colour
    # ------------------------------------------------------------------

    def get_flag_list(self) -> list[str]:
        """Return the list of flag colours applied to this clip.

        Returns
        -------
        list[str]
            Flag colour names, or an empty list if none are set.
        """
        result = self._obj.GetFlagList()
        return result if result is not None else []

    def add_flag(self, color: str) -> bool:
        """Add a flag of the specified colour.

        Parameters
        ----------
        color:
            Flag colour name (e.g. ``"Blue"``, ``"Red"``).

        Returns
        -------
        bool
            ``True`` if the flag was added.
        """
        return self._obj.AddFlag(color)

    def clear_flags(self, color: str = "") -> bool:
        """Clear flags from this clip.

        Parameters
        ----------
        color:
            Colour to clear.  Use ``""`` to clear all flags.

        Returns
        -------
        bool
            ``True`` if flags were cleared.
        """
        return self._obj.ClearFlags(color)

    def get_clip_color(self) -> str:
        """Return the clip colour label."""
        return self._obj.GetClipColor()

    def set_clip_color(self, color: str) -> bool:
        """Set the clip colour label.

        Parameters
        ----------
        color:
            Colour name (e.g. ``"Orange"``, ``"Teal"``).

        Returns
        -------
        bool
            ``True`` if the colour was set successfully.
        """
        return self._obj.SetClipColor(color)

    # ------------------------------------------------------------------
    # Takes
    # ------------------------------------------------------------------

    def get_selected_take_number(self) -> int:
        """Return the 1-based index of the currently selected take.

        Returns
        -------
        int
            The selected take number, or ``0`` if the method is
            unavailable or no take is selected.
        """
        fn = getattr(self._obj, "GetSelectedTakeIndex", None)
        if not callable(fn):
            return 0
        return fn()

    def get_takes_count(self) -> int:
        """Return the number of takes on this clip.

        Returns
        -------
        int
            The take count, or ``0`` if the method is unavailable.
        """
        fn = getattr(self._obj, "GetTakesCount", None)
        if not callable(fn):
            return 0
        return fn()

    def select_take_by_index(self, index: int) -> bool:
        """Select a take by its 1-based index.

        Parameters
        ----------
        index:
            1-based take index to select.

        Returns
        -------
        bool
            ``True`` if the take was selected, or ``False`` if the
            method is unavailable.
        """
        fn = getattr(self._obj, "SelectTakeByIndex", None)
        if not callable(fn):
            return False
        return bool(fn(index))

    def finalize_take(self) -> bool:
        """Finalize the currently selected take.

        Finalizing flattens the take and removes the other takes from
        the clip.

        Returns
        -------
        bool
            ``True`` if the take was finalized, or ``False`` if the
            method is unavailable.
        """
        fn = getattr(self._obj, "FinalizeTake", None)
        if not callable(fn):
            return False
        return bool(fn())

    def add_take(
        self,
        media_pool_item,
        start_frame: int = 0,
        end_frame: int = 0,
    ) -> bool:
        """Add a take to this clip from a media pool item.

        Parameters
        ----------
        media_pool_item:
            A :class:`MediaPoolItem` wrapper or raw Resolve media pool
            item object to use as the take source.
        start_frame:
            Start frame within the source media (default ``0``).
        end_frame:
            End frame within the source media (default ``0``).

        Returns
        -------
        bool
            ``True`` if the take was added, or ``False`` if the method
            is unavailable.
        """
        raw = getattr(media_pool_item, "_obj", media_pool_item)
        fn = getattr(self._obj, "AddTake", None)
        if not callable(fn):
            return False
        return bool(fn(raw, start_frame, end_frame))

    def delete_take_by_index(self, index: int) -> bool:
        """Delete a take by its 1-based index.

        Parameters
        ----------
        index:
            1-based take index to delete.

        Returns
        -------
        bool
            ``True`` if the take was deleted, or ``False`` if the
            method is unavailable.
        """
        fn = getattr(self._obj, "DeleteTakeByIndex", None)
        if not callable(fn):
            return False
        return bool(fn(index))

    # ------------------------------------------------------------------
    # Fusion Comp Management
    # ------------------------------------------------------------------

    def get_fusion_comp_count(self) -> int:
        """Return the number of Fusion compositions on this clip."""
        return self._obj.GetFusionCompCount()

    def get_fusion_comp_by_index(self, index: int) -> object:
        """Return a Fusion composition by its 1-based index.

        Parameters
        ----------
        index:
            1-based index of the Fusion composition.

        Returns
        -------
        object
            The raw Fusion composition object.
        """
        return self._obj.GetFusionCompByIndex(index)

    def get_fusion_comp_name_list(self) -> list[str]:
        """Return the names of all Fusion compositions on this clip.

        Returns
        -------
        list[str]
            Composition names, or an empty list when none exist.
        """
        result = self._obj.GetFusionCompNameList()
        return result if result is not None else []

    def add_fusion_comp(self) -> object:
        """Add a new Fusion composition to this clip.

        Returns
        -------
        object
            The raw Fusion composition object.

        Raises
        ------
        ResolveOperationError
            If the composition could not be created.
        """
        result = self._obj.AddFusionComp()
        if result is None:
            raise ResolveOperationError("Failed to add Fusion composition")
        return result

    def import_fusion_comp(self, path: str) -> object:
        """Import a Fusion composition from a file.

        Parameters
        ----------
        path:
            File path to the ``.comp`` or ``.setting`` file.

        Returns
        -------
        object
            The raw Fusion composition object.

        Raises
        ------
        ResolveOperationError
            If the composition could not be imported.
        """
        result = self._obj.ImportFusionComp(path)
        if result is None:
            raise ResolveOperationError(
                f"Failed to import Fusion composition from {path!r}"
            )
        return result

    def export_fusion_comp(self, path: str, index: int) -> bool:
        """Export a Fusion composition to a file.

        Parameters
        ----------
        path:
            Destination file path for the exported composition.
        index:
            1-based index of the Fusion composition to export.

        Returns
        -------
        bool
            ``True`` if the composition was exported successfully.
        """
        return self._obj.ExportFusionComp(path, index)

    def delete_fusion_comp_by_name(self, name: str) -> bool:
        """Delete a Fusion composition by name.

        Parameters
        ----------
        name:
            Name of the Fusion composition to delete.

        Returns
        -------
        bool
            ``True`` if the composition was deleted.
        """
        return self._obj.DeleteFusionCompByName(name)

    def load_fusion_comp_by_name(self, name: str) -> object:
        """Load a Fusion composition by name into the Fusion page.

        Parameters
        ----------
        name:
            Name of the Fusion composition to load.

        Returns
        -------
        object
            The raw Fusion composition object.
        """
        return self._obj.LoadFusionCompByName(name)

    def rename_fusion_comp(self, old_name: str, new_name: str) -> bool:
        """Rename a Fusion composition.

        Parameters
        ----------
        old_name:
            Current name of the composition.
        new_name:
            Desired new name.

        Returns
        -------
        bool
            ``True`` if the composition was renamed successfully.
        """
        return self._obj.RenameFusionCompByName(old_name, new_name)

    # ------------------------------------------------------------------
    # Fusion Tool Inputs
    # ------------------------------------------------------------------

    def get_fusion_tool_input(
        self, tool_id: str, input_name: str, comp_index: int = 1
    ) -> object | None:
        """Get an input value from a Fusion tool in this clip's composition.

        Parameters
        ----------
        tool_id:
            Fusion tool ID (e.g. ``"TextPlus"``, ``"Background"``).
        input_name:
            Name of the input (e.g. ``"StyledText"``, ``"TopLeftRed"``).
        comp_index:
            1-based index of the Fusion composition (default ``1``).

        Returns
        -------
        object | None
            The current input value, or ``None`` if the tool or input
            was not found.
        """
        comp = self._obj.GetFusionCompByIndex(comp_index)
        if comp is None:
            return None
        tool = comp.FindToolByID(tool_id)
        if tool is None:
            return None
        return tool.GetInput(input_name)

    def set_fusion_tool_input(
        self,
        tool_id: str,
        input_name: str,
        value: object,
        comp_index: int = 1,
    ) -> bool:
        """Set an input value on a Fusion tool in this clip's composition.

        Parameters
        ----------
        tool_id:
            Fusion tool ID (e.g. ``"TextPlus"``, ``"Background"``).
        input_name:
            Name of the input (e.g. ``"StyledText"``, ``"Font"``).
        value:
            The value to set.
        comp_index:
            1-based index of the Fusion composition (default ``1``).

        Returns
        -------
        bool
            ``True`` if the value was set successfully.
        """
        comp = self._obj.GetFusionCompByIndex(comp_index)
        if comp is None:
            return False
        tool = comp.FindToolByID(tool_id)
        if tool is None:
            return False
        tool.SetInput(input_name, value)
        # SetInput returns None; verify by reading back
        result = tool.GetInput(input_name)
        return result == value

    # ------------------------------------------------------------------
    # Colour Versions
    # ------------------------------------------------------------------

    def get_current_version(self, version_type: str = "local") -> dict:
        """Return information about the current colour version.

        Parameters
        ----------
        version_type:
            ``"local"`` or ``"remote"`` version type.

        Returns
        -------
        dict
            Version information, or an empty dict if the method is
            unavailable.
        """
        fn = getattr(self._obj, "GetCurrentVersion", None)
        if not callable(fn):
            return {}
        return fn()

    def get_version_name_list(self, version_type: str = "local") -> list[str]:
        """Return a list of colour version names.

        Parameters
        ----------
        version_type:
            ``"local"`` or ``"remote"`` version type.

        Returns
        -------
        list[str]
            Version names, or an empty list when none exist.
        """
        fn = getattr(self._obj, "GetVersionNameList", None)
        if not callable(fn):
            return []
        result = fn(_VER_TYPE.get(version_type, version_type))
        return result if result is not None else []

    def load_version_by_name(
        self, name: str, version_type: str = "local"
    ) -> bool:
        """Load a colour version by name.

        Parameters
        ----------
        name:
            Name of the colour version to load.
        version_type:
            ``"local"`` or ``"remote"`` version type.

        Returns
        -------
        bool
            ``True`` if the version was loaded successfully.
        """
        return self._obj.LoadVersionByName(name, _VER_TYPE.get(version_type, version_type))

    def add_version(self, name: str, version_type: str = "local") -> bool:
        """Create a new colour version.

        Parameters
        ----------
        name:
            Name for the new version.
        version_type:
            ``"local"`` or ``"remote"`` version type.

        Returns
        -------
        bool
            ``True`` if the version was created successfully.
        """
        return self._obj.AddVersion(name, _VER_TYPE.get(version_type, version_type))

    def rename_version_by_name(
        self, old_name: str, new_name: str, version_type: str = "local"
    ) -> bool:
        """Rename a colour version.

        Parameters
        ----------
        old_name:
            Current name of the colour version.
        new_name:
            Desired new name.
        version_type:
            ``"local"`` or ``"remote"`` version type.

        Returns
        -------
        bool
            ``True`` if the version was renamed successfully.
        """
        return self._obj.RenameVersionByName(old_name, new_name, _VER_TYPE.get(version_type, version_type))

    def delete_version_by_name(
        self, name: str, version_type: str = "local"
    ) -> bool:
        """Delete a colour version by name.

        Parameters
        ----------
        name:
            Name of the colour version to delete.
        version_type:
            ``"local"`` or ``"remote"`` version type.

        Returns
        -------
        bool
            ``True`` if the version was deleted successfully.
        """
        return self._obj.DeleteVersionByName(name, _VER_TYPE.get(version_type, version_type))

    # ------------------------------------------------------------------
    # CDL
    # ------------------------------------------------------------------

    def get_cdl(self) -> dict:
        """Return the CDL (Color Decision List) values for this clip.

        Returns
        -------
        dict
            A dict with keys ``"slope"``, ``"offset"``, ``"power"``,
            and ``"saturation"``, or an empty dict if the method is
            unavailable.
        """
        fn = getattr(self._obj, "GetCDL", None)
        if not callable(fn):
            return {}
        return fn()

    def set_cdl(self, cdl: dict) -> bool:
        """Set the CDL values for this clip.

        Parameters
        ----------
        cdl:
            A dict with keys ``"slope"``, ``"offset"``, ``"power"``,
            and/or ``"saturation"``.

        Returns
        -------
        bool
            ``True`` if the CDL was applied, or ``False`` if the method
            is unavailable.
        """
        fn = getattr(self._obj, "SetCDL", None)
        if not callable(fn):
            return False
        return bool(fn(cdl))

    # ------------------------------------------------------------------
    # Copy / Export Grades
    # ------------------------------------------------------------------

    def copy_grades(self, items: list[TimelineItem]) -> bool:
        """Copy the grade from this clip to other timeline items.

        Parameters
        ----------
        items:
            A list of :class:`TimelineItem` wrappers that will receive
            the grade from this clip.

        Returns
        -------
        bool
            ``True`` if the grades were copied, or ``False`` if the
            method is unavailable.
        """
        fn = getattr(self._obj, "CopyGrades", None)
        if not callable(fn):
            return False
        return bool(fn([i._obj for i in items]))

    def export_lut(self, export_type: str, path: str) -> bool:
        """Export a LUT for this clip's grade.

        Parameters
        ----------
        export_type:
            LUT export type (e.g. ``"3dl"``, ``"cube"``, ``"dat"``).
        path:
            Destination file path for the exported LUT.

        Returns
        -------
        bool
            ``True`` if the LUT was exported, or ``False`` if the
            method is unavailable.
        """
        fn = getattr(self._obj, "ExportLUT", None)
        if not callable(fn):
            return False
        return bool(fn(export_type, path))

    # ------------------------------------------------------------------
    # Node Graph
    # ------------------------------------------------------------------

    def get_node_graph(self) -> Graph | None:
        """Return the colour node graph for this clip.

        Returns
        -------
        Graph | None
            The wrapped node graph, or ``None`` if unavailable.
        """
        from resolve_lib.graph import Graph

        fn = getattr(self._obj, "GetNodeGraph", None)
        if not callable(fn):
            return None
        obj = fn()
        return Graph(obj) if obj else None

    # ------------------------------------------------------------------
    # Node Colors
    # ------------------------------------------------------------------

    def reset_all_node_colors(self) -> bool:
        """Reset all node label colours on this timeline item.

        Returns
        -------
        bool
            ``True`` if the node colours were reset, or ``False`` if the
            method is unavailable.
        """
        fn = getattr(self._obj, "ResetAllNodeColors", None)
        if not callable(fn):
            return False
        return bool(fn())

    # ------------------------------------------------------------------
    # Color Output Cache
    # ------------------------------------------------------------------

    def get_color_output_cache(self) -> bool:
        """Return whether colour output cache is enabled.

        Returns
        -------
        bool
            ``True`` if colour output cache is enabled, or ``False`` if
            the method is unavailable.
        """
        fn = getattr(self._obj, "GetIsColorOutputCacheEnabled", None)
        if not callable(fn):
            return False
        return bool(fn())

    def set_color_output_cache(self, enabled: bool) -> bool:
        """Enable or disable colour output cache.

        Parameters
        ----------
        enabled:
            ``True`` to enable, ``False`` to disable.

        Returns
        -------
        bool
            ``True`` if the setting was applied, or ``False`` if the
            method is unavailable.
        """
        fn = getattr(self._obj, "SetColorOutputCache", None)
        if not callable(fn):
            return False
        return bool(fn(int(enabled)))

    # ------------------------------------------------------------------
    # Fusion Output Cache
    # ------------------------------------------------------------------

    def set_fusion_output_cache(self, enabled: bool) -> bool:
        """Enable or disable Fusion output cache for this clip.

        Enabling the Fusion output cache forces Resolve to render and cache
        the Fusion composition immediately, making effects visible in the
        Edit page without requiring a manual Fusion page visit.

        Parameters
        ----------
        enabled:
            ``True`` to enable, ``False`` to disable.

        Returns
        -------
        bool
            ``True`` if the setting was applied, or ``False`` if the
            method is unavailable.
        """
        fn = getattr(self._obj, "SetFusionOutputCache", None)
        if not callable(fn):
            return False
        return bool(fn("enable" if enabled else "disable"))

    def get_fusion_output_cache(self) -> bool:
        """Return whether Fusion output cache is enabled.

        Returns
        -------
        bool
            ``True`` if Fusion output cache is enabled.
        """
        fn = getattr(self._obj, "GetIsFusionOutputCacheEnabled", None)
        if not callable(fn):
            return False
        return bool(fn())

    # ------------------------------------------------------------------
    # Colour Group
    # ------------------------------------------------------------------

    def get_color_group(self) -> ColorGroup | None:
        """Return the colour group this clip belongs to.

        Returns
        -------
        ColorGroup | None
            The wrapped colour group, or ``None`` if the clip is not
            assigned to a group or the method is unavailable.
        """
        from resolve_lib.color_group import ColorGroup

        fn = getattr(self._obj, "GetColorGroup", None)
        if not callable(fn):
            return None
        obj = fn()
        return ColorGroup(obj) if obj else None

    def assign_to_color_group(self, group) -> bool:
        """Assign this clip to a colour group.

        Parameters
        ----------
        group:
            A :class:`ColorGroup` wrapper or raw Resolve colour group
            object.

        Returns
        -------
        bool
            ``True`` if the assignment succeeded, or ``False`` if the
            method is unavailable.
        """
        raw = getattr(group, "_obj", group)
        fn = getattr(self._obj, "AssignToColorGroup", None)
        if not callable(fn):
            return False
        return bool(fn(raw))

    def remove_from_color_group(self) -> bool:
        """Remove this clip from its current colour group.

        Returns
        -------
        bool
            ``True`` if the clip was removed from its group, or
            ``False`` if the method is unavailable.
        """
        fn = getattr(self._obj, "RemoveFromColorGroup", None)
        if not callable(fn):
            return False
        return bool(fn())

    # ------------------------------------------------------------------
    # AI Operations
    # ------------------------------------------------------------------

    def apply_magic_mask(self, mode: str = "forward") -> bool:
        """Apply DaVinci Neural Engine magic mask to this clip.

        Parameters
        ----------
        mode:
            Processing direction: ``"forward"`` or ``"backward"``.

        Returns
        -------
        bool
            ``True`` if the magic mask was applied, or ``False`` if the
            method is unavailable.
        """
        fn = getattr(self._obj, "CreateMagicMask", None)
        if not callable(fn):
            return False
        return bool(fn(mode))

    def apply_stabilization(self) -> bool:
        """Apply AI-based stabilization to this clip.

        Returns
        -------
        bool
            ``True`` if stabilization was applied, or ``False`` if the
            method is unavailable.
        """
        fn = getattr(self._obj, "Stabilize", None)
        if not callable(fn):
            return False
        return bool(fn())

    def apply_smart_reframe(self) -> bool:
        """Apply AI-based smart reframe to this clip.

        Returns
        -------
        bool
            ``True`` if smart reframe was applied, or ``False`` if the
            method is unavailable.
        """
        fn = getattr(self._obj, "SmartReframe", None)
        if not callable(fn):
            return False
        return bool(fn())

    # ------------------------------------------------------------------
    # Caching
    # ------------------------------------------------------------------

    def set_clip_cache(self, enabled: bool) -> bool:
        """Enable or disable clip caching.

        Parameters
        ----------
        enabled:
            ``True`` to enable caching, ``False`` to disable.

        Returns
        -------
        bool
            ``True`` if the cache setting was applied, or ``False`` if
            the method is unavailable.
        """
        fn = getattr(self._obj, "SetClipCache", None)
        if not callable(fn):
            return False
        return bool(fn(enabled))

    def get_clip_cache(self) -> bool:
        """Return whether clip caching is enabled.

        Returns
        -------
        bool
            ``True`` if caching is enabled, or ``False`` if the method
            is unavailable.
        """
        fn = getattr(self._obj, "GetClipCache", None)
        if not callable(fn):
            return False
        return bool(fn())

    # ------------------------------------------------------------------
    # Voice Isolation
    # ------------------------------------------------------------------

    def apply_voice_isolation(self, enable: bool = True) -> bool:
        """Enable or disable AI-based voice isolation on this clip.

        Parameters
        ----------
        enable:
            ``True`` to enable voice isolation, ``False`` to disable.

        Returns
        -------
        bool
            ``True`` if voice isolation state was set, or ``False`` if
            the method is unavailable.
        """
        fn = getattr(self._obj, "SetVoiceIsolationState", None)
        if not callable(fn):
            return False
        return bool(fn(enable))

    def get_voice_isolation_state(self) -> dict | None:
        """Return voice isolation state for this clip.

        Returns
        -------
        dict | None
            Dict with ``isEnabled`` and ``amount`` keys, or ``None``
            if the method is unavailable.
        """
        fn = getattr(self._obj, "GetVoiceIsolationState", None)
        if not callable(fn):
            return None
        return fn()

    # ------------------------------------------------------------------
    # Unique ID
    # ------------------------------------------------------------------

    def get_unique_id(self) -> str:
        """Return the unique identifier for this timeline item.

        Returns
        -------
        str
            A string that uniquely identifies this timeline item within
            the project.
        """
        return self._obj.GetUniqueId()
