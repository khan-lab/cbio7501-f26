# Codespaces / devcontainer image for the workshop: Ubuntu with Pixi.
# Adapted from NBIS workshop-reproducible-research (.devcontainer/Dockerfile,
# CC BY 4.0): newer base image and Pixi version.
FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

ARG PIXI_VERSION=v0.83.0

RUN curl -fsSL --compressed -o /usr/local/bin/pixi \
        "https://github.com/prefix-dev/pixi/releases/download/${PIXI_VERSION}/pixi-$(uname -m)-unknown-linux-musl" \
    && chmod +x /usr/local/bin/pixi \
    && pixi --version

USER vscode
RUN echo 'eval "$(pixi completion --shell bash)"' >> /home/vscode/.bashrc
