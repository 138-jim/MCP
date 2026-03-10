"""MCP tools for render/deliver operations."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from resolve_mcp.helpers import resolve_tool, format_list, format_dict, get_project
from resolve_mcp.state import ServerState


def register_deliver_tools(mcp: FastMCP, state: ServerState):

    @mcp.tool()
    @resolve_tool
    def resolve_list_render_presets() -> str:
        """List available render presets."""
        proj = get_project(state)
        presets = proj.get_render_preset_list()
        return format_list(presets, "render presets")

    @mcp.tool()
    @resolve_tool
    def resolve_load_render_preset(name: str) -> str:
        """Load a render preset by name."""
        proj = get_project(state)
        if proj.load_render_preset(name):
            return f"Loaded render preset: {name}"
        return f"Failed to load render preset: {name}"

    @mcp.tool()
    @resolve_tool
    def resolve_get_render_format_and_codec() -> str:
        """Get the current render format and codec."""
        proj = get_project(state)
        result = proj.get_current_render_format_and_codec()
        return format_dict(result, "Current render format/codec")

    @mcp.tool()
    @resolve_tool
    def resolve_list_render_formats() -> str:
        """List available render formats."""
        proj = get_project(state)
        formats = proj.get_render_formats()
        return format_dict(formats, "Render formats")

    @mcp.tool()
    @resolve_tool
    def resolve_list_render_codecs(format_name: str) -> str:
        """List available codecs for a render format."""
        proj = get_project(state)
        codecs = proj.get_render_codecs(format_name)
        return format_dict(codecs, f"Codecs for {format_name}")

    @mcp.tool()
    @resolve_tool
    def resolve_delete_render_preset(name: str) -> str:
        """Delete a render preset by name."""
        proj = get_project(state)
        if proj.delete_render_preset(name):
            return f"Deleted render preset: {name}"
        return f"Failed to delete render preset: {name}"

    @mcp.tool()
    @resolve_tool
    def resolve_set_render_format_and_codec(render_format: str, codec: str) -> str:
        """Set render format and codec directly.

        Args:
            render_format: Render format identifier (e.g. 'mp4', 'mov').
            codec: Codec identifier (e.g. 'H264', 'H265').
        """
        proj = get_project(state)
        if proj.set_current_render_format_and_codec(render_format, codec):
            return f"Set render format={render_format}, codec={codec}"
        return "Failed to set render format/codec"

    @mcp.tool()
    @resolve_tool
    def resolve_set_render_settings(target_dir: str, custom_name: str = "", preset: str = "") -> str:
        """Configure render settings.

        Args:
            target_dir: Output directory for rendered files.
            custom_name: Custom output filename (optional).
            preset: Render preset to load first (optional).
        """
        proj = get_project(state)
        if preset:
            proj.load_render_preset(preset)
        settings: dict = {"TargetDir": target_dir, "SelectAllFrames": True}
        if custom_name:
            settings["CustomName"] = custom_name
        if proj.set_render_settings(settings):
            return f"Render settings configured: target={target_dir}"
        return "Failed to set render settings"

    @mcp.tool()
    @resolve_tool
    def resolve_add_render_job() -> str:
        """Add the current render settings as a render job to the queue."""
        proj = get_project(state)
        job_id = proj.add_render_job()
        if job_id:
            return f"Added render job: {job_id}"
        return "Failed to add render job"

    @mcp.tool()
    @resolve_tool
    def resolve_list_render_jobs() -> str:
        """List all render jobs in the queue."""
        proj = get_project(state)
        jobs = proj.get_render_job_list()
        if not jobs:
            return "No render jobs in queue"
        lines = ["Render jobs:"]
        for job in jobs:
            lines.append(f"  {job}")
        return "\n".join(lines)

    @mcp.tool()
    @resolve_tool
    def resolve_start_render(job_ids: list[str] | None = None) -> str:
        """Start rendering. Optionally specify job IDs to render.

        Args:
            job_ids: List of job IDs. If empty or null, renders all jobs.
        """
        proj = get_project(state)
        if job_ids:
            proj.start_rendering(*job_ids)
            return f"Rendering started for jobs: {', '.join(job_ids)}"
        proj.start_rendering()
        return "Rendering started for all jobs"

    @mcp.tool()
    @resolve_tool
    def resolve_stop_render() -> str:
        """Stop the current render."""
        proj = get_project(state)
        proj.stop_rendering()
        return "Rendering stopped"

    @mcp.tool()
    @resolve_tool
    def resolve_get_render_status(job_id: str) -> str:
        """Get the status of a render job."""
        proj = get_project(state)
        status = proj.get_render_job_status(job_id)
        return format_dict(status, f"Render job {job_id}")

    @mcp.tool()
    @resolve_tool
    def resolve_is_rendering() -> str:
        """Check if rendering is currently in progress."""
        proj = get_project(state)
        if proj.is_rendering_in_progress():
            return "Rendering is in progress"
        return "No rendering in progress"

    @mcp.tool()
    @resolve_tool
    def resolve_delete_render_job(job_id: str) -> str:
        """Delete a specific render job from the queue."""
        proj = get_project(state)
        if proj.delete_render_job(job_id):
            return f"Deleted render job: {job_id}"
        return f"Failed to delete render job: {job_id}"

    @mcp.tool()
    @resolve_tool
    def resolve_clear_render_queue() -> str:
        """Delete all render jobs from the queue."""
        proj = get_project(state)
        if proj.delete_all_render_jobs():
            return "Render queue cleared"
        return "Failed to clear render queue"
