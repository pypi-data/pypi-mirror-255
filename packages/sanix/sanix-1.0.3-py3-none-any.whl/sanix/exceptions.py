"""Sanix exceptions."""

class SanixException(Exception):
    """Raised when Sanix API ended with error."""

    def __init__(self, status):
        """Initialize the Sanix Exception."""
        self.status = status
