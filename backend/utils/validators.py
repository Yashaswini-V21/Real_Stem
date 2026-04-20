"""Data validators"""
import re
from typing import Optional


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_username(username: str) -> bool:
    """Validate username format"""
    return len(username) >= 3 and len(username) <= 50 and username.isalnum()


def validate_password(password: str) -> bool:
    """Validate password strength"""
    return len(password) >= 8


def validate_url(url: str) -> bool:
    """Validate URL format"""
    pattern = r'^https?://'
    return re.match(pattern, url) is not None
