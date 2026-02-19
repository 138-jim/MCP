"""Shared test fixtures."""

import pytest
from unittest.mock import MagicMock

from tests.mocks.mock_resolve import create_mock_resolve
from resolve_lib.session import Session
from resolve_lib.project_manager import ProjectManager
from resolve_lib.project import Project
from resolve_lib.media_pool import MediaPool
from resolve_lib.timeline import Timeline


@pytest.fixture
def mock_resolve():
    """Return a fully configured mock Resolve API object."""
    return create_mock_resolve()


@pytest.fixture
def session(mock_resolve):
    """Return a Session wrapping the mock Resolve object."""
    return Session(mock_resolve)


@pytest.fixture
def project_manager(session):
    """Return a ProjectManager from the session."""
    return session.get_project_manager()


@pytest.fixture
def project(project_manager):
    """Return the current Project."""
    return project_manager.get_current_project()


@pytest.fixture
def media_pool(project):
    """Return the MediaPool from the current project."""
    return project.get_media_pool()


@pytest.fixture
def timeline(project):
    """Return the current Timeline."""
    return project.get_current_timeline()
