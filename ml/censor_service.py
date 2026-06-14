from functools import lru_cache
from pathlib import Path

import joblib


ARTIFACT_PATH = Path(__file__).resolve().parent / "artifacts" / "baseline.joblib"


@lru_cache(maxsize=1)
def load_censor_model():
    return joblib.load(ARTIFACT_PATH)


def score_request(text: str) -> float:
    model_bundle = load_censor_model()
    vectorizer = model_bundle["vectorizer"]
    model = model_bundle["model"]
    threshold = float(model_bundle.get("threshold", 0.5))

    features = vectorizer.transform([text])
    probability = float(model.predict_proba(features)[0][1])
    return probability, threshold


def is_request_allowed(text: str) -> tuple[bool, float, float]:
    probability, threshold = score_request(text)
    return probability < threshold, probability, threshold
