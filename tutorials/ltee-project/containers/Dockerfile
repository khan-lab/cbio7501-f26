# Container image of this project's software, built from pixi.lock, so the
# container and your laptop run exactly the same packages.
#
# Adapted from the example in the Pixi documentation ("Containerizing",
# https://pixi.prefix.dev/latest/deployment/container/), Copyright (c) 2023,
# prefix.dev GmbH, BSD 3-Clause License
# (https://github.com/prefix-dev/pixi/blob/main/LICENSE): install the locked
# environment in a Pixi image, then copy only the environment into a small
# Ubuntu image. Changes: environment name as a build argument, PATH set for
# Apptainer, project mounted at /work instead of copied in.
#
# Build from the project folder (lesson 08):
#   docker build --platform linux/amd64 -f containers/Dockerfile \
#     --build-arg ENV_NAME=default -t PROJECT:0.1.0 .
# Run a command with the project folder mounted at /work:
#   docker run --rm -v "$PWD":/work -w /work PROJECT:0.1.0 python --version

ARG PIXI_VERSION=0.83.0

FROM ghcr.io/prefix-dev/pixi:${PIXI_VERSION} AS build
# Which Pixi environment to put in the image (see [environments] in pixi.toml)
ARG ENV_NAME=default
WORKDIR /opt/project
COPY pixi.toml pixi.lock ./
# --locked: fail if pixi.lock does not match pixi.toml
RUN pixi install --locked --environment ${ENV_NAME}
# A start script that activates the environment, then runs the command
RUN pixi shell-hook --environment ${ENV_NAME} --shell bash > /shell-hook.sh \
 && printf '#!/bin/bash\n' > /entrypoint.sh \
 && cat /shell-hook.sh >> /entrypoint.sh \
 && printf 'exec "$@"\n' >> /entrypoint.sh

FROM ubuntu:24.04 AS production
ARG ENV_NAME=default
LABEL org.opencontainers.image.description="Software environment '${ENV_NAME}' of this project, built from pixi.lock"
# The environment must keep the same path (prefix) as in the build stage:
# environments cannot be moved.
COPY --from=build /opt/project/.pixi/envs/${ENV_NAME} /opt/project/.pixi/envs/${ENV_NAME}
COPY --from=build --chmod=0755 /entrypoint.sh /entrypoint.sh
# PATH as well, for tools that ignore the entrypoint (apptainer exec)
ENV PATH=/opt/project/.pixi/envs/${ENV_NAME}/bin:$PATH
WORKDIR /work
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
