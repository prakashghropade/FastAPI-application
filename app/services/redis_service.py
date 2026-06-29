from typing import Any, Optional
import redis.asyncio as aioredis
from app.core.config import settings
from app.core.logging_config import logger


class RedisService:
    """
    Service class managing connection and operations for Redis.
    Uses redis.asyncio for non-blocking I/O.
    """
    def __init__(self) -> None:
        self.client: Optional[aioredis.Redis] = None

    async def connect(self) -> None:
        """
        Initializes the Redis connection pool.
        """
        try:
            self.client = aioredis.Redis.from_url(
                settings.REDIS_URL,
                decode_responses=True, # Automatically decode bytes to strings
                socket_timeout=5.0
            )
            await self.client.ping()
            logger.info("Successfully connected to Redis.")
        except Exception as e:
            logger.error(f"Failed to connect to Redis at {settings.REDIS_URL}: {str(e)}")
            self.client = None

    async def disconnect(self) -> None:
        """
        Closes the Redis connection pool.
        """
        if self.client:
            await self.client.aclose()
            logger.info("Redis connection closed.")
            self.client = None

    async def ping(self) -> bool:
        """
        Pings Redis server to check connection health.
        """
        if not self.client:
            return False
        try:
            await self.client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis ping failed: {str(e)}")
            return False

    async def get(self, key: str) -> Optional[str]:
        """
        Retrieves a string value from Redis cache.
        """
        if not self.client:
            return None
        try:
            return await self.client.get(key)
        except Exception as e:
            logger.error(f"Redis GET failed for key {key}: {str(e)}")
            return None

    async def set(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        """
        Sets a key-value pair in Redis cache with an optional TTL (in seconds).
        """
        if not self.client:
            return False
        try:
            await self.client.set(key, value, ex=expire)
            return True
        except Exception as e:
            logger.error(f"Redis SET failed for key {key}: {str(e)}")
            return False

    async def delete(self, key: str) -> bool:
        """
        Deletes a key from Redis cache.
        """
        if not self.client:
            return False
        try:
            result = await self.client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis DELETE failed for key {key}: {str(e)}")
            return False

    async def check_rate_limit(self, key: str, limit: int, window: int) -> bool:
        """
        Enforces a fixed-window rate limit using a Redis transaction pipeline.
        Returns True if the request is within the limit, False if rate-limited.
        """
        if not self.client:
            # Fail-open if Redis is unavailable to preserve api availability
            return True
            
        try:
            async with self.client.pipeline(transaction=True) as pipe:
                pipe.incr(key)
                pipe.ttl(key)
                current_count, ttl = await pipe.execute()
                
            # If it's a new key or TTL was lost, establish expiration
            if current_count == 1 or ttl == -1:
                await self.client.expire(key, window)
                
            return current_count <= limit
        except Exception as e:
            logger.error(f"Rate limit validation failed in Redis: {str(e)}")
            # Fail-open in case of Redis errors so API stays operational
            return True


# Instantiate the global singleton service
redis_service = RedisService()
