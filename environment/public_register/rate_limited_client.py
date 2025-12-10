"""
Rate-limited DEFRA Public Register Client with circuit breaker and retry logic.

Prevents 403 rate limit errors during bulk operations with automatic retry and circuit breaker protection.
"""

from __future__ import annotations

import asyncio
import json
import time
from enum import Enum
from functools import wraps
from typing import Any, Callable, Optional
import httpx
from tenacity import (
    retry,
    retry_if_not_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .client import PublicRegisterClient

# DEFRA retry configuration
DEFRA_MAX_RETRY_ATTEMPTS = 3
DEFRA_RETRY_MULTIPLIER = 1
DEFRA_RETRY_MIN_WAIT_SECONDS = 1
DEFRA_RETRY_MAX_WAIT_SECONDS = 10

# DEFRA rate limiting configuration
# Source: https://developer-portal.trade.defra.gov.uk/documentation/reference-guide#rate-limiting
DEFRA_REQUESTS_PER_SECOND = 5
DEFRA_RATE_LIMIT_TIMEOUT_SECONDS = 30.0
DEFRA_RATE_LIMIT_RETRY_DELAY_SECONDS = 0.2

# Circuit breaker configuration
DEFRA_CIRCUIT_FAILURE_THRESHOLD = 3
DEFRA_CIRCUIT_RECOVERY_TIMEOUT_SECONDS = 60.0
DEFRA_CIRCUIT_HALF_OPEN_MAX_ATTEMPTS = 1
DEFRA_CIRCUIT_MAX_BACKOFF_SECONDS = 300.0


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is open and request is rejected."""

    pass


class RateLimitError(Exception):
    """Raised when API rate limit is hit (e.g., HTTP 403)."""

    def __init__(self, message: str, response: httpx.Response | None = None):
        self.response = response
        super().__init__(message)


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
        max_backoff_seconds: float = 300.0,
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
        self._request_count = 0
        self._opened_at: Optional[float] = None
        self._backoff_multiplier = 1
        self._lock = asyncio.Lock()

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """Decorator to apply circuit breaker to async functions."""

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await self._call_with_circuit(func, *args, **kwargs)

        return wrapper

    async def _call_with_circuit(
        self, func: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> Any:
        """Execute function with circuit breaker protection."""
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
                self._failure_count = 0

    async def _handle_request_failure(self, exception: Exception) -> None:
        """Handle request failure and potentially open the circuit."""
        async with self._lock:
            self._failure_count += 1

            if self._failure_count >= self.failure_threshold:
                if self._state == CircuitState.HALF_OPEN:
                    self._backoff_multiplier *= 2
                self._open_circuit()

    def _close_circuit(self) -> None:
        """Transition circuit to CLOSED state and reset all counters."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._request_count = 0
        self._opened_at = None
        self._backoff_multiplier = 1

    def _half_open_circuit(self) -> None:
        """Transition circuit to HALF_OPEN state to test recovery."""
        self._state = CircuitState.HALF_OPEN
        self._success_count = 0

    def _open_circuit(self) -> None:
        """Transition circuit to OPEN state after failure threshold reached."""
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

        raise CircuitBreakerOpen(
            f"{self.service_name} circuit breaker is open. "
            f"Service is temporarily unavailable after {self._failure_count} failures. "
            f"Retry after {current_backoff - elapsed:.1f}s."
        )

    def _reject_request_half_open_limit(self) -> None:
        """Raise exception when half-open request limit is reached."""
        raise CircuitBreakerOpen(
            f"{self.service_name} circuit breaker is testing recovery. "
            "Please wait before retrying."
        )


class ApiRateLimiter:
    """
    Rate limiter for external API calls.

    Enforces request rate limits to prevent overwhelming external services
    and avoid 403 rate limiting errors during bulk operations.
    """

    def __init__(
        self,
        requests_per_second: int,
        timeout_seconds: float,
        retry_delay_seconds: float,
        service_name: str,
    ):
        """
        Initialize rate limiter.

        Args:
            requests_per_second: Maximum number of requests allowed per second
            timeout_seconds: Maximum time to wait for rate limit slot
            retry_delay_seconds: Delay between retry attempts when rate limited
            service_name: Name of the service for logging and error messages
        """
        self.requests_per_second = requests_per_second
        self.timeout_seconds = timeout_seconds
        self.retry_delay_seconds = retry_delay_seconds
        self.service_name = service_name

        # Simple implementation using asyncio semaphore and timing
        self._semaphore = asyncio.Semaphore(requests_per_second)
        self._last_request_times: list[float] = []

    async def _acquire_rate_limit_slot(self) -> None:
        """
        Acquire a rate limit slot, waiting and retrying if necessary.

        Raises:
            RuntimeError: If rate limit cannot be acquired within timeout period
        """
        start_time = time.time()

        while True:
            # Clean up old request times
            current_time = time.time()
            self._last_request_times = [
                t for t in self._last_request_times if current_time - t < 1.0
            ]

            # Check if we can make a request
            if len(self._last_request_times) < self.requests_per_second:
                self._last_request_times.append(current_time)
                return

            elapsed = time.time() - start_time
            if elapsed > self.timeout_seconds:
                raise RuntimeError(
                    f"{self.service_name} API rate limit exceeded - could not acquire slot within {self.timeout_seconds}s. "
                    "The service may be experiencing high load or rate limiting. Please try again later."
                )

            await asyncio.sleep(self.retry_delay_seconds)

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """Decorator to apply rate limiting to async functions."""

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            await self._acquire_rate_limit_slot()
            return await func(*args, **kwargs)

        return wrapper


class DefraRateLimitedCircuitBreaker:
    """
    DEFRA-specific rate limiter + circuit breaker that treats 403s as rate limit events.

    Combines rate limiting, circuit breaking, and HTTP 403 detection.
    """

    def __init__(
        self,
        service_name: str = "DEFRA",
        requests_per_second: int = DEFRA_REQUESTS_PER_SECOND,
        rate_limit_timeout_seconds: float = DEFRA_RATE_LIMIT_TIMEOUT_SECONDS,
        rate_limit_retry_delay_seconds: float = DEFRA_RATE_LIMIT_RETRY_DELAY_SECONDS,
        circuit_failure_threshold: int = DEFRA_CIRCUIT_FAILURE_THRESHOLD,
        circuit_recovery_timeout_seconds: float = DEFRA_CIRCUIT_RECOVERY_TIMEOUT_SECONDS,
        circuit_half_open_max_attempts: int = DEFRA_CIRCUIT_HALF_OPEN_MAX_ATTEMPTS,
        circuit_max_backoff_seconds: float = DEFRA_CIRCUIT_MAX_BACKOFF_SECONDS,
    ):
        """
        Initialize DEFRA-specific rate limiter + circuit breaker.

        Treats HTTP 403 responses as rate limit events that trigger circuit breaking.
        """
        self.rate_limiter = ApiRateLimiter(
            requests_per_second=requests_per_second,
            timeout_seconds=rate_limit_timeout_seconds,
            retry_delay_seconds=rate_limit_retry_delay_seconds,
            service_name=service_name,
        )

        self.circuit_breaker = CircuitBreaker(
            failure_threshold=circuit_failure_threshold,
            recovery_timeout_seconds=circuit_recovery_timeout_seconds,
            expected_exception_type=RateLimitError,
            service_name=service_name,
            half_open_max_attempts=circuit_half_open_max_attempts,
            max_backoff_seconds=circuit_max_backoff_seconds,
        )

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Decorator that applies rate limiting, circuit breaking, and 403 detection.

        Order of execution:
        1. Circuit breaker checks state (rejects if open)
        2. Rate limiter acquires slot
        3. Function executes, wrapped to detect 403s
        4. If 403 detected, converts to RateLimitError
        5. Circuit breaker records success/failure
        """

        @wraps(func)
        async def detect_403_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await func(*args, **kwargs)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 403:
                    raise RateLimitError(
                        f"Assuming rate limit: HTTP 403 from {e.response.url}",
                        response=e.response,
                    ) from e
                raise

        circuit_protected = self.circuit_breaker(detect_403_wrapper)
        rate_limited = self.rate_limiter(circuit_protected)
        return rate_limited


class RateLimitedPublicRegisterClient(PublicRegisterClient):
    """
    DEFRA PublicRegisterClient with automatic rate limiting, circuit breaker, and retry logic.

    All HTTP requests are protected by:
    - Rate limiting: 5 requests/second with 30s timeout
    - Circuit breaker: Opens after 3 consecutive 403 errors, prevents cascade failures
    - Automatic retry: Up to 3 attempts with exponential backoff
    """

    def __init__(self, timeout=30.0, verbose=False, **kwargs):
        """
        Initialize the rate-limited client.

        Args:
            timeout (float, optional): The timeout for requests in seconds. Defaults to 30.0.
            verbose (bool, optional): If True, logs requests and responses. Defaults to False.
            **kwargs: Additional keyword arguments to pass to the httpx.AsyncClient constructor.
        """
        super().__init__(timeout=timeout, verbose=verbose, **kwargs)
        # Each instance gets its own circuit breaker for proper isolation
        self._circuit_breaker = DefraRateLimitedCircuitBreaker()

    async def get(self, url: str, **kwargs: Any) -> httpx.Response:
        """
        Make a protected GET request with rate limiting, circuit breaker, and retries.

        Retries up to 3 times with exponential backoff on transient errors.
        Does NOT retry on circuit breaker open or rate limit errors (403s).

        Args:
            url: The URL to request
            **kwargs: Additional arguments to pass to the underlying get method

        Returns:
            Response from the API

        Raises:
            CircuitBreakerOpen: If circuit breaker is open due to repeated failures
            RateLimitError: If 403 rate limit error is encountered
        """

        @retry(
            stop=stop_after_attempt(DEFRA_MAX_RETRY_ATTEMPTS),
            wait=wait_exponential(
                multiplier=DEFRA_RETRY_MULTIPLIER,
                min=DEFRA_RETRY_MIN_WAIT_SECONDS,
                max=DEFRA_RETRY_MAX_WAIT_SECONDS,
            ),
            retry=retry_if_not_exception_type((CircuitBreakerOpen, RateLimitError)),
            reraise=True,
        )
        @self._circuit_breaker
        async def _make_request() -> httpx.Response:
            return await super(RateLimitedPublicRegisterClient, self).get(url, **kwargs)

        return await _make_request()

    async def get_as_json(self, url: str, **kwargs: Any) -> dict[str, Any]:
        """
        Get a URL and return the parsed JSON response.

        This is a convenience method that:
        1. Makes a GET request
        2. Checks the response status (raises HTTPStatusError if not successful)
        3. Parses the response as JSON
        4. If JSON parsing fails, raises an error with the response body

        Args:
            url: The URL to request
            **kwargs: Additional arguments to pass to the underlying get method

        Returns:
            Parsed JSON response as a dictionary

        Raises:
            CircuitBreakerOpen: If circuit breaker is open due to repeated failures
            RateLimitError: If 403 rate limit error is encountered
            httpx.HTTPStatusError: If the response status indicates an error (4xx, 5xx)
            ValueError: If the response cannot be parsed as JSON
        """
        response = await self.get(url, **kwargs)
        response.raise_for_status()

        try:
            return response.json()
        except (json.JSONDecodeError, ValueError) as e:
            # If JSON parsing fails, include the response body in the error
            body = None
            try:
                body = response.text
            except Exception:
                pass

            if body:
                raise ValueError(
                    f"Failed to parse JSON response from DEFRA API for {url}. "
                    f"Response body: {body[:500]}"
                ) from e
            raise ValueError(
                f"Failed to parse JSON response from DEFRA API for {url}"
            ) from e
