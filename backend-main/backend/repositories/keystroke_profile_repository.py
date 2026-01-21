from extensions import db
from models.keystroke_profile import BiometricProfile
from models.user_registration import UserRegistration
import logging

logger = logging.getLogger(__name__)


class KeystrokeProfileRepository:
    """Repository for BiometricProfile (your biometric_profile table)"""
    
    @staticmethod
    def create(user_id, keystroke_features, sample_text="", attempts=1):
        """
        Create biometric profile in YOUR existing table
        """
        try:
            # Get reg_id from user_registration
            registration = UserRegistration.query.filter_by(user_id=user_id).first()
            if not registration:
                raise ValueError(f"No registration found for user_id {user_id}")
            
            profile = BiometricProfile(
                user_id=user_id,
                reg_id=registration.registration_id,
                sample_text=sample_text
            )
            profile.set_keystroke_features(keystroke_features)
            
            db.session.add(profile)
            db.session.commit()
            return profile
            
        except Exception as e:
            db.session.rollback()  # Critical: rollback to release the lock
            logger.error(f"Error creating keystroke profile: {str(e)}")
            raise
    
    @staticmethod
    def find_by_user_id(user_id):
        """Find all biometric profiles for a user"""
        try:
            return BiometricProfile.query.filter_by(user_id=user_id).all()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error finding profiles for user {user_id}: {str(e)}")
            raise
    
    @staticmethod
    def find_latest_by_user_id(user_id):
        """Find the latest biometric profile"""
        try:
            return BiometricProfile.query.filter_by(user_id=user_id).order_by(
                BiometricProfile.created_date.desc()
            ).first()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error finding latest profile for user {user_id}: {str(e)}")
            raise