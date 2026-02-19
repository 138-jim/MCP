"""Wrapper around the DaVinci Resolve MediaStorage object."""

from __future__ import annotations

from resolve_lib.exceptions import ResolveOperationError


class MediaStorage:
    """Wrapper around the Resolve MediaStorage subsystem.

    Provides clean Python methods for browsing mounted volumes, listing
    files and sub-folders, and adding media to the media pool.
    """

    def __init__(self, obj) -> None:
        """Initialise with the raw MediaStorage object.

        Parameters
        ----------
        obj:
            The raw object returned by ``Resolve.GetMediaStorage()``.
        """
        self._obj = obj

    # ------------------------------------------------------------------
    # Volume / file browsing
    # ------------------------------------------------------------------

    def get_mounted_volumes(self) -> list[str]:
        """Return the list of currently mounted volume paths.

        Returns
        -------
        list[str]
            Mounted volume paths, or an empty list if none are available.
        """
        result = self._obj.GetMountedVolumeList()
        return result if result is not None else []

    def get_subfolder_list(self, path: str) -> list[str]:
        """Return the sub-folders at the given path.

        Parameters
        ----------
        path:
            Absolute filesystem path to list sub-folders for.

        Returns
        -------
        list[str]
            Sub-folder paths, or an empty list if none exist.
        """
        result = self._obj.GetSubFolderList(path)
        return result if result is not None else []

    def get_file_list(self, path: str) -> list[str]:
        """Return the files at the given path.

        Parameters
        ----------
        path:
            Absolute filesystem path to list files for.

        Returns
        -------
        list[str]
            File paths, or an empty list if none exist.
        """
        result = self._obj.GetFileList(path)
        return result if result is not None else []

    # ------------------------------------------------------------------
    # Adding media to the pool
    # ------------------------------------------------------------------

    def add_items_to_media_pool(self, *paths: str) -> list[MediaPoolItem]:
        """Add media files to the current media pool folder.

        Parameters
        ----------
        *paths:
            One or more absolute file paths to add.

        Returns
        -------
        list[MediaPoolItem]
            Wrapped :class:`MediaPoolItem` instances for each item added,
            or an empty list if the operation returned nothing.
        """
        from resolve_lib.media_pool_item import MediaPoolItem

        result = self._obj.AddItemListToMediaPool(list(paths))
        if result is None:
            return []
        return [MediaPoolItem(item) for item in result]

    def add_clip_mattes_to_media_pool(
        self,
        item: MediaPoolItem,
        paths: list[str],
        stereo_eye: str = "",
    ) -> bool:
        """Add clip mattes for a media pool item.

        Parameters
        ----------
        item:
            The :class:`MediaPoolItem` to attach mattes to.
        paths:
            File paths of the matte images.
        stereo_eye:
            Stereo eye identifier (``"left"`` or ``"right"``). Leave
            empty for non-stereo clips.

        Returns
        -------
        bool
            ``True`` if the mattes were added successfully.
        """
        from resolve_lib.media_pool_item import MediaPoolItem

        return self._obj.AddClipMattesToMediaPool(item._obj, paths, stereo_eye)

    def reveal_in_storage(self, path: str) -> bool:
        """Reveal the specified path in media storage.

        Parameters
        ----------
        path:
            Absolute filesystem path to reveal.

        Returns
        -------
        bool
            ``True`` if the path was revealed successfully.
        """
        return self._obj.RevealInStorage(path)

    def add_timeline_mattes_to_media_pool(self, paths: list[str]) -> list:
        """Add timeline mattes to the media pool.

        Parameters
        ----------
        paths:
            File paths of the timeline matte images.

        Returns
        -------
        list
            The items added, or an empty list if the operation returned
            nothing.
        """
        result = self._obj.AddTimelineMattesToMediaPool(paths)
        return result if result is not None else []
