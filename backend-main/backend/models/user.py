from datetime import datetime
from extensions import db


class User(db.Model):
    """Maps to your existing 'user' table"""
    __tablename__ = 'user'
    
    # Map to your existing columns
    user_id = db.Column('user_id', db.Integer, primary_key=True)
    name = db.Column('name', db.Text, nullable=False)
    email = db.Column('email', db.Text, unique=True, nullable=False)
    created_at = db.Column('created_at', db.Text, default=lambda: datetime.utcnow().isoformat())
    
    # Relationship to biometric_profile
    biometric_profiles = db.relationship(
        'BiometricProfile',
        backref='user',
        lazy=True,
        foreign_keys='BiometricProfile.user_id'
    )
    
    # Relationship to user_registration for password
    registrations = db.relationship(
        'UserRegistration',
        backref='user',
        lazy=True,
        foreign_keys='UserRegistration.user_id'
    )
    
    def __repr__(self):
        return f''
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at
        }