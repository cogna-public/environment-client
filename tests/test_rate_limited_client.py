import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
import asyncio

from environment.public_register import RateLimitedPublicRegisterClient
from environment.public_register.rate_limited_client import (
    CircuitBreakerOpen,
    RateLimitError,
)


class TestRateLimitedPublicRegisterClient:
    """Test cases for the RateLimitedPublicRegisterClient."""

    @pytest_asyncio.fixture
    async def client(self):
        """Create a RateLimitedPublicRegisterClient instance for testing."""
        async with RateLimitedPublicRegisterClient() as client:
            yield client

    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test that the client initializes correctly."""
        client = RateLimitedPublicRegisterClient()
        assert (
            str(client.base_url) == "https://environment.data.gov.uk/public-register/"
        )
        await client.aclose()

    @pytest.mark.asyncio
    async def test_successful_get_request(self, client):
        """Test a successful GET request with rate limiting and circuit breaker."""
        with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock) as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"test": "data"}
            mock_get.return_value = mock_response

            response = await client.get("/test-endpoint")

            assert response.status_code == 200
            assert mock_get.called

    @pytest.mark.asyncio
    async def test_get_as_json_success(self, client):
        """Test successful get_as_json request."""
        with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock) as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"items": [{"id": "test"}]}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = await client.get_as_json("/test-endpoint")

            assert result == {"items": [{"id": "test"}]}
            mock_response.raise_for_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_as_json_invalid_json(self, client):
        """Test get_as_json with invalid JSON response."""
        with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock) as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_response.text = "Not JSON content"
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            with pytest.raises(ValueError, match="Failed to parse JSON response"):
                await client.get_as_json("/test-endpoint")

    @pytest.mark.asyncio
    async def test_retry_on_transient_errors(self, client):
        """Test that transient errors are retried."""
        with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock) as mock_get:
            # First two calls fail, third succeeds
            mock_response_success = MagicMock()
            mock_response_success.status_code = 200
            mock_response_success.json.return_value = {"test": "data"}

            mock_get.side_effect = [
                httpx.RequestError("Connection error"),
                httpx.RequestError("Timeout"),
                mock_response_success,
            ]

            response = await client.get("/test-endpoint")

            assert response.status_code == 200
            assert mock_get.call_count == 3

    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test that rate limiting enforces requests per second limit."""
        client = RateLimitedPublicRegisterClient()

        with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock) as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            # Make more requests than the rate limit
            start_time = asyncio.get_event_loop().time()
            tasks = [client.get("/test-endpoint") for _ in range(10)]
            await asyncio.gather(*tasks)
            elapsed_time = asyncio.get_event_loop().time() - start_time

            # With 5 req/sec, 10 requests should take at least ~1 second
            assert elapsed_time >= 1.0, f"Rate limiting not working: {elapsed_time}s"
            assert mock_get.call_count == 10

        await client.aclose()

    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_on_403_errors(self):
        """Test that circuit breaker opens after multiple 403 errors."""
        client = RateLimitedPublicRegisterClient()

        with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock) as mock_get:
            # Mock 403 responses
            mock_response = MagicMock()
            mock_response.status_code = 403
            mock_response.url = "https://test.example.com/test"

            def raise_403(*args, **kwargs):
                raise httpx.HTTPStatusError(
                    "403 Forbidden", request=MagicMock(), response=mock_response
                )

            mock_get.side_effect = raise_403

            # First 3 requests should trigger 403 errors
            for _ in range(3):
                with pytest.raises(RateLimitError):
                    await client.get("/test-endpoint")

            # Circuit should now be open, next request should fail immediately with CircuitBreakerOpen
            with pytest.raises(CircuitBreakerOpen):
                await client.get("/test-endpoint")

        await client.aclose()

    @pytest.mark.asyncio
    async def test_403_converts_to_rate_limit_error(self, client):
        """Test that 403 HTTP errors are converted to RateLimitError."""
        with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock) as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 403
            mock_response.url = "https://test.example.com/test"

            def raise_403(*args, **kwargs):
                raise httpx.HTTPStatusError(
                    "403 Forbidden", request=MagicMock(), response=mock_response
                )

            mock_get.side_effect = raise_403

            with pytest.raises(RateLimitError, match="rate limit"):
                await client.get("/test-endpoint")

    @pytest.mark.asyncio
    async def test_non_403_errors_propagate(self, client):
        """Test that non-403 HTTP errors are not converted to RateLimitError."""
        with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock) as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.url = "https://test.example.com/test"

            def raise_500(*args, **kwargs):
                raise httpx.HTTPStatusError(
                    "500 Internal Server Error",
                    request=MagicMock(),
                    response=mock_response,
                )

            mock_get.side_effect = raise_500

            # Should retry and eventually fail with HTTPStatusError, not RateLimitError
            with pytest.raises(httpx.HTTPStatusError):
                await client.get("/test-endpoint")

    @pytest.mark.asyncio
    async def test_get_waste_operations_with_rate_limiting(self, client):
        """Test that high-level API methods inherit rate limiting behavior."""
        mock_response_data = {
            "meta": {
                "publisher": "Environment Agency",
                "licence": "https://www.gov.uk/government/publications/environment-agency-conditional-licence",
                "documentation": "https://environment.data.gov.uk/public-register/view/api-reference",
                "hasFormat": ["application/json", "application/csv"],
                "version": "1.0.0",
                "limit": 5,
                "offset": 0,
            },
            "items": [
                {
                    "@id": "http://environment.data.gov.uk/public-register/waste-operations/registration/CB/HE5831CE",
                    "register": {
                        "@id": "http://environment.data.gov.uk/public-register/waste-operations",
                        "label": "Waste Operations",
                    },
                    "registrationNumber": "CB/HE5831CE",
                    "type": [
                        "http://environment.data.gov.uk/public-register/vocab/Registration"
                    ],
                    "holder": {
                        "@id": "http://environment.data.gov.uk/public-register/holder/12345",
                        "name": "Waste Company Limited",
                    },
                }
            ],
        }

        with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock) as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = await client.get_waste_operations(limit=5)

            assert len(result.items) == 1
            assert result.items[0].registration_number == "CB/HE5831CE"
            mock_get.assert_called()

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self):
        """Test that requests fail after max retry attempts."""
        client = RateLimitedPublicRegisterClient()

        with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock) as mock_get:
            # Always fail with a transient error
            mock_get.side_effect = httpx.RequestError("Connection error")

            with pytest.raises(httpx.RequestError):
                await client.get("/test-endpoint")

            # Should have retried 3 times (DEFRA_MAX_RETRY_ATTEMPTS)
            assert mock_get.call_count == 3

        await client.aclose()
