"""Tests for API rate limiter implementation."""

import asyncio
import pytest
import time

from environment.resilience.rate_limiter import ApiRateLimiter
from environment.resilience.exceptions import RateLimitExceeded


class CustomRateLimitException(RateLimitExceeded):
    """Custom rate limit exception for testing."""

    pass


class TestApiRateLimiter:
    """Test suite for ApiRateLimiter."""

    @pytest.mark.asyncio
    async def test_rate_limiter_allows_requests_within_limit(self):
        """Rate limiter should allow requests within the rate limit."""
        limiter = ApiRateLimiter(
            requests_per_second=10,
            timeout_seconds=5.0,
            retry_delay_seconds=0.1,
            service_name="test-service",
        )

        @limiter
        async def test_func():
            return "success"

        # Should complete without errors
        result = await test_func()
        assert result == "success"

    @pytest.mark.asyncio
    async def test_rate_limiter_enforces_rate_limit(self):
        """Rate limiter should enforce the specified rate limit."""
        limiter = ApiRateLimiter(
            requests_per_second=2,
            timeout_seconds=5.0,
            retry_delay_seconds=0.1,
            service_name="test-service",
        )

        call_times = []

        @limiter
        async def test_func():
            call_times.append(time.time())
            return "success"

        # Make 5 requests - with 2 req/s this should take at least 2 seconds
        await asyncio.gather(*[test_func() for _ in range(5)])

        # All requests should complete
        assert len(call_times) == 5

        # Calculate time span
        time_span = call_times[-1] - call_times[0]

        # Should take at least 1.5 seconds for 5 requests at 2 req/s
        # (allowing some tolerance for timing variations)
        assert time_span >= 1.0

    @pytest.mark.asyncio
    async def test_rate_limiter_timeout_raises_exception(self):
        """Rate limiter should raise exception when timeout is exceeded."""
        limiter = ApiRateLimiter(
            requests_per_second=1,
            timeout_seconds=0.2,  # Very short timeout
            retry_delay_seconds=0.05,
            service_name="test-service",
        )

        @limiter
        async def test_func():
            return "success"

        # Fill the rate limit
        await test_func()

        # Next request should timeout while waiting for rate limit slot
        with pytest.raises(RateLimitExceeded) as exc_info:
            # Create many concurrent requests to exceed the rate limit
            tasks = [test_func() for _ in range(5)]
            await asyncio.gather(*tasks)

        assert "test-service" in str(exc_info.value)
        assert "rate limit exceeded" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_rate_limiter_retries_with_delay(self):
        """Rate limiter should retry with specified delay when rate limited."""
        limiter = ApiRateLimiter(
            requests_per_second=2,
            timeout_seconds=2.0,
            retry_delay_seconds=0.1,
            service_name="test-service",
        )

        execution_count = 0

        @limiter
        async def test_func():
            nonlocal execution_count
            execution_count += 1
            return "success"

        # Make 3 requests - third should wait for rate limit slot
        start_time = time.time()
        await asyncio.gather(*[test_func() for _ in range(3)])
        elapsed = time.time() - start_time

        assert execution_count == 3
        # Should take at least 0.5 seconds for 3 requests at 2 req/s
        assert elapsed >= 0.4

    @pytest.mark.asyncio
    async def test_rate_limiter_with_custom_exception_class(self):
        """Rate limiter should use custom exception class when specified."""
        limiter = ApiRateLimiter(
            requests_per_second=1,
            timeout_seconds=0.1,
            retry_delay_seconds=0.05,
            service_name="test-service",
            exception_class=CustomRateLimitException,
        )

        @limiter
        async def test_func():
            return "success"

        # Fill the rate limit
        await test_func()

        # Next request should timeout with custom exception
        with pytest.raises(CustomRateLimitException):
            tasks = [test_func() for _ in range(5)]
            await asyncio.gather(*tasks)

    @pytest.mark.asyncio
    async def test_rate_limiter_with_function_arguments(self):
        """Rate limiter should work with functions that have arguments."""
        limiter = ApiRateLimiter(
            requests_per_second=10,
            timeout_seconds=5.0,
            retry_delay_seconds=0.1,
            service_name="test-service",
        )

        @limiter
        async def test_func(x, y, z=None):
            if z:
                return x + y + z
            return x + y

        result1 = await test_func(1, 2)
        assert result1 == 3

        result2 = await test_func(1, 2, z=3)
        assert result2 == 6

    @pytest.mark.asyncio
    async def test_rate_limiter_allows_errors_to_propagate(self):
        """Rate limiter should not interfere with function exceptions."""
        limiter = ApiRateLimiter(
            requests_per_second=10,
            timeout_seconds=5.0,
            retry_delay_seconds=0.1,
            service_name="test-service",
        )

        class CustomError(Exception):
            pass

        @limiter
        async def failing_func():
            raise CustomError("Test error")

        with pytest.raises(CustomError) as exc_info:
            await failing_func()

        assert str(exc_info.value) == "Test error"

    @pytest.mark.asyncio
    async def test_multiple_rate_limiters_are_independent(self):
        """Multiple rate limiter instances should not interfere with each other."""
        limiter1 = ApiRateLimiter(
            requests_per_second=2,
            timeout_seconds=5.0,
            retry_delay_seconds=0.1,
            service_name="service-1",
        )

        limiter2 = ApiRateLimiter(
            requests_per_second=2,
            timeout_seconds=5.0,
            retry_delay_seconds=0.1,
            service_name="service-2",
        )

        count1 = 0
        count2 = 0

        @limiter1
        async def func1():
            nonlocal count1
            count1 += 1
            return "service1"

        @limiter2
        async def func2():
            nonlocal count2
            count2 += 1
            return "service2"

        # Each limiter should independently allow 2 requests quickly
        await asyncio.gather(func1(), func1(), func2(), func2())

        assert count1 == 2
        assert count2 == 2

    @pytest.mark.asyncio
    async def test_rate_limiter_identifier_uses_service_name(self):
        """Rate limiter should use service name for identifier."""
        limiter = ApiRateLimiter(
            requests_per_second=5,
            timeout_seconds=5.0,
            retry_delay_seconds=0.1,
            service_name="MyTestService",
        )

        # Identifier should be lowercase service name + suffix
        assert limiter._identifier == "mytestservice-api"

    @pytest.mark.asyncio
    async def test_concurrent_requests_respect_rate_limit(self):
        """Concurrent requests should all respect the rate limit."""
        limiter = ApiRateLimiter(
            requests_per_second=2,
            timeout_seconds=5.0,
            retry_delay_seconds=0.1,
            service_name="test-service",
        )

        completed_times = []

        @limiter
        async def test_func():
            completed_times.append(time.time())
            return "success"

        # Launch 5 concurrent requests
        start_time = time.time()
        results = await asyncio.gather(*[test_func() for _ in range(5)])

        assert len(results) == 5
        assert all(r == "success" for r in results)

        # Should take at least 1.5 seconds for 5 requests at 2 req/s
        total_time = time.time() - start_time
        assert total_time >= 1.0  # Allow some tolerance

    @pytest.mark.asyncio
    async def test_rate_limiter_timeout_error_message(self):
        """Rate limiter timeout error should include helpful details."""
        limiter = ApiRateLimiter(
            requests_per_second=1,
            timeout_seconds=0.15,
            retry_delay_seconds=0.05,
            service_name="MyService",
        )

        @limiter
        async def test_func():
            return "success"

        # Fill the rate limit
        await test_func()

        # Force timeout
        with pytest.raises(RateLimitExceeded) as exc_info:
            tasks = [test_func() for _ in range(10)]
            await asyncio.gather(*tasks)

        error_message = str(exc_info.value)
        assert "MyService" in error_message
        assert "0.15" in error_message  # timeout value
        assert "rate limit" in error_message.lower()
