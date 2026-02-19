from resolve_lib.project import Project
import pytest

def test_get_database_list(project_manager):
    dbs = project_manager.get_database_list()
    assert len(dbs) == 1
    assert dbs[0]["DbName"] == "Local Database"

def test_get_current_database(project_manager):
    db = project_manager.get_current_database()
    assert db["DbType"] == "Disk"

def test_get_project_list(project_manager):
    projects = project_manager.get_project_list_in_current_folder()
    assert "MyProject" in projects

def test_create_project(project_manager):
    proj = project_manager.create_project("NewProject")
    assert isinstance(proj, Project)

def test_load_project(project_manager):
    proj = project_manager.load_project("TestProject")
    assert isinstance(proj, Project)

def test_get_current_project(project_manager):
    proj = project_manager.get_current_project()
    assert isinstance(proj, Project)

def test_save_project(project_manager):
    assert project_manager.save_project() is True

def test_folder_operations(project_manager):
    folders = project_manager.get_folder_list_in_current_folder()
    assert "Drama" in folders
    assert project_manager.create_folder("NewFolder") is True
    assert project_manager.open_folder("Drama") is True

def test_goto_root_folder(project_manager):
    assert project_manager.goto_root_folder() is True

def test_goto_parent_folder(project_manager):
    assert project_manager.goto_parent_folder() is True

def test_delete_folder(project_manager):
    assert project_manager.delete_folder("OldFolder") is True
    project_manager._obj.DeleteFolder.assert_called_with("OldFolder")
