FROM python:3.10-slim

WORKDIR /app

# 1) Bring in your Stockfish binary and make executable
COPY stockfish-ubuntu-x86-64-avx2 /usr/local/bin/stockfish
RUN chmod +x /usr/local/bin/stockfish

# 2) Install your Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3) Copy **everything else** (your code, weights, web folder, etc.)
COPY . .

# 4) Listen on the Cloud Run port
EXPOSE 8080
ENTRYPOINT ["sh","-c","exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
