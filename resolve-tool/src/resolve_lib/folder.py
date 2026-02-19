"""Wrapper around a DaVinci Resolve Folder (media pool bin) object."""

from __future__ import annotations

from resolve_lib.exceptions import ResolveOperationError


class Folder:
    """Wrapper around a Resolve media pool Folder (bin).

    Provides clean Python methods for listing clips, navigating
    sub-folders, exporting, and transcription operations.
    """

    def __init__(self, obj) -> None:
        """Initialise with the raw Folder object.

        Parameters
        ----------
        obj:
            The raw object returned by the Resolve API for a media pool folder.
        """
        self._obj = obj

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    def get_name(self) -> str:
        """Return the folder name."""
        return self._obj.GetName()

    def get_unique_id(self) -> str:
        """Return the unique identifier for this folder."""
        return self._obj.GetUniqueId()

    # ------------------------------------------------------------------
    # Contents
    # ------------------------------------------------------------------

    def get_clips(self) -> list[MediaPoolItem]:
        """Return the clips contained in this folder.

        Returns
        -------
        list[MediaPoolItem]
            Wrapped media pool items, or an empty list if the folder
            contains no clips.
        """
        from resolve_lib.media_pool_item import MediaPoolItem

        result = self._obj.GetClipList()
        if result is None:
            return []
        return [MediaPoolItem(item) for item in result]

    def get_subfolders(self) -> list[Folder]:
        """Return the immediate sub-folders of this folder.

        Returns
        -------
        list[Folder]
            Wrapped :class:`Folder` instances, or an empty list if there
            are no sub-folders.
        """
        result = self._obj.GetSubFolderList()
        if result is None:
            return []
        return [Folder(f) for f in result]

    # ------------------------------------------------------------------
    # Export / transcription
    # ------------------------------------------------------------------

    def export(self, path: str) -> bool:
        """Export the folder contents to a file.

        Parameters
        ----------
        path:
            Destination file path.

        Returns
        -------
        bool
            ``True`` if the export succeeded.
        """
        return self._obj.Export(path)

    def transcribe_audio(self) -> bool:
        """Start audio transcription for all clips in this folder.

        Returns
        -------
        bool
            ``True`` if transcription was started successfully.
        """
        return self._obj.TranscribeAudio()

    def clear_transcription(self) -> bool:
        """Clear audio transcription for all clips in this folder.

        Returns
        -------
        bool
            ``True`` if the transcription was cleared.
        """
        return self._obj.ClearTranscription()
