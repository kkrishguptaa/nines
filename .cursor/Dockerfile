# syntax=docker/dockerfile:1
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    git \
    gh \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    sudo \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Non-root-friendly sudo for Cursor cloud tooling
RUN echo "ALL ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/cursor && chmod 440 /etc/sudoers.d/cursor

# Ensure `python` resolves
RUN ln -sf /usr/bin/python3 /usr/local/bin/python

WORKDIR /workspace
