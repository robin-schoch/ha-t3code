ARG BUILD_VERSION=0.1.0
ARG BUILD_ARCH=amd64

FROM node:24-bookworm-slim

ARG BUILD_VERSION
ARG BUILD_ARCH
ARG T3_VERSION=0.0.24
ARG CODEX_VERSION=0.133.0

LABEL \
  io.hass.version="${BUILD_VERSION}" \
  io.hass.type="addon" \
  io.hass.arch="${BUILD_ARCH}"

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    bash \
    ca-certificates \
    git \
    jq \
    openssh-client \
    procps \
    ripgrep \
  && rm -rf /var/lib/apt/lists/*

RUN npm install -g \
    "t3@${T3_VERSION}" \
    "@openai/codex@${CODEX_VERSION}" \
  && npm cache clean --force

COPY run.sh /run.sh
RUN chmod +x /run.sh

WORKDIR /homeassistant
EXPOSE 8099

CMD ["/run.sh"]
