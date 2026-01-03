"""
Pytest configuration and fixtures
"""
import pytest
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set test environment variables
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-testing-only-min-32-chars-long")
os.environ.setdefault("RATE_LIMIT_ENABLED", "true")
os.environ.setdefault("LOG_LEVEL", "DEBUG")
os.environ.setdefault("API_ENV", "test")

