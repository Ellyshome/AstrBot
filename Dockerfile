FROM python:3.12-slim
WORKDIR /AstrBot

COPY . /AstrBot/

ARG HTTP_PROXY
ARG HTTPS_PROXY

RUN if [ -n "$HTTP_PROXY" ]; then \
        echo "Acquire::http::Proxy \"$HTTP_PROXY\";" > /etc/apt/apt.conf.d/99proxy; \
        echo "Acquire::https::Proxy \"$HTTPS_PROXY\";" >> /etc/apt/apt.conf.d/99proxy; \
    fi \
    && apt-get update && apt-get install -y --no-install-recommends \
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

EXPOSE 6185
# CMD ["tail", "-f", "/dev/null"]
# CMD ["python", "main.py"]
