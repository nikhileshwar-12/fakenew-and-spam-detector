FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends tesseract-ocr && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=8080
EXPOSE 8080
RUN python -c "import model; model.train_and_save(force=True)" || true
CMD gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app
