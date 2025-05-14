FROM python:3.10-slim
WORKDIR /app

# Copy your actual binary name and place it on PATH as 'stockfish'
COPY stockfish-ubuntu-x86-64-avx2 /usr/local/bin/stockfish
RUN chmod +x /usr/local/bin/stockfish

# ... rest of Dockerfile unchanged ...


# 2) Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3) Copy your app
COPY . .

# 4) Expose and launch on $PORT
EXPOSE 8080
ENTRYPOINT ["sh","-c","exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
