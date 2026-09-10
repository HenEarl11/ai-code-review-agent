FROM python:3.11-slim AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements from repo root context
COPY backend/requirements-docker.txt ./requirements-docker.txt

# Install Python dependencies (docker-optimized list)
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copy full repository into the image (so tests and samples are available)
COPY . .

# Create database directory under backend
RUN mkdir -p /app/backend/db


# Runtime image (keep small surface for running the app)
FROM base AS runtime
EXPOSE 5000
CMD ["python", "backend/app.py"]


# Test stage: build with --target test to run tests inside the image
FROM base AS test
# Install test runner
RUN pip install --no-cache-dir pytest

# Run a focused test selection during build; this will make the build fail if tests fail
RUN pytest -q tests/test_terraform_mixed_severity.py tests/test_typescript_mixed_severity.py
