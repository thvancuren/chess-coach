FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including build tools for Stockfish
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libpq-dev \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Download and compile Stockfish
RUN mkdir -p /engines/stockfish && \
    cd /engines/stockfish && \
    wget https://github.com/official-stockfish/Stockfish/archive/refs/heads/master.zip -O stockfish-src.zip && \
    unzip stockfish-src.zip && \
    cd Stockfish-master/src && \
    make -j$(nproc) build ARCH=x86-64-modern && \
    cp stockfish /engines/stockfish/stockfish && \
    chmod +x /engines/stockfish/stockfish && \
    cd / && rm -rf /engines/stockfish/Stockfish-master /engines/stockfish/stockfish-src.zip

# Copy requirements
COPY apps/backend/pyproject.toml .

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Copy application code
COPY apps/backend/ .

# Create data directory
RUN mkdir -p /data

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

