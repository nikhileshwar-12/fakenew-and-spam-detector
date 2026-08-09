# 🛡️ TruthGuard — AI-Powered Fake News & Spam Detector

### 🔗 [Live Demo](https://truthguard-d1xv.onrender.com) · [GitHub](https://github.com/nikhileshwar-12/fakenew-and-spam-detector)

TruthGuard is a full-stack machine-learning web application that classifies text as **fake vs. real news** and **spam vs. legitimate (ham)** messages. It goes beyond a simple classifier — it **cross-checks claims against live news and professional fact-checkers**, explains its reasoning with **AI (Google Gemini)**, reads text from **images (OCR)**, and even ships with a **browser extension** to verify text on any website.

Both ML models are trained on **~50,000 real-world examples** and achieve **~99% accuracy**.

---

## ✨ Features

### 🔎 Detection
- 📰 **Fake-news detection** — flags unreliable / clickbait content vs. credible reporting
- ✉️ **Spam detection** — flags scam / phishing / promotional spam vs. normal messages
- 🔍 **Explainable results** — confidence scores + the top keywords driving each prediction
- 🚩 **Signal analysis** — heuristic red-flags (ALL-CAPS ratio, exclamation marks, links, money mentions)

### 🧾 Six ways to input
1. ✍️ **Text** — type or paste
2. 📄 **File upload** — analyze a `.txt` file
3. 📊 **Batch CSV** — classify many rows, download a results file
4. 🔗 **URL** — fetch & analyze an online article (with source-credibility rating)
5. 📷 **Image / screenshot** — reads text via **Tesseract OCR**, then classifies it
6. 🌐 **Live Verify** — cross-checks a claim against real sources (see below)

### 🌐 Live Verify (real-world fact-checking)
Combines multiple signals into one verdict:
- 🤖 **Our ML model** rating
- 🧠 **AI reasoning** — Google Gemini explains *why* a claim looks credible or fake, in plain English
- ✅ **Professional fact-checkers** — via Google Fact Check Tools API
- 📰 **Live news coverage** — via NewsAPI / Google News (smart keyword search)

### 🧩 Browser Extension
Highlight text on **any website** (news sites, social media, messaging apps), right-click → **"🛡️ Check with TruthGuard"** → instant verdict in a popup card. A ToS-compliant way to fact-check while you browse.

### 📊 Extras
- 🗄️ **Analytics dashboard** — live stats (total checks, % fake/spam, top keywords, recent activity) backed by SQLite
- 🌍 **Source credibility checker** — flags known reliable / satire / low-credibility domains
- 🇮🇳 **Multi-language detection** — Hindi, Telugu, Tamil, and more (Unicode-based)

---

## 📊 Model Performance

| Model | Trained on | Accuracy | F1 Score |
|-------|-----------|----------|----------|
| 📰 Fake-news detector | ~44,900 news articles | **99.5%** | 0.995 |
| ✉️ Spam detector | ~5,570 SMS messages | **98.9%** | 0.959 |

*Datasets: [Fake and Real News](https://www.kaggle.com/datasets/clmentbisaillon/fake-and-real-news-dataset) & [SMS Spam Collection](https://www.kaggle.com/datasets/uciml/sms-spam-collection-dataset) (Kaggle).*

---

## 🛠️ Tech Stack

- **Backend:** Python, Flask, Gunicorn
- **Machine Learning:** scikit-learn (TF-IDF + Logistic Regression)
- **OCR:** Tesseract (`pytesseract`)
- **AI reasoning:** Google Gemini API
- **External APIs:** Google Fact Check Tools, NewsAPI, Google News RSS
- **Web scraping:** requests + BeautifulSoup
- **Storage:** SQLite
- **Frontend:** HTML, CSS, vanilla JavaScript (single-page)
- **Browser extension:** Chrome/Edge Manifest V3
- **Deployment:** Docker on Render

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) (for the image feature)

### Installation
\`\`\`bash
git clone https://github.com/nikhileshwar-12/fakenew-and-spam-detector.git
cd "fakenew-and-spam-detector/backend"

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
python app.py
\`\`\`
Open **http://localhost:5000**.

### Optional API keys (for Live Verify's full power)
Set as environment variables — never hard-coded:
\`\`\`bash
setx GEMINI_API_KEY "your_key"            # AI reasoning (aistudio.google.com)
setx NEWSAPI_KEY "your_key"               # richer news (newsapi.org)
setx GOOGLE_FACTCHECK_API_KEY "your_key"  # fact-checker ratings (Google Cloud)
\`\`\`
> The app works without keys too — Live Verify falls back to free Google News, and all other features run offline.

### Browser extension
1. `chrome://extensions` → enable **Developer mode** → **Load unpacked** → select the `extension/` folder
2. Highlight text on any page → right-click → **🛡️ Check with TruthGuard**

---

## 📁 Project Structure
\`\`\`
fakenew-and-spam-detector/
├── backend/
│   ├── app.py                # Flask server + REST API
│   ├── model.py              # ML pipelines, training, inference
│   ├── datasets.py           # sample training data
│   ├── train_from_csv.py     # train on real Kaggle datasets
│   ├── image_analysis.py     # Tesseract OCR
│   ├── live_verify.py        # fact-check + news + Gemini reasoning
│   ├── 