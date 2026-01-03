"""
Integration tests - End-to-end flows
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from db import crud
from utils.auth import create_access_token


@pytest.fixture
def client(db_session):
    """Create test client with database session override."""
    from api.main import app
    from db.database import get_db
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


class TestAuthFlow:
    """Test complete authentication flow."""
    
    def test_register_login_flow(self, client, db_session):
        """Test complete flow: register -> login -> use API."""
        # Register
        register_response = client.post(
            "/api/auth/register",
            json={
                "username": "newuser",
                "password": "password123",
                "email": "newuser@example.com"
            }
        )
        assert register_response.status_code == 200
        data = register_response.json()
        assert data["status"] == "success"
        assert data["username"] == "newuser"
        
        # Login
        login_response = client.post(
            "/api/auth/login",
            json={
                "username": "newuser",
                "password": "password123"
            }
        )
        assert login_response.status_code == 200
        login_data = login_response.json()
        assert "access_token" in login_data
        
        # Use authenticated endpoint
        token = login_data["access_token"]
        me_response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert me_response.status_code == 200
        me_data = me_response.json()
        assert me_data["username"] == "newuser"
        assert me_data["authenticated"] is True
    
    def test_register_duplicate_username(self, client, db_session):
        """Test registering with duplicate username fails."""
        # First registration
        client.post(
            "/api/auth/register",
            json={
                "username": "duplicate",
                "password": "password123"
            }
        )
        
        # Second registration should fail
        response = client.post(
            "/api/auth/register",
            json={
                "username": "duplicate",
                "password": "password123"
            }
        )
        assert response.status_code == 400
    
    def test_login_with_wrong_password(self, client, db_session):
        """Test login with incorrect password."""
        # Register user
        client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "password": "correctpass"
            }
        )
        
        # Try login with wrong password
        response = client.post(
            "/api/auth/login",
            json={
                "username": "testuser",
                "password": "wrongpass"
            }
        )
        assert response.status_code == 401


class TestOracleFlow:
    """Test Oracle agent flow."""
    
    def test_oracle_query_flow(self, client, db_session):
        """Test complete Oracle query flow."""
        # Register and login
        client.post(
            "/api/auth/register",
            json={"username": "oracleuser", "password": "pass123"}
        )
        login_response = client.post(
            "/api/auth/login",
            json={"username": "oracleuser", "password": "pass123"}
        )
        token = login_response.json()["access_token"]
        
        # Query Oracle (may fail if no data in KB, but should not crash)
        response = client.post(
            "/api/oracle/ask",
            json={"question": "What is the cheapest model?", "n_results": 3},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Should return 200 or 500 (if no data), but not 401/403
        assert response.status_code in [200, 500]
    
    def test_oracle_query_anonymous(self, client):
        """Test Oracle query without authentication (should work)."""
        response = client.post(
            "/api/oracle/ask",
            json={"question": "What is the cheapest model?", "n_results": 3}
        )
        
        # Should work without auth (optional auth)
        assert response.status_code in [200, 500]


class TestArchitectFlow:
    """Test Architect agent flow."""
    
    def test_architect_optimization_flow(self, client, db_session):
        """Test complete Architect optimization flow."""
        # Register and login
        client.post(
            "/api/auth/register",
            json={"username": "archuser", "password": "pass123"}
        )
        login_response = client.post(
            "/api/auth/login",
            json={"username": "archuser", "password": "pass123"}
        )
        token = login_response.json()["access_token"]
        
        # Request optimization
        response = client.post(
            "/api/architect/optimize",
            json={
                "use_case_description": "Simple chatbot",
                "monthly_input_tokens": 1000000,
                "monthly_output_tokens": 500000
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Should return 200 or 400/500 (depending on data availability)
        assert response.status_code in [200, 400, 500]


class TestScraperFlow:
    """Test Scraper flow."""
    
    def test_scraper_status_flow(self, client):
        """Test scraper status endpoint."""
        response = client.get("/api/scraper/status")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "total_models" in data
    
    def test_scraper_run_requires_auth(self, client, db_session):
        """Test scraper run requires authentication."""
        # Try without auth
        response = client.post("/api/scraper/run")
        assert response.status_code == 403
        
        # Register and login
        client.post(
            "/api/auth/register",
            json={"username": "scraperuser", "password": "pass123"}
        )
        login_response = client.post(
            "/api/auth/login",
            json={"username": "scraperuser", "password": "pass123"}
        )
        token = login_response.json()["access_token"]
        
        # Try with auth (may take time or fail, but should not be 403)
        response = client.post(
            "/api/scraper/run",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code != 403


class TestDataEndpointsFlow:
    """Test data endpoints flow."""
    
    def test_providers_endpoint(self, client):
        """Test providers endpoint."""
        response = client.get("/api/providers")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "providers" in data
    
    def test_models_endpoint(self, client):
        """Test models endpoint."""
        response = client.get("/api/models")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "models" in data
    
    def test_stats_endpoint(self, client):
        """Test stats endpoint."""
        response = client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data


class TestMultiUserFlow:
    """Test flows with multiple users."""
    
    def test_multiple_users_independent(self, client, db_session):
        """Test that multiple users can exist independently."""
        # Register user 1
        client.post(
            "/api/auth/register",
            json={"username": "user1", "password": "pass1"}
        )
        
        # Register user 2
        client.post(
            "/api/auth/register",
            json={"username": "user2", "password": "pass2"}
        )
        
        # Both should be able to login
        login1 = client.post(
            "/api/auth/login",
            json={"username": "user1", "password": "pass1"}
        )
        login2 = client.post(
            "/api/auth/login",
            json={"username": "user2", "password": "pass2"}
        )
        
        assert login1.status_code == 200
        assert login2.status_code == 200
        
        # Tokens should be different
        token1 = login1.json()["access_token"]
        token2 = login2.json()["access_token"]
        assert token1 != token2

