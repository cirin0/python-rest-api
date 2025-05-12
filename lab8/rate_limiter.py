from fastapi import Depends, Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import timedelta
import redis.asyncio as redis
from typing import Optional
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
LIMIT_AUTHENTICATED = 10
LIMIT_ANONYMOUS = 2


class RateLimiter:
    def __init__(self):
        self.redis = redis.from_url(REDIS_URL)

    async def _get_key(self, request: Request, user: Optional[str] = None) -> str:
        if user:
            return f"rate_limit:{user}:{request.url.path}"
        return f"rate_limit:{request.client.host}:{request.url.path}"

    async def check_rate_limit(self, request: Request, user: Optional[str] = None):
        limit = LIMIT_AUTHENTICATED if user else LIMIT_ANONYMOUS
        key = await self._get_key(request, user)
        current = await self.redis.incr(key)
        if current == 1:
            await self.redis.expire(key, timedelta(minutes=1))

        if current > limit:
            raise HTTPException(
                status_code=429,
                detail=f"Too many requests. Limit is {limit} per minute.",
                headers={"Retry-After": "60"},
            )


class RateLimitDependency:
    def __init__(self, limiter: RateLimiter):
        self.limiter = limiter

    async def __call__(self, request: Request):
        await self.limiter.check_rate_limit(request)


class AuthRateLimitDependency(RateLimitDependency):
    async def __call__(
        self,
        request: Request,
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    ):
        from auth_service import decode_token

        payload = decode_token(credentials.credentials)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid token")

        await self.limiter.check_rate_limit(request, payload["sub"])
