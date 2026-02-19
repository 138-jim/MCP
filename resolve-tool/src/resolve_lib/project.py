"""Wrapper for DaVinci Resolve Project object."""

from __future__ import annotations

from resolve_lib.exceptions import ResolveNotFoundError, ResolveOperationError


class Project:
    """Wraps a Resolve Project API object.

    Provides clean Python methods for project-level operations including
    timeline access, media pool, gallery, render jobs, and colour groups.
    """

    def __init__(self, obj) -> None:
        """Initialise with the raw Project object.

        Parameters
        ----------
        obj:
            The raw object returned by ``ProjectManager.CreateProject()``
            or ``ProjectManager.LoadProject()``.
        """
        self._obj = obj

    # ------------------------------------------------------------------
    # Identity / settings
    # ------------------------------------------------------------------

    def get_name(self) -> str:
        """Return the project name."""
        return self._obj.GetName()

    def set_name(self, name: str) -> bool:
        """Rename the project.

        Parameters
        ----------
        name:
            The new project name.

        Returns
        -------
        bool
            ``True`` if the rename succeeded.
        """
        return self._obj.SetName(name)

    def get_unique_id(self) -> str:
        """Return the unique identifier for the project."""
        return self._obj.GetUniqueId()

    def get_setting(self, key: str = "") -> str | dict:
        """Return a project setting value.

        Parameters
        ----------
        key:
            Setting key to query.  When empty, all settings are returned
            as a dictionary.

        Returns
        -------
        str | dict
            A single setting value, or all settings as a dict when *key*
            is empty.
        """
        if key:
            return self._obj.GetSetting(key)
        return self._obj.GetSetting()

    def set_setting(self, key: str, value: str) -> bool:
        """Set a project setting.

        Parameters
        ----------
        key:
            Setting key.
        value:
            Setting value.

        Returns
        -------
        bool
            ``True`` if the setting was applied.
        """
        return self._obj.SetSetting(key, value)

    def get_preset_list(self) -> list[str]:
        """Return a list of render preset names.

        Returns
        -------
        list[str]
            Preset names, or an empty list when none exist.
        """
        result = self._obj.GetPresetList()
        return result if result is not None else []

    # ------------------------------------------------------------------
    # Timeline access
    # ------------------------------------------------------------------

    def get_timeline_count(self) -> int:
        """Return the number of timelines in the project."""
        return self._obj.GetTimelineCount()

    def get_timeline_by_index(self, index: int) -> Timeline:
        """Return a timeline by its 1-based index.

        Parameters
        ----------
        index:
            1-based timeline index.

        Returns
        -------
        Timeline
            The wrapped timeline object.

        Raises
        ------
        ResolveNotFoundError
            If no timeline exists at *index*.
        """
        from resolve_lib.timeline import Timeline

        obj = self._obj.GetTimelineByIndex(index)
        if obj is None:
            raise ResolveNotFoundError(
                f"No timeline found at index {index}"
            )
        return Timeline(obj)

    def get_current_timeline(self) -> Timeline:
        """Return the currently active timeline.

        Returns
        -------
        Timeline
            The wrapped timeline object.

        Raises
        ------
        ResolveNotFoundError
            If no timeline is currently active.
        """
        from resolve_lib.timeline import Timeline

        obj = self._obj.GetCurrentTimeline()
        if obj is None:
            raise ResolveNotFoundError("No current timeline")
        return Timeline(obj)

    def set_current_timeline(self, timeline: Timeline) -> bool:
        """Set the active timeline.

        Parameters
        ----------
        timeline:
            The :class:`Timeline` wrapper to activate.

        Returns
        -------
        bool
            ``True`` if the timeline was activated successfully.
        """
        return self._obj.SetCurrentTimeline(timeline._obj)

    # ------------------------------------------------------------------
    # MediaPool / Gallery
    # ------------------------------------------------------------------

    def get_media_pool(self) -> MediaPool:
        """Return the media pool for this project.

        Returns
        -------
        MediaPool
            The wrapped media pool object.

        Raises
        ------
        ResolveOperationError
            If the media pool could not be obtained.
        """
        from resolve_lib.media_pool import MediaPool

        obj = self._obj.GetMediaPool()
        if obj is None:
            raise ResolveOperationError("Failed to get media pool")
        return MediaPool(obj)

    def get_gallery(self) -> Gallery:
        """Return the gallery for this project.

        Returns
        -------
        Gallery
            The wrapped gallery object.

        Raises
        ------
        ResolveOperationError
            If the gallery could not be obtained.
        """
        from resolve_lib.gallery import Gallery

        obj = self._obj.GetGallery()
        if obj is None:
            raise ResolveOperationError("Failed to get gallery")
        return Gallery(obj)

    # ------------------------------------------------------------------
    # Render presets
    # ------------------------------------------------------------------

    def get_render_preset_list(self) -> list[str]:
        """Return a list of render preset names.

        Returns
        -------
        list[str]
            Preset names, or an empty list when none exist.
        """
        result = self._obj.GetRenderPresetList()
        return result if result is not None else []

    def load_render_preset(self, name: str) -> bool:
        """Load a render preset by name.

        Parameters
        ----------
        name:
            Preset name to load.

        Returns
        -------
        bool
            ``True`` if the preset was loaded successfully.
        """
        return self._obj.LoadRenderPreset(name)

    def save_as_new_render_preset(self, name: str) -> bool:
        """Save current render settings as a new preset.

        Parameters
        ----------
        name:
            Name for the new preset.

        Returns
        -------
        bool
            ``True`` if the preset was saved successfully.
        """
        return self._obj.SaveAsNewRenderPreset(name)

    def delete_render_preset(self, name: str) -> bool:
        """Delete a render preset by name.

        Parameters
        ----------
        name:
            Preset name to delete.

        Returns
        -------
        bool
            ``True`` if the preset was deleted successfully.
        """
        return self._obj.DeleteRenderPreset(name)

    def import_render_preset(self, path: str) -> bool:
        """Import a render preset from a file.

        Parameters
        ----------
        path:
            File path of the preset to import.

        Returns
        -------
        bool
            ``True`` if the preset was imported successfully.
        """
        return self._obj.ImportRenderPreset(path)

    def export_render_preset(self, name: str, path: str) -> bool:
        """Export a render preset to a file.

        Parameters
        ----------
        name:
            Preset name to export.
        path:
            Destination file path.

        Returns
        -------
        bool
            ``True`` if the preset was exported successfully.
        """
        return self._obj.ExportRenderPreset(name, path)

    # ------------------------------------------------------------------
    # Render formats and codecs
    # ------------------------------------------------------------------

    def get_current_render_format_and_codec(self) -> dict:
        """Return the current render format and codec as a dictionary."""
        return self._obj.GetCurrentRenderFormatAndCodec()

    def get_render_formats(self) -> dict:
        """Return all available render formats.

        Returns
        -------
        dict
            Mapping of format identifiers to display names.
        """
        return self._obj.GetRenderFormats()

    def get_render_codecs(self, format: str) -> dict:
        """Return available codecs for a given render format.

        Parameters
        ----------
        format:
            Render format identifier.

        Returns
        -------
        dict
            Mapping of codec identifiers to display names.
        """
        return self._obj.GetRenderCodecs(format)

    def set_current_render_format_and_codec(
        self, format: str, codec: str
    ) -> bool:
        """Set the current render format and codec directly.

        Parameters
        ----------
        format:
            Render format identifier.
        codec:
            Codec identifier.

        Returns
        -------
        bool
            ``True`` if the format and codec were set successfully.
        """
        return self._obj.SetCurrentRenderFormatAndCodec(format, codec)

    def set_render_settings(self, settings: dict) -> bool:
        """Apply render settings.

        Parameters
        ----------
        settings:
            Dictionary of render setting key-value pairs.

        Returns
        -------
        bool
            ``True`` if the settings were applied successfully.
        """
        return self._obj.SetRenderSettings(settings)

    # ------------------------------------------------------------------
    # Render jobs
    # ------------------------------------------------------------------

    def get_render_job_list(self) -> list[dict]:
        """Return a list of render jobs.

        Returns
        -------
        list[dict]
            Job descriptors, or an empty list when none exist.
        """
        result = self._obj.GetRenderJobList()
        return result if result is not None else []

    def get_render_job_status(self, job_id: str) -> dict:
        """Return the status of a render job.

        Parameters
        ----------
        job_id:
            Identifier for the render job.

        Returns
        -------
        dict
            Status information for the job.
        """
        return self._obj.GetRenderJobStatus(job_id)

    def add_render_job(self) -> str:
        """Add a render job using the current render settings.

        Returns
        -------
        str
            The identifier for the newly created render job.

        Raises
        ------
        ResolveOperationError
            If the render job could not be added.
        """
        result = self._obj.AddRenderJob()
        if result is None:
            raise ResolveOperationError("Failed to add render job")
        return result

    def delete_render_job(self, job_id: str) -> bool:
        """Delete a render job.

        Parameters
        ----------
        job_id:
            Identifier of the render job to delete.

        Returns
        -------
        bool
            ``True`` if the job was deleted successfully.
        """
        return self._obj.DeleteRenderJob(job_id)

    def delete_all_render_jobs(self) -> bool:
        """Delete all render jobs.

        Returns
        -------
        bool
            ``True`` if all jobs were deleted successfully.
        """
        return self._obj.DeleteAllRenderJobs()

    def start_rendering(
        self, *job_ids: str, is_interactive: bool = False
    ) -> bool:
        """Start rendering.

        Parameters
        ----------
        *job_ids:
            Optional job identifiers to render.  When omitted, all
            queued jobs are started.
        is_interactive:
            When ``True``, error dialogs will be shown to the user.

        Returns
        -------
        bool
            ``True`` if rendering started successfully.
        """
        if job_ids:
            return self._obj.StartRendering(list(job_ids), is_interactive)
        return self._obj.StartRendering(is_interactive)

    def stop_rendering(self) -> None:
        """Stop any in-progress rendering."""
        self._obj.StopRendering()

    def is_rendering_in_progress(self) -> bool:
        """Return whether a render is currently in progress."""
        return self._obj.IsRenderingInProgress()

    # ------------------------------------------------------------------
    # Color groups
    # ------------------------------------------------------------------

    def get_color_group_list(self) -> list[ColorGroup]:
        """Return a list of colour groups in the project.

        Returns
        -------
        list[ColorGroup]
            Wrapped colour group objects, or an empty list when none
            exist.
        """
        from resolve_lib.color_group import ColorGroup

        result = self._obj.GetColorGroupsList()
        if result is None:
            return []
        return [ColorGroup(g) for g in result]

    def add_color_group(self, name: str) -> ColorGroup:
        """Create a new colour group.

        Parameters
        ----------
        name:
            Name for the new colour group.

        Returns
        -------
        ColorGroup
            The wrapped colour group object.

        Raises
        ------
        ResolveOperationError
            If the colour group could not be created.
        """
        from resolve_lib.color_group import ColorGroup

        obj = self._obj.AddColorGroup(name)
        if obj is None:
            raise ResolveOperationError(
                f"Failed to add color group {name!r}"
            )
        return ColorGroup(obj)

    def delete_color_group(self, group: ColorGroup) -> bool:
        """Delete a colour group.

        Parameters
        ----------
        group:
            The :class:`ColorGroup` wrapper to delete.

        Returns
        -------
        bool
            ``True`` if the group was deleted successfully.
        """
        return self._obj.DeleteColorGroup(group._obj)

    # ------------------------------------------------------------------
    # Miscellaneous
    # ------------------------------------------------------------------

    def insert_audio_to_current_track_at_playhead(
        self, path: str, start_offset: int, duration: int
    ) -> bool:
        """Insert an audio clip on the current track at the playhead.

        Parameters
        ----------
        path:
            File path to the audio clip.
        start_offset:
            Start offset in the audio file (in frames).
        duration:
            Duration of the inserted audio (in frames).

        Returns
        -------
        bool
            ``True`` if the audio was inserted successfully.
        """
        return self._obj.InsertAudioToCurrentTrackAtPlayhead(
            path, start_offset, duration
        )

    def import_burn_in_preset(self, path: str) -> bool:
        """Import a burn-in preset from a file.

        Parameters
        ----------
        path:
            File path of the burn-in preset to import.

        Returns
        -------
        bool
            ``True`` if the preset was imported successfully.
        """
        return self._obj.ImportBurnInPreset(path)

    def export_burn_in_preset(self, name: str, path: str) -> bool:
        """Export a burn-in preset to a file.

        Parameters
        ----------
        name:
            Preset name to export.
        path:
            Destination file path.

        Returns
        -------
        bool
            ``True`` if the preset was exported successfully.
        """
        return self._obj.ExportBurnInPreset(name, path)

    def load_burn_in_preset(self, name: str) -> bool:
        """Load a burn-in preset by name.

        Parameters
        ----------
        name:
            Preset name to load.

        Returns
        -------
        bool
            ``True`` if the preset was loaded successfully.
        """
        return self._obj.LoadBurnInPreset(name)

    def export_current_frame_as_still(self, path: str) -> bool:
        """Export the current frame as a still image.

        Parameters
        ----------
        path:
            Destination file path for the still image.

        Returns
        -------
        bool
            ``True`` if the frame was exported successfully.
        """
        fn = getattr(self._obj, "ExportCurrentFrameAsStill", None)
        if not callable(fn):
            return False
        return bool(fn(path))
