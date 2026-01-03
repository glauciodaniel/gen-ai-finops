"""
Tests for database operations
"""
import pytest
from sqlalchemy.exc import IntegrityError
from db import crud
from db.models import User


class TestUserCRUD:
    """Test CRUD operations for users."""
    
    def test_create_user(self, db_session):
        """Test creating a new user."""
        user = crud.create_user(
            db=db_session,
            username="newuser",
            password="password123",
            email="newuser@example.com"
        )
        
        assert user.id is not None
        assert user.username == "newuser"
        assert user.email == "newuser@example.com"
        assert user.is_active is True
        assert user.is_admin is False
        assert user.hashed_password != "password123"  # Should be hashed
    
    def test_create_user_duplicate_username(self, db_session):
        """Test creating user with duplicate username fails."""
        crud.create_user(
            db=db_session,
            username="duplicate",
            password="pass123"
        )
        
        with pytest.raises(ValueError, match="Username.*already exists"):
            crud.create_user(
                db=db_session,
                username="duplicate",
                password="pass123"
            )
    
    def test_create_user_duplicate_email(self, db_session):
        """Test creating user with duplicate email fails."""
        crud.create_user(
            db=db_session,
            username="user1",
            password="pass123",
            email="same@example.com"
        )
        
        with pytest.raises(ValueError, match="Email.*already exists"):
            crud.create_user(
                db=db_session,
                username="user2",
                password="pass123",
                email="same@example.com"
            )
    
    def test_get_user_by_username(self, db_session, test_user):
        """Test retrieving user by username."""
        user = crud.get_user_by_username(db_session, "testuser")
        
        assert user is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
    
    def test_get_user_by_username_not_found(self, db_session):
        """Test retrieving non-existent user."""
        user = crud.get_user_by_username(db_session, "nonexistent")
        assert user is None
    
    def test_get_user_by_email(self, db_session, test_user):
        """Test retrieving user by email."""
        user = crud.get_user_by_email(db_session, "test@example.com")
        
        assert user is not None
        assert user.username == "testuser"
    
    def test_get_user_by_id(self, db_session, test_user):
        """Test retrieving user by ID."""
        user = crud.get_user_by_id(db_session, test_user.id)
        
        assert user is not None
        assert user.id == test_user.id
        assert user.username == "testuser"
    
    def test_verify_user_password_correct(self, db_session, test_user):
        """Test password verification with correct password."""
        user = crud.verify_user_password(db_session, "testuser", "testpass123")
        
        assert user is not None
        assert user.username == "testuser"
    
    def test_verify_user_password_incorrect(self, db_session, test_user):
        """Test password verification with incorrect password."""
        user = crud.verify_user_password(db_session, "testuser", "wrongpassword")
        
        assert user is None
    
    def test_verify_user_password_nonexistent(self, db_session):
        """Test password verification for non-existent user."""
        user = crud.verify_user_password(db_session, "nonexistent", "password")
        
        assert user is None
    
    def test_update_user(self, db_session, test_user):
        """Test updating user information."""
        updated = crud.update_user(
            db=db_session,
            user_id=test_user.id,
            email="newemail@example.com",
            is_admin=True
        )
        
        assert updated is not None
        assert updated.email == "newemail@example.com"
        assert updated.is_admin is True
    
    def test_update_user_password(self, db_session, test_user):
        """Test updating user password."""
        old_hash = test_user.hashed_password
        
        updated = crud.update_user(
            db=db_session,
            user_id=test_user.id,
            password="newpassword123"
        )
        
        assert updated is not None
        assert updated.hashed_password != old_hash
        # Verify new password works
        verified = crud.verify_user_password(db_session, "testuser", "newpassword123")
        assert verified is not None
    
    def test_update_user_not_found(self, db_session):
        """Test updating non-existent user."""
        updated = crud.update_user(db_session, user_id=99999, email="test@test.com")
        assert updated is None
    
    def test_delete_user(self, db_session, test_user):
        """Test deleting a user."""
        user_id = test_user.id
        result = crud.delete_user(db_session, user_id)
        
        assert result is True
        # Verify user is deleted
        user = crud.get_user_by_id(db_session, user_id)
        assert user is None
    
    def test_delete_user_not_found(self, db_session):
        """Test deleting non-existent user."""
        result = crud.delete_user(db_session, 99999)
        assert result is False
    
    def test_list_users(self, db_session):
        """Test listing users with pagination."""
        # Create multiple users
        for i in range(5):
            crud.create_user(
                db=db_session,
                username=f"user{i}",
                password="pass123"
            )
        
        users = crud.list_users(db_session, skip=0, limit=10)
        assert len(users) >= 5
    
    def test_list_users_pagination(self, db_session):
        """Test user pagination."""
        # Create 10 users
        for i in range(10):
            crud.create_user(
                db=db_session,
                username=f"paguser{i}",
                password="pass123"
            )
        
        # Get first page
        page1 = crud.list_users(db_session, skip=0, limit=5)
        assert len(page1) == 5
        
        # Get second page
        page2 = crud.list_users(db_session, skip=5, limit=5)
        assert len(page2) == 5
        
        # Verify different users
        assert page1[0].username != page2[0].username
    
    def test_list_users_active_only(self, db_session):
        """Test listing only active users."""
        # Create active and inactive users
        active = crud.create_user(db_session, username="active", password="pass123")
        inactive = crud.create_user(db_session, username="inactive", password="pass123")
        crud.update_user(db_session, inactive.id, is_active=False)
        
        active_users = crud.list_users(db_session, active_only=True)
        usernames = [u.username for u in active_users]
        
        assert "active" in usernames
        assert "inactive" not in usernames

