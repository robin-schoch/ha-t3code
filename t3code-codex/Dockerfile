ARG BUILD_VERSION=0.2.7
ARG BUILD_ARCH=amd64

FROM node:24-bookworm-slim

ARG BUILD_VERSION
ARG BUILD_ARCH
ARG T3_VERSION=0.1.9
ARG CODEX_VERSION=0.159.0
ARG CLAUDE_VERSION=2.1.311
ARG ANTIGRAVITY_CLI_VERSION=1.5.10-5253791805734912
ARG ANTIGRAVITY_CLI_SHA256_AMD64=72fb2946d6f5bee3d4e8928fb8a7901104361566619e69d40ae6dc03e094917b
ARG ANTIGRAVITY_CLI_SHA256_AARCH64=5ecb4e7763dc497a7d0157d5605a8c86ec55f24dc4efd8f597bc499d2ebca7c6

LABEL \
  io.hass.version="${BUILD_VERSION}" \
  io.hass.type="addon" \
  io.hass.arch="${BUILD_ARCH}"

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    bash \
    ca-certificates \
    curl \
    g++ \
    git \
    jq \
    make \
    openssh-client \
    procps \
    python3 \
    ripgrep \
  && rm -rf /var/lib/apt/lists/*

RUN npm install -g \
    "t3@${T3_VERSION}" \
    "@openai/codex@${CODEX_VERSION}" \
    "@anthropic-ai/claude-code@${CLAUDE_VERSION}" \
  && claude --version \
  && npm cache clean --force

RUN set -eux; \
  case "${BUILD_ARCH}" in \
    amd64) \
      agy_path="linux-x64/cli_linux_x64.tar.gz"; \
      agy_sha256="${ANTIGRAVITY_CLI_SHA256_AMD64}"; \
      ;; \
    aarch64) \
      agy_path="linux-arm/cli_linux_arm64.tar.gz"; \
      agy_sha256="${ANTIGRAVITY_CLI_SHA256_AARCH64}"; \
      ;; \
    *) \
      echo "Unsupported BUILD_ARCH: ${BUILD_ARCH}" >&2; \
      exit 1; \
      ;; \
  esac; \
  mkdir -p /opt/antigravity-cli; \
  curl -fsSL "https://storage.googleapis.com/antigravity-public/antigravity-cli/${ANTIGRAVITY_CLI_VERSION}/${agy_path}" -o /tmp/antigravity-cli.tar.gz; \
  echo "${agy_sha256}  /tmp/antigravity-cli.tar.gz" | sha256sum -c -; \
  tar -xzf /tmp/antigravity-cli.tar.gz -C /opt/antigravity-cli; \
  rm -f /tmp/antigravity-cli.tar.gz; \
  chmod 0755 /opt/antigravity-cli/antigravity; \
  ln -sf /opt/antigravity-cli/antigravity /usr/local/bin/agy; \
  ln -sf /opt/antigravity-cli/antigravity /usr/local/bin/antigravity; \
  ln -sf /opt/antigravity-cli/antigravity /usr/local/bin/agy_acp_server.par; \
  AGY_CLI_DISABLE_AUTO_UPDATE=true agy --version; \
  AGY_CLI_DISABLE_AUTO_UPDATE=true agy_acp_server.par acp --help >/dev/null

COPY run.sh /run.sh
RUN chmod +x /run.sh

ENV HOME=/data
ENV AGY_CLI_DISABLE_AUTO_UPDATE=true

WORKDIR /homeassistant
EXPOSE 8099

CMD ["/run.sh"]
