"""Wrapper around the DaVinci Resolve ProjectManager API object."""

from __future__ import annotations

from resolve_lib.exceptions import ResolveOperationError


class ProjectManager:
    """Wrapper around the Resolve ProjectManager object.

    Provides methods for database, folder, and project operations.
    """

    def __init__(self, obj) -> None:
        """Initialise with the raw ProjectManager object.

        Parameters
        ----------
        obj:
            The raw object returned by ``Resolve.GetProjectManager()``.
        """
        self._obj = obj

    # ------------------------------------------------------------------
    # Database operations
    # ------------------------------------------------------------------

    def get_database_list(self) -> list[dict]:
        """Return a list of available database descriptors."""
        return self._obj.GetDatabaseList()

    def get_current_database(self) -> dict:
        """Return a descriptor for the currently active database."""
        return self._obj.GetCurrentDatabase()

    def set_current_database(self, db_info: dict) -> bool:
        """Switch to a different database.

        Parameters
        ----------
        db_info:
            A database descriptor dict (see :class:`resolve_lib.types.DatabaseInfo`).

        Returns
        -------
        bool
            ``True`` if the database was switched successfully.
        """
        return self._obj.SetCurrentDatabase(db_info)

    # ------------------------------------------------------------------
    # Folder operations
    # ------------------------------------------------------------------

    def open_folder(self, path: str) -> bool:
        """Open a project folder by its path.

        Parameters
        ----------
        path:
            Folder path within the project database.

        Returns
        -------
        bool
            ``True`` if the folder was opened successfully.
        """
        return self._obj.OpenFolder(path)

    def get_current_folder(self) -> str:
        """Return the name of the current project folder."""
        return self._obj.GetCurrentFolder()

    def get_folder_list_in_current_folder(self) -> list[str]:
        """Return a list of sub-folder names in the current folder."""
        return self._obj.GetFolderListInCurrentFolder()

    def create_folder(self, name: str) -> bool:
        """Create a new sub-folder in the current folder.

        Parameters
        ----------
        name:
            Name for the new folder.

        Returns
        -------
        bool
            ``True`` if the folder was created successfully.
        """
        return self._obj.CreateFolder(name)

    def goto_root_folder(self) -> bool:
        """Navigate to the root project folder.

        Returns
        -------
        bool
            ``True`` if navigation succeeded.
        """
        return self._obj.GotoRootFolder()

    def goto_parent_folder(self) -> bool:
        """Navigate to the parent project folder.

        Returns
        -------
        bool
            ``True`` if navigation succeeded.
        """
        return self._obj.GotoParentFolder()

    def delete_folder(self, name: str) -> bool:
        """Delete a project folder by name.

        Parameters
        ----------
        name:
            Name of the folder to delete.

        Returns
        -------
        bool
            ``True`` if the folder was deleted successfully.
        """
        return self._obj.DeleteFolder(name)

    # ------------------------------------------------------------------
    # Project CRUD
    # ------------------------------------------------------------------

    def get_project_list_in_current_folder(self) -> list[str]:
        """Return a list of project names in the current folder."""
        return self._obj.GetProjectListInCurrentFolder()

    def create_project(self, name: str) -> Project:
        """Create a new project.

        Parameters
        ----------
        name:
            Name for the new project.

        Returns
        -------
        Project
            The newly created project wrapper.

        Raises
        ------
        ResolveOperationError
            If the project could not be created (e.g. name already exists).
        """
        from resolve_lib.project import Project

        result = self._obj.CreateProject(name)
        if result is None:
            raise ResolveOperationError(
                f"Failed to create project {name!r}"
            )
        return Project(result)

    def load_project(self, name: str) -> Project:
        """Load an existing project by name.

        Parameters
        ----------
        name:
            Name of the project to load.

        Returns
        -------
        Project
            The loaded project wrapper.

        Raises
        ------
        ResolveOperationError
            If the project could not be loaded (e.g. not found).
        """
        from resolve_lib.project import Project

        result = self._obj.LoadProject(name)
        if result is None:
            raise ResolveOperationError(
                f"Failed to load project {name!r}"
            )
        return Project(result)

    def get_current_project(self) -> Project:
        """Return the currently open project.

        Returns
        -------
        Project
            The current project wrapper.

        Raises
        ------
        ResolveOperationError
            If no project is currently open.
        """
        from resolve_lib.project import Project

        result = self._obj.GetCurrentProject()
        if result is None:
            raise ResolveOperationError("No project is currently open")
        return Project(result)

    def save_project(self) -> bool:
        """Save the current project.

        Returns
        -------
        bool
            ``True`` if the project was saved successfully.
        """
        return self._obj.SaveProject()

    def close_project(self, project: Project) -> bool:
        """Close the specified project.

        Parameters
        ----------
        project:
            The :class:`Project` wrapper to close.

        Returns
        -------
        bool
            ``True`` if the project was closed successfully.
        """
        return self._obj.CloseProject(project._obj)

    def delete_project(self, name: str) -> bool:
        """Delete a project by name.

        Parameters
        ----------
        name:
            Name of the project to delete.

        Returns
        -------
        bool
            ``True`` if the project was deleted successfully.
        """
        return self._obj.DeleteProject(name)

    # ------------------------------------------------------------------
    # Import / Export / Archive
    # ------------------------------------------------------------------

    def import_project(self, path: str, name: str | None = None) -> bool:
        """Import a project from a file.

        Parameters
        ----------
        path:
            File path of the project to import.
        name:
            Optional name to assign to the imported project.

        Returns
        -------
        bool
            ``True`` if the project was imported successfully.
        """
        if name is not None:
            return self._obj.ImportProject(path, name)
        return self._obj.ImportProject(path)

    def export_project(
        self,
        name: str,
        path: str,
        with_stills_and_luts: bool = True,
    ) -> bool:
        """Export a project to a file.

        Parameters
        ----------
        name:
            Name of the project to export.
        path:
            Destination file path.
        with_stills_and_luts:
            Whether to include stills and LUTs in the export.

        Returns
        -------
        bool
            ``True`` if the project was exported successfully.
        """
        return self._obj.ExportProject(name, path, with_stills_and_luts)

    def restore_project(self, path: str, name: str | None = None) -> bool:
        """Restore a project from an archive file.

        Parameters
        ----------
        path:
            File path of the archive to restore.
        name:
            Optional name to assign to the restored project.

        Returns
        -------
        bool
            ``True`` if the project was restored successfully.
        """
        if name is not None:
            return self._obj.RestoreProject(path, name)
        return self._obj.RestoreProject(path)

    def archive_project(
        self,
        name: str,
        path: str,
        archive_type: str = "archiveAsIndividualClip",
    ) -> bool:
        """Archive a project to disk.

        Parameters
        ----------
        name:
            Name of the project to archive.
        path:
            Destination file path for the archive.
        archive_type:
            Archive type identifier (default ``"archiveAsIndividualClip"``).

        Returns
        -------
        bool
            ``True`` if the project was archived successfully.
        """
        return self._obj.ArchiveProject(name, path, archive_type)
