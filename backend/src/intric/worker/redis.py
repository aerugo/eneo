from datetime import datetime, timezone
from typing import NamedTuple

import redis.asyncio as aioredis

from intric.main.config import SETTINGS

"""
Redis Connection Setup with Conditional Authentication

This module establishes a Redis connection pool with optional password authentication.
Authentication is enabled when the REDIS_PASSWORD environment variable is set.

Environment Variables:
- REDIS_HOST: Redis server hostname (required)
- REDIS_PORT: Redis server port (required)
- REDIS_PASSWORD: Redis password (optional)

Usage:
- If REDIS_PASSWORD is set: Connects using password authentication
- If REDIS_PASSWORD is not set: Connects without authentication (assumes no password)

The Redis connection is shared across the application for:
- WebSocket pub/sub messaging
- Worker health monitoring
- General Redis operations
"""

# Build Redis URL with conditional password authentication
if SETTINGS.redis_password:
    redis_url = f"redis://:{SETTINGS.redis_password}@{SETTINGS.redis_host}:{SETTINGS.redis_port}"
else:
    redis_url = f"redis://{SETTINGS.redis_host}:{SETTINGS.redis_port}"

pool = aioredis.ConnectionPool.from_url(redis_url)
r = aioredis.Redis(connection_pool=pool)


class WorkerHealth(NamedTuple):
    status: str  # "healthy", "unhealthy", "unknown"
    last_heartbeat: str | None
    details: str | None


async def get_worker_health() -> WorkerHealth:
    """
    Check the health status of the arq worker by looking for its health check key in Redis.

    Returns:
        WorkerHealth: Contains status, last_heartbeat timestamp, and details
    """
    try:
        # Check for arq worker health check key
        # Default queue name in arq is "arq:queue", health check key is "{queue_name}:health-check"
        health_key = "arq:queue:health-check"
        worker_health_data = await r.get(health_key)

        if worker_health_data:
            worker_health_str = worker_health_data.decode("utf-8")
            return WorkerHealth(
                status="HEALTHY",
                last_heartbeat=datetime.now(timezone.utc).isoformat(),
                details=worker_health_str,
            )
        else:
            return WorkerHealth(
                status="UNHEALTHY",
                last_heartbeat=None,
                details="Worker health check key not found or expired",
            )

    except Exception as e:
        return WorkerHealth(
            status="UNKNOWN",
            last_heartbeat=None,
            details=f"Redis connection error: {str(e)}",
        )
