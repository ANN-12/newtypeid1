"""
UserRegistration model mapping to your existing table
"""
from datetime import datetime
from extensions import db


class UserRegistration(db.Model):
    """Maps to your existing 'user_registration' table"""
    __tablename__ = 'user_registration'
    
    registration_id = db.Column('registration_id', db.Integer, primary_key=True)
    reg_id = db.Column('reg_id', db.Integer, unique=True)
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    password = db.Column('password', db.Text, nullable=False)
    biometriclogin = db.Column('biometriclogin', db.Text)
    registration_date = db.Column('registration_date', db.Text, default=lambda: datetime.utcnow().isoformat())
    
    def __repr__(self):
        return f'<UserRegistration user_id={self.user_id}>'