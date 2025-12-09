"""
Generic rate limiter for external API calls.

Prevents overwhelming external services with too many concurrent requests.
"""

import asyncio
import time
from functools import wraps
from typing import Any, Callable

from limits import RateLimitItemPerSecond
from limits.aio.storage import MemoryStorage
from limits.aio.strategies import MovingWindowRateLimiter
import structlog

from .exceptions import RateLimitExceeded

logger = structlog.get_logger(__name__)


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
        exception_class: type[RateLimitExceeded] = RateLimitExceeded,
    ):
        """
        Initialize rate limiter.

        Args:
            requests_per_second: Maximum number of requests allowed per second
            timeout_seconds: Maximum time to wait for rate limit slot
            retry_delay_seconds: Delay between retry attempts when rate limited
            service_name: Name of the service for logging and error messages
            exception_class: Exception to raise when timeout is exceeded
        """
        self.requests_per_second = requests_per_second
        self.timeout_seconds = timeout_seconds
        self.retry_delay_seconds = retry_delay_seconds
        self.service_name = service_name
        self.exception_class = exception_class

        self._storage = MemoryStorage()
        self._limiter = MovingWindowRateLimiter(self._storage)
        self._rate_limit = RateLimitItemPerSecond(requests_per_second, 1)
        self._identifier = f"{service_name.lower()}-api"

    async def _acquire_rate_limit_slot(self) -> None:
        """
        Acquire a rate limit slot, waiting and retrying if necessary.

        Raises:
            exception_class: If rate limit cannot be acquired within timeout period
        """
        start_time = time.time()

        while True:
            if await self._limiter.hit(self._rate_limit, self._identifier):
                return

            elapsed = time.time() - start_time
            if elapsed > self.timeout_seconds:
                logger.error(
                    "Rate limit timeout exceeded",
                    service=self.service_name,
                    timeout_seconds=self.timeout_seconds,
                    elapsed_seconds=elapsed,
                    requests_per_second=self.requests_per_second,
                )
                raise self.exception_class(
                    f"{self.service_name} API rate limit exceeded - could not acquire slot within {self.timeout_seconds}s. "
                    "The service may be experiencing high load or rate limiting. Please try again later."
                )

            logger.debug(
                f"{self.service_name} rate limit reached, waiting before next request",
                service=self.service_name,
                elapsed_seconds=elapsed,
            )
            await asyncio.sleep(self.retry_delay_seconds)

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Decorator to apply rate limiting to async functions.

        Example:
            rate_limiter = ApiRateLimiter(...)

            @rate_limiter
            async def my_api_call():
                return await client.get(...)
        """

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            await self._acquire_rate_limit_slot()
            return await func(*args, **kwargs)

        return wrapper
