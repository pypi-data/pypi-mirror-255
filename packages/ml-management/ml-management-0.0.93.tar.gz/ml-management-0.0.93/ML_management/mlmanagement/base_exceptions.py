"""Base classes for custom exceptions used in project."""


class MLMBaseError(Exception):
    """Base exception for all custom exceptions."""

    pass


class MLMServerError(MLMBaseError):
    """Base exception for all server mlmanager exceptions."""

    pass


class RegistryError(MLMBaseError):
    """Base exception for all registry exceptions."""

    pass


class MLMClientError(MLMBaseError):
    """Base exception for all client-side specific exceptions."""

    pass


class PylintError(MLMBaseError):
    """Base exception for all errors within linter check."""

    def __init__(self, message):
        super().__init__("Pylint found errors in code of uploaded modules:\n" + message)
