"""Sanix exceptions."""

class SanixException(Exception):
    """Raised when Sanix API ended with error."""


class SanixInvalidAuthException(SanixException):
    """Sanix API Invalid Auth exception."""
