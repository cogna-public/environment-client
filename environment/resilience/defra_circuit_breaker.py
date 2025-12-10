"""
DEFRA-specific rate limiter with circuit breaker for HTTP 403 handling.

Treats HTTP 403 responses as rate limit events, triggering circuit breaker
to prevent further requests until recovery.
"""

from functools import wraps
from typing import Any, Callable
import httpx
import structlog

from .circuit_breaker import CircuitBreaker
from .rate_limiter import ApiRateLimiter
from .exceptions import RateLimitError, RateLimitExceeded

logger = structlog.get_logger(__name__)

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

        Args:
            service_name: Name of the service for logging and error messages
            requests_per_second: Maximum requests per second (proactive rate limiting)
            rate_limit_timeout_seconds: Timeout for acquiring rate limit slot
            rate_limit_retry_delay_seconds: Delay between rate limit retry attempts
            circuit_failure_threshold: Number of 403s before opening circuit
            circuit_recovery_timeout_seconds: Initial wait before testing recovery
            circuit_half_open_max_attempts: Test requests in half-open state
            circuit_max_backoff_seconds: Maximum backoff time
        """
        self.rate_limiter = ApiRateLimiter(
            requests_per_second=requests_per_second,
            timeout_seconds=rate_limit_timeout_seconds,
            retry_delay_seconds=rate_limit_retry_delay_seconds,
            service_name=service_name,
            exception_class=RateLimitExceeded,
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

        Example:
            defra_protection = DefraRateLimitedCircuitBreaker()

            @defra_protection
            async def fetch_data():
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        """

        @wraps(func)
        async def detect_403_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await func(*args, **kwargs)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 403:
                    logger.warning(
                        f"{self.circuit_breaker.service_name} received HTTP 403 - treating as rate limit",
                        service=self.circuit_breaker.service_name,
                        url=str(e.response.url),
                        status_code=403,
                    )
                    raise RateLimitError(
                        f"Assuming rate limit: HTTP 403 from {e.response.url}",
                        response=e.response,
                    ) from e
                raise

        circuit_protected = self.circuit_breaker(detect_403_wrapper)
        rate_limited = self.rate_limiter(circuit_protected)
        return rate_limited
