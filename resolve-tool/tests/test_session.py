from resolve_lib.session import Session
from resolve_lib.project_manager import ProjectManager
from resolve_lib.media_storage import MediaStorage
from resolve_lib.exceptions import ResolveValidationError
import pytest

def test_get_version(session):
    assert session.get_version() == "19.0.0"

def test_get_product_name(session):
    assert session.get_product_name() == "DaVinci Resolve"

def test_get_current_page(session):
    assert session.get_current_page() == "edit"

def test_set_current_page(session):
    session.set_current_page("color")
    session._obj.OpenPage.assert_called_with("color")

def test_set_current_page_invalid(session):
    with pytest.raises(ResolveValidationError):
        session.set_current_page("invalid_page")

def test_get_project_manager(session):
    pm = session.get_project_manager()
    assert isinstance(pm, ProjectManager)

def test_get_media_storage(session):
    ms = session.get_media_storage()
    assert isinstance(ms, MediaStorage)

def test_keyframe_mode(session):
    assert session.get_keyframe_mode() == 0
    session.set_keyframe_mode(1)
    session._obj.SetKeyframeMode.assert_called_with(1)

def test_layout_preset(session):
    assert session.load_layout_preset("Default") is True

def test_import_layout_preset(session):
    assert session.import_layout_preset("MyLayout", "/tmp/layout.preset") is True
    session._obj.ImportLayoutPreset.assert_called_with("MyLayout", "/tmp/layout.preset")
