"""Wrapper around a DaVinci Resolve MediaPoolItem object."""

from __future__ import annotations

from resolve_lib.exceptions import ResolveOperationError


class MediaPoolItem:
    """Wrapper around a single Resolve MediaPoolItem.

    Provides clean Python methods for clip identity, metadata, markers,
    properties, and media operations exposed by the Resolve scripting API.
    """

    def __init__(self, obj) -> None:
        """Initialise with the raw MediaPoolItem object.

        Parameters
        ----------
        obj:
            The raw object returned by the Resolve API for a media pool item.
        """
        self._obj = obj

    @property
    def raw(self):
        """Return the underlying raw Resolve API object."""
        return self._obj

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    def get_name(self) -> str:
        """Return the clip name."""
        return self._obj.GetName()

    def get_unique_id(self) -> str:
        """Return the unique identifier for this media pool item."""
        return self._obj.GetUniqueId()

    def get_media_id(self) -> str:
        """Return the media identifier for this clip."""
        return self._obj.GetMediaId()

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    def get_metadata(self, key: str | None = None) -> str | dict:
        """Return clip metadata.

        Parameters
        ----------
        key:
            If provided, return the value for that single metadata key.
            If ``None``, return a dict of all metadata.

        Returns
        -------
        str | dict
            A single metadata value or a dict of all metadata.
        """
        if key is not None:
            return self._obj.GetMetadata(key)
        return self._obj.GetMetadata()

    def set_metadata(self, data: dict | str, value: str = "") -> bool:
        """Set clip metadata.

        Parameters
        ----------
        data:
            If a dict, sets multiple metadata key-value pairs at once.
            If a str, used as the metadata key together with *value*.
        value:
            The value to set when *data* is a string key.

        Returns
        -------
        bool
            ``True`` if the metadata was set successfully.
        """
        if isinstance(data, dict):
            return self._obj.SetMetadata(data)
        return self._obj.SetMetadata(data, value)

    def get_third_party_metadata(self, key: str | None = None) -> str | dict:
        """Return third-party metadata.

        Parameters
        ----------
        key:
            If provided, return the value for that single key.
            If ``None``, return a dict of all third-party metadata.

        Returns
        -------
        str | dict
            A single value or a dict of all third-party metadata.
        """
        if key is not None:
            return self._obj.GetThirdPartyMetadata(key)
        return self._obj.GetThirdPartyMetadata()

    def set_third_party_metadata(self, data: dict | str, value: str = "") -> bool:
        """Set third-party metadata.

        Parameters
        ----------
        data:
            If a dict, sets multiple key-value pairs at once.
            If a str, used as the key together with *value*.
        value:
            The value to set when *data* is a string key.

        Returns
        -------
        bool
            ``True`` if the metadata was set successfully.
        """
        if isinstance(data, dict):
            return self._obj.SetThirdPartyMetadata(data)
        return self._obj.SetThirdPartyMetadata(data, value)

    def delete_third_party_metadata(self, key: str) -> bool:
        """Delete a third-party metadata entry.

        Parameters
        ----------
        key:
            The metadata key to delete.

        Returns
        -------
        bool
            ``True`` if the key was deleted successfully.
        """
        return self._obj.DeleteThirdPartyMetadata(key)

    # ------------------------------------------------------------------
    # Markers
    # ------------------------------------------------------------------

    def get_markers(self) -> dict:
        """Return all markers on this clip.

        Returns
        -------
        dict
            A dict keyed by frame number, each value being marker info.
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
        """Add a marker to this clip.

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
    # Properties
    # ------------------------------------------------------------------

    def get_clip_property(self, key: str | None = None) -> str | dict:
        """Return clip properties.

        Parameters
        ----------
        key:
            If provided, return the value for that single property.
            If ``None``, return a dict of all clip properties.

        Returns
        -------
        str | dict
            A single property value or a dict of all properties.
        """
        if key is not None:
            return self._obj.GetClipProperty(key)
        return self._obj.GetClipProperty()

    def set_clip_property(self, key: str, value: str) -> bool:
        """Set a clip property.

        Parameters
        ----------
        key:
            Property name.
        value:
            Property value.

        Returns
        -------
        bool
            ``True`` if the property was set successfully.
        """
        return self._obj.SetClipProperty(key, value)

    def get_clip_color(self) -> str:
        """Return the clip colour label."""
        return self._obj.GetClipColor()

    def set_clip_color(self, color: str) -> bool:
        """Set the clip colour label.

        Parameters
        ----------
        color:
            Colour name (e.g. ``"Orange"``, ``"Blue"``).

        Returns
        -------
        bool
            ``True`` if the colour was set successfully.
        """
        return self._obj.SetClipColor(color)

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
            Flag colour name.

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
            Colour to clear. Use ``""`` to clear all flags.

        Returns
        -------
        bool
            ``True`` if flags were cleared.
        """
        return self._obj.ClearFlags(color)

    # ------------------------------------------------------------------
    # Media
    # ------------------------------------------------------------------

    def replace_clip(self, path: str) -> bool:
        """Replace the underlying media file for this clip.

        Parameters
        ----------
        path:
            File path to the replacement media.

        Returns
        -------
        bool
            ``True`` if the clip was replaced successfully.
        """
        return self._obj.ReplaceClip(path)

    def link_proxy_media(self, path: str, proxy_type: str = "File") -> bool:
        """Link a proxy media file to this clip.

        Parameters
        ----------
        path:
            File path to the proxy media.
        proxy_type:
            Proxy type identifier (default ``"File"``).

        Returns
        -------
        bool
            ``True`` if the proxy was linked successfully.
        """
        return self._obj.LinkProxyMedia(path, proxy_type)

    def unlink_proxy_media(self) -> bool:
        """Unlink proxy media from this clip.

        Returns
        -------
        bool
            ``True`` if the proxy was unlinked successfully.
        """
        return self._obj.UnlinkProxyMedia()

    def get_mark_in(self) -> int:
        """Return the mark-in frame position.

        Returns
        -------
        int
            The mark-in frame number.
        """
        return self._obj.GetMarkIn()

    def get_mark_out(self) -> int:
        """Return the mark-out frame position.

        Returns
        -------
        int
            The mark-out frame number.
        """
        return self._obj.GetMarkOut()

    def transcribe_audio(self) -> bool:
        """Start audio transcription for this clip.

        Returns
        -------
        bool
            ``True`` if transcription was started successfully.
        """
        return self._obj.TranscribeAudio()

    def clear_transcription(self) -> bool:
        """Clear the audio transcription for this clip.

        Returns
        -------
        bool
            ``True`` if the transcription was cleared.
        """
        return self._obj.ClearTranscription()

    def clear_mark_in(self) -> bool:
        """Clear the mark-in point for this clip.

        Returns
        -------
        bool
            ``True`` if the mark-in was cleared successfully.
        """
        return self._obj.ClearMarkIn()

    def clear_mark_out(self) -> bool:
        """Clear the mark-out point for this clip.

        Returns
        -------
        bool
            ``True`` if the mark-out was cleared successfully.
        """
        return self._obj.ClearMarkOut()

    def get_audio_mapping(self) -> str | None:
        """Return the audio channel mapping for this clip.

        Returns
        -------
        str | None
            The audio mapping string, or ``None`` if not available.
        """
        fn = getattr(self._obj, "GetAudioMapping", None)
        if not callable(fn):
            return None
        return fn()
