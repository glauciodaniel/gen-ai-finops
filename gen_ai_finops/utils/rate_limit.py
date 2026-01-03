"""
Rate Limiting Middleware
"""
import os
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request

# Rate limiting configuration
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
RATE_LIMIT_PER_HOUR = int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))

# Create limiter instance
limiter = Limiter(key_func=get_remote_address)


def get_rate_limit_config():
    """Get rate limit configuration."""
    return {
        "enabled": RATE_LIMIT_ENABLED,
        "per_minute": RATE_LIMIT_PER_MINUTE,
        "per_hour": RATE_LIMIT_PER_HOUR
    }


def setup_rate_limiting(app):
    """
    Setup rate limiting middleware for FastAPI app.
    
    Usage:
        from utils.rate_limit import setup_rate_limiting
        setup_rate_limiting(app)
    """
    if RATE_LIMIT_ENABLED:
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        return True
    return False


def rate_limit_decorator(calls: int = None, period: str = "minute"):
    """
    Decorator for rate limiting endpoints.
    
    Usage:
        @app.get("/api/endpoint")
        @rate_limit_decorator(calls=10, period="minute")
        async def endpoint():
            return {"message": "ok"}
    """
    if not RATE_LIMIT_ENABLED:
        # Return a no-op decorator if rate limiting is disabled
        def noop_decorator(func):
            return func
        return noop_decorator
    
    if calls is None:
        calls = RATE_LIMIT_PER_MINUTE if period == "minute" else RATE_LIMIT_PER_HOUR
    
    limit_str = f"{calls}/{period}"
    return limiter.limit(limit_str)

