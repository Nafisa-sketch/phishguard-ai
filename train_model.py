"""
train_model.py

Loads the Kaggle phishing dataset (data/raw/Phishing_Email/phishing_email.csv),
trains the TF-IDF + Random Forest classifier, and prints evaluation
metrics (accuracy, precision, recall, F1, confusion matrix).

Run with:
    python train_model.py
"""

import sys
import os
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src import ml_classifier

DATASET_PATH = os.path.join("data", "raw", "Phishing_Email", "phishing_email.csv")


def main():
    if not os.path.exists(DATASET_PATH):
        print(f"Dataset not found at {DATASET_PATH}")
        print("Make sure phishing_email.csv is inside data/raw/Phishing_Email/")
        return

    print(f"Loading dataset from {DATASET_PATH} ...")
    df = pd.read_csv(DATASET_PATH)
    print(f"Loaded {len(df)} rows.")

    # Drop rows with missing text or label -- can't train on those
    df = df.dropna(subset=["text_combined", "label"])
    print(f"{len(df)} rows remain after dropping missing values.")

    print("\nLabel distribution:")
    print(df["label"].value_counts())

    texts = df["text_combined"].astype(str).tolist()
    labels = df["label"].astype(int).tolist()

    print("\nTraining TF-IDF + Random Forest model (this may take a few minutes)...")
    metrics = ml_classifier.train(texts, labels)

    print("\n" + "=" * 50)
    print("EVALUATION RESULTS")
    print("=" * 50)
    print(f"Train size: {metrics['train_size']}")
    print(f"Test size:  {metrics['test_size']}")
    print(f"Accuracy:   {metrics['accuracy']:.4f}")
    print(f"Precision:  {metrics['precision']:.4f}")
    print(f"Recall:     {metrics['recall']:.4f}")
    print(f"F1 Score:   {metrics['f1_score']:.4f}")
    print("\nConfusion Matrix:")
    print(metrics["confusion_matrix"])
    print("\nFull classification report:")
    print(metrics["classification_report"])
    print("\nModel saved to models/phishing_classifier.pkl")
    print("Metrics saved to models/metrics.txt")


if __name__ == "__main__":
    main()
