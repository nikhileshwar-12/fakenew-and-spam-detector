"""
TruthGuard - Flask web app
AI-powered Fake News & Spam detector.
"""
from flask import Flask, render_template, request, jsonify
import model

app = Flask(__name__)

# Train (or load cached) models at startup
print("[TruthGuard] Preparing models...")
METRICS = model.train_and_save(force=False)
if not METRICS:  # already cached -> re-run to get metrics for display
    METRICS = model.train_and_save(force=True)
print("[TruthGuard] Ready.")


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
    if len(text) > 20000:
        text = text[:20000]
    try:
        result = model.analyze(text, mode=mode)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {e}"}), 500


@app.route("/api/metrics")
def api_metrics():
    return jsonify(METRICS)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
