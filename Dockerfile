FROM python:3.10-slim

WORKDIR /app

# Copy in the bundled Stockfish binary
COPY bin/stockfish /usr/local/bin/stockfish
RUN chmod +x /usr/local/bin/stockfish

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your app code
COPY . .

# Expose and run
EXPOSE 10000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
