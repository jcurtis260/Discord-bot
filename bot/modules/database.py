"""
Database module for Discord bot.
Handles database connections and provides async database operations.
"""

import asyncpg
import redis.asyncio as redis
from typing import Optional, Any, Dict, List
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)


class Database:
    """Async PostgreSQL database manager."""
    
    def __init__(self, database_url: str):
        """
        Initialize database manager.
        
        Args:
            database_url: PostgreSQL connection URL
        """
        self.database_url = database_url
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self) -> None:
        """Create database connection pool."""
        if self.pool is None:
            try:
                self.pool = await asyncpg.create_pool(
                    self.database_url,
                    min_size=5,
                    max_size=20,
                    command_timeout=60
                )
                logger.info("Database connection pool created")
            except Exception as e:
                logger.error(f"Failed to create database pool: {e}")
                raise
    
    async def close(self) -> None:
        """Close database connection pool."""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")
    
    @asynccontextmanager
    async def acquire(self):
        """
        Acquire a database connection from the pool.
        
        Yields:
            Database connection
        """
        if not self.pool:
            await self.connect()
        
        async with self.pool.acquire() as conn:
            yield conn
    
    async def execute(self, query: str, *args) -> str:
        """
        Execute a query that doesn't return rows.
        
        Args:
            query: SQL query
            *args: Query parameters
        
        Returns:
            Query result status
        """
        async with self.acquire() as conn:
            return await conn.execute(query, *args)
    
    async def fetch(self, query: str, *args) -> List[asyncpg.Record]:
        """
        Fetch multiple rows from database.
        
        Args:
            query: SQL query
            *args: Query parameters
        
        Returns:
            List of database records
        """
        async with self.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args) -> Optional[asyncpg.Record]:
        """
        Fetch a single row from database.
        
        Args:
            query: SQL query
            *args: Query parameters
        
        Returns:
            Database record or None
        """
        async with self.acquire() as conn:
            return await conn.fetchrow(query, *args)
    
    async def fetchval(self, query: str, *args) -> Any:
        """
        Fetch a single value from database.
        
        Args:
            query: SQL query
            *args: Query parameters
        
        Returns:
            Single value
        """
        async with self.acquire() as conn:
            return await conn.fetchval(query, *args)


class RedisCache:
    """Async Redis cache manager."""
    
    def __init__(self, redis_url: str):
        """
        Initialize Redis cache manager.
        
        Args:
            redis_url: Redis connection URL
        """
        self.redis_url = redis_url
        self.client: Optional[redis.Redis] = None
    
    async def connect(self) -> None:
        """Create Redis connection."""
        if self.client is None:
            try:
                self.client = await redis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True
                )
                await self.client.ping()
                logger.info("Redis connection established")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise
    
    async def close(self) -> None:
        """Close Redis connection."""
        if self.client:
            await self.client.close()
            logger.info("Redis connection closed")
    
    async def get(self, key: str) -> Optional[str]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None
        """
        if not self.client:
            await self.connect()
        return await self.client.get(key)
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (optional)
        
        Returns:
            True if successful
        """
        if not self.client:
            await self.connect()
        
        if ttl:
            return await self.client.setex(key, ttl, value)
        else:
            return await self.client.set(key, value)
    
    async def delete(self, key: str) -> int:
        """
        Delete key from cache.
        
        Args:
            key: Cache key
        
        Returns:
            Number of keys deleted
        """
        if not self.client:
            await self.connect()
        return await self.client.delete(key)
    
    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.
        
        Args:
            key: Cache key
        
        Returns:
            True if key exists
        """
        if not self.client:
            await self.connect()
        return await self.client.exists(key) > 0
    
    async def expire(self, key: str, ttl: int) -> bool:
        """
        Set expiration on key.
        
        Args:
            key: Cache key
            ttl: Time to live in seconds
        
        Returns:
            True if successful
        """
        if not self.client:
            await self.connect()
        return await self.client.expire(key, ttl)
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """
        Increment value in cache.
        
        Args:
            key: Cache key
            amount: Amount to increment by
        
        Returns:
            New value
        """
        if not self.client:
            await self.connect()
        return await self.client.incrby(key, amount)
    
    async def decrement(self, key: str, amount: int = 1) -> int:
        """
        Decrement value in cache.
        
        Args:
            key: Cache key
            amount: Amount to decrement by
        
        Returns:
            New value
        """
        if not self.client:
            await self.connect()
        return await self.client.decrby(key, amount)
