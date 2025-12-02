FROM python:3.11-slim

# Install system libraries + ImageMagick
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        imagemagick \
        ghostscript \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your full app
COPY . /app

# Script entrypoint (you can override in Synology Task Scheduler)
ENTRYPOINT ["python", "/app/goesgif.py"]
