"""
TruthGuard - ML core
--------------------
Trains two text classifiers:
  1. Fake-news detector  (REAL vs FAKE news / articles / headlines)
  2. Spam detector       (SPAM vs HAM messages / emails)

Both use TF-IDF features + a Logistic Regression / Naive Bayes ensemble.
Models are trained once and cached to disk with joblib so the app starts fast.
"""

import os
import re
import joblib
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score

from data.datasets import build_fake_news_dataset, build_spam_dataset

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(HERE, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

FAKE_MODEL_PATH = os.path.join(MODEL_DIR, "fake_news.joblib")
SPAM_MODEL_PATH = os.path.join(MODEL_DIR, "spam.joblib")


# ---------------------------------------------------------------------------
# Text cleaning
# ---------------------------------------------------------------------------
URL_RE = re.compile(r"https?://\S+|www\.\S+")
NON_ALNUM_RE = re.compile(r"[^a-z0-9\s$!?%]")
MULTISPACE_RE = re.compile(r"\s+")


def clean_text(text: str) -> str:
    text = (text or "").lower()
    text = URL_RE.sub(" _url_ ", text)
    text = re.sub(r"\b\d{6,}\b", " _num_ ", text)   # long numbers (phone/codes)
    text = NON_ALNUM_RE.sub(" ", text)
    text = MULTISPACE_RE.sub(" ", text).strip()
    return text


# ---------------------------------------------------------------------------
# Hand-crafted "signal" features that help catch spam / clickbait patterns
# ---------------------------------------------------------------------------
def extract_signals(text: str) -> dict:
    raw = text or ""
    words = raw.split()
    n = max(len(words), 1)
    upper_words = sum(1 for w in words if len(w) > 2 and w.isupper())
    exclam = raw.count("!")
    money = len(re.findall(r"[$₹£€]|\b(usd|rs|inr)\b", raw.lower()))
    urls = len(URL_RE.findall(raw))
    digits = sum(c.isdigit() for c in raw)
    return {
        "caps_ratio": round(upper_words / n, 3),
        "exclamations": exclam,
        "money_mentions": money,
        "links": urls,
        "digit_ratio": round(digits / max(len(raw), 1), 3),
        "length_words": len(words),
    }


# ---------------------------------------------------------------------------
# Model building
# ---------------------------------------------------------------------------
def _make_pipeline(kind: str) -> Pipeline:
    vectorizer = TfidfVectorizer(
        preprocessor=clean_text,
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.9,
        sublinear_tf=True,
    )
    if kind == "nb":
        clf = MultinomialNB(alpha=0.3)
    else:
        clf = LogisticRegression(max_iter=1000, C=4.0, class_weight="balanced")
    return Pipeline([("tfidf", vectorizer), ("clf", clf)])


def _train_one(texts, labels, name):
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )
    pipe = _make_pipeline("lr")
    pipe.fit(X_train, y_train)
    preds = pipe.predict(X_test)
    metrics = {
        "name": name,
        "train_size": len(X_train),
        "test_size": len(X_test),
        "accuracy": round(float(accuracy_score(y_test, preds)), 4),
        "f1": round(float(f1_score(y_test, preds)), 4),
    }
    # refit on ALL data for the deployed model
    pipe.fit(texts, labels)
    return pipe, metrics


def train_and_save(force: bool = False):
    """Train both models (if not cached) and return their metrics."""
    metrics = {}

    if force or not os.path.exists(FAKE_MODEL_PATH):
        texts, labels = build_fake_news_dataset()
        model, m = _train_one(texts, labels, "Fake-news detector")
        joblib.dump(model, FAKE_MODEL_PATH)
        metrics["fake_news"] = m
    if force or not os.path.exists(SPAM_MODEL_PATH):
        texts, labels = build_spam_dataset()
        model, m = _train_one(texts, labels, "Spam detector")
        joblib.dump(model, SPAM_MODEL_PATH)
        metrics["spam"] = m

    return metrics


# ---------------------------------------------------------------------------
# Inference
# ---------------------------------------------------------------------------
_FAKE_MODEL = None
_SPAM_MODEL = None


def _load():
    global _FAKE_MODEL, _SPAM_MODEL
    if _FAKE_MODEL is None:
        _FAKE_MODEL = joblib.load(FAKE_MODEL_PATH)
    if _SPAM_MODEL is None:
        _SPAM_MODEL = joblib.load(SPAM_MODEL_PATH)


def _top_contributing_words(model, text, positive_class, k=6):
    """Return words in the text that push most toward the predicted class."""
    try:
        tfidf = model.named_steps["tfidf"]
        clf = model.named_steps["clf"]
        vocab = tfidf.get_feature_names_out()
        row = tfidf.transform([text])
        coefs = clf.coef_[0]
        idx = row.nonzero()[1]
        contribs = []
        for j in idx:
            weight = row[0, j] * coefs[j]
            contribs.append((vocab[j], weight))
        # positive weight -> class 1
        sign = 1 if positive_class == 1 else -1
        contribs = [(w, s) for (w, s) in contribs if s * sign > 0]
        contribs.sort(key=lambda t: abs(t[1]), reverse=True)
        return [w for w, _ in contribs[:k] if w not in ("_url_", "_num_")]
    except Exception:
        return []


def analyze(text: str, mode: str = "auto") -> dict:
    """
    mode: 'fake_news', 'spam', or 'auto' (run both).
    Returns a dict with predictions, confidences, signals and explanations.
    """
    _load()
    text = (text or "").strip()
    result = {"input_preview": text[:280], "signals": extract_signals(text)}

    def run_fake():
        proba = _FAKE_MODEL.predict_proba([text])[0]
        # class 1 == FAKE in our dataset
        p_fake = float(proba[1])
        label = "FAKE / Unreliable" if p_fake >= 0.5 else "REAL / Credible"
        pred_class = 1 if p_fake >= 0.5 else 0
        return {
            "label": label,
            "is_fake": p_fake >= 0.5,
            "confidence": round(max(p_fake, 1 - p_fake) * 100, 1),
            "fake_probability": round(p_fake * 100, 1),
            "keywords": _top_contributing_words(_FAKE_MODEL, text, pred_class),
        }

    def run_spam():
        proba = _SPAM_MODEL.predict_proba([text])[0]
        # class 1 == SPAM
        p_spam = float(proba[1])
        label = "SPAM" if p_spam >= 0.5 else "NOT SPAM (Ham)"
        pred_class = 1 if p_spam >= 0.5 else 0
        return {
            "label": label,
            "is_spam": p_spam >= 0.5,
            "confidence": round(max(p_spam, 1 - p_spam) * 100, 1),
            "spam_probability": round(p_spam * 100, 1),
            "keywords": _top_contributing_words(_SPAM_MODEL, text, pred_class),
        }

    if mode in ("fake_news", "auto"):
        result["fake_news"] = run_fake()
    if mode in ("spam", "auto"):
        result["spam"] = run_spam()

    return result


if __name__ == "__main__":
    print("Training models...")
    m = train_and_save(force=True)
    import json
    print(json.dumps(m, indent=2))
    print("\nDemo:")
    print(json.dumps(analyze(
        "CONGRATULATIONS!!! You WON a $1000 Walmart gift card. CLICK http://bit.ly/x to claim NOW!!!"
    ), indent=2))
