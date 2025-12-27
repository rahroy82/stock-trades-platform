FROM python:3.10-slim

WORKDIR /app

# System deps (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy project
COPY . /app

# Default command (can be overridden by ECS task definition)
CMD ["python", "-c", "print('Container built. Override CMD in ECS task to run pipeline steps.')"]
