import pytest
from unittest.mock import patch, MagicMock
from resolve_lib.connect import connect, _load_script_module, _default_script_paths
from resolve_lib.exceptions import ResolveConnectionError

def test_connect_via_import():
    """Test tier-1: direct import succeeds."""
    mock_mod = MagicMock()
    mock_mod.scriptapp.return_value = MagicMock(name="Resolve")
    with patch("resolve_lib.connect.importlib.import_module", return_value=mock_mod):
        result = connect()
        assert result is not None
        mock_mod.scriptapp.assert_called_once_with("Resolve")

def test_connect_resolve_not_running():
    """Both scriptapp and GetResolve return None -> ResolveConnectionError."""
    mock_mod = MagicMock()
    mock_mod.scriptapp.return_value = None
    mock_mod.GetResolve.return_value = None
    with patch("resolve_lib.connect._load_script_module", return_value=mock_mod):
        with patch("resolve_lib.connect.sys") as mock_sys:
            mock_sys.modules = {}
            with pytest.raises(ResolveConnectionError, match="not running"):
                connect()

def test_default_paths_returns_list():
    paths = _default_script_paths()
    assert isinstance(paths, list)
    assert len(paths) >= 1
