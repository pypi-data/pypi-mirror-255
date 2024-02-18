"""Exceptions for WireGuard status API."""


class WireGuardException(Exception):
    """Base exception for WireGuard status API."""


class WireGuardInvalidJson(WireGuardException, ValueError):
    """Exception to indicate incorrect json data."""


class WireGuardRequestError(WireGuardException):
    """Exception to indicate request error."""


class WireGuardTimeoutError(WireGuardRequestError):
    """Exception to indicate connection error."""


class WireGuardResponseError(WireGuardRequestError):
    """Exception to indicate an unexpected response."""
