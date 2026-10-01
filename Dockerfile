FROM python:3.11-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code into /app
COPY backend/ .

# Copy data folder into /app/data
COPY data/ ./data/

# Environment variables
ENV PORT=8000
ENV ENVIRONMENT=production
ENV DATABASE_URL=sqlite:////app/nutrition.db
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
