"""
train_from_csv.py  --  Train TruthGuard on REAL datasets (CSV files)
====================================================================

This lets you replace the small built-in dataset with large, real-world data.

WHAT TO DOWNLOAD (free Kaggle accounts):
  * Fake news  -> "Fake and Real News Dataset" (Clement Bisaillon)
                  gives you  Fake.csv  and  True.csv
  * Spam       -> "SMS Spam Collection Dataset"
                  gives you  spam.csv

WHERE TO PUT THEM:
  Create a folder called  realdata  next to this script and drop the files in:

      backend/
        train_from_csv.py
        realdata/
          Fake.csv
          True.csv
          spam.csv

HOW TO RUN (from inside the backend folder):

      python train_from_csv.py

  It trains both models, prints accuracy, and saves them to  models/
  so that app.py will use YOUR trained models automatically.

You can also train just one:
      python train_from_csv.py fake
      python train_from_csv.py spam
"""

import os
import sys
import pandas as pd

# reuse the exact same pipeline + paths the app already uses
from model import _make_pipeline, FAKE_MODEL_PATH, SPAM_MODEL_PATH
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, classification_report
import joblib

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "realdata")


def _find(*names):
    """Find the first file that exists (case-insensitive) among given names."""
    for n in names:
        p = os.path.join(DATA_DIR, n)
        if os.path.exists(p):
            return p
    # case-insensitive fallback
    if os.path.isdir(DATA_DIR):
        low = {f.lower(): f for f in os.listdir(DATA_DIR)}
        for n in names:
            if n.lower() in low:
                return os.path.join(DATA_DIR, low[n.lower()])
    return None


def _train(texts, labels, save_path, title):
    print(f"\n=== Training: {title} ===")
    print(f"Total samples: {len(texts):,}  |  positive(1)={sum(labels):,}  negative(0)={len(labels)-sum(labels):,}")

    X_tr, X_te, y_tr, y_te = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )
    pipe = _make_pipeline("lr")
    print("Fitting model... (this can take a minute on big data)")
    pipe.fit(X_tr, y_tr)

    preds = pipe.predict(X_te)
    acc = accuracy_score(y_te, preds)
    f1 = f1_score(y_te, preds)
    print(f"Accuracy: {acc:.4f}   F1: {f1:.4f}")
    print(classification_report(y_te, preds, digits=3))

    # refit on ALL data, then save
    pipe.fit(texts, labels)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    joblib.dump(pipe, save_path)
    print(f"Saved -> {save_path}")


def train_fake_news():
    fake_p = _find("Fake.csv", "fake.csv")
    true_p = _find("True.csv", "true.csv")
    if not fake_p or not true_p:
        print("!! Could not find Fake.csv / True.csv in the 'realdata' folder. Skipping fake-news.")
        return
    fake = pd.read_csv(fake_p)
    true = pd.read_csv(true_p)

    def pick_text(df):
        # these datasets usually have 'title' and 'text' columns
        cols = [c for c in ("title", "text") if c in df.columns]
        if not cols:
            cols = [df.columns[0]]
        return (df[cols].fillna("").agg(" ".join, axis=1)).tolist()

    texts = pick_text(fake) + pick_text(true)
    labels = [1] * len(fake) + [0] * len(true)   # 1 = FAKE, 0 = REAL
    _train(texts, labels, FAKE_MODEL_PATH, "Fake-news detector (real data)")


def train_spam():
    spam_p = _find("spam.csv", "SMSSpamCollection.csv", "sms_spam.csv")
    if not spam_p:
        print("!! Could not find spam.csv in the 'realdata' folder. Skipping spam.")
        return
    # the Kaggle spam.csv is latin-1 encoded with extra empty columns
    try:
        df = pd.read_csv(spam_p, encoding="latin-1")
    except Exception:
        df = pd.read_csv(spam_p)

    # figure out label + text columns
    if {"v1", "v2"}.issubset(df.columns):          # classic SMS spam format
        label_col, text_col = "v1", "v2"
    elif {"label", "text"}.issubset(df.columns):
        label_col, text_col = "label", "text"
    elif {"Category", "Message"}.issubset(df.columns):
        label_col, text_col = "Category", "Message"
    else:
        label_col, text_col = df.columns[0], df.columns[1]

    df = df[[label_col, text_col]].dropna()
    texts = df[text_col].astype(str).tolist()
    labels = [1 if str(v).strip().lower() in ("spam", "1", "true") else 0
              for v in df[label_col]]
    _train(texts, labels, SPAM_MODEL_PATH, "Spam detector (real data)")


def main():
    which = sys.argv[1].lower() if len(sys.argv) > 1 else "both"
    if not os.path.isdir(DATA_DIR):
        print(f"Create a folder called 'realdata' here and add your CSV files:\n  {DATA_DIR}")
        return
    if which in ("fake", "both"):
        train_fake_news()
    if which in ("spam", "both"):
        train_spam()
    print("\nDone. Now run:  python app.py   (it will use your newly trained models)")


if __name__ == "__main__":
    main()
