"""
FIXED Authentication service using ML model + Statistical Matching
Two-Layer Authentication:
1. Statistical matching against registered samples in database
2. ML model prediction
"""

import sys
import os
import numpy as np
from scipy.spatial.distance import euclidean
from scipy.stats import zscore
from collections import Counter

# ---------------------------------------------------
# ML MODEL PATH FIX (folder name has space)
# ---------------------------------------------------
current_file = os.path.abspath(__file__)
services_dir = os.path.dirname(current_file)
backend_dir = os.path.dirname(services_dir)
backend_main_dir = os.path.dirname(backend_dir)
typing_inner = os.path.dirname(backend_main_dir)
typing_outer = os.path.dirname(typing_inner)

ml_model_path = os.path.join(typing_outer, "ml model")

print(f"🔍 Current file: {current_file}")
print(f"🔍 ML Model Path: {ml_model_path}")
print(f"📁 ML Model exists: {os.path.exists(ml_model_path)}")
print(f"📁 predict.py exists: {os.path.exists(os.path.join(ml_model_path, 'predict.py'))}")

if os.path.exists(ml_model_path):
    sys.path.insert(0, ml_model_path)
    print(f"✅ Added {ml_model_path} to sys.path")
else:
    print("❌ ML Model path does not exist")

# Import predict_user
try:
    from predict import predict_user
    print("✅ Successfully imported predict_user")
except Exception as e:
    print(f"❌ Failed to import predict_user: {e}")
    def predict_user(x):
        return {
            "predicted_user": "unknown",
            "confidence": 0.0,
            "raw_predictions": []
        }

from services.user_service import UserService


# ===================================================
# AUTH SERVICE (FIXED)
# ===================================================
class AuthService:
    def __init__(self):
        self.user_service = UserService()
        
        # Thresholds
        self.STATISTICAL_THRESHOLD = 0.65   # 65% similarity required
        self.ML_CONFIDENCE_THRESHOLD = 30.0  # 30% confidence required (0-100 scale)

    # ---------------------------------------------------
    # MAIN AUTH FUNCTION
    # ---------------------------------------------------
    def authenticate_user(self, username, keystroke_features_list):
        """
        Two-layer authentication:
        1. Statistical matching against stored DB samples
        2. ML model prediction
        
        Both must pass for authentication to succeed
        """
        print(f"\n{'='*80}")
        print(f"🔐 AUTHENTICATION REQUEST for user: {username}")
        print(f"{'='*80}")

        # Find user in database
        user = self.user_service.find_user_by_name(username)
        if not user:
            print("❌ User not found in database")
            return {
                "authenticated": False,
                "message": "User not found",
                "user": None,
                "details": None
            }

        # Get registered samples from database
        registered_samples = self.user_service.get_user_keystroke_samples(username)
        if not registered_samples or len(registered_samples) < 3:
            print(f"⚠️  Insufficient registered samples: {len(registered_samples) if registered_samples else 0}")
            return {
                "authenticated": False,
                "message": "Insufficient training data. Please register first.",
                "user": None,
                "details": None
            }

        print(f"✅ Found {len(registered_samples)} registered samples for {username}")

        # ---------------- LAYER 1: Statistical Matching ----------------
        print(f"\n{'─'*80}")
        print("📊 LAYER 1: Statistical Matching Against Database Samples")
        print(f"{'─'*80}")
        
        statistical_score = self.statistical_matching(
            keystroke_features_list,
            registered_samples
        )
        
        statistical_pass = statistical_score >= self.STATISTICAL_THRESHOLD
        
        print(f"\n   📈 Statistical Score: {statistical_score:.2%}")
        print(f"   🎯 Threshold: {self.STATISTICAL_THRESHOLD:.2%}")
        print(f"   {'✅ PASSED' if statistical_pass else '❌ FAILED'}")

        # ---------------- LAYER 2: ML Model Prediction ----------------
        print(f"\n{'─'*80}")
        print("🤖 LAYER 2: ML Model Prediction")
        print(f"{'─'*80}")
        
        predicted_user, ml_confidence = self.predict_user_from_keystroke(
            keystroke_features_list
        )

        ml_user_match = predicted_user.lower() == username.lower()
        ml_confidence_pass = ml_confidence >= self.ML_CONFIDENCE_THRESHOLD
        ml_pass = ml_user_match and ml_confidence_pass

        print(f"\n   🎯 Expected User: {username}")
        print(f"   🤖 Predicted User: {predicted_user}")
        print(f"   📊 Confidence: {ml_confidence:.2f}%")
        print(f"   🎯 Threshold: {self.ML_CONFIDENCE_THRESHOLD:.2f}%")
        print(f"   {'✅ User Match: YES' if ml_user_match else '❌ User Match: NO'}")
        print(f"   {'✅ Confidence Pass: YES' if ml_confidence_pass else '❌ Confidence Pass: NO'}")
        print(f"   {'✅ PASSED' if ml_pass else '❌ FAILED'}")

        # ---------------- FINAL DECISION ----------------
        print(f"\n{'='*80}")
        print("🎯 AUTHENTICATION DECISION")
        print(f"{'='*80}")
        
        # BOTH layers must pass
        authenticated = statistical_pass and ml_pass

        print(f"   Layer 1 (Statistical): {'✅ PASS' if statistical_pass else '❌ FAIL'}")
        print(f"   Layer 2 (ML Model):     {'✅ PASS' if ml_pass else '❌ FAIL'}")
        print(f"\n   {'🎉 AUTHENTICATION SUCCESSFUL' if authenticated else '🚫 AUTHENTICATION FAILED'}")
        print(f"{'='*80}\n")

        if authenticated:
            message = "Authentication successful - Both statistical and ML verification passed"
        else:
            reasons = []
            if not statistical_pass:
                reasons.append(f"statistical match too low ({statistical_score:.1%} < {self.STATISTICAL_THRESHOLD:.1%})")
            if not ml_user_match:
                reasons.append(f"predicted user mismatch (got '{predicted_user}', expected '{username}')")
            if not ml_confidence_pass:
                reasons.append(f"confidence too low ({ml_confidence:.1f}% < {self.ML_CONFIDENCE_THRESHOLD:.1f}%)")
            message = f"Authentication failed: {', '.join(reasons)}"

        return {
            "authenticated": authenticated,
            "user": user if authenticated else None,
            "message": message,
            "details": {
                "statistical_match": {
                    "score": statistical_score,
                    "passed": statistical_pass,
                    "threshold": self.STATISTICAL_THRESHOLD
                },
                "ml_prediction": {
                    "predicted_user": predicted_user,
                    "confidence": ml_confidence,
                    "user_match": ml_user_match,
                    "confidence_pass": ml_confidence_pass,
                    "passed": ml_pass,
                    "threshold": self.ML_CONFIDENCE_THRESHOLD
                }
            }
        }

    # ---------------------------------------------------
    # STATISTICAL MATCHING
    # ---------------------------------------------------
    def statistical_matching(self, login_samples, registered_samples):
        """
        Compare login keystroke features against stored registration samples
        Uses cosine similarity of normalized feature vectors
        """
        try:
            # Extract feature vectors from login samples
            login_vectors = [self._extract_feature_vector(s) for s in login_samples]
            login_avg = np.mean(login_vectors, axis=0)
            
            print(f"   📥 Login samples: {len(login_samples)}")
            print(f"   📥 Login avg vector: {login_avg[:3]}... (showing first 3)")

            # Extract feature vectors from registered samples
            reg_vectors = [self._extract_feature_vector(s) for s in registered_samples]
            reg_avg = np.mean(reg_vectors, axis=0)
            
            print(f"   📊 Registered samples: {len(registered_samples)}")
            print(f"   📊 Registered avg vector: {reg_avg[:3]}... (showing first 3)")

            # Calculate similarity
            similarity = self._calculate_similarity(login_avg, reg_avg)
            
            return similarity

        except Exception as e:
            print(f"   ⚠️  Statistical matching error: {e}")
            import traceback
            traceback.print_exc()
            return 0.0

    # ---------------------------------------------------
    # FEATURE EXTRACTION (FIXED ORDER)
    # ---------------------------------------------------
    def _extract_feature_vector(self, sample):
        """
        Extract feature vector in the EXACT order used during training
        CRITICAL: Must match train_model.py feature order
        """
        if isinstance(sample, list):
            sample = sample[0]

        # EXACT order from training
        feature_keys = [
            "ks_count", "ks_rate",
            "dwell_mean", "dwell_std",
            "flight_mean", "flight_std",
            "digraph_mean", "digraph_std",
            "backspace_rate", "wps", "wpm"
        ]

        vector = []
        for key in feature_keys:
            value = sample.get(key, 0.0)
            # Handle None values
            if value is None:
                value = 0.0
            vector.append(float(value))
        
        return np.array(vector)

    # ---------------------------------------------------
    # SIMILARITY CALCULATION
    # ---------------------------------------------------
    def _calculate_similarity(self, v1, v2):
        """
        Calculate similarity between two feature vectors
        Uses z-score normalization + exponential distance
        """
        try:
            # Normalize using z-score
            v1_norm = np.nan_to_num(zscore(v1))
            v2_norm = np.nan_to_num(zscore(v2))
            
            # Calculate Euclidean distance
            distance = euclidean(v1_norm, v2_norm)
            
            # Convert distance to similarity (0-1 scale)
            # Lower distance = higher similarity
            similarity = np.exp(-distance / len(v1))
            
            return float(similarity)
            
        except Exception as e:
            print(f"      ⚠️  Similarity calculation error: {e}")
            return 0.0

    # ---------------------------------------------------
    # ML PREDICTION (FIXED)
    # ---------------------------------------------------
    def predict_user_from_keystroke(self, keystroke_features_list):
        """
        Use ML model to predict user from keystroke features
        
        Returns:
            (predicted_user, confidence)
            confidence is on 0-100 scale
        """
        try:
            result = predict_user(keystroke_features_list)

            predicted_user = result.get("predicted_user", "unknown")
            confidence = result.get("confidence", 0.0)  # Already in 0-100 scale from fixed predict.py

            print(f"   🤖 ML Model returned:")
            print(f"      User: {predicted_user}")
            print(f"      Confidence: {confidence}%")
            print(f"      Raw predictions: {result.get('raw_predictions', [])}")

            return predicted_user, confidence

        except Exception as e:
            print(f"   ❌ ML Prediction error: {e}")
            import traceback
            traceback.print_exc()
            return "unknown", 0.0