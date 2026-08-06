"""
TruthGuard - Flask web app. Input: text, .txt, .csv, URL, or image.
"""
import io
import csv
import re
from flask import Flask, render_template, request, jsonify, Response
import model

app = Flask(__name__)

print("[TruthGuard] Preparing models...")
METRICS = model.train_and_save(force=False)
if not METRICS:
    METRICS = model.train_and_save(force=True)
print("[TruthGuard] Ready.")

MAX_TEXT = 20000


@app.route("/")
def index():
    return render_template("index.html", metrics=METRICS)


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    mode = data.get("mode", "auto")
    if not text:
        return jsonify({"error": "Please enter some text to analyze."}), 400
    text = text[:MAX_TEXT]
    try:
        return jsonify(model.analyze(text, mode=mode))
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {e}"}), 500


@app.route("/api/analyze-file", methods=["POST"])
def api_analyze_file():
    f = request.files.get("file")
    mode = request.form.get("mode", "auto")
    if not f or not f.filename:
        return jsonify({"error": "No file uploaded."}), 400
    try:
        text = f.read().decode("utf-8", errors="ignore").strip()
    except Exception as e:
        return jsonify({"error": f"Could not read file: {e}"}), 400
    if not text:
        return jsonify({"error": "The file appears to be empty."}), 400
    result = model.analyze(text[:MAX_TEXT], mode=mode)
    result["source"] = f"File: {f.filename}"
    return jsonify(result)


@app.route("/api/analyze-csv", methods=["POST"])
def api_analyze_csv():
    f = request.files.get("file")
    mode = request.form.get("mode", "auto")
    if not f or not f.filename:
        return jsonify({"error": "No CSV uploaded."}), 400
    try:
        raw = f.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return jsonify({"error": f"Could not read CSV: {e}"}), 400

    reader = csv.reader(io.StringIO(raw))
    rows = [r for r in reader if any(cell.strip() for cell in r)]
    if not rows:
        return jsonify({"error": "CSV is empty."}), 400

    header = rows[0]
    text_col = 0
    start = 0
    lowered = [c.strip().lower() for c in header]
    for cand in ("text", "message", "content", "v2", "body", "sms"):
        if cand in lowered:
            text_col = lowered.index(cand)
            start = 1
            break
    else:
        if all(len(c) < 20 for c in header) and len(header) > 1:
            start = 1
        widths = [max((len(r[i]) for r in rows[start:] if i < len(r)), default=0)
                  for i in range(len(header))]
        if widths:
            text_col = widths.index(max(widths))

    out = io.StringIO()
    writer = csv.writer(out)
    header_out = ["text"]
    if mode in ("fake_news", "auto"):
        header_out += ["fake_news_label", "fake_probability_%"]
    if mode in ("spam", "auto"):
        header_out += ["spam_label", "spam_probability_%"]
    writer.writerow(header_out)

    processed = 0
    for r in rows[start:]:
        if text_col >= len(r):
            continue
        txt = (r[text_col] or "").strip()
        if not txt:
            continue
        res = model.analyze(txt[:MAX_TEXT], mode=mode)
        row_out = [txt[:500]]
        if "fake_news" in res:
            row_out += [res["fake_news"]["label"], res["fake_news"]["fake_probability"]]
        if "spam" in res:
            row_out += [res["spam"]["label"], res["spam"]["spam_probability"]]
        writer.writerow(row_out)
        processed += 1
        if processed >= 5000:
            break

    if processed == 0:
        return jsonify({"error": "No text rows found in the CSV."}), 400

    return Response(
        out.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=truthguard_results.csv",
            "X-Rows-Processed": str(processed),
        },
    )


@app.route("/api/analyze-url", methods=["POST"])
def api_analyze_url():
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()
    mode = data.get("mode", "auto")
    if not url:
        return jsonify({"error": "Please enter a URL."}), 400
    if not re.match(r"^https?://", url):
        url = "https://" + url
    try:
        import requests
        from bs4 import BeautifulSoup
        headers = {"User-Agent": "Mozilla/5.0 (TruthGuard news reader)"}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
            tag.decompose()
        title = (soup.title.string or "").strip() if soup.title else ""
        paras = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
        body = " ".join(p for p in paras if len(p) > 40)
        text = (title + ". " + body).strip()
    except Exception as e:
        return jsonify({"error": f"Could not fetch the page: {e}"}), 400
    if len(text) < 40:
        return jsonify({"error": "Couldn't extract readable article text from that URL."}), 400
    result = model.analyze(text[:MAX_TEXT], mode=mode)
    result["source"] = f"URL: {url}"
    result["extracted_title"] = title[:200]
    result["extracted_chars"] = len(text)
    return jsonify(result)


@app.route("/api/analyze-image", methods=["POST"])
def api_analyze_image():
    f = request.files.get("file")
    mode = request.form.get("mode", "auto")
    do_ai = request.form.get("check_ai", "true").lower() != "false"
    if not f or not f.filename:
        return jsonify({"error": "No image uploaded."}), 400
    try:
        img_bytes = f.read()
    except Exception as e:
        return jsonify({"error": f"Could not read image: {e}"}), 400

    import image_analysis
    out = {"source": f"Image: {f.filename}"}

    ocr = image_analysis.extract_text(img_bytes)
    out["ocr"] = {"ok": ocr["ok"], "error": ocr["error"], "text": ocr["text"][:MAX_TEXT]}
    if ocr["ok"] and ocr["text"].strip():
        text_result = model.analyze(ocr["text"][:MAX_TEXT], mode=mode)
        out["fake_news"] = text_result.get("fake_news")
        out["spam"] = text_result.get("spam")
        out["signals"] = text_result.get("signals")

    if do_ai:
        out["ai_image"] = image_analysis.detect_ai_image(img_bytes)

    return jsonify(out)


@app.route("/api/capabilities")
def api_capabilities():
    try:
        import image_analysis
        return jsonify(image_analysis.status())
    except Exception:
        return jsonify({"ocr": False, "ai_detector": False})


@app.route("/api/metrics")
def api_metrics():
    return jsonify(METRICS)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)