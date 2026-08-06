import io
import os
import shutil

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

_configured = False
_config_error = None


def _configure_tesseract():
    global _configured, _config_error
    if _configured:
        return _config_error is None
    try:
        import pytesseract
    except Exception as e:
        _config_error = "pytesseract not installed. Run: python -m pip install pytesseract pillow (details: " + str(e) + ")"
        _configured = True
        return False
    path = TESSERACT_PATH if os.path.exists(TESSERACT_PATH) else shutil.which("tesseract")
    if path:
        pytesseract.pytesseract.tesseract_cmd = path
        _config_error = None
    else:
        _config_error = "Tesseract program not found. Install from https://github.com/UB-Mannheim/tesseract/wiki then restart."
    _configured = True
    return _config_error is None


def _load_pil(image_bytes):
    from PIL import Image
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode != "RGB":
        img = img.convert("RGB")
    return img


def extract_text(image_bytes):
    if not _configure_tesseract():
        return {"text": "", "ok": False, "error": _config_error}
    try:
        import pytesseract
        img = _load_pil(image_bytes)
        try:
            from PIL import Image
            w, h = img.size
            if max(w, h) < 1000:
                scale = 1000 / max(w, h)
                img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        except Exception:
            pass
        text = pytesseract.image_to_string(img).strip()
        return {"text": text, "ok": True, "error": None}
    except Exception as e:
        return {"text": "", "ok": False, "error": "OCR failed: " + str(e)}


def detect_ai_image(image_bytes):
    return {"ok": False,
            "error": "AI-generated image detection is turned off in this build. The text-reading (OCR) feature works fully.",
            "label": None, "ai_probability": None, "raw": None}


def status():
    return {"ocr": _configure_tesseract(), "ai_detector": False}
