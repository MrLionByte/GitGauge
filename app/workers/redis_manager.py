import os
import redis.asyncio as aioredis
from app.config import settings


class RedisManager:
    def __init__(self):
        self.client = None

    async def connect(self):
        if not self.client:
            self.client = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )

    async def set(self, key: str, value: str, expire_seconds: int = 3600):
        await self.connect()
        await self.client.set(key, value, ex=expire_seconds)

    async def get(self, key: str):
        await self.connect()
        return await self.client.get(key)

    async def delete(self, key: str):
        await self.connect()
        await self.client.delete(key)

    async def close(self):
        if self.client:
            await self.client.close()

# Singleton instance
redis_manager = RedisManager()
