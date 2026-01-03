"""
Pytest configuration and fixtures
"""
import pytest
import os
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set test environment variables
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-testing-only-min-32-chars-long")
os.environ.setdefault("RATE_LIMIT_ENABLED", "true")
os.environ.setdefault("LOG_LEVEL", "DEBUG")
os.environ.setdefault("API_ENV", "test")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

# Import after setting environment
from db.database import Base, get_db
from db import crud


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session using SQLite in-memory."""
    # Create in-memory SQLite database for testing
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = crud.create_user(
        db=db_session,
        username="testuser",
        password="testpass123",
        email="test@example.com"
    )
    return user


@pytest.fixture
def admin_user(db_session):
    """Create an admin test user."""
    user = crud.create_user(
        db=db_session,
        username="admin",
        password="admin123",
        email="admin@example.com",
        is_admin=True
    )
    return user

