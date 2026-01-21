import joblib
import numpy as np
import os
from collections import Counter

# -----------------------------
# Load artifacts
# -----------------------------
ARTIFACT_DIR = os.path.join(os.path.dirname(__file__), "artifacts")

model = joblib.load(os.path.join(ARTIFACT_DIR, "xgb_model_raw.pkl"))
scaler = joblib.load(os.path.join(ARTIFACT_DIR, "scaler_raw.pkl"))
encoder = joblib.load(os.path.join(ARTIFACT_DIR, "encoder_raw.pkl"))
feature_cols = joblib.load(os.path.join(ARTIFACT_DIR, "feature_cols_raw.pkl"))


def predict_user(feature_list):
    """
    Predict user from keystroke feature samples

    Args:
        feature_list (list[dict]): list of keystroke feature dicts

    Returns:
        dict: {
            "predicted_user": str,
            "confidence": float,
            "raw_predictions": list
        }
    """

    if not feature_list:
        return {
            "predicted_user": "unknown",
            "confidence": 0.0,
            "raw_predictions": []
        }

    # -----------------------------
    # Build feature matrix
    # -----------------------------
    X = np.array([
        [float(sample.get(f, 0)) for f in feature_cols]
        for sample in feature_list
    ])

    # Scale
    X_scaled = scaler.transform(X)

    # Predict encoded labels
    encoded_preds = model.predict(X_scaled)

    # Decode labels → usernames
    decoded_preds = encoder.inverse_transform(encoded_preds)

    # -----------------------------
    # Majority voting
    # -----------------------------
    counts = Counter(decoded_preds)

    predicted_user, vote_count = counts.most_common(1)[0]
    confidence = (vote_count / len(decoded_preds)) * 100

    return {
        "predicted_user": predicted_user,
        "confidence": round(confidence, 2),
        "raw_predictions": decoded_preds.tolist()
    }


# -----------------------------
# Test
# -----------------------------
if __name__ == "__main__":
    dummy = [{f: 0 for f in feature_cols}]
    print(predict_user(dummy))
