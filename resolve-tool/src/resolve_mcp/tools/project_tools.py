"""MCP tools for project and database management."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from resolve_mcp.helpers import resolve_tool, format_list, format_dict
from resolve_mcp.state import ServerState


def register_project_tools(mcp: FastMCP, state: ServerState):

    @mcp.tool()
    @resolve_tool
    def resolve_list_databases() -> str:
        """List all available databases."""
        pm = state.session.get_project_manager()
        databases = pm.get_database_list()
        return format_list(databases, "databases")

    @mcp.tool()
    @resolve_tool
    def resolve_get_current_database() -> str:
        """Get information about the currently active database."""
        pm = state.session.get_project_manager()
        db = pm.get_current_database()
        return format_dict(db, "Current database")

    @mcp.tool()
    @resolve_tool
    def resolve_switch_database(
        db_name: str, db_type: str = "Disk", ip_address: str = ""
    ) -> str:
        """Switch to a different database.

        Args:
            db_name: Name of the database to switch to.
            db_type: Database type (Disk or PostgreSQL).
            ip_address: IP address for PostgreSQL databases (leave empty for Disk).
        """
        pm = state.session.get_project_manager()
        db_info = {"DbName": db_name, "DbType": db_type}
        if ip_address:
            db_info["IpAddress"] = ip_address
        if pm.set_current_database(db_info):
            return f"Switched to database: {db_name}"
        return f"Failed to switch to database: {db_name}"

    @mcp.tool()
    @resolve_tool
    def resolve_list_project_folders() -> str:
        """List folders in the current project database location."""
        pm = state.session.get_project_manager()
        folders = pm.get_folder_list_in_current_folder()
        return format_list(folders, "folders")

    @mcp.tool()
    @resolve_tool
    def resolve_open_project_folder(path: str) -> str:
        """Open a project folder by its path.

        Args:
            path: Folder path within the project database.
        """
        pm = state.session.get_project_manager()
        if pm.open_folder(path):
            return f"Opened folder: {path}"
        return f"Failed to open folder: {path}"

    @mcp.tool()
    @resolve_tool
    def resolve_create_project_folder(name: str) -> str:
        """Create a new folder in the current project database location.

        Args:
            name: Name for the new folder.
        """
        pm = state.session.get_project_manager()
        if pm.create_folder(name):
            return f"Created folder: {name}"
        return f"Failed to create folder: {name}"

    @mcp.tool()
    @resolve_tool
    def resolve_goto_root_folder() -> str:
        """Navigate to root project folder."""
        pm = state.session.get_project_manager()
        if pm.goto_root_folder():
            return "Navigated to root folder"
        return "Failed to navigate to root folder"

    @mcp.tool()
    @resolve_tool
    def resolve_goto_parent_folder() -> str:
        """Navigate to parent project folder."""
        pm = state.session.get_project_manager()
        if pm.goto_parent_folder():
            return "Navigated to parent folder"
        return "Failed to navigate to parent folder"

    @mcp.tool()
    @resolve_tool
    def resolve_delete_project_folder(name: str) -> str:
        """Delete a project folder.

        Args:
            name: Name of the folder to delete.
        """
        pm = state.session.get_project_manager()
        if pm.delete_folder(name):
            return f"Deleted folder: {name}"
        return f"Failed to delete folder: {name}"

    @mcp.tool()
    @resolve_tool
    def resolve_list_projects() -> str:
        """List all projects in the current folder."""
        pm = state.session.get_project_manager()
        projects = pm.get_project_list_in_current_folder()
        return format_list(projects, "projects")

    @mcp.tool()
    @resolve_tool
    def resolve_create_project(name: str) -> str:
        """Create and open a new project.

        Args:
            name: Name for the new project.
        """
        pm = state.session.get_project_manager()
        project = pm.create_project(name)
        project.set_setting("timelineInputResMismatchBehavior", "centerCrop")
        return f"Created and opened project: {project.get_name()}"

    @mcp.tool()
    @resolve_tool
    def resolve_load_project(name: str) -> str:
        """Load an existing project by name.

        Args:
            name: Name of the project to load.
        """
        pm = state.session.get_project_manager()
        project = pm.load_project(name)
        return f"Loaded project: {project.get_name()}"

    @mcp.tool()
    @resolve_tool
    def resolve_get_current_project() -> str:
        """Get the name of the currently open project."""
        pm = state.session.get_project_manager()
        project = pm.get_current_project()
        return f"Current project: {project.get_name()}"

    @mcp.tool()
    @resolve_tool
    def resolve_export_project(
        name: str, path: str, with_stills_and_luts: bool = True
    ) -> str:
        """Export a project to a file.

        Args:
            name: Name of the project to export.
            path: Destination file path.
            with_stills_and_luts: Include stills and LUTs in the export.
        """
        pm = state.session.get_project_manager()
        if pm.export_project(name, path, with_stills_and_luts):
            return f"Exported project {name!r} to {path}"
        return f"Failed to export project {name!r}"

    @mcp.tool()
    @resolve_tool
    def resolve_get_project_setting(key: str) -> str:
        """Get a project setting by key. Use empty string to get all settings.

        Common keys: timelineFrameRate, timelineResolutionWidth,
        timelineResolutionHeight, videoMonitorFormat, superScale.

        Args:
            key: Setting key (empty string returns all settings).
        """
        proj = state.session.get_project_manager().get_current_project()
        result = proj.get_setting(key)
        if isinstance(result, dict):
            return format_dict(result, "Project settings")
        return f"{key}: {result}"

    @mcp.tool()
    @resolve_tool
    def resolve_set_project_setting(key: str, value: str) -> str:
        """Set a project setting.

        Common keys: timelineFrameRate (e.g. "24", "29.97 DF"),
        timelineResolutionWidth, timelineResolutionHeight.

        Args:
            key: Setting key.
            value: Setting value.
        """
        if key.lower() == "timelineplaybackframerate":
            return (
                "Unsupported key: timelinePlaybackFrameRate. "
                "Use timelineFrameRate instead (set it before creating timelines)."
            )
        proj = state.session.get_project_manager().get_current_project()
        if proj.set_setting(key, value):
            return f"Set {key}={value}"
        return f"Failed to set {key}"

    @mcp.tool()
    @resolve_tool
    def resolve_import_project(path: str, name: str = "") -> str:
        """Import a project from a file.

        Args:
            path: File path of the project to import.
            name: Optional name to assign to the imported project.
        """
        pm = state.session.get_project_manager()
        import_name = name if name else None
        if pm.import_project(path, import_name):
            return f"Imported project from {path}"
        return f"Failed to import project from {path}"
