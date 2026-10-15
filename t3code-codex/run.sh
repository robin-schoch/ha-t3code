#!/usr/bin/env bash
set -euo pipefail
umask 077

export HOME=/data
export T3CODE_HOME=/data/t3code
export T3CODE_PORT=8099
export T3CODE_LOG_LEVEL="${T3CODE_LOG_LEVEL:-Info}"

mkdir -p "$T3CODE_HOME" "$HOME/.codex" /config
remote_url=""

if [ -f /data/options.json ]; then
  OPENAI_API_KEY_FROM_OPTIONS="$(jq -r '.openai_api_key // empty' /data/options.json)"
  T3CODE_LOG_LEVEL_FROM_OPTIONS="$(jq -r '.t3code_log_level // "Info"' /data/options.json)"
  remote_url="$(jq -r '.remote_url // empty' /data/options.json)"

  if [ -n "$OPENAI_API_KEY_FROM_OPTIONS" ]; then
    export OPENAI_API_KEY="$OPENAI_API_KEY_FROM_OPTIONS"
  fi

  # T3's environment parser accepts Info/Debug/etc., not lowercase CLI values.
  export T3CODE_LOG_LEVEL="$T3CODE_LOG_LEVEL_FROM_OPTIONS"
fi

if [ -n "$remote_url" ]; then
  # Pairing must use the host's reachable address, not a container or loopback IP.
  node - "$remote_url" <<'JS'
const value = process.argv[2];
try {
  const url = new URL(value);
  if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password ||
      url.pathname !== '/' || url.search || url.hash ||
      ['localhost', '127.0.0.1', '0.0.0.0', '[::]', '[::1]'].includes(url.hostname)) {
    throw new Error('Invalid remote URL');
  }
} catch {
  console.error('remote_url must be an HTTP(S) origin reachable from your desktop, for example http://100.101.102.103:8099');
  process.exit(1);
}
JS
fi

if [ ! -d /homeassistant ]; then
  echo "The Home Assistant configuration directory is not mounted at /homeassistant."
  exit 1
fi

cd /homeassistant

# Avoid git ownership warnings when the mounted config repository has host-side ownership.
git config --global --add safe.directory /homeassistant >/dev/null 2>&1 || true

if [ -n "${OPENAI_API_KEY:-}" ]; then
  # Codex app-server needs a saved login; exporting the key alone is insufficient.
  printf '%s' "$OPENAI_API_KEY" | codex -c 'cli_auth_credentials_store="file"' login --with-api-key
elif [ ! -f "$HOME/.codex/auth.json" ]; then
  echo "No Codex CLI login found. You can use your ChatGPT account: pair your desktop, select Home Assistant in Settings > Providers, and choose Connect with ChatGPT. No API key is required."
fi

if [ -n "$remote_url" ]; then
  echo "Desktop pairing link for $remote_url (one use, expires in 10 minutes):"
  t3 auth pairing create \
    --base-dir "$T3CODE_HOME" \
    --base-url "$remote_url" \
    --ttl 10m \
    --label "Home Assistant desktop"
else
  echo "Set remote_url to your Home Assistant Tailscale URL for a ready-to-use desktop pairing link."
fi

exec t3 serve \
  --mode web \
  --host 0.0.0.0 \
  --port "$T3CODE_PORT" \
  --base-dir "$T3CODE_HOME" \
  --no-browser
