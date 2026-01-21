from models.user import User
from models.user_registration import UserRegistration
from extensions import db


class UserRepository:
    """Repository for User model database operations."""
    
    def create_user(self, name, email):
        """Create user in 'user' table"""
        user = User(name=name, email=email)
        db.session.add(user)
        db.session.commit()
        return user
    
    def create_registration(self, user_id, password_hash):
        """Create entry in 'user_registration' table"""
        registration = UserRegistration(
            user_id=user_id,
            reg_id=user_id,  # Use user_id as reg_id
            password=password_hash,
            biometriclogin='enabled'
        )
        db.session.add(registration)
        db.session.commit()
        return registration
    
    def find_by_email(self, email):
        """Find user by email"""
        return User.query.filter_by(email=email).first()
    
    def find_by_name(self, name):
        """Find user by name"""
        return User.query.filter_by(name=name).first()
    
    def find_by_id(self, user_id):
        """Find user by ID"""
        return User.query.filter_by(user_id=user_id).first()
    
    def get_user_password(self, user_id):
        """Get hashed password from user_registration"""
        registration = UserRegistration.query.filter_by(user_id=user_id).first()
        return registration.password if registration else None