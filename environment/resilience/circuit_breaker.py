"""
Circuit breaker for handling API failures and preventing cascade failures.

Implements the circuit breaker pattern to detect failures, open the circuit,
and allow gradual recovery with exponential backoff.
"""

import asyncio
import time
from enum import Enum
from functools import wraps
from typing import Any, Callable, Optional
import structlog

from .exceptions import CircuitBreakerOpen

logger = structlog.get_logger(__name__)


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """
    Generic circuit breaker for preventing cascade failures.

    When failures exceed a threshold, the circuit opens and rejects requests
    until a cooldown period expires. Then it enters half-open state to test recovery.
    """

    def __init__(
        self,
        failure_threshold: int,
        recovery_timeout_seconds: float,
        expected_exception_type: type[Exception],
        service_name: str,
        half_open_max_attempts: int = 1,
        max_backoff_seconds: float = 300.0,  # 5 minutes max
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of consecutive failures before opening circuit
            recovery_timeout_seconds: Initial time to wait before attempting recovery
            expected_exception_type: Exception type that should trigger circuit breaking
            service_name: Name of the service for logging
            half_open_max_attempts: Number of test requests allowed in half-open state
            max_backoff_seconds: Maximum backoff time (caps exponential growth)
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout_seconds = recovery_timeout_seconds
        self.expected_exception_type = expected_exception_type
        self.service_name = service_name
        self.half_open_max_attempts = half_open_max_attempts
        self.max_backoff_seconds = max_backoff_seconds

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._request_count = 0  # Total requests in current window
        self._opened_at: Optional[float] = None
        self._backoff_multiplier = 1  # Exponential backoff multiplier
        self._lock = asyncio.Lock()

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Decorator to apply circuit breaker to async functions.

        Example:
            circuit_breaker = CircuitBreaker(...)

            @circuit_breaker
            async def my_api_call():
                return await client.get(...)
        """

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await self._call_with_circuit(func, *args, **kwargs)

        return wrapper

    async def _call_with_circuit(
        self, func: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> Any:
        """
        Execute function with circuit breaker protection.

        Args:
            func: Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            Result from the function

        Raises:
            CircuitBreakerOpen: If circuit is open and not ready for retry
            Exception: Original exception from the function
        """
        await self._check_circuit_state_before_request()

        self._request_count += 1

        try:
            result = await func(*args, **kwargs)
            await self._handle_request_success()
            return result

        except Exception as e:
            if not isinstance(e, self.expected_exception_type):
                raise

            await self._handle_request_failure(e)
            raise

    async def _check_circuit_state_before_request(self) -> None:
        """Check circuit state and determine if request should proceed."""
        async with self._lock:
            if self._state == CircuitState.OPEN:
                if self._should_attempt_recovery():
                    self._half_open_circuit()
                else:
                    self._reject_request_circuit_open()

            if self._state == CircuitState.HALF_OPEN:
                if self._success_count >= self.half_open_max_attempts:
                    self._reject_request_half_open_limit()

    async def _handle_request_success(self) -> None:
        """Handle successful request and update circuit state accordingly."""
        async with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.half_open_max_attempts:
                    self._close_circuit()

            elif self._state == CircuitState.CLOSED and self._failure_count > 0:
                logger.debug(
                    f"{self.service_name} circuit breaker reset after success",
                    service=self.service_name,
                    previous_failures=self._failure_count,
                )
                self._failure_count = 0

    async def _handle_request_failure(self, exception: Exception) -> None:
        """Handle request failure and potentially open the circuit."""
        async with self._lock:
            self._failure_count += 1

            logger.warning(
                f"{self.service_name} circuit breaker recorded failure",
                service=self.service_name,
                failure_count=self._failure_count,
                threshold=self.failure_threshold,
                exception_type=type(exception).__name__,
                state=self._state.value,
                requests_before_failure=self._request_count,
            )

            if self._failure_count >= self.failure_threshold:
                if self._state == CircuitState.HALF_OPEN:
                    self._backoff_multiplier *= 2
                    logger.error(
                        "Circuit breaker recovery failed, increasing backoff",
                        service=self.service_name,
                        backoff_multiplier=self._backoff_multiplier,
                        state=self._state.value,
                        failure_count=self._failure_count,
                        failure_threshold=self.failure_threshold,
                    )
                self._open_circuit()

    def _close_circuit(self) -> None:
        """Transition circuit to CLOSED state and reset all counters."""
        logger.info(
            f"{self.service_name} circuit breaker closed after successful recovery",
            service=self.service_name,
            test_requests=self._success_count,
        )
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._request_count = 0
        self._opened_at = None
        self._backoff_multiplier = 1

    def _half_open_circuit(self) -> None:
        """Transition circuit to HALF_OPEN state to test recovery."""
        logger.info(
            f"{self.service_name} circuit breaker attempting recovery",
            service=self.service_name,
            state="half_open",
            backoff_multiplier=self._backoff_multiplier,
        )
        self._state = CircuitState.HALF_OPEN
        self._success_count = 0

    def _open_circuit(self) -> None:
        """Transition circuit to OPEN state after failure threshold reached."""
        logger.error(
            "Circuit breaker opened after failure threshold reached",
            service=self.service_name,
            failure_count=self._failure_count,
            failure_threshold=self.failure_threshold,
            requests_in_window=self._request_count,
            state="open",
            backoff_multiplier=self._backoff_multiplier,
            base_recovery_timeout_seconds=self.recovery_timeout_seconds,
        )
        self._state = CircuitState.OPEN
        self._opened_at = time.time()
        self._success_count = 0

    def _should_attempt_recovery(self) -> bool:
        """Check if enough time has passed to attempt circuit recovery."""
        if self._opened_at is None:
            return False
        elapsed = time.time() - self._opened_at
        return elapsed >= self._get_current_backoff()

    def _get_current_backoff(self) -> float:
        """Calculate current backoff time with exponential growth."""
        return min(
            self.recovery_timeout_seconds * self._backoff_multiplier,
            self.max_backoff_seconds,
        )

    def _reject_request_circuit_open(self) -> None:
        """Raise exception when circuit is open and not ready for recovery."""
        if self._opened_at is None:
            return

        elapsed = time.time() - self._opened_at
        current_backoff = self._get_current_backoff()

        logger.warning(
            f"{self.service_name} circuit breaker is open, rejecting request",
            service=self.service_name,
            failure_count=self._failure_count,
            elapsed_seconds=elapsed,
            current_backoff_seconds=current_backoff,
        )
        raise CircuitBreakerOpen(
            f"{self.service_name} circuit breaker is open. "
            f"Service is temporarily unavailable after {self._failure_count} failures. "
            f"Retry after {current_backoff - elapsed:.1f}s."
        )

    def _reject_request_half_open_limit(self) -> None:
        """Raise exception when half-open request limit is reached."""
        logger.warning(
            f"{self.service_name} circuit breaker half-open limit reached",
            service=self.service_name,
            success_count=self._success_count,
        )
        raise CircuitBreakerOpen(
            f"{self.service_name} circuit breaker is testing recovery. "
            "Please wait before retrying."
        )
