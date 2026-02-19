"""Wrappers for DaVinci Resolve Gallery and GalleryStillAlbum."""

from __future__ import annotations

from resolve_lib.exceptions import ResolveOperationError


class GalleryStillAlbum:
    """Wraps a Resolve GalleryStillAlbum object."""

    def __init__(self, obj):
        self._obj = obj

    def get_stills(self) -> list:
        """Return list of still objects in this album."""
        return self._obj.GetStills() or []

    def get_label(self, still) -> str:
        """Get the label of a still."""
        raw = still._obj if hasattr(still, "_obj") else still
        return self._obj.GetLabel(raw) or ""

    def set_label(self, still, label: str) -> bool:
        """Set the label of a still."""
        raw = still._obj if hasattr(still, "_obj") else still
        return bool(self._obj.SetLabel(raw, label))

    def import_stills(self, paths: list[str]) -> bool:
        """Import stills from file paths into this album."""
        return bool(self._obj.ImportStills(paths))

    def export_stills(
        self, stills: list, path: str, file_prefix: str = "", format: str = "dpx"
    ) -> bool:
        """Export stills to a directory.

        Args:
            stills: List of still objects to export.
            path: Target directory.
            file_prefix: Prefix for exported file names.
            format: Export format (dpx, cin, tif, jpg, png, ppm, bmp, xpm).
        """
        raw_stills = [s._obj if hasattr(s, "_obj") else s for s in stills]
        return bool(self._obj.ExportStills(raw_stills, path, file_prefix, format))

    def delete_stills(self, stills: list) -> bool:
        """Delete stills from this album."""
        raw_stills = [s._obj if hasattr(s, "_obj") else s for s in stills]
        return bool(self._obj.DeleteStills(raw_stills))


class Gallery:
    """Wraps a Resolve Gallery object."""

    def __init__(self, obj):
        self._obj = obj

    def get_album_name(self, album: GalleryStillAlbum) -> str:
        """Get the name of a still album."""
        return self._obj.GetAlbumName(album._obj) or ""

    def set_album_name(self, album: GalleryStillAlbum, name: str) -> bool:
        """Set the name of a still album."""
        return bool(self._obj.SetAlbumName(album._obj, name))

    def get_current_still_album(self) -> GalleryStillAlbum:
        """Get the currently selected still album."""
        obj = self._obj.GetCurrentStillAlbum()
        if obj is None:
            raise ResolveOperationError("No current still album")
        return GalleryStillAlbum(obj)

    def set_current_still_album(self, album: GalleryStillAlbum) -> bool:
        """Set the currently selected still album."""
        return bool(self._obj.SetCurrentStillAlbum(album._obj))

    def get_gallery_still_albums(self) -> list[GalleryStillAlbum]:
        """Get all still albums in the gallery."""
        result = self._obj.GetGalleryStillAlbums()
        return [GalleryStillAlbum(a) for a in result] if result else []

    def get_gallery_powergrade_albums(self) -> list[GalleryStillAlbum]:
        """Get all powergrade albums in the gallery."""
        fn = getattr(self._obj, "GetGalleryPowerGradeAlbums", None)
        if fn is None:
            return []
        result = fn()
        return [GalleryStillAlbum(a) for a in result] if result else []

    def create_gallery_still_album(self) -> GalleryStillAlbum:
        """Create a new still album."""
        fn = getattr(self._obj, "CreateGalleryStillAlbum", None)
        if fn is None:
            raise ResolveOperationError("CreateGalleryStillAlbum not available")
        obj = fn()
        if obj is None:
            raise ResolveOperationError("Failed to create still album")
        return GalleryStillAlbum(obj)

    def create_gallery_powergrade_album(self) -> GalleryStillAlbum:
        """Create a new powergrade album."""
        fn = getattr(self._obj, "CreateGalleryPowerGradeAlbum", None)
        if fn is None:
            raise ResolveOperationError("CreateGalleryPowerGradeAlbum not available")
        obj = fn()
        if obj is None:
            raise ResolveOperationError("Failed to create powergrade album")
        return GalleryStillAlbum(obj)
