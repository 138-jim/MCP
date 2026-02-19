"""Wrapper for DaVinci Resolve Timeline object."""

from __future__ import annotations

from resolve_lib.exceptions import ResolveOperationError, ResolveValidationError
from resolve_lib.validators import validate_track_index, validate_track_type


class Timeline:
    """Wraps a Resolve Timeline API object.

    Provides clean Python methods for every timeline-level operation exposed
    by the DaVinci Resolve scripting API, including track management, markers,
    import/export, generators, scene detection, subtitles, and more.
    """

    def __init__(self, obj) -> None:
        """Initialise with the raw Timeline object.

        Parameters
        ----------
        obj:
            The raw object returned by the Resolve API for a timeline.
        """
        self._obj = obj

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    def get_name(self) -> str:
        """Return the timeline name."""
        return self._obj.GetName()

    def set_name(self, name: str) -> bool:
        """Set the timeline name.

        Parameters
        ----------
        name:
            The new name for the timeline.

        Returns
        -------
        bool
            ``True`` if the name was set successfully.
        """
        return self._obj.SetName(name)

    def get_unique_id(self) -> str:
        """Return the unique identifier for this timeline."""
        return self._obj.GetUniqueId()

    # ------------------------------------------------------------------
    # Frame / Timecode
    # ------------------------------------------------------------------

    def get_start_frame(self) -> int:
        """Return the start frame number of the timeline."""
        return self._obj.GetStartFrame()

    def get_end_frame(self) -> int:
        """Return the end frame number of the timeline."""
        return self._obj.GetEndFrame()

    def get_start_timecode(self) -> str:
        """Return the start timecode of the timeline as a string."""
        return self._obj.GetStartTimecode()

    def set_start_timecode(self, tc: str) -> bool:
        """Set the start timecode of the timeline.

        Parameters
        ----------
        tc:
            Timecode string (e.g. ``"01:00:00:00"``).

        Returns
        -------
        bool
            ``True`` if the timecode was set successfully.
        """
        return self._obj.SetStartTimecode(tc)

    def get_current_timecode(self) -> str:
        """Return the current playhead timecode as a string."""
        return self._obj.GetCurrentTimecode()

    def set_current_timecode(self, tc: str) -> bool:
        """Set the current playhead timecode.

        Parameters
        ----------
        tc:
            Timecode string (e.g. ``"01:00:05:12"``).

        Returns
        -------
        bool
            ``True`` if the playhead was moved successfully.
        """
        return self._obj.SetCurrentTimecode(tc)

    # ------------------------------------------------------------------
    # Track Management
    # ------------------------------------------------------------------

    def get_track_count(self, track_type: str) -> int:
        """Return the number of tracks of the given type.

        Parameters
        ----------
        track_type:
            Track type (``"video"``, ``"audio"``, or ``"subtitle"``).

        Returns
        -------
        int
            The track count.

        Raises
        ------
        ResolveValidationError
            If *track_type* is not a valid track type.
        """
        validated = validate_track_type(track_type)
        return self._obj.GetTrackCount(validated)

    def add_track(self, track_type: str) -> bool:
        """Add a new track of the given type.

        Parameters
        ----------
        track_type:
            Track type (``"video"``, ``"audio"``, or ``"subtitle"``).

        Returns
        -------
        bool
            ``True`` if the track was added successfully.

        Raises
        ------
        ResolveValidationError
            If *track_type* is not a valid track type.
        """
        validated = validate_track_type(track_type)
        return self._obj.AddTrack(validated)

    def delete_track(self, track_type: str, index: int) -> bool:
        """Delete a track by type and index.

        Parameters
        ----------
        track_type:
            Track type (``"video"``, ``"audio"``, or ``"subtitle"``).
        index:
            1-based track index.

        Returns
        -------
        bool
            ``True`` if the track was deleted successfully.

        Raises
        ------
        ResolveValidationError
            If *track_type* or *index* is invalid.
        """
        validated = validate_track_type(track_type)
        validate_track_index(index)
        return self._obj.DeleteTrack(validated, index)

    def get_track_name(self, track_type: str, index: int) -> str:
        """Return the name of a track.

        Parameters
        ----------
        track_type:
            Track type (``"video"``, ``"audio"``, or ``"subtitle"``).
        index:
            1-based track index.

        Returns
        -------
        str
            The track name.

        Raises
        ------
        ResolveValidationError
            If *track_type* or *index* is invalid.
        """
        validated = validate_track_type(track_type)
        validate_track_index(index)
        return self._obj.GetTrackName(validated, index)

    def set_track_name(self, track_type: str, index: int, name: str) -> bool:
        """Set the name of a track.

        Parameters
        ----------
        track_type:
            Track type (``"video"``, ``"audio"``, or ``"subtitle"``).
        index:
            1-based track index.
        name:
            The new track name.

        Returns
        -------
        bool
            ``True`` if the name was set successfully.

        Raises
        ------
        ResolveValidationError
            If *track_type* or *index* is invalid.
        """
        validated = validate_track_type(track_type)
        validate_track_index(index)
        return self._obj.SetTrackName(validated, index, name)

    def set_track_enable(self, track_type: str, index: int, enabled: bool) -> bool:
        """Enable or disable a track.

        Parameters
        ----------
        track_type:
            Track type (``"video"``, ``"audio"``, or ``"subtitle"``).
        index:
            1-based track index.
        enabled:
            ``True`` to enable, ``False`` to disable.

        Returns
        -------
        bool
            ``True`` if the operation succeeded.
        """
        validated = validate_track_type(track_type)
        validate_track_index(index)
        return self._obj.SetTrackEnable(validated, index, enabled)

    def get_is_track_enabled(self, track_type: str, index: int) -> bool:
        """Return whether a track is enabled.

        Parameters
        ----------
        track_type:
            Track type (``"video"``, ``"audio"``, or ``"subtitle"``).
        index:
            1-based track index.

        Returns
        -------
        bool
            ``True`` if the track is enabled.
        """
        validated = validate_track_type(track_type)
        validate_track_index(index)
        return self._obj.GetIsTrackEnabled(validated, index)

    def set_track_lock(self, track_type: str, index: int, locked: bool) -> bool:
        """Lock or unlock a track.

        Parameters
        ----------
        track_type:
            Track type (``"video"``, ``"audio"``, or ``"subtitle"``).
        index:
            1-based track index.
        locked:
            ``True`` to lock, ``False`` to unlock.

        Returns
        -------
        bool
            ``True`` if the operation succeeded.
        """
        validated = validate_track_type(track_type)
        validate_track_index(index)
        return self._obj.SetTrackLock(validated, index, locked)

    def get_is_track_locked(self, track_type: str, index: int) -> bool:
        """Return whether a track is locked.

        Parameters
        ----------
        track_type:
            Track type (``"video"``, ``"audio"``, or ``"subtitle"``).
        index:
            1-based track index.

        Returns
        -------
        bool
            ``True`` if the track is locked.
        """
        validated = validate_track_type(track_type)
        validate_track_index(index)
        return self._obj.GetIsTrackLocked(validated, index)

    # ------------------------------------------------------------------
    # Items in Track
    # ------------------------------------------------------------------

    def get_item_list_in_track(self, track_type: str, index: int) -> list[TimelineItem]:
        """Return all timeline items on the specified track.

        Parameters
        ----------
        track_type:
            Track type (``"video"``, ``"audio"``, or ``"subtitle"``).
        index:
            1-based track index.

        Returns
        -------
        list[TimelineItem]
            Wrapped timeline items, or an empty list if the track is empty.

        Raises
        ------
        ResolveValidationError
            If *track_type* or *index* is invalid.
        """
        from resolve_lib.timeline_item import TimelineItem

        validated = validate_track_type(track_type)
        validate_track_index(index)
        result = self._obj.GetItemListInTrack(validated, index)
        if result is None:
            return []
        return [TimelineItem(item) for item in result]

    def delete_clips(self, clips: list[TimelineItem], ripple: bool = False) -> bool:
        """Delete clips from the timeline.

        Parameters
        ----------
        clips:
            List of :class:`TimelineItem` wrappers to delete.
        ripple:
            If ``True``, ripple-delete (close the gap left by removed clips).

        Returns
        -------
        bool
            ``True`` if the clips were deleted successfully.
        """
        raw_clips = [c._obj for c in clips]
        return self._obj.DeleteClips(raw_clips, ripple)

    # ------------------------------------------------------------------
    # Stills
    # ------------------------------------------------------------------

    def grab_still(self) -> object:
        """Grab a still frame from the current playhead position.

        Returns
        -------
        object
            The raw still object returned by the Resolve API.

        Raises
        ------
        ResolveOperationError
            If the still could not be grabbed.
        """
        result = self._obj.GrabStill()
        if result is None:
            raise ResolveOperationError("Failed to grab still from timeline")
        return result

    def grab_all_stills(self, still_frame_source: int) -> list:
        """Grab stills from all frames according to the source mode.

        Parameters
        ----------
        still_frame_source:
            Integer specifying which frames to grab stills from.

        Returns
        -------
        list
            A list of raw still objects, or an empty list on failure.
        """
        result = self._obj.GrabAllStills(still_frame_source)
        if result is None:
            return []
        return result

    # ------------------------------------------------------------------
    # Markers
    # ------------------------------------------------------------------

    def get_markers(self) -> dict:
        """Return all markers on this timeline.

        Returns
        -------
        dict
            A dict keyed by frame number, each value being marker info.
            Returns an empty dict if no markers exist.
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
        """Add a marker to the timeline.

        Parameters
        ----------
        frame_id:
            Frame position for the marker.
        color:
            Marker colour (e.g. ``"Blue"``, ``"Red"``).
        name:
            Display name for the marker.
        note:
            Optional note text.
        duration:
            Duration in frames (default ``1``).
        custom_data:
            Optional custom data string.

        Returns
        -------
        bool
            ``True`` if the marker was added successfully.
        """
        return self._obj.AddMarker(frame_id, color, name, note, duration, custom_data)

    def delete_marker_at_frame(self, frame_id: int) -> bool:
        """Delete the marker at the specified frame.

        Parameters
        ----------
        frame_id:
            Frame position of the marker to delete.

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
            Marker colour to delete (e.g. ``"Blue"``). Use ``""`` to
            delete all markers regardless of colour.

        Returns
        -------
        bool
            ``True`` if markers were deleted.
        """
        return self._obj.DeleteMarkersByColor(color)

    def update_marker_custom_data(self, frame_id: int, custom_data: str) -> bool:
        """Update the custom data on the marker at *frame_id*.

        Parameters
        ----------
        frame_id:
            Frame position of the marker.
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
            Frame position of the marker.

        Returns
        -------
        str
            The custom data string, or ``""`` if none is set.
        """
        return self._obj.GetMarkerCustomData(frame_id)

    # ------------------------------------------------------------------
    # Export / Import
    # ------------------------------------------------------------------

    def export(
        self,
        path: str,
        export_type,
        export_subtype=None,
    ) -> bool:
        """Export the timeline to a file.

        Parameters
        ----------
        path:
            Destination file path.
        export_type:
            Export format — either a Resolve constant (int) obtained from
            ``resolve.EXPORT_*``, or a string name like ``"EDL"`` which
            will be passed through directly.
        export_subtype:
            Optional export subtype for formats that support it.

        Returns
        -------
        bool
            ``True`` if the export succeeded.
        """
        if export_subtype is not None:
            return bool(self._obj.Export(path, export_type, export_subtype))
        return bool(self._obj.Export(path, export_type))

    def import_into_timeline(self, path: str, options: dict | None = None) -> bool:
        """Import media or timeline data into this timeline.

        Parameters
        ----------
        path:
            File path of the data to import.
        options:
            Optional dict of import options (see
            :class:`resolve_lib.types.TimelineImportOptions`).

        Returns
        -------
        bool
            ``True`` if the import succeeded.
        """
        return self._obj.ImportIntoTimeline(path, options or {})

    # ------------------------------------------------------------------
    # Duplicate / Compound
    # ------------------------------------------------------------------

    def duplicate_timeline(self, name: str | None = None) -> Timeline:
        """Create a duplicate of this timeline.

        Parameters
        ----------
        name:
            Optional name for the duplicate. If ``None``, Resolve assigns
            a default name.

        Returns
        -------
        Timeline
            The newly created duplicate timeline.

        Raises
        ------
        ResolveOperationError
            If the timeline could not be duplicated.
        """
        if name is not None:
            result = self._obj.DuplicateTimeline(name)
        else:
            result = self._obj.DuplicateTimeline()
        if result is None:
            raise ResolveOperationError("Failed to duplicate timeline")
        return Timeline(result)

    def create_compound_clip(
        self,
        items: list[TimelineItem],
        clip_info: dict | None = None,
    ) -> TimelineItem:
        """Create a compound clip from the given timeline items.

        Parameters
        ----------
        items:
            List of :class:`TimelineItem` wrappers to combine.
        clip_info:
            Optional dict of clip info (see
            :class:`resolve_lib.types.ClipInfo`).

        Returns
        -------
        TimelineItem
            The new compound clip.

        Raises
        ------
        ResolveOperationError
            If the compound clip could not be created.
        """
        from resolve_lib.timeline_item import TimelineItem

        raw_items = [i._obj for i in items]
        result = self._obj.CreateCompoundClip(raw_items, clip_info or {})
        if result is None:
            raise ResolveOperationError("Failed to create compound clip")
        return TimelineItem(result)

    def create_fusion_clip(self, items: list[TimelineItem]) -> TimelineItem:
        """Create a Fusion clip from the given timeline items.

        Parameters
        ----------
        items:
            List of :class:`TimelineItem` wrappers to combine.

        Returns
        -------
        TimelineItem
            The new Fusion clip.

        Raises
        ------
        ResolveOperationError
            If the Fusion clip could not be created.
        """
        from resolve_lib.timeline_item import TimelineItem

        raw_items = [i._obj for i in items]
        result = self._obj.CreateFusionClip(raw_items)
        if result is None:
            raise ResolveOperationError("Failed to create Fusion clip")
        return TimelineItem(result)

    # ------------------------------------------------------------------
    # Generators / Titles / Transitions
    # ------------------------------------------------------------------

    def get_available_generators(self) -> list[dict]:
        """Return a list of available generator descriptors.

        Returns
        -------
        list[dict]
            Each dict contains ``"Name"`` and ``"Type"`` keys describing
            a generator. Returns an empty list if none are available.
        """
        fn = getattr(self._obj, "GetAvailableGenerators", None)
        if not callable(fn):
            return []
        result = fn()
        if result is None:
            return []
        return result

    def insert_generator_in_timeline(self, name: str) -> TimelineItem:
        """Insert a generator into the timeline at the playhead.

        Parameters
        ----------
        name:
            Name of the generator to insert.

        Returns
        -------
        TimelineItem
            The newly inserted generator clip.

        Raises
        ------
        ResolveOperationError
            If the generator could not be inserted.
        """
        from resolve_lib.timeline_item import TimelineItem

        fn = getattr(self._obj, "InsertGeneratorIntoTimeline", None)
        if not callable(fn):
            raise ResolveOperationError(
                "InsertGeneratorIntoTimeline is not available in this Resolve version"
            )
        result = fn(name)
        if result is None:
            raise ResolveOperationError(
                f"Failed to insert generator {name!r} in timeline"
            )
        return TimelineItem(result)

    def get_available_titles(self) -> list[dict]:
        """Return a list of available title descriptors.

        Returns
        -------
        list[dict]
            Each dict contains ``"Name"`` and ``"Type"`` keys describing
            a title template. Returns an empty list if none are available.
        """
        fn = getattr(self._obj, "GetAvailableTitles", None)
        if not callable(fn):
            return []
        result = fn()
        if result is None:
            return []
        return result

    def insert_title_in_timeline(self, name: str) -> TimelineItem:
        """Insert a title into the timeline at the playhead.

        Parameters
        ----------
        name:
            Name of the title template to insert.

        Returns
        -------
        TimelineItem
            The newly inserted title clip.

        Raises
        ------
        ResolveOperationError
            If the title could not be inserted.
        """
        from resolve_lib.timeline_item import TimelineItem

        fn = getattr(self._obj, "InsertTitleIntoTimeline", None)
        if not callable(fn):
            raise ResolveOperationError(
                "InsertTitleIntoTimeline is not available in this Resolve version"
            )
        result = fn(name)
        if result is None:
            raise ResolveOperationError(
                f"Failed to insert title {name!r} in timeline"
            )
        return TimelineItem(result)

    def insert_ofx_generator_in_timeline(self, name: str) -> TimelineItem:
        """Insert an OFX generator into the timeline at the playhead.

        Parameters
        ----------
        name:
            Name of the OFX generator to insert.

        Returns
        -------
        TimelineItem
            The newly inserted generator clip.

        Raises
        ------
        ResolveOperationError
            If the generator could not be inserted.
        """
        from resolve_lib.timeline_item import TimelineItem

        result = self._obj.InsertOFXGeneratorIntoTimeline(name)
        if result is None:
            raise ResolveOperationError(
                f"Failed to insert OFX generator {name!r} in timeline"
            )
        return TimelineItem(result)

    def insert_fusion_generator_in_timeline(self, name: str) -> TimelineItem:
        """Insert a Fusion generator into the timeline at the playhead.

        Parameters
        ----------
        name:
            Name of the Fusion generator to insert.

        Returns
        -------
        TimelineItem
            The newly inserted generator clip.

        Raises
        ------
        ResolveOperationError
            If the generator could not be inserted.
        """
        from resolve_lib.timeline_item import TimelineItem

        fn = getattr(self._obj, "InsertFusionGeneratorIntoTimeline", None)
        if not callable(fn):
            raise ResolveOperationError(
                "InsertFusionGeneratorIntoTimeline is not available in this Resolve version"
            )
        result = fn(name)
        if result is None:
            raise ResolveOperationError(
                f"Failed to insert Fusion generator {name!r} in timeline"
            )
        return TimelineItem(result)

    def insert_fusion_title_in_timeline(self, name: str) -> TimelineItem:
        """Insert a Fusion title into the timeline at the playhead.

        Parameters
        ----------
        name:
            Name of the Fusion title to insert.

        Returns
        -------
        TimelineItem
            The newly inserted title clip.

        Raises
        ------
        ResolveOperationError
            If the title could not be inserted.
        """
        from resolve_lib.timeline_item import TimelineItem

        fn = getattr(self._obj, "InsertFusionTitleIntoTimeline", None)
        if not callable(fn):
            raise ResolveOperationError(
                "InsertFusionTitleIntoTimeline is not available in this Resolve version"
            )
        result = fn(name)
        if result is None:
            raise ResolveOperationError(
                f"Failed to insert Fusion title {name!r} in timeline"
            )
        return TimelineItem(result)

    def get_current_video_item(self) -> TimelineItem | None:
        """Return the currently selected video item on the timeline.

        Returns
        -------
        TimelineItem | None
            The wrapped timeline item, or ``None`` if no video item is
            currently selected.
        """
        from resolve_lib.timeline_item import TimelineItem

        result = self._obj.GetCurrentVideoItem()
        if result is None:
            return None
        return TimelineItem(result)

    def convert_timeline_to_stereo(self) -> bool:
        """Convert this timeline to stereoscopic mode.

        Returns
        -------
        bool
            ``True`` if the conversion succeeded.
        """
        return self._obj.ConvertTimelineToStereo()

    def get_available_transitions(self) -> list[dict]:
        """Return a list of available transition descriptors.

        Returns
        -------
        list[dict]
            Each dict contains information about an available transition.
            Returns an empty list if none are available.
        """
        result = self._obj.GetAvailableTransitions()
        if result is None:
            return []
        return result

    # ------------------------------------------------------------------
    # Scene Detect
    # ------------------------------------------------------------------

    def detect_scene_cuts(self) -> list[int]:
        """Detect scene cuts in the timeline.

        Returns
        -------
        list[int]
            Frame positions where scene cuts were detected, or an empty
            list if none were found.
        """
        fn = getattr(self._obj, "DetectSceneCuts", None)
        if not callable(fn):
            return []
        result = fn()
        # API may return bool (success/failure) or a list of frames
        if result is None or isinstance(result, bool):
            return []
        return result

    # ------------------------------------------------------------------
    # Subtitles
    # ------------------------------------------------------------------

    def create_subtitle_from_audio(self, settings: dict | None = None) -> bool:
        """Create subtitle track content from the audio in the timeline.

        Parameters
        ----------
        settings:
            Optional dict of subtitle generation settings.

        Returns
        -------
        bool
            ``True`` if subtitle creation succeeded.
        """
        fn = getattr(self._obj, "CreateSubtitlesFromAudio", None)
        if not callable(fn):
            return False
        if settings:
            return bool(fn(settings))
        return bool(fn())

    def export_subtitles(self, path: str, format: str = "SRT") -> bool:
        """Export subtitles to a file.

        Parameters
        ----------
        path:
            Destination file path.
        format:
            Subtitle format (default ``"SRT"``).

        Returns
        -------
        bool
            ``True`` if the export succeeded.
        """
        return self._obj.ExportSubtitle(path, format)

    # ------------------------------------------------------------------
    # Mark In / Out
    # ------------------------------------------------------------------

    def get_mark_in(self) -> int:
        """Return the mark-in frame position.

        Returns
        -------
        int
            The mark-in frame number, or ``-1`` if not set or the
            method is unavailable.
        """
        fn = getattr(self._obj, "GetMarkIn", None)
        if not callable(fn):
            return -1
        return fn()

    def get_mark_out(self) -> int:
        """Return the mark-out frame position.

        Returns
        -------
        int
            The mark-out frame number, or ``-1`` if not set or the
            method is unavailable.
        """
        fn = getattr(self._obj, "GetMarkOut", None)
        if not callable(fn):
            return -1
        return fn()

    def set_mark_in(self, frame: int) -> bool:
        """Set the mark-in point.

        Parameters
        ----------
        frame:
            Frame number for the mark-in point.

        Returns
        -------
        bool
            ``True`` if the mark-in was set successfully, or ``False``
            if the method is unavailable.
        """
        fn = getattr(self._obj, "SetMarkIn", None)
        if not callable(fn):
            return False
        return bool(fn(frame))

    def set_mark_out(self, frame: int) -> bool:
        """Set the mark-out point.

        Parameters
        ----------
        frame:
            Frame number for the mark-out point.

        Returns
        -------
        bool
            ``True`` if the mark-out was set successfully, or ``False``
            if the method is unavailable.
        """
        fn = getattr(self._obj, "SetMarkOut", None)
        if not callable(fn):
            return False
        return bool(fn(frame))

    # ------------------------------------------------------------------
    # Dolby Vision
    # ------------------------------------------------------------------

    def get_dolby_vision_metadata(self, frame: int = 0) -> dict:
        """Return Dolby Vision metadata for the given frame.

        Parameters
        ----------
        frame:
            Frame number to query (default ``0``).

        Returns
        -------
        dict
            Dolby Vision metadata dict, or an empty dict if unavailable
            or the API method is not present.
        """
        fn = getattr(self._obj, "GetDolbyVisionMetadata", None)
        if not callable(fn):
            return {}
        return fn(frame)

    # ------------------------------------------------------------------
    # Node Graph (Color page)
    # ------------------------------------------------------------------

    def get_node_graph(self) -> Graph | None:
        """Return the node graph for this timeline (Color page).

        Returns
        -------
        Graph | None
            A wrapped :class:`Graph` instance, or ``None`` if the node
            graph is not available (e.g. wrong page or unsupported API).
        """
        from resolve_lib.graph import Graph

        fn = getattr(self._obj, "GetNodeGraph", None)
        if not callable(fn):
            return None
        obj = fn()
        if obj is None:
            return None
        return Graph(obj)

    # ------------------------------------------------------------------
    # Settings
    # ------------------------------------------------------------------

    def get_setting(self, key: str = "") -> str | dict:
        """Return a timeline setting.

        Parameters
        ----------
        key:
            Setting key to query. If empty, returns all settings as a dict.

        Returns
        -------
        str | dict
            The setting value for a specific key, or a dict of all settings
            when *key* is empty.
        """
        if key:
            return self._obj.GetSetting(key)
        return self._obj.GetSetting()

    def set_setting(self, key: str, value: str) -> bool:
        """Set a timeline setting.

        Parameters
        ----------
        key:
            Setting key.
        value:
            Setting value.

        Returns
        -------
        bool
            ``True`` if the setting was applied successfully.
        """
        return self._obj.SetSetting(key, value)

    # ------------------------------------------------------------------
    # Thumbnail
    # ------------------------------------------------------------------

    def get_thumbnail(self, frame: int, width: int = 0, height: int = 0) -> dict:
        """Return a thumbnail image for the given frame.

        Parameters
        ----------
        frame:
            Frame number to capture.
        width:
            Desired thumbnail width in pixels (``0`` for default).
        height:
            Desired thumbnail height in pixels (``0`` for default).

        Returns
        -------
        dict
            A dict with keys ``"width"``, ``"height"``, ``"format"``,
            and ``"data"`` describing the thumbnail image.

        Raises
        ------
        ResolveOperationError
            If the thumbnail could not be retrieved.
        """
        result = self._obj.GetThumbnail(frame, width, height)
        if result is None:
            raise ResolveOperationError(
                f"Failed to get thumbnail for frame {frame}"
            )
        return result

    # ------------------------------------------------------------------
    # Voice Isolation (newer Resolve versions)
    # ------------------------------------------------------------------

    def apply_voice_isolation_to_timeline(self, enable: bool = True) -> bool:
        """Enable or disable voice isolation on the timeline audio.

        Parameters
        ----------
        enable:
            ``True`` to enable voice isolation, ``False`` to disable.

        Returns
        -------
        bool
            ``True`` if voice isolation state was set successfully.
        """
        fn = getattr(self._obj, "SetVoiceIsolationState", None)
        if not callable(fn):
            return False
        return bool(fn(enable))

    def get_voice_isolation_state(self) -> bool:
        """Return whether voice isolation is enabled on the timeline.

        Returns
        -------
        bool
            ``True`` if voice isolation is enabled.
        """
        fn = getattr(self._obj, "GetVoiceIsolationState", None)
        if not callable(fn):
            return False
        result = fn()
        if result is None:
            return False
        return bool(result)
