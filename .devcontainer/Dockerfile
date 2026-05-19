FROM python:3.12-slim

WORKDIR /AstrBot

# Use Tsinghua mirrors for apt, pip, npm
RUN sed -i 's|deb.debian.org|mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list.d/debian.sources \
    && sed -i 's|security.debian.org|mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list.d/debian.sources

ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
    UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
    NVM_NODEJS_ORG_MIRROR=https://mirrors.tuna.tsinghua.edu.cn/nodejs-release/

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
    && sed -i 's|deb.nodesource.com|mirrors.tuna.tsinghua.edu.cn/nodesource|g' /etc/apt/sources.list.d/nodesource.list \
    && apt-get install -y --no-install-recommends nodejs \
    && npm config set registry https://registry.npmmirror.com \
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
