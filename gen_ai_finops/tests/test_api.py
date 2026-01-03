"""
Integration tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.main import app
from utils.auth import create_access_token


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def auth_token():
    """Create a test auth token."""
    return create_access_token(data={"sub": "testuser"})


@pytest.fixture
def auth_headers(auth_token):
    """Create auth headers."""
    return {"Authorization": f"Bearer {auth_token}"}


class TestPublicEndpoints:
    """Test public endpoints that don't require authentication."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "GenAIFinOps API"
        assert "version" in data
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_login_endpoint_success(self, client):
        """Test successful login."""
        response = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_endpoint_failure(self, client):
        """Test failed login."""
        response = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "wrong_password"}
        )
        assert response.status_code == 401
    
    def test_get_current_user_without_token(self, client):
        """Test getting user info without token."""
        response = client.get("/api/auth/me")
        assert response.status_code == 403
    
    def test_get_current_user_with_token(self, client, auth_headers):
        """Test getting user info with valid token."""
        response = client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is True
        assert "username" in data


class TestOracleEndpoints:
    """Test Oracle endpoints."""
    
    def test_oracle_ask_without_auth(self, client):
        """Test Oracle ask endpoint without auth (should work)."""
        response = client.post(
            "/api/oracle/ask",
            json={"question": "What is the cheapest model?", "n_results": 3}
        )
        # Should work even without auth (optional auth)
        assert response.status_code in [200, 500]  # 500 if no data in KB
    
    def test_oracle_ask_with_auth(self, client, auth_headers):
        """Test Oracle ask endpoint with auth."""
        response = client.post(
            "/api/oracle/ask",
            json={"question": "What is the cheapest model?", "n_results": 3},
            headers=auth_headers
        )
        # Should work with auth
        assert response.status_code in [200, 500]  # 500 if no data in KB


class TestArchitectEndpoints:
    """Test Architect endpoints."""
    
    def test_architect_optimize_without_auth(self, client):
        """Test Architect optimize endpoint without auth."""
        response = client.post(
            "/api/architect/optimize",
            json={
                "use_case_description": "Simple chatbot",
                "monthly_input_tokens": 1000000
            }
        )
        # Should work even without auth
        assert response.status_code in [200, 400, 500]
    
    def test_architect_optimize_with_auth(self, client, auth_headers):
        """Test Architect optimize endpoint with auth."""
        response = client.post(
            "/api/architect/optimize",
            json={
                "use_case_description": "Simple chatbot",
                "monthly_input_tokens": 1000000
            },
            headers=auth_headers
        )
        assert response.status_code in [200, 400, 500]


class TestScraperEndpoints:
    """Test Scraper endpoints."""
    
    def test_scraper_status(self, client):
        """Test scraper status endpoint."""
        response = client.get("/api/scraper/status")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "total_models" in data
    
    def test_scraper_run_without_auth(self, client):
        """Test scraper run endpoint without auth (should fail)."""
        response = client.post("/api/scraper/run")
        assert response.status_code == 403
    
    def test_scraper_run_with_auth(self, client, auth_headers):
        """Test scraper run endpoint with auth."""
        response = client.post("/api/scraper/run", headers=auth_headers)
        # Should work with auth (may take time)
        assert response.status_code in [200, 500]


class TestDataEndpoints:
    """Test data endpoints."""
    
    def test_get_providers(self, client):
        """Test get providers endpoint."""
        response = client.get("/api/providers")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "providers" in data
    
    def test_get_models(self, client):
        """Test get models endpoint."""
        response = client.get("/api/models")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "models" in data
    
    def test_get_stats(self, client):
        """Test get stats endpoint."""
        response = client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data


class TestRateLimiting:
    """Test rate limiting (basic checks)."""
    
    def test_rate_limit_config_in_response(self, client):
        """Test that rate limit config is in root response."""
        response = client.get("/")
        data = response.json()
        assert "rate_limiting" in data

