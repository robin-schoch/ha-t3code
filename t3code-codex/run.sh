#!/usr/bin/env bash
set -euo pipefail

export HOME=/data
export T3CODE_HOME=/data/t3code
export T3CODE_PORT=8099

mkdir -p "$T3CODE_HOME" "$HOME/.codex" /config

if [ -f /data/options.json ]; then
  OPENAI_API_KEY_FROM_OPTIONS="$(jq -r '.openai_api_key // empty' /data/options.json)"
  T3CODE_LOG_LEVEL_FROM_OPTIONS="$(jq -r '.t3code_log_level // "Info"' /data/options.json)"

  if [ -n "$OPENAI_API_KEY_FROM_OPTIONS" ]; then
    export OPENAI_API_KEY="$OPENAI_API_KEY_FROM_OPTIONS"
  fi

  export T3CODE_LOG_LEVEL="$(printf '%s' "$T3CODE_LOG_LEVEL_FROM_OPTIONS" | tr '[:upper:]' '[:lower:]')"
fi

if [ ! -d /homeassistant ]; then
  echo "The Home Assistant configuration directory is not mounted at /homeassistant."
  exit 1
fi

cd /homeassistant

# Avoid git ownership warnings when the mounted config repository has host-side ownership.
git config --global --add safe.directory /homeassistant >/dev/null 2>&1 || true

if [ -z "${OPENAI_API_KEY:-}" ] && [ ! -f "$HOME/.codex/auth.json" ]; then
  echo "OPENAI_API_KEY is not set and no Codex auth file exists at $HOME/.codex/auth.json."
  echo "Set openai_api_key in the add-on options, then restart the add-on."
fi

exec t3 start \
  --mode web \
  --host 0.0.0.0 \
  --port "$T3CODE_PORT" \
  --base-dir "$T3CODE_HOME" \
  --no-browser \
  --auto-bootstrap-project-from-cwd \
  --log-level "${T3CODE_LOG_LEVEL:-info}"
