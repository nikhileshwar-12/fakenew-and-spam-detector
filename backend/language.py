"""language.py -- lightweight language detection (no external libraries)."""
import re

_RANGES = [
    ("Hindi", r"[\u0900-\u097F]"),
    ("Telugu", r"[\u0C00-\u0C7F]"),
    ("Tamil", r"[\u0B80-\u0BFF]"),
    ("Kannada", r"[\u0C80-\u0CFF]"),
    ("Bengali", r"[\u0980-\u09FF]"),
    ("Malayalam", r"[\u0D00-\u0D7F]"),
    ("Gujarati", r"[\u0A80-\u0AFF]"),
    ("Arabic", r"[\u0600-\u06FF]"),
]


def detect(text):
    text = text or ""
    if not text.strip():
        return {"language": "unknown", "code": "und", "is_english": False, "note": "No text provided."}
    counts = {name: len(re.findall(pat, text)) for name, pat in _RANGES}
    latin = len(re.findall(r"[A-Za-z]", text))
    best = max(counts, key=counts.get) if counts else None
    best_count = counts.get(best, 0)
    if best_count > latin and best_count > 0:
        lang = best
        english = False
        note = (f"Detected {lang}. Note: the ML models are trained mainly on English, "
                f"so predictions for {lang} text are less reliable.")
    else:
        lang = "English"
        english = True
        note = "Detected English."
    codes = {"Hindi": "hi", "Telugu": "te", "Tamil": "ta", "Kannada": "kn",
             "Bengali": "bn", "Malayalam": "ml", "Gujarati": "gu", "Arabic": "ar", "English": "en"}
    return {"language": lang, "code": codes.get(lang, "und"), "is_english": english, "note": note}