# 1) Base image
FROM python:3.10-slim

# 2) Create and switch to your app directory
WORKDIR /app

# 3) Copy the Linux Stockfish binary you uploaded, rename to "stockfish"
#    (make sure this file sits next to Dockerfile in the same folder)
COPY stockfish-ubuntu-x86-64-avx2 /usr/local/bin/stockfish

# 4) Ensure it’s executable
RUN chmod +x /usr/local/bin/stockfish

# 5) Copy & install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6) Copy your FastAPI app and engines
COPY . .

# 7) (Optional) document the port—Cloud Run will inject $PORT
EXPOSE 8080

# 8) Start Uvicorn on the injected PORT (defaults to 8080 locally)
ENTRYPOINT ["sh","-c","exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
