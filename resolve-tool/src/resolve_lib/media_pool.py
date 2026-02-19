"""Wrapper around the DaVinci Resolve MediaPool object."""

from __future__ import annotations

from resolve_lib.exceptions import ResolveOperationError


class MediaPool:
    """Wrapper around the Resolve MediaPool subsystem.

    Provides clean Python methods for folder management, media import,
    timeline creation, clip operations, and metadata export.
    """

    def __init__(self, obj) -> None:
        """Initialise with the raw MediaPool object.

        Parameters
        ----------
        obj:
            The raw object returned by ``Project.GetMediaPool()``.
        """
        self._obj = obj

    # ------------------------------------------------------------------
    # Folder operations
    # ------------------------------------------------------------------

    def get_root_folder(self) -> Folder:
        """Return the root folder of the media pool.

        Returns
        -------
        Folder
            The wrapped root :class:`Folder`.

        Raises
        ------
        ResolveOperationError
            If the root folder could not be obtained.
        """
        from resolve_lib.folder import Folder

        result = self._obj.GetRootFolder()
        if result is None:
            raise ResolveOperationError("Failed to get root folder")
        return Folder(result)

    def get_current_folder(self) -> Folder:
        """Return the currently selected media pool folder.

        Returns
        -------
        Folder
            The wrapped current :class:`Folder`.

        Raises
        ------
        ResolveOperationError
            If the current folder could not be obtained.
        """
        from resolve_lib.folder import Folder

        result = self._obj.GetCurrentFolder()
        if result is None:
            raise ResolveOperationError("Failed to get current folder")
        return Folder(result)

    def set_current_folder(self, folder: Folder) -> bool:
        """Set the currently selected media pool folder.

        Parameters
        ----------
        folder:
            The :class:`Folder` to make current.

        Returns
        -------
        bool
            ``True`` if the folder was set successfully.
        """
        from resolve_lib.folder import Folder

        return self._obj.SetCurrentFolder(folder._obj)

    def add_subfolder(self, name: str, parent: Folder) -> Folder:
        """Create a new sub-folder inside *parent*.

        Parameters
        ----------
        name:
            Name for the new sub-folder.
        parent:
            The parent :class:`Folder` to create the sub-folder in.

        Returns
        -------
        Folder
            The newly created :class:`Folder`.

        Raises
        ------
        ResolveOperationError
            If the sub-folder could not be created.
        """
        from resolve_lib.folder import Folder

        result = self._obj.AddSubFolder(parent._obj, name)
        if result is None:
            raise ResolveOperationError(
                f"Failed to create sub-folder {name!r}"
            )
        return Folder(result)

    def delete_folders(self, folders: list[Folder]) -> bool:
        """Delete one or more media pool folders.

        Parameters
        ----------
        folders:
            List of :class:`Folder` instances to delete.

        Returns
        -------
        bool
            ``True`` if the folders were deleted successfully.
        """
        from resolve_lib.folder import Folder

        return self._obj.DeleteFolders([f._obj for f in folders])

    def move_folders(self, folders: list[Folder], target: Folder) -> bool:
        """Move folders into a target folder.

        Parameters
        ----------
        folders:
            List of :class:`Folder` instances to move.
        target:
            The destination :class:`Folder`.

        Returns
        -------
        bool
            ``True`` if the folders were moved successfully.
        """
        from resolve_lib.folder import Folder

        return self._obj.MoveFolders([f._obj for f in folders], target._obj)

    def move_clips(self, clips: list[MediaPoolItem], target: Folder) -> bool:
        """Move clips into a target folder.

        Parameters
        ----------
        clips:
            List of :class:`MediaPoolItem` instances to move.
        target:
            The destination :class:`Folder`.

        Returns
        -------
        bool
            ``True`` if the clips were moved successfully.
        """
        from resolve_lib.folder import Folder
        from resolve_lib.media_pool_item import MediaPoolItem

        return self._obj.MoveClips([c._obj for c in clips], target._obj)

    # ------------------------------------------------------------------
    # Import
    # ------------------------------------------------------------------

    def import_media(self, paths: list[str]) -> list[MediaPoolItem]:
        """Import media files into the current media pool folder.

        Parameters
        ----------
        paths:
            List of absolute file paths to import.

        Returns
        -------
        list[MediaPoolItem]
            Wrapped :class:`MediaPoolItem` instances for each imported
            clip, or an empty list if the operation returned nothing.
        """
        from resolve_lib.media_pool_item import MediaPoolItem

        result = self._obj.ImportMedia(paths)
        if result is None:
            return []
        return [MediaPoolItem(item) for item in result]

    def import_timeline_from_file(
        self, path: str, options: dict | None = None
    ) -> Timeline:
        """Import a timeline from a file (e.g. AAF, EDL, XML, OTIO).

        Parameters
        ----------
        path:
            Path to the timeline file.
        options:
            Optional import options dict
            (see :class:`resolve_lib.types.TimelineImportOptions`).

        Returns
        -------
        Timeline
            The imported :class:`Timeline`.

        Raises
        ------
        ResolveOperationError
            If the timeline could not be imported.
        """
        from resolve_lib.timeline import Timeline

        result = self._obj.ImportTimelineFromFile(path, options or {})
        if result is None:
            raise ResolveOperationError(
                f"Failed to import timeline from {path!r}"
            )
        return Timeline(result)

    # ------------------------------------------------------------------
    # Timeline creation
    # ------------------------------------------------------------------

    def create_empty_timeline(self, name: str) -> Timeline:
        """Create a new empty timeline.

        Parameters
        ----------
        name:
            Name for the new timeline.

        Returns
        -------
        Timeline
            The newly created :class:`Timeline`.

        Raises
        ------
        ResolveOperationError
            If the timeline could not be created.
        """
        from resolve_lib.timeline import Timeline

        result = self._obj.CreateEmptyTimeline(name)
        if result is None:
            raise ResolveOperationError(
                f"Failed to create empty timeline {name!r}"
            )
        return Timeline(result)

    def create_timeline_from_clips(
        self, name: str, clips: list[MediaPoolItem | dict]
    ) -> Timeline:
        """Create a new timeline from a list of clips.

        Parameters
        ----------
        name:
            Name for the new timeline.
        clips:
            A list where each element is either a :class:`MediaPoolItem`
            (which will be unwrapped) or a dict of clip info
            (see :class:`resolve_lib.types.ClipInfo`).

        Returns
        -------
        Timeline
            The newly created :class:`Timeline`.

        Raises
        ------
        ResolveOperationError
            If the timeline could not be created.
        """
        from resolve_lib.media_pool_item import MediaPoolItem
        from resolve_lib.timeline import Timeline

        clip_infos = [
            c._obj if isinstance(c, MediaPoolItem) else c for c in clips
        ]
        result = self._obj.CreateTimelineFromClips(name, clip_infos)
        if result is None:
            raise ResolveOperationError(
                f"Failed to create timeline {name!r} from clips"
            )
        return Timeline(result)

    def append_to_timeline(
        self, clips: list[MediaPoolItem | dict]
    ) -> list[MediaPoolItem]:
        """Append clips to the current timeline.

        Parameters
        ----------
        clips:
            A list where each element is either a :class:`MediaPoolItem`
            (which will be unwrapped) or a dict of clip info
            (see :class:`resolve_lib.types.ClipInfo`).

        Returns
        -------
        list[MediaPoolItem]
            Wrapped :class:`MediaPoolItem` instances for each appended
            clip, or an empty list if the operation returned nothing.
        """
        from resolve_lib.media_pool_item import MediaPoolItem

        clip_infos = [
            c._obj if isinstance(c, MediaPoolItem) else c for c in clips
        ]
        result = self._obj.AppendToTimeline(clip_infos)
        if result is None:
            return []
        return [MediaPoolItem(item) for item in result]

    # ------------------------------------------------------------------
    # Clip operations
    # ------------------------------------------------------------------

    def delete_clips(self, clips: list[MediaPoolItem]) -> bool:
        """Delete clips from the media pool.

        Parameters
        ----------
        clips:
            List of :class:`MediaPoolItem` instances to delete.

        Returns
        -------
        bool
            ``True`` if the clips were deleted successfully.
        """
        from resolve_lib.media_pool_item import MediaPoolItem

        return self._obj.DeleteClips([c._obj for c in clips])

    def relink_clips(self, clips: list[MediaPoolItem], path: str) -> bool:
        """Relink clips to media at a new path.

        Parameters
        ----------
        clips:
            List of :class:`MediaPoolItem` instances to relink.
        path:
            New base path for the media files.

        Returns
        -------
        bool
            ``True`` if the clips were relinked successfully.
        """
        from resolve_lib.media_pool_item import MediaPoolItem

        return self._obj.RelinkClips([c._obj for c in clips], path)

    def unlink_clips(self, clips: list[MediaPoolItem]) -> bool:
        """Unlink clips from their media files.

        Parameters
        ----------
        clips:
            List of :class:`MediaPoolItem` instances to unlink.

        Returns
        -------
        bool
            ``True`` if the clips were unlinked successfully.
        """
        from resolve_lib.media_pool_item import MediaPoolItem

        return self._obj.UnlinkClips([c._obj for c in clips])

    def auto_sync_audio(
        self, clips: list[MediaPoolItem], mode: int = 0
    ) -> list[MediaPoolItem]:
        """Auto-sync audio for the given clips.

        Parameters
        ----------
        clips:
            List of :class:`MediaPoolItem` instances to sync.
        mode:
            Sync mode (``0`` for sound-based, ``1`` for timecode-based).

        Returns
        -------
        list[MediaPoolItem]
            Wrapped :class:`MediaPoolItem` instances for the synced
            clips, or an empty list if the operation returned nothing.
        """
        from resolve_lib.media_pool_item import MediaPoolItem

        clips_raw = [c._obj for c in clips]
        result = self._obj.AutoSyncAudio(clips_raw, mode)
        if result is None:
            return []
        return [MediaPoolItem(item) for item in result]

    # ------------------------------------------------------------------
    # Metadata / export
    # ------------------------------------------------------------------

    def export_metadata(
        self, path: str, clips: list[MediaPoolItem] | None = None
    ) -> bool:
        """Export metadata to a file.

        Parameters
        ----------
        path:
            Destination file path for the metadata export.
        clips:
            Optional list of :class:`MediaPoolItem` instances whose
            metadata should be exported. If ``None``, exports metadata
            for all clips.

        Returns
        -------
        bool
            ``True`` if the metadata was exported successfully.
        """
        from resolve_lib.media_pool_item import MediaPoolItem

        if clips is not None:
            return self._obj.ExportMetadata(path, [c._obj for c in clips])
        return self._obj.ExportMetadata(path)

    def refresh_folders(self) -> bool:
        """Refresh the media pool folder list.

        Returns
        -------
        bool
            ``True`` if the folders were refreshed successfully.
        """
        return self._obj.RefreshFolders()

    def create_stereo_clip(
        self, left_item: MediaPoolItem, right_item: MediaPoolItem
    ) -> MediaPoolItem:
        """Create a stereoscopic clip from left and right eye items.

        Parameters
        ----------
        left_item:
            The :class:`MediaPoolItem` for the left eye.
        right_item:
            The :class:`MediaPoolItem` for the right eye.

        Returns
        -------
        MediaPoolItem
            The newly created stereo clip.

        Raises
        ------
        ResolveOperationError
            If the stereo clip could not be created.
        """
        from resolve_lib.media_pool_item import MediaPoolItem

        result = self._obj.CreateStereoClip(left_item._obj, right_item._obj)
        if result is None:
            raise ResolveOperationError("Failed to create stereo clip")
        return MediaPoolItem(result)

    def get_unique_id(self) -> str:
        """Return the unique identifier for this media pool."""
        return self._obj.GetUniqueId()
