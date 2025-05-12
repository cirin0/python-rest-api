from datetime import timedelta
import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException
from starlette.requests import Request
from rate_limiter import RateLimiter


@pytest.fixture
def mock_request():
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/test/path",
        "headers": [],
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
        "scheme": "http",
        "root_path": "",
    }
    request = Request(scope)
    return request


@pytest.fixture
def rate_limiter():
    limiter = RateLimiter()
    limiter.redis = AsyncMock()
    return limiter


@pytest.mark.asyncio
async def test_rate_limit_anonymous_not_exceeded(mock_request, rate_limiter):
    rate_limiter.redis.incr.return_value = 1
    rate_limiter.redis.expire.return_value = True

    await rate_limiter.check_rate_limit(mock_request)

    rate_limiter.redis.incr.assert_awaited_once()
    rate_limiter.redis.expire.assert_awaited_once()


@pytest.mark.asyncio
async def test_rate_limit_anonymous_exceeded(mock_request, rate_limiter):
    rate_limiter.redis.incr.return_value = 3

    with pytest.raises(HTTPException) as exc_info:
        await rate_limiter.check_rate_limit(mock_request)

    assert exc_info.value.status_code == 429
    assert "Too many requests" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_rate_limit_authenticated_not_exceeded(mock_request, rate_limiter):
    rate_limiter.redis.incr.return_value = 1
    rate_limiter.redis.expire.return_value = True

    await rate_limiter.check_rate_limit(mock_request, user="testuser")

    rate_limiter.redis.incr.assert_awaited_once()

    rate_limiter.redis.expire.assert_awaited_once_with(
        "rate_limit:testuser:/test/path", timedelta(minutes=1)
    )


@pytest.mark.asyncio
async def test_rate_limit_authenticated_not_first_request(mock_request, rate_limiter):
    rate_limiter.redis.incr.return_value = 2

    await rate_limiter.check_rate_limit(mock_request, user="testuser")

    rate_limiter.redis.incr.assert_awaited_once()

    rate_limiter.redis.expire.assert_not_awaited()


@pytest.mark.asyncio
async def test_rate_limit_authenticated_exceeded(mock_request, rate_limiter):
    rate_limiter.redis.incr.return_value = 11

    with pytest.raises(HTTPException) as exc_info:
        await rate_limiter.check_rate_limit(mock_request, user="testuser")

    assert exc_info.value.status_code == 429
    assert "Too many requests" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_rate_limit_key_generation(mock_request, rate_limiter):
    key = await rate_limiter._get_key(mock_request)
    assert key == "rate_limit:127.0.0.1:/test/path"

    key = await rate_limiter._get_key(mock_request, user="testuser")
    assert key == "rate_limit:testuser:/test/path"
