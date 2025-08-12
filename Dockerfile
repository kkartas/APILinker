# syntax=docker/dockerfile:1

FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps (keep minimal)
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Install application
COPY pyproject.toml setup.py README.md requirements.txt ./
COPY apilinker ./apilinker
COPY docs ./docs

# Install dependencies and package
RUN python -m pip install --upgrade pip \
 && if [ -f requirements.txt ]; then pip install -r requirements.txt; fi \
 && pip install .

# Default command runs the CLI
ENTRYPOINT ["python", "-m", "apilinker"]
CMD ["--help"]


