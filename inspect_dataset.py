"""
inspect_dataset.py

Run this FIRST after downloading the Kaggle dataset. It looks inside
data/raw/, finds any CSV files, and prints their column names and a
few sample rows -- this tells us exactly how to write the cleaning
script next (every Kaggle dataset names its columns differently).

Run with:
    python inspect_dataset.py
"""

import os
import pandas as pd

RAW_DIR = os.path.join("data", "raw")


def main():
    print(f"Looking inside: {os.path.abspath(RAW_DIR)}\n")

    csv_files = []
    for root, _, files in os.walk(RAW_DIR):
        for f in files:
            if f.lower().endswith(".csv"):
                csv_files.append(os.path.join(root, f))

    if not csv_files:
        print("No CSV files found. Make sure the dataset is unzipped inside data/raw/.")
        return

    print(f"Found {len(csv_files)} CSV file(s):\n")

    for path in csv_files:
        print("=" * 70)
        print(f"FILE: {path}")
        try:
            df = pd.read_csv(path, nrows=5)
            print(f"Columns: {list(df.columns)}")
            print(f"Shape (first 5 rows shown): {df.shape}")
            print("\nSample data:")
            print(df.head(3).to_string())
        except Exception as e:
            print(f"Could not read this file: {e}")
        print()


if __name__ == "__main__":
    main()
