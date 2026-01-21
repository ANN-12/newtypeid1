"""
BiometricProfile model mapping to your existing table
"""
from datetime import datetime
from extensions import db
import json


class BiometricProfile(db.Model):
    """Maps to your existing 'biometric_profile' table"""
    __tablename__ = 'biometric_profile'
    
    biometric_id = db.Column('biometric_id', db.Integer, primary_key=True)
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    reg_id = db.Column('reg_id', db.Integer, db.ForeignKey('user_registration.registration_id'), nullable=False)
    sample_text = db.Column('sample_text', db.Text)
    typing_pattern = db.Column('typing_pattern', db.Text)
    created_date = db.Column('created_date', db.Text, default=lambda: datetime.utcnow().isoformat())
    last_updated = db.Column('last_updated', db.Text, default=lambda: datetime.utcnow().isoformat())
    
    def set_keystroke_features(self, features_dict):
        """Store features as JSON string"""
        self.typing_pattern = json.dumps(features_dict)
    
    def get_keystroke_features(self):
        """Retrieve features as dictionary"""
        if self.typing_pattern:
            return json.loads(self.typing_pattern)
        return {}
    
    def __repr__(self):
        return f'<BiometricProfile user_id={self.user_id}>'