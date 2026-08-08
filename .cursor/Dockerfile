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

# Shared virtualenv on PATH so python/pip/pytest resolve in every shell
# (login or not) and installs avoid PEP 668 externally-managed errors.
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv "$VIRTUAL_ENV" \
    && "$VIRTUAL_ENV/bin/python" -m pip install --upgrade pip setuptools wheel \
    && chmod -R a+rwX "$VIRTUAL_ENV"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Ensure `python` resolves to the venv interpreter
RUN ln -sf "$VIRTUAL_ENV/bin/python" /usr/local/bin/python

WORKDIR /workspace
