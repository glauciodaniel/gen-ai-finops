"""
Tests for rate limiting
"""
import pytest
import os
from utils.rate_limit import get_rate_limit_config, RATE_LIMIT_ENABLED


class TestRateLimitConfig:
    """Test rate limiting configuration."""
    
    def test_get_rate_limit_config(self):
        """Test getting rate limit configuration."""
        config = get_rate_limit_config()
        
        assert "enabled" in config
        assert "per_minute" in config
        assert "per_hour" in config
        assert isinstance(config["enabled"], bool)
        assert isinstance(config["per_minute"], int)
        assert isinstance(config["per_hour"], int)
    
    def test_rate_limit_env_vars(self):
        """Test rate limit environment variables."""
        # These should be set in the module
        assert isinstance(RATE_LIMIT_ENABLED, bool)
        assert RATE_LIMIT_PER_MINUTE > 0
        assert RATE_LIMIT_PER_HOUR > 0

