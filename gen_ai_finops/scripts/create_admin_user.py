#!/usr/bin/env python3
"""
Script to create an admin user in the database
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from db.database import SessionLocal
from db import crud
from dotenv import load_dotenv

load_dotenv()


def create_admin_user(username: str = "admin", password: str = "admin123", email: str = None):
    """Create an admin user."""
    db = SessionLocal()
    try:
        # Check if user already exists
        existing = crud.get_user_by_username(db, username)
        if existing:
            print(f"User '{username}' already exists!")
            return False
        
        # Create admin user
        user = crud.create_user(
            db=db,
            username=username,
            password=password,
            email=email,
            is_admin=True
        )
        
        print(f"Admin user '{username}' created successfully!")
        print(f"User ID: {user.id}")
        print(f"Email: {user.email or 'N/A'}")
        return True
    
    except ValueError as e:
        print(f"Error: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Create an admin user")
    parser.add_argument("--username", default="admin", help="Username (default: admin)")
    parser.add_argument("--password", default="admin123", help="Password (default: admin123)")
    parser.add_argument("--email", help="Email address (optional)")
    
    args = parser.parse_args()
    
    create_admin_user(args.username, args.password, args.email)

