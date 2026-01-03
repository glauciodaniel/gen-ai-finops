#!/usr/bin/env python3
"""
Validation script for GenAIFinOps improvements
Checks if all new features are properly implemented
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("="*70)
print("GenAIFinOps - Implementation Validation")
print("="*70)

errors = []
warnings = []

# Check 1: Dependencies
print("\n1. Checking dependencies...")
try:
    import fastapi
    print("   [OK] FastAPI installed")
except ImportError:
    errors.append("FastAPI not installed")
    print("   [ERROR] FastAPI not installed")

try:
    from jose import jwt
    print("   [OK] python-jose installed")
except ImportError:
    errors.append("python-jose not installed")
    print("   [ERROR] python-jose not installed (required for JWT)")

try:
    from passlib.context import CryptContext
    print("   [OK] passlib installed")
except ImportError:
    errors.append("passlib not installed")
    print("   [ERROR] passlib not installed (required for password hashing)")

try:
    from slowapi import Limiter
    print("   [OK] slowapi installed")
except ImportError:
    errors.append("slowapi not installed")
    print("   [ERROR] slowapi not installed (required for rate limiting)")

try:
    from pythonjsonlogger import jsonlogger
    print("   [OK] python-json-logger installed")
except ImportError:
    warnings.append("python-json-logger not installed (optional, falls back to standard logging)")
    print("   [WARN] python-json-logger not installed (optional)")

# Check 2: Files exist
print("\n2. Checking file structure...")
required_files = [
    "utils/auth.py",
    "utils/logger.py",
    "utils/rate_limit.py",
    "api/models.py",
    "api/main.py",
    "env.example",
    "tests/test_auth.py",
    "tests/test_api.py",
    "tests/test_logger.py",
    "tests/test_rate_limit.py",
]

for file in required_files:
    file_path = Path(__file__).parent / file
    if file_path.exists():
        print(f"   [OK] {file}")
    else:
        errors.append(f"Missing file: {file}")
        print(f"   [ERROR] Missing: {file}")

# Check 3: Code imports
print("\n3. Checking code imports...")
try:
    from utils.auth import (
        verify_password, get_password_hash, create_access_token,
        get_current_user, get_current_user_optional
    )
    print("   [OK] Authentication utilities importable")
except Exception as e:
    errors.append(f"Auth import error: {str(e)}")
    print(f"   [ERROR] Auth import error: {str(e)}")

try:
    from utils.logger import logger, StructuredLogger
    print("   [OK] Logger importable")
except Exception as e:
    errors.append(f"Logger import error: {str(e)}")
    print(f"   [ERROR] Logger import error: {str(e)}")

try:
    from utils.rate_limit import (
        setup_rate_limiting, rate_limit_decorator, get_rate_limit_config
    )
    print("   [OK] Rate limiting utilities importable")
except Exception as e:
    errors.append(f"Rate limit import error: {str(e)}")
    print(f"   [ERROR] Rate limit import error: {str(e)}")

try:
    from api.models import LoginRequest, TokenResponse, UserResponse
    print("   [OK] Auth models importable")
except Exception as e:
    errors.append(f"Auth models import error: {str(e)}")
    print(f"   [ERROR] Auth models import error: {str(e)}")

# Check 4: API endpoints
print("\n4. Checking API endpoints...")
try:
    from api.main import app
    routes = [route.path for route in app.routes]
    
    required_routes = [
        "/",
        "/health",
        "/api/auth/login",
        "/api/auth/me",
        "/api/oracle/ask",
        "/api/architect/optimize",
    ]
    
    for route in required_routes:
        if route in routes:
            print(f"   [OK] {route}")
        else:
            errors.append(f"Missing route: {route}")
            print(f"   [ERROR] Missing route: {route}")
    
    print(f"   Total routes: {len(routes)}")
except Exception as e:
    errors.append(f"API import error: {str(e)}")
    print(f"   [ERROR] API import error: {str(e)}")

# Check 5: Environment variables
print("\n5. Checking environment configuration...")
env_file = Path(__file__).parent / "env.example"
if env_file.exists():
    print("   [OK] env.example exists")
    content = env_file.read_text()
    required_vars = [
        "JWT_SECRET_KEY",
        "RATE_LIMIT_ENABLED",
        "LOG_LEVEL",
        "CORS_ORIGINS"
    ]
    for var in required_vars:
        if var in content:
            print(f"   [OK] {var} in env.example")
        else:
            warnings.append(f"{var} not in env.example")
            print(f"   [WARN] {var} not in env.example")
else:
    errors.append("env.example not found")
    print("   [ERROR] env.example not found")

# Check 6: Dependencies in requirements.txt
print("\n6. Checking requirements.txt...")
req_file = Path(__file__).parent / "requirements.txt"
if req_file.exists():
    content = req_file.read_text()
    required_packages = [
        "fastapi",
        "python-jose",
        "passlib",
        "slowapi",
        "python-json-logger"
    ]
    for pkg in required_packages:
        if pkg in content:
            print(f"   [OK] {pkg} in requirements.txt")
        else:
            warnings.append(f"{pkg} not in requirements.txt")
            print(f"   [WARN] {pkg} not in requirements.txt")

# Summary
print("\n" + "="*70)
print("Validation Summary")
print("="*70)

if errors:
    print(f"\n[ERROR] Errors found: {len(errors)}")
    for error in errors:
        print(f"   - {error}")
else:
    print("\n[OK] No critical errors found!")

if warnings:
    print(f"\n[WARN] Warnings: {len(warnings)}")
    for warning in warnings:
        print(f"   - {warning}")

if not errors and not warnings:
    print("\n[SUCCESS] All checks passed! Implementation is complete.")
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Copy env.example to .env and configure")
    print("3. Run tests: pytest tests/ -v")
    print("4. Start server: python main.py server")
else:
    if errors:
        print("\n⚠️  Please fix the errors above before proceeding.")
        sys.exit(1)
    else:
        print("\n✅ Implementation complete with minor warnings.")
        sys.exit(0)

