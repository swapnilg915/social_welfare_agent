# ---- Base Image ----
FROM python:3.10-slim

# ---- Metadata ----
LABEL maintainer="Swapnil Gaikwad"
LABEL description="Agentic AI-based Social Welfare Automation System"

# ---- Set environment variables ----
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    LANG=C.UTF-8 \
    DEBIAN_FRONTEND=noninteractive

# ---- Install system dependencies ----
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ---- Create working directory ----
WORKDIR /app

# ---- Copy requirements first for caching ----
COPY requirements.txt .

# ---- Install Python dependencies ----
RUN python -m venv /opt/venv \
    && . /opt/venv/bin/activate \
    && pip install --upgrade pip \
    && pip install -r requirements.txt

# ---- Copy application files ----
COPY . .

# ---- Activate venv on container start ----
ENV PATH="/opt/venv/bin:$PATH"

# ---- Expose Flask default port ----
EXPOSE 5000

# ---- Default command ----
CMD ["python", "app/api.py"]
