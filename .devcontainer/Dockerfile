FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        curl \
        file \
        git-lfs \
        jq \
        libayatana-appindicator3-dev \
        librsvg2-dev \
        libssl-dev \
        libwebkit2gtk-4.1-dev \
        libxdo-dev \
        poppler-utils \
        ripgrep \
        shellcheck \
        sqlite3 \
        tree \
        unzip \
        wget \
        zip \
    && rm -rf /var/lib/apt/lists/*
