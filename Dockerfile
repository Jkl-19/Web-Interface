# Dockerfile
FROM python:3.10-slim

# Install wget & unzip so we can fetch the precompiled binary
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      wget unzip ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Download the official Stockfish Linux x64 build, unzip, and make it executable
RUN wget -qO /tmp/stockfish.zip "https://stockfishchess.org/download/stockfish_15.1_linux_x64.zip" && \
    unzip -q /tmp/stockfish.zip -d /tmp/ && \
    mv /tmp/stockfish_15_x64_bmi2 /usr/local/bin/stockfish && \
    chmod +x /usr/local/bin/stockfish && \
    rm -rf /tmp/stockfish.zip

WORKDIR /app

# Install your Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your code
COPY . .

# Expose the port and start Uvicorn
EXPOSE 10000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
