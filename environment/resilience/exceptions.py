"""
Exceptions for resilience components.
"""

import httpx


class RateLimitExceeded(Exception):
    """Raised when an API rate limit is exceeded and cannot be acquired within timeout."""

    pass


class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is open and request is rejected."""

    pass


class RateLimitError(Exception):
    """Raised when API rate limit is hit (e.g., HTTP 403)."""

    def __init__(self, message: str, response: httpx.Response | None = None):
        self.response = response
        super().__init__(message)
