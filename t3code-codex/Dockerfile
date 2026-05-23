ARG BUILD_VERSION=0.1.2
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
  && find /usr/local/lib/node_modules/t3/dist/client -name index.html -print -exec sed -i \
    -e 's|href="/favicon.ico"|href="./favicon.ico"|g' \
    -e 's|href="/apple-touch-icon.png"|href="./apple-touch-icon.png"|g' \
    -e 's|src="/assets/|src="./assets/|g' \
    -e 's|href="/assets/|href="./assets/|g' \
    {} \; \
  && find /usr/local/lib/node_modules/t3/dist/client/assets -name 'index-*.js' -print -exec sed -i \
    -e 's|new Worker(`/assets/|new Worker(`./assets/|g' \
    {} \; \
  && npm cache clean --force

COPY run.sh /run.sh
RUN chmod +x /run.sh

WORKDIR /homeassistant
EXPOSE 8099

CMD ["/run.sh"]
