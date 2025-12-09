"""Tests for resilience exceptions."""

import pytest
import httpx
from unittest.mock import Mock

from environment.resilience.exceptions import (
    RateLimitExceeded,
    CircuitBreakerOpen,
    RateLimitError,
)


class TestRateLimitExceeded:
    """Test suite for RateLimitExceeded exception."""

    def test_exception_can_be_raised_and_caught(self):
        """RateLimitExceeded should be a standard exception."""
        with pytest.raises(RateLimitExceeded) as exc_info:
            raise RateLimitExceeded("Rate limit exceeded")

        assert str(exc_info.value) == "Rate limit exceeded"

    def test_exception_is_instance_of_exception(self):
        """RateLimitExceeded should be an instance of Exception."""
        exc = RateLimitExceeded("Test message")
        assert isinstance(exc, Exception)

    def test_exception_with_custom_message(self):
        """RateLimitExceeded should preserve custom message."""
        message = "Custom rate limit message with details"
        exc = RateLimitExceeded(message)
        assert str(exc) == message

    def test_exception_can_be_used_in_try_except(self):
        """RateLimitExceeded should work in try-except blocks."""
        try:
            raise RateLimitExceeded("Rate limit hit")
        except RateLimitExceeded as e:
            assert "Rate limit hit" in str(e)


class TestCircuitBreakerOpen:
    """Test suite for CircuitBreakerOpen exception."""

    def test_exception_can_be_raised_and_caught(self):
        """CircuitBreakerOpen should be a standard exception."""
        with pytest.raises(CircuitBreakerOpen) as exc_info:
            raise CircuitBreakerOpen("Circuit breaker is open")

        assert str(exc_info.value) == "Circuit breaker is open"

    def test_exception_is_instance_of_exception(self):
        """CircuitBreakerOpen should be an instance of Exception."""
        exc = CircuitBreakerOpen("Test message")
        assert isinstance(exc, Exception)

    def test_exception_with_custom_message(self):
        """CircuitBreakerOpen should preserve custom message."""
        message = "Circuit open: service unavailable after 5 failures"
        exc = CircuitBreakerOpen(message)
        assert str(exc) == message

    def test_exception_can_be_used_in_try_except(self):
        """CircuitBreakerOpen should work in try-except blocks."""
        try:
            raise CircuitBreakerOpen("Circuit tripped")
        except CircuitBreakerOpen as e:
            assert "Circuit tripped" in str(e)


class TestRateLimitError:
    """Test suite for RateLimitError exception."""

    def test_exception_with_message_only(self):
        """RateLimitError should work with message only."""
        message = "Rate limit error occurred"
        exc = RateLimitError(message)

        assert str(exc) == message
        assert exc.response is None

    def test_exception_with_response(self):
        """RateLimitError should store response object."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 403
        mock_response.url = "https://api.example.com/data"

        message = "Rate limit hit: HTTP 403"
        exc = RateLimitError(message, response=mock_response)

        assert str(exc) == message
        assert exc.response == mock_response
        assert exc.response.status_code == 403

    def test_exception_is_instance_of_exception(self):
        """RateLimitError should be an instance of Exception."""
        exc = RateLimitError("Test message")
        assert isinstance(exc, Exception)

    def test_exception_can_be_raised_and_caught(self):
        """RateLimitError should be a standard exception."""
        with pytest.raises(RateLimitError) as exc_info:
            raise RateLimitError("Rate limit detected")

        assert str(exc_info.value) == "Rate limit detected"

    def test_exception_response_can_be_accessed(self):
        """RateLimitError response should be accessible after catching."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 403
        mock_response.headers = {"X-RateLimit-Remaining": "0"}

        try:
            raise RateLimitError("Rate limit hit", response=mock_response)
        except RateLimitError as e:
            assert e.response is not None
            assert e.response.status_code == 403
            assert e.response.headers["X-RateLimit-Remaining"] == "0"

    def test_exception_without_response_has_none(self):
        """RateLimitError without response should have None."""
        exc = RateLimitError("Rate limit error")
        assert exc.response is None

    def test_exception_with_none_response_explicit(self):
        """RateLimitError with explicit None response should work."""
        exc = RateLimitError("Rate limit error", response=None)
        assert exc.response is None

    def test_exception_preserves_response_attributes(self):
        """RateLimitError should preserve all response attributes."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 403
        mock_response.url = "https://api.example.com/endpoint"
        mock_response.text = "Forbidden: Rate limit exceeded"
        mock_response.headers = {
            "X-RateLimit-Limit": "100",
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": "1234567890",
        }

        exc = RateLimitError("Rate limit hit", response=mock_response)

        assert exc.response.status_code == 403
        assert str(exc.response.url) == "https://api.example.com/endpoint"
        assert exc.response.text == "Forbidden: Rate limit exceeded"
        assert exc.response.headers["X-RateLimit-Limit"] == "100"
        assert exc.response.headers["X-RateLimit-Remaining"] == "0"
        assert exc.response.headers["X-RateLimit-Reset"] == "1234567890"


class TestExceptionHierarchy:
    """Test suite for exception inheritance and hierarchy."""

    def test_all_exceptions_inherit_from_exception(self):
        """All custom exceptions should inherit from Exception."""
        assert issubclass(RateLimitExceeded, Exception)
        assert issubclass(CircuitBreakerOpen, Exception)
        assert issubclass(RateLimitError, Exception)

    def test_exceptions_are_distinct_types(self):
        """Each exception should be a distinct type."""
        exc1 = RateLimitExceeded("message")
        exc2 = CircuitBreakerOpen("message")
        exc3 = RateLimitError("message")

        assert type(exc1) is not type(exc2)
        assert type(exc1) is not type(exc3)
        assert type(exc2) is not type(exc3)

    def test_can_catch_specific_exception_types(self):
        """Should be able to catch specific exception types."""
        # Test RateLimitExceeded
        try:
            raise RateLimitExceeded("rate limit")
        except CircuitBreakerOpen:
            pytest.fail("Should not catch CircuitBreakerOpen")
        except RateLimitExceeded:
            pass  # Expected

        # Test CircuitBreakerOpen
        try:
            raise CircuitBreakerOpen("circuit open")
        except RateLimitExceeded:
            pytest.fail("Should not catch RateLimitExceeded")
        except CircuitBreakerOpen:
            pass  # Expected

        # Test RateLimitError
        try:
            raise RateLimitError("rate limit error")
        except RateLimitExceeded:
            pytest.fail("Should not catch RateLimitExceeded")
        except CircuitBreakerOpen:
            pytest.fail("Should not catch CircuitBreakerOpen")
        except RateLimitError:
            pass  # Expected

    def test_can_catch_all_as_generic_exception(self):
        """All custom exceptions should be catchable as Exception."""
        exceptions = [
            RateLimitExceeded("message"),
            CircuitBreakerOpen("message"),
            RateLimitError("message"),
        ]

        for exc in exceptions:
            try:
                raise exc
            except Exception:
                pass  # Expected - all should be caught
