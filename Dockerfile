FROM python:3.10-slim

# Install stockfish from apt
RUN apt-get update && \
    apt-get install -y stockfish && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Tell Stockfish wrapper to use the `stockfish` binary on PATH
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
