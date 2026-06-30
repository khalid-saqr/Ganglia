class GangliaError(Exception):
    """Base error for Ganglia."""


class OperatorLoadError(GangliaError):
    """Raised when an operator cannot be loaded."""


class OperatorNotFoundError(GangliaError):
    """Raised when an operator id is not registered."""


class LLMClientError(GangliaError):
    """Raised when the LLM backend fails."""


class ValidationFailure(GangliaError):
    """Raised when a model output fails validation."""
