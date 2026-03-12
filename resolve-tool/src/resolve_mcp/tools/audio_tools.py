"""MCP tools for audio/Fairlight operations."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from resolve_mcp.helpers import resolve_tool
from resolve_mcp.state import ServerState


def register_audio_tools(mcp: FastMCP, state: ServerState):

    @mcp.tool()
    @resolve_tool
    def resolve_insert_audio_at_playhead(
        file_path: str,
        start_offset_samples: int = 0,
        duration_samples: int = 0,
    ) -> str:
        """Insert an audio file on the selected Fairlight track at the playhead.

        IMPORTANT: This tool only works on the Fairlight page with an audio
        track selected.  Switch to the Fairlight page first if needed.

        Args:
            file_path: Absolute path to the audio file.
            start_offset_samples: Start offset within the audio file in
                samples (e.g. 44100 = 1 second at 44.1 kHz).  0 = beginning.
            duration_samples: Duration in samples.  0 = use the full clip
                length.
        """
        import os

        if not os.path.isfile(file_path):
            return f"File not found: {file_path}"
        project = state.session.get_project_manager().get_current_project()
        result = project.insert_audio_to_current_track_at_playhead(
            file_path, start_offset_samples, duration_samples
        )
        if result:
            return f"Inserted audio: {file_path}"
        return (
            f"Failed to insert audio: {file_path}. "
            "Ensure you are on the Fairlight page with an audio track selected."
        )

    @mcp.tool()
    @resolve_tool
    def resolve_load_burn_in_preset(name: str) -> str:
        """Load a burn-in preset by name."""
        project = state.session.get_project_manager().get_current_project()
        if project.load_burn_in_preset(name):
            return f"Loaded burn-in preset: {name}"
        return f"Failed to load burn-in preset: {name}"

    # Disabled: SetVoiceIsolationState always returns False (may need Studio)
    @resolve_tool
    def resolve_voice_isolation_timeline() -> str:
        """Apply voice isolation to the current timeline (Resolve 19+)."""
        project = state.session.get_project_manager().get_current_project()
        timeline = project.get_current_timeline()
        if timeline.apply_voice_isolation_to_timeline():
            return "Voice isolation applied to timeline"
        return "Failed to apply voice isolation (may require Resolve 19+)"

    # Disabled: SetVoiceIsolationState always returns False (may need Studio)
    @resolve_tool
    def resolve_voice_isolation_clip(track_type: str, track_index: int, item_index: int) -> str:
        """Apply voice isolation to a specific clip.

        Args:
            track_type: Track type (video or audio).
            track_index: Track index (1-based).
            item_index: Item index within the track (0-based).
        """
        project = state.session.get_project_manager().get_current_project()
        timeline = project.get_current_timeline()
        items = timeline.get_item_list_in_track(track_type, track_index)
        if item_index >= len(items):
            return f"Item index {item_index} out of range (track has {len(items)} items)"
        item = items[item_index]
        if item.apply_voice_isolation():
            return "Voice isolation applied to clip"
        return "Failed to apply voice isolation"
