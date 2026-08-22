# -----------------------------
# Base Image
# -----------------------------
FROM python:3.11-slim

# -----------------------------
# Environment
# -----------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# -----------------------------
# Working Directory
# -----------------------------
WORKDIR /app

# -----------------------------
# System Dependencies
# -----------------------------
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libglib2.0-0 \
    libgl1 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------
# Install Python Packages
# -----------------------------
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# -----------------------------
# Copy Project
# -----------------------------
COPY . .

# -----------------------------
# Create Runtime Folders
# -----------------------------
RUN mkdir -p uploads exports logs temp output

# -----------------------------
# Expose FastAPI Port
# -----------------------------
EXPOSE 8000

# -----------------------------
# Health Check
# -----------------------------
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
CMD curl -f http://localhost:8000/health || exit 1

# -----------------------------
# Start FastAPI
# -----------------------------
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]