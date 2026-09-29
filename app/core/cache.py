from __future__ import annotations

import json
import logging
from collections.abc import Callable
from typing import Any

import redis.asyncio as aioredis

logger = logging.getLogger(__name__)


class CacheService:
    def __init__(self, redis_url: str, default_ttl: int = 300) -> None:
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self.client: aioredis.Redis | None = None

    async def connect(self) -> None:
        try:
            self.client = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20,
            )
            await self.client.ping()
            logger.info("Connected to Redis at %s", self.redis_url)
        except Exception as e:
            logger.warning("Redis connection failed; caching will be bypassed: %s", e)
            self.client = None

    async def close(self) -> None:
        if self.client:
            await self.client.aclose()
            logger.info("Closed Redis connection.")

    async def get(self, key: str) -> Any | None:
        if not self.client:
            return None
        try:
            val = await self.client.get(key)
            if val is not None:
                return json.loads(val)
        except Exception as e:
            logger.warning("Cache GET failed for key '%s': %s", key, e)
        return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        if not self.client:
            return False
        try:
            payload = json.dumps(value, default=str)
            expires = ttl if ttl is not None else self.default_ttl
            await self.client.set(key, payload, ex=expires)
            return True
        except Exception as e:
            logger.warning("Cache SET failed for key '%s': %s", key, e)
            return False

    async def invalidate(self, *keys: str) -> int:
        if not self.client or not keys:
            return 0
        try:
            return await self.client.delete(*keys)
        except Exception as e:
            logger.warning("Cache invalidation failed for keys %s: %s", keys, e)
            return 0

    async def get_or_set(
        self, key: str, producer: Callable[[], Any], ttl: int | None = None
    ) -> Any:
        cached = await self.get(key)
        if cached is not None:
            return cached
        data = await producer()
        await self.set(key, data, ttl=ttl)
        return data


cache_service: CacheService | None = None


def get_cache() -> CacheService:
    global cache_service
    if cache_service is None:
        raise RuntimeError("CacheService is not initialized.")
    return cache_service
