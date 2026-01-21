"""
Password utility functions for hashing and verification.
"""
import bcrypt


def hash_password(password):
    """
    Hash a plain text password using bcrypt.
    
    Args:
        password: Plain text password string
    
    Returns:
        Hashed password string (UTF-8 encoded)
    """
    # Generate salt and hash the password
    salt = bcrypt.gensalt()
    password_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(password, password_hash):
    """
    Verify a plain text password against a hash.
    
    Args:
        password: Plain text password string
        password_hash: Hashed password string
    
    Returns:
        True if password matches, False otherwise
    """
    password_bytes = password.encode('utf-8')
    hash_bytes = password_hash.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hash_bytes)
