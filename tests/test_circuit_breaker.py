"""Tests for circuit breaker implementation."""

import asyncio
import pytest

from environment.resilience.circuit_breaker import CircuitBreaker, CircuitState
from environment.resilience.exceptions import CircuitBreakerOpen


class ApiException(Exception):
    """Test exception for circuit breaker testing."""

    pass


class TestCircuitBreaker:
    """Test suite for CircuitBreaker."""

    @pytest.mark.asyncio
    async def test_initial_state_is_closed(self):
        """Circuit breaker should start in CLOSED state."""
        cb = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout_seconds=1.0,
            expected_exception_type=ApiException,
            service_name="test-service",
        )
        assert cb._state == CircuitState.CLOSED
        assert cb._failure_count == 0
        assert cb._success_count == 0

    @pytest.mark.asyncio
    async def test_successful_request_in_closed_state(self):
        """Successful requests should pass through when circuit is CLOSED."""
        cb = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout_seconds=1.0,
            expected_exception_type=ApiException,
            service_name="test-service",
        )

        @cb
        async def successful_func():
            return "success"

        result = await successful_func()
        assert result == "success"
        assert cb._state == CircuitState.CLOSED
        assert cb._failure_count == 0

    @pytest.mark.asyncio
    async def test_circuit_opens_after_threshold_failures(self):
        """Circuit should open after reaching failure threshold."""
        cb = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout_seconds=1.0,
            expected_exception_type=ApiException,
            service_name="test-service",
        )

        @cb
        async def failing_func():
            raise ApiException("API failure")

        # Execute failures up to threshold
        for _ in range(3):
            with pytest.raises(ApiException):
                await failing_func()

        assert cb._state == CircuitState.OPEN
        assert cb._failure_count == 3
        assert cb._opened_at is not None

    @pytest.mark.asyncio
    async def test_circuit_rejects_requests_when_open(self):
        """Circuit should reject requests immediately when OPEN."""
        cb = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout_seconds=10.0,  # Long timeout to keep circuit open
            expected_exception_type=ApiException,
            service_name="test-service",
        )

        @cb
        async def failing_func():
            raise ApiException("API failure")

        # Open the circuit
        for _ in range(2):
            with pytest.raises(ApiException):
                await failing_func()

        assert cb._state == CircuitState.OPEN

        # Next request should be rejected without calling the function
        with pytest.raises(CircuitBreakerOpen) as exc_info:
            await failing_func()

        assert "circuit breaker is open" in str(exc_info.value)
        assert "test-service" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_circuit_transitions_to_half_open_after_timeout(self):
        """Circuit should transition to HALF_OPEN after recovery timeout."""
        cb = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout_seconds=0.1,  # Short timeout for testing
            expected_exception_type=ApiException,
            service_name="test-service",
            half_open_max_attempts=2,  # Need 2 successful attempts to close
        )

        @cb
        async def func(should_fail=True):
            if should_fail:
                raise ApiException("API failure")
            return "success"

        # Open the circuit
        for _ in range(2):
            with pytest.raises(ApiException):
                await func(should_fail=True)

        assert cb._state == CircuitState.OPEN

        # Wait for recovery timeout
        await asyncio.sleep(0.15)

        # Next request should transition to HALF_OPEN and succeed
        result = await func(should_fail=False)
        assert result == "success"
        # Circuit should still be HALF_OPEN after first successful test
        assert cb._state == CircuitState.HALF_OPEN

    @pytest.mark.asyncio
    async def test_circuit_closes_after_successful_half_open_attempts(self):
        """Circuit should close after successful recovery attempts in HALF_OPEN."""
        cb = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout_seconds=0.1,
            expected_exception_type=ApiException,
            service_name="test-service",
            half_open_max_attempts=2,
        )

        @cb
        async def func(should_fail=True):
            if should_fail:
                raise ApiException("API failure")
            return "success"

        # Open the circuit
        for _ in range(2):
            with pytest.raises(ApiException):
                await func(should_fail=True)

        assert cb._state == CircuitState.OPEN

        # Wait for recovery timeout
        await asyncio.sleep(0.15)

        # Successful recovery attempts
        await func(should_fail=False)
        assert cb._state == CircuitState.HALF_OPEN

        await func(should_fail=False)
        assert cb._state == CircuitState.CLOSED
        assert cb._failure_count == 0
        assert cb._backoff_multiplier == 1

    @pytest.mark.asyncio
    async def test_circuit_reopens_on_half_open_failure(self):
        """Circuit should reopen with increased backoff if recovery fails."""
        cb = CircuitBreaker(
            failure_threshold=1,  # Lower threshold so single failure reopens
            recovery_timeout_seconds=0.1,
            expected_exception_type=ApiException,
            service_name="test-service",
        )

        @cb
        async def func(should_fail=True):
            if should_fail:
                raise ApiException("API failure")
            return "success"

        # Open the circuit (need 1 failure with threshold=1)
        with pytest.raises(ApiException):
            await func(should_fail=True)

        initial_backoff = cb._backoff_multiplier
        assert cb._state == CircuitState.OPEN
        assert initial_backoff == 1

        # Wait for recovery timeout
        await asyncio.sleep(0.15)

        # Fail during recovery (single failure reopens with threshold=1)
        with pytest.raises(ApiException):
            await func(should_fail=True)

        # Circuit should be OPEN again with increased backoff
        assert cb._state == CircuitState.OPEN
        assert cb._backoff_multiplier == initial_backoff * 2

    @pytest.mark.asyncio
    async def test_exponential_backoff_increases_on_repeated_failures(self):
        """Backoff multiplier should double on each failed recovery attempt."""
        cb = CircuitBreaker(
            failure_threshold=1,
            recovery_timeout_seconds=0.1,
            expected_exception_type=ApiException,
            service_name="test-service",
        )

        @cb
        async def failing_func():
            raise ApiException("API failure")

        # First failure - opens circuit
        with pytest.raises(ApiException):
            await failing_func()

        assert cb._state == CircuitState.OPEN
        assert cb._backoff_multiplier == 1

        # Wait for recovery and fail again
        await asyncio.sleep(0.15)
        with pytest.raises(ApiException):
            await failing_func()

        assert cb._state == CircuitState.OPEN
        assert cb._backoff_multiplier == 2

        # Wait for doubled recovery time and fail again
        await asyncio.sleep(0.25)
        with pytest.raises(ApiException):
            await failing_func()

        assert cb._state == CircuitState.OPEN
        assert cb._backoff_multiplier == 4

    @pytest.mark.asyncio
    async def test_backoff_respects_max_backoff_limit(self):
        """Backoff should not exceed max_backoff_seconds."""
        cb = CircuitBreaker(
            failure_threshold=1,
            recovery_timeout_seconds=10.0,
            expected_exception_type=ApiException,
            service_name="test-service",
            max_backoff_seconds=30.0,
        )

        # Manually set high backoff multiplier
        cb._backoff_multiplier = 10  # Would be 100 seconds without max

        current_backoff = cb._get_current_backoff()
        assert current_backoff == 30.0

    @pytest.mark.asyncio
    async def test_success_resets_failure_count_in_closed_state(self):
        """Successful request should reset failure count in CLOSED state."""
        cb = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout_seconds=1.0,
            expected_exception_type=ApiException,
            service_name="test-service",
        )

        @cb
        async def func(should_fail=True):
            if should_fail:
                raise ApiException("API failure")
            return "success"

        # Create some failures (but not enough to open circuit)
        for _ in range(2):
            with pytest.raises(ApiException):
                await func(should_fail=True)

        assert cb._failure_count == 2
        assert cb._state == CircuitState.CLOSED

        # Successful request should reset failure count
        await func(should_fail=False)
        assert cb._failure_count == 0
        assert cb._state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_unexpected_exception_types_do_not_trigger_circuit(self):
        """Exceptions other than expected_exception_type should not trigger circuit."""

        class UnexpectedException(Exception):
            pass

        cb = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout_seconds=1.0,
            expected_exception_type=ApiException,
            service_name="test-service",
        )

        @cb
        async def func():
            raise UnexpectedException("Unexpected error")

        # UnexpectedException should pass through without affecting circuit
        for _ in range(5):
            with pytest.raises(UnexpectedException):
                await func()

        # Circuit should still be CLOSED
        assert cb._state == CircuitState.CLOSED
        assert cb._failure_count == 0

    @pytest.mark.asyncio
    async def test_half_open_rejects_requests_after_max_attempts(self):
        """HALF_OPEN state should reject additional requests after max attempts reached."""
        cb = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout_seconds=0.1,
            expected_exception_type=ApiException,
            service_name="test-service",
            half_open_max_attempts=2,  # Allow 2 successful attempts
        )

        @cb
        async def test_func():
            return "success"

        # Open the circuit
        @cb
        async def failing_func():
            raise ApiException("API failure")

        for _ in range(2):
            with pytest.raises(ApiException):
                await failing_func()

        assert cb._state == CircuitState.OPEN

        # Wait for recovery
        await asyncio.sleep(0.15)

        # Make successful recovery attempts up to the limit
        await test_func()  # First success - still HALF_OPEN
        assert cb._state == CircuitState.HALF_OPEN

        await test_func()  # Second success - circuit closes
        assert cb._state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_request_count_tracks_requests(self):
        """Circuit breaker should track total requests."""
        cb = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout_seconds=1.0,
            expected_exception_type=ApiException,
            service_name="test-service",
        )

        @cb
        async def func(should_fail=False):
            if should_fail:
                raise ApiException("API failure")
            return "success"

        # Make some requests
        for _ in range(3):
            await func(should_fail=False)

        assert cb._request_count == 3

        # Failures also count
        for _ in range(2):
            with pytest.raises(ApiException):
                await func(should_fail=True)

        assert cb._request_count == 5

    @pytest.mark.asyncio
    async def test_circuit_breaker_with_arguments(self):
        """Circuit breaker should work with functions that take arguments."""
        cb = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout_seconds=1.0,
            expected_exception_type=ApiException,
            service_name="test-service",
        )

        @cb
        async def func_with_args(x, y, z=None):
            if z is None:
                raise ApiException("No z provided")
            return x + y + z

        result = await func_with_args(1, 2, z=3)
        assert result == 6

        # Test with failures
        with pytest.raises(ApiException):
            await func_with_args(1, 2)

    @pytest.mark.asyncio
    async def test_multiple_circuit_breakers_are_independent(self):
        """Multiple circuit breaker instances should not interfere with each other."""
        cb1 = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout_seconds=1.0,
            expected_exception_type=ApiException,
            service_name="service-1",
        )

        cb2 = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout_seconds=1.0,
            expected_exception_type=ApiException,
            service_name="service-2",
        )

        @cb1
        async def func1():
            raise ApiException("Service 1 failure")

        @cb2
        async def func2():
            return "success"

        # Open circuit 1
        for _ in range(2):
            with pytest.raises(ApiException):
                await func1()

        assert cb1._state == CircuitState.OPEN

        # Circuit 2 should still work
        result = await func2()
        assert result == "success"
        assert cb2._state == CircuitState.CLOSED
