#Keystroke service for managing keystroke biometric data
#DATABASE ONLY - No CSV saving during registration

from repositories.keystroke_profile_repository import KeystrokeProfileRepository


class KeystrokeService:
    """Service layer for keystroke operations"""
    
    def __init__(self):
        self.profile_repo = KeystrokeProfileRepository()
    
    def create_keystroke_profile(self, user_id, keystroke_features, attempts=1):
        """
        Save keystroke profile to DATABASE ONLY
        
        Args:
            user_id: User ID
            keystroke_features: Dictionary with 11 features
            attempts: Attempt number (1-3)
            
        Returns:
            BiometricProfile object
        """
        return self.profile_repo.create(
            user_id=user_id,
            keystroke_features=keystroke_features,
            sample_text=f"Registration attempt {attempts}",
            attempts=attempts
        )
    
    def get_user_profiles(self, user_id):
        """Get all keystroke profiles for a user from database"""
        return self.profile_repo.find_by_user_id(user_id)