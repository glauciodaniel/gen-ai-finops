"""
CRUD operations for database models
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from db.models import User
from utils.auth import get_password_hash, verify_password


def create_user(
    db: Session,
    username: str,
    password: str,
    email: Optional[str] = None,
    is_admin: bool = False
) -> User:
    """
    Create a new user in the database.
    
    Args:
        db: Database session
        username: Unique username
        password: Plain text password (will be hashed)
        email: Optional email address
        is_admin: Whether user is an admin
    
    Returns:
        User: Created user object
    
    Raises:
        ValueError: If username or email already exists
    """
    hashed_password = get_password_hash(password)
    
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        is_admin=is_admin
    )
    
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError as e:
        db.rollback()
        if "username" in str(e.orig).lower():
            raise ValueError(f"Username '{username}' already exists")
        elif "email" in str(e.orig).lower():
            raise ValueError(f"Email '{email}' already exists")
        raise ValueError("User creation failed due to constraint violation")


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username."""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def verify_user_password(db: Session, username: str, password: str) -> Optional[User]:
    """
    Verify user credentials.
    
    Args:
        db: Database session
        username: Username
        password: Plain text password
    
    Returns:
        User if credentials are valid, None otherwise
    """
    user = get_user_by_username(db, username)
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    if not user.is_active:
        return None
    
    return user


def update_user(
    db: Session,
    user_id: int,
    username: Optional[str] = None,
    email: Optional[str] = None,
    password: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_admin: Optional[bool] = None
) -> Optional[User]:
    """
    Update user information.
    
    Args:
        db: Database session
        user_id: User ID to update
        username: New username (optional)
        email: New email (optional)
        password: New password (optional, will be hashed)
        is_active: New active status (optional)
        is_admin: New admin status (optional)
    
    Returns:
        Updated User object, or None if user not found
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    
    if username is not None:
        user.username = username
    if email is not None:
        user.email = email
    if password is not None:
        user.hashed_password = get_password_hash(password)
    if is_active is not None:
        user.is_active = is_active
    if is_admin is not None:
        user.is_admin = is_admin
    
    try:
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError as e:
        db.rollback()
        raise ValueError("Update failed due to constraint violation")


def delete_user(db: Session, user_id: int) -> bool:
    """
    Delete a user from the database.
    
    Args:
        db: Database session
        user_id: User ID to delete
    
    Returns:
        True if deleted, False if user not found
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    
    db.delete(user)
    db.commit()
    return True


def list_users(db: Session, skip: int = 0, limit: int = 100, active_only: bool = False) -> List[User]:
    """
    List users with pagination.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        active_only: Only return active users
    
    Returns:
        List of User objects
    """
    query = db.query(User)
    
    if active_only:
        query = query.filter(User.is_active == True)
    
    return query.offset(skip).limit(limit).all()

