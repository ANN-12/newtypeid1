"""
Validation utility functions for input validation.
"""
import re


def validate_email(email):
    """
    Validate email address format.
    
    Args:
        email: Email address string
    
    Returns:
        True if email is valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_role(role):
    """
    Validate user role.
    
    Allowed roles: student, teacher, admin
    
    Args:
        role: Role string
    
    Returns:
        True if role is valid, False otherwise
    """
    if not role or not isinstance(role, str):
        return False
    
    allowed_roles = ['student', 'teacher', 'admin']
    return role.lower() in allowed_roles


def validate_name(name):
    """
    Validate user name.
    
    Rules:
    - 2 to 100 characters
    - Can contain letters, spaces, hyphens, and apostrophes
    
    Args:
        name: Name string
    
    Returns:
        True if name is valid, False otherwise
    """
    if not name or not isinstance(name, str):
        return False
    
    # Check length
    if len(name.strip()) < 2 or len(name) > 100:
        return False
    
    # Check format: letters, spaces, hyphens, apostrophes
    pattern = r"^[a-zA-Z\s\-']+$"
    return re.match(pattern, name.strip()) is not None
