"""High-level render/deliver workflow helpers."""

from __future__ import annotations

from resolve_lib.exceptions import ResolveOperationError


class Deliver:
    """Convenience helpers for common render workflows.

    Wraps a Project object to provide simplified render operations.
    """

    def __init__(self, project):
        """Initialize with a Project wrapper instance."""
        self._project = project

    def quick_render(
        self,
        target_dir: str,
        preset: str | None = None,
        custom_name: str | None = None,
        format_: str | None = None,
        codec: str | None = None,
        start: bool = True,
    ) -> str:
        """Set up and optionally start a render job.

        Args:
            target_dir: Output directory.
            preset: Render preset name to load. If None, uses current settings.
            custom_name: Custom filename for the output.
            format_: Render format (e.g. 'mp4', 'mov'). Overrides preset.
            codec: Render codec (e.g. 'H.264', 'H.265'). Overrides preset.
            start: Whether to start rendering immediately.

        Returns:
            The render job ID.
        """
        proj = self._project

        if preset:
            if not proj.load_render_preset(preset):
                raise ResolveOperationError(f"Failed to load render preset: {preset}")

        settings: dict = {"TargetDir": target_dir, "SelectAllFrames": True}
        if custom_name:
            settings["CustomName"] = custom_name
        if format_:
            settings["FormatWidth"] = format_  # Resolve uses SetRenderSettings for format
        proj.set_render_settings(settings)

        if format_ and codec:
            # Use the lower-level API for explicit format/codec
            proj._obj.SetRenderSettings({"FormatWidth": 0})  # reset
            proj._obj.SetCurrentRenderFormatAndCodec(format_, codec)

        job_id = proj.add_render_job()
        if not job_id:
            raise ResolveOperationError("Failed to add render job")

        if start:
            proj.start_rendering(job_id)

        return job_id

    def render_timeline(
        self,
        target_dir: str,
        timeline=None,
        preset: str | None = None,
        custom_name: str | None = None,
        start: bool = True,
    ) -> str:
        """Render a specific timeline.

        Args:
            target_dir: Output directory.
            timeline: Timeline wrapper to render. If None, uses current.
            preset: Render preset name.
            custom_name: Custom filename.
            start: Whether to start rendering immediately.

        Returns:
            The render job ID.
        """
        proj = self._project

        if timeline:
            proj.set_current_timeline(timeline)

        return self.quick_render(
            target_dir=target_dir,
            preset=preset,
            custom_name=custom_name,
            start=start,
        )

    def get_render_progress(self, job_id: str) -> dict:
        """Get the status and progress of a render job.

        Returns:
            Dict with keys like 'JobStatus', 'CompletionPercentage', etc.
        """
        return self._project.get_render_job_status(job_id)

    def wait_for_render(self, job_id: str, poll_interval: float = 1.0) -> dict:
        """Block until a render job completes.

        Args:
            job_id: The render job ID.
            poll_interval: Seconds between status checks.

        Returns:
            Final job status dict.
        """
        import time

        while True:
            status = self.get_render_progress(job_id)
            if not self._project.is_rendering_in_progress():
                return status
            time.sleep(poll_interval)

    def list_formats(self) -> dict:
        """List available render formats."""
        return self._project.get_render_formats()

    def list_codecs(self, format_: str) -> dict:
        """List available codecs for a render format."""
        return self._project.get_render_codecs(format_)

    def list_presets(self) -> list[str]:
        """List available render presets."""
        return self._project.get_render_preset_list()

    def clear_all_jobs(self) -> bool:
        """Delete all render jobs from the queue."""
        return self._project.delete_all_render_jobs()

    def cancel_render(self) -> None:
        """Stop the current render."""
        self._project.stop_rendering()
