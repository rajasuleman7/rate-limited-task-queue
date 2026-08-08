
"""
Per-user rate limiting backed by Redis (sliding window counter).
Falls back to an in-memory counter if Redis is unavailable.
"""
import time
import logging
from functools import wraps
from typing import Callable

from fastapi import HTTPException, Request

logger = logging.getLogger("rate_limiter")

# In-memory fallback: {user_id: [timestamps]}
_memory_store: dict[str, list] = {}

ROLE_LIMITS = {
    "user":    30,   # requests per minute
    "premium": 100,
    "admin":   500,
}


def _get_redis():
    try:
        import redis
        from .config import get_settings
        r = redis.from_url(get_settings().redis_url, socket_connect_timeout=1)
        r.ping()
        return r
    except Exception:
        return None


def check_rate_limit(user_id: str, role: str = "user") -> dict:
    """
    Sliding-window rate limiter.
    Returns {"allowed": bool, "remaining": int, "limit": int, "reset_in": int}
    """
    limit  = ROLE_LIMITS.get(role, ROLE_LIMITS["user"])
    window = 60   # 1 minute window
    now    = time.time()
    key    = f"rl:{user_id}"

    redis  = _get_redis()
    if redis:
        try:
            pipe = redis.pipeline()
            pipe.zremrangebyscore(key, 0, now - window)
            pipe.zadd(key, {str(now): now})
            pipe.zcard(key)
            pipe.expire(key, window)
            _, _, count, _ = pipe.execute()
            count = int(count)
            remaining = max(0, limit - count)
            return {
                "allowed":   count <= limit,
                "remaining": remaining,
                "limit":     limit,
                "reset_in":  window,
                "backend":   "redis",
            }
        except Exception as e:
            logger.warning("Redis rate limit error: %s — falling back to memory", e)

    # In-memory fallback
    timestamps = _memory_store.get(key, [])
    timestamps = [t for t in timestamps if now - t < window]
    timestamps.append(now)
    _memory_store[key] = timestamps
    count = len(timestamps)
    remaining = max(0, limit - count)
    return {
        "allowed":   count <= limit,
        "remaining": remaining,
        "limit":     limit,
        "reset_in":  window,
        "backend":   "memory",
    }


def rate_limit(get_user_fn: Callable = None):
    """FastAPI dependency for rate limiting."""
    from fastapi import Depends
    from .auth import get_current_user

    async def _check(request: Request, user: dict = Depends(get_current_user)):
        result = check_rate_limit(user["sub"], user.get("role", "user"))
        request.state.rate_limit = result
        if not result["allowed"]:
            raise HTTPException(
                status_code=429,
                detail={
                    "error":     "Rate limit exceeded",
                    "limit":     result["limit"],
                    "reset_in":  result["reset_in"],
                    "role":      user.get("role", "user"),
                },
                headers={"Retry-After": str(result["reset_in"])},
            )
        return user
    return _check
