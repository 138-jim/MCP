"""Exception hierarchy for resolve_lib."""


class ResolveError(Exception):
    """Base exception for all resolve_lib errors."""


class ResolveConnectionError(ResolveError):
    """Failed to connect to DaVinci Resolve."""


class ResolveOperationError(ResolveError):
    """A Resolve API call returned failure (False/None)."""


class ResolveNotFoundError(ResolveError):
    """Requested resource (project, timeline, clip, etc.) not found."""


class ResolveValidationError(ResolveError):
    """Invalid argument passed to a library method."""
