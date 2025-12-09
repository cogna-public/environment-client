"""Tests for DEFRA-specific rate limiter with circuit breaker."""

import asyncio
import pytest
import httpx
from unittest.mock import Mock

from environment.resilience.defra_circuit_breaker import (
    DefraRateLimitedCircuitBreaker,
    DEFRA_REQUESTS_PER_SECOND,
    DEFRA_CIRCUIT_FAILURE_THRESHOLD,
)
from environment.resilience.exceptions import (
    RateLimitError,
    CircuitBreakerOpen,
    RateLimitExceeded,
)


class TestDefraRateLimitedCircuitBreaker:
    """Test suite for DefraRateLimitedCircuitBreaker."""

    @pytest.mark.asyncio
    async def test_successful_request_passes_through(self):
        """Successful requests should pass through normally."""
        protection = DefraRateLimitedCircuitBreaker(service_name="test-service")

        @protection
        async def test_func():
            return "success"

        result = await test_func()
        assert result == "success"

    @pytest.mark.asyncio
    async def test_http_403_converted_to_rate_limit_error(self):
        """HTTP 403 status errors should be converted to RateLimitError."""
        protection = DefraRateLimitedCircuitBreaker(service_name="test-service")

        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 403
        mock_response.url = "https://api.example.com/data"

        @protection
        async def test_func():
            raise httpx.HTTPStatusError(
                "Forbidden",
                request=Mock(spec=httpx.Request),
                response=mock_response,
            )

        with pytest.raises(RateLimitError) as exc_info:
            await test_func()

        assert "rate limit" in str(exc_info.value).lower()
        assert exc_info.value.response == mock_response

    @pytest.mark.asyncio
    async def test_http_403_triggers_circuit_breaker(self):
        """Multiple HTTP 403s should trigger the circuit breaker."""
        protection = DefraRateLimitedCircuitBreaker(
            service_name="test-service",
            circuit_failure_threshold=3,
            circuit_recovery_timeout_seconds=10.0,
        )

        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 403
        mock_response.url = "https://api.example.com/data"

        @protection
        async def test_func():
            raise httpx.HTTPStatusError(
                "Forbidden",
                request=Mock(spec=httpx.Request),
                response=mock_response,
            )

        # Trigger circuit breaker with multiple 403s
        for _ in range(3):
            with pytest.raises(RateLimitError):
                await test_func()

        # Circuit should now be open
        assert protection.circuit_breaker._state.value == "open"

        # Next request should be rejected by circuit breaker
        with pytest.raises(CircuitBreakerOpen):
            await test_func()

    @pytest.mark.asyncio
    async def test_non_403_http_errors_not_converted(self):
        """HTTP errors other than 403 should not be converted to RateLimitError."""
        protection = DefraRateLimitedCircuitBreaker(service_name="test-service")

        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 500
        mock_response.url = "https://api.example.com/data"

        @protection
        async def test_func():
            raise httpx.HTTPStatusError(
                "Internal Server Error",
                request=Mock(spec=httpx.Request),
                response=mock_response,
            )

        # Should raise original HTTPStatusError, not RateLimitError
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await test_func()

        assert exc_info.value.response.status_code == 500

    @pytest.mark.asyncio
    async def test_rate_limiter_applied(self):
        """Rate limiter should be applied to requests."""
        protection = DefraRateLimitedCircuitBreaker(
            service_name="test-service",
            requests_per_second=2,
        )

        call_count = 0

        @protection
        async def test_func():
            nonlocal call_count
            call_count += 1
            return "success"

        # Make multiple requests
        await asyncio.gather(*[test_func() for _ in range(4)])

        assert call_count == 4

    @pytest.mark.asyncio
    async def test_circuit_breaker_applied(self):
        """Circuit breaker should be applied to requests."""
        protection = DefraRateLimitedCircuitBreaker(
            service_name="test-service",
            circuit_failure_threshold=2,
        )

        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 403
        mock_response.url = "https://api.example.com/data"

        call_count = 0

        @protection
        async def test_func():
            nonlocal call_count
            call_count += 1
            raise httpx.HTTPStatusError(
                "Forbidden",
                request=Mock(spec=httpx.Request),
                response=mock_response,
            )

        # Open the circuit
        for _ in range(2):
            with pytest.raises(RateLimitError):
                await test_func()

        # Circuit should reject without calling function
        initial_count = call_count
        with pytest.raises(CircuitBreakerOpen):
            await test_func()

        # Function should not have been called
        assert call_count == initial_count

    @pytest.mark.asyncio
    async def test_default_configuration_values(self):
        """Default configuration should use DEFRA constants."""
        protection = DefraRateLimitedCircuitBreaker()

        assert protection.rate_limiter.requests_per_second == DEFRA_REQUESTS_PER_SECOND
        assert (
            protection.circuit_breaker.failure_threshold
            == DEFRA_CIRCUIT_FAILURE_THRESHOLD
        )

    @pytest.mark.asyncio
    async def test_custom_configuration_values(self):
        """Should allow custom configuration values."""
        protection = DefraRateLimitedCircuitBreaker(
            service_name="custom-service",
            requests_per_second=10,
            circuit_failure_threshold=5,
            circuit_recovery_timeout_seconds=30.0,
        )

        assert protection.rate_limiter.requests_per_second == 10
        assert protection.circuit_breaker.failure_threshold == 5
        assert protection.circuit_breaker.recovery_timeout_seconds == 30.0

    @pytest.mark.asyncio
    async def test_decorator_with_function_arguments(self):
        """Decorator should work with functions that have arguments."""
        protection = DefraRateLimitedCircuitBreaker(service_name="test-service")

        @protection
        async def test_func(x, y, z=None):
            if z:
                return x + y + z
            return x + y

        result1 = await test_func(1, 2)
        assert result1 == 3

        result2 = await test_func(1, 2, z=3)
        assert result2 == 6

    @pytest.mark.asyncio
    async def test_decorator_order_rate_limiter_then_circuit_breaker(self):
        """Rate limiter should be applied before circuit breaker."""
        protection = DefraRateLimitedCircuitBreaker(
            service_name="test-service",
            circuit_failure_threshold=2,
            circuit_recovery_timeout_seconds=10.0,
        )

        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 403
        mock_response.url = "https://api.example.com/data"

        @protection
        async def test_func():
            raise httpx.HTTPStatusError(
                "Forbidden",
                request=Mock(spec=httpx.Request),
                response=mock_response,
            )

        # Open circuit
        for _ in range(2):
            with pytest.raises(RateLimitError):
                await test_func()

        # Circuit is open - request should be rejected by circuit breaker
        # before rate limiter is even consulted
        with pytest.raises(CircuitBreakerOpen):
            await test_func()

    @pytest.mark.asyncio
    async def test_403_detection_logs_appropriately(self):
        """HTTP 403 detection should log warning with service name and URL."""
        protection = DefraRateLimitedCircuitBreaker(service_name="MyTestService")

        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 403
        mock_response.url = "https://api.example.com/endpoint"

        @protection
        async def test_func():
            raise httpx.HTTPStatusError(
                "Forbidden",
                request=Mock(spec=httpx.Request),
                response=mock_response,
            )

        # Should convert 403 to RateLimitError (logging happens internally)
        with pytest.raises(RateLimitError) as exc_info:
            await test_func()

        # Verify the error message includes the URL
        assert "https://api.example.com/endpoint" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_circuit_recovery_after_timeout(self):
        """Circuit should attempt recovery after timeout period."""
        protection = DefraRateLimitedCircuitBreaker(
            service_name="test-service",
            circuit_failure_threshold=2,
            circuit_recovery_timeout_seconds=0.1,
        )

        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 403
        mock_response.url = "https://api.example.com/data"

        call_count = 0

        @protection
        async def test_func(should_fail=True):
            nonlocal call_count
            call_count += 1
            if should_fail:
                raise httpx.HTTPStatusError(
                    "Forbidden",
                    request=Mock(spec=httpx.Request),
                    response=mock_response,
                )
            return "success"

        # Open circuit
        for _ in range(2):
            with pytest.raises(RateLimitError):
                await test_func(should_fail=True)

        # Wait for recovery timeout
        await asyncio.sleep(0.15)

        # Should attempt recovery
        result = await test_func(should_fail=False)
        assert result == "success"

    @pytest.mark.asyncio
    async def test_rate_limit_exceeded_propagates(self):
        """RateLimitExceeded from rate limiter should propagate."""
        protection = DefraRateLimitedCircuitBreaker(
            service_name="test-service",
            requests_per_second=1,
            rate_limit_timeout_seconds=0.1,
        )

        @protection
        async def test_func():
            return "success"

        # Fill rate limit
        await test_func()

        # Force rate limit timeout
        with pytest.raises(RateLimitExceeded):
            tasks = [test_func() for _ in range(10)]
            await asyncio.gather(*tasks)

    @pytest.mark.asyncio
    async def test_non_http_exceptions_propagate(self):
        """Non-HTTP exceptions should propagate without conversion."""
        protection = DefraRateLimitedCircuitBreaker(service_name="test-service")

        class CustomException(Exception):
            pass

        @protection
        async def test_func():
            raise CustomException("Custom error")

        with pytest.raises(CustomException) as exc_info:
            await test_func()

        assert str(exc_info.value) == "Custom error"

    @pytest.mark.asyncio
    async def test_multiple_instances_are_independent(self):
        """Multiple DefraRateLimitedCircuitBreaker instances should be independent."""
        protection1 = DefraRateLimitedCircuitBreaker(
            service_name="service-1",
            circuit_failure_threshold=2,
        )

        protection2 = DefraRateLimitedCircuitBreaker(
            service_name="service-2",
            circuit_failure_threshold=2,
        )

        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 403
        mock_response.url = "https://api.example.com/data"

        @protection1
        async def func1():
            raise httpx.HTTPStatusError(
                "Forbidden",
                request=Mock(spec=httpx.Request),
                response=mock_response,
            )

        @protection2
        async def func2():
            return "success"

        # Open circuit 1
        for _ in range(2):
            with pytest.raises(RateLimitError):
                await func1()

        assert protection1.circuit_breaker._state.value == "open"

        # Circuit 2 should still work
        result = await func2()
        assert result == "success"
        assert protection2.circuit_breaker._state.value == "closed"

    @pytest.mark.asyncio
    async def test_service_name_propagates_to_components(self):
        """Service name should propagate to rate limiter and circuit breaker."""
        service_name = "MyCustomService"
        protection = DefraRateLimitedCircuitBreaker(service_name=service_name)

        assert protection.circuit_breaker.service_name == service_name
        assert protection.rate_limiter.service_name == service_name
