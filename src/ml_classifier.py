"""
ml_classifier.py

Trains and uses a real machine-learning phishing classifier -- TF-IDF
text vectorization + Random Forest, the same approach used in the
"Random Forest for Phishing Email Detection" paper we referenced
earlier. This is separate from (and complements) the rule-based
detector.py -- the ML model catches patterns in wording/style that
fixed keyword rules can't, while the rules catch structural evidence
(QR codes, domain mismatches, auth failures) the ML model never sees.
"""

import os
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
VECTORIZER_PATH = os.path.join(MODELS_DIR, "tfidf_vectorizer.pkl")
MODEL_PATH = os.path.join(MODELS_DIR, "phishing_classifier.pkl")
METRICS_PATH = os.path.join(MODELS_DIR, "metrics.txt")


def train(texts, labels, test_size: float = 0.2, random_state: int = 42) -> dict:
    """
    Trains the TF-IDF + Random Forest model and saves it to models/.
    Returns a dict of evaluation metrics on a held-out test set.
    """
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=test_size, random_state=random_state, stratify=labels
    )

    vectorizer = TfidfVectorizer(max_features=10000, ngram_range=(1, 2), stop_words="english")
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    model = RandomForestClassifier(n_estimators=200, max_depth=30, n_jobs=-1, random_state=random_state)
    model.fit(X_train_vec, y_train)

    y_pred = model.predict(X_test_vec)

    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "f1_score": f1_score(y_test, y_pred),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "classification_report": classification_report(y_test, y_pred),
        "train_size": len(X_train),
        "test_size": len(X_test),
    }

    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(vectorizer, VECTORIZER_PATH)
    joblib.dump(model, MODEL_PATH)

    with open(METRICS_PATH, "w") as f:
        f.write(f"Train size: {metrics['train_size']}\n")
        f.write(f"Test size: {metrics['test_size']}\n")
        f.write(f"Accuracy:  {metrics['accuracy']:.4f}\n")
        f.write(f"Precision: {metrics['precision']:.4f}\n")
        f.write(f"Recall:    {metrics['recall']:.4f}\n")
        f.write(f"F1 Score:  {metrics['f1_score']:.4f}\n\n")
        f.write("Confusion Matrix (rows=actual, cols=predicted, order=[legit, phishing]):\n")
        f.write(str(metrics["confusion_matrix"]) + "\n\n")
        f.write(metrics["classification_report"])

    return metrics


_vectorizer = None
_model = None


def _load_model():
    global _vectorizer, _model
    if _vectorizer is None or _model is None:
        if not os.path.exists(MODEL_PATH):
            return None, None
        _vectorizer = joblib.load(VECTORIZER_PATH)
        _model = joblib.load(MODEL_PATH)
    return _vectorizer, _model


def predict_proba(text: str) -> float:
    """
    Returns the model's predicted probability (0.0-1.0) that this text
    is phishing. Returns None if no trained model exists yet (caller
    should fall back to rule-based-only scoring in that case).
    """
    vectorizer, model = _load_model()
    if vectorizer is None:
        return None

    vec = vectorizer.transform([text or ""])
    proba = model.predict_proba(vec)[0]
    # proba[1] = probability of the "phishing" class (label 1)
    return float(proba[1]) if len(proba) > 1 else float(proba[0])


def is_model_available() -> bool:
    return os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH)
