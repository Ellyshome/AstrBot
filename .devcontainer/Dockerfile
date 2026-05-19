FROM python:3.12-slim

WORKDIR /AstrBot

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    python3-dev \
    libffi-dev \
    libssl-dev \
    ca-certificates \
    bash \
    ffmpeg \
    libavcodec-extra \
    curl \
    gnupg \
    git \
    ripgrep \
    && curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install uv and Python dependencies
RUN python -m pip install uv \
    && echo "3.12" > .python-version

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock* ./

RUN uv export --format requirements.txt --output-file requirements.txt --frozen 2>/dev/null || true \
    && uv pip install -r requirements.txt --no-cache-dir --system 2>/dev/null || true \
    && uv pip install socksio uv pilk --no-cache-dir --system

# Install dev dependencies
RUN uv pip install commitizen pytest pytest-asyncio pytest-cov ruff --no-cache-dir --system

EXPOSE 6185
