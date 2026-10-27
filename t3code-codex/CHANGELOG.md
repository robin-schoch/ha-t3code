# Changelog

## 0.2.6

- Bundle Claude Code CLI 2.1.311 alongside Codex, available as `claude` on both supported architectures.
- Preserve Claude credentials and settings in private persistent add-on storage.

## 0.2.5

- Add a persistent `server_name` option to distinguish Home Assistant servers in T3 Code.
- Apply the display name through the add-on container's Linux pretty hostname.

## 0.2.4

- Upgrade T3 Code from 0.0.45 to 0.1.2.

## 0.2.2

- Preserve the case of `T3CODE_LOG_LEVEL` so pairing and startup no longer fail with a configuration schema error.
- Exercise the launcher's option-loading environment in the server/authentication smoke test.
- Clarify that a missing Codex CLI login does not prevent connecting a ChatGPT account through T3.

## 0.2.1

- Fix Home Assistant rejecting the default empty `remote_url` as an invalid URL.
- Explain the Tailscale URL and optional API key directly in the configuration form.
- Clarify using a ChatGPT account without an API key.

## 0.2.0

- Replace the Ingress web UI and client patches with the unmodified T3 Code 0.0.45 headless server.
- Update Codex CLI to 0.159.0, matching T3 Code's bundled compatibility recommendation.
- Add an optional host port and `remote_url` setting for desktop pairing over Tailscale.
- Print a one-time remote pairing link at startup, valid for ten minutes.
- Persist Codex API-key login in private add-on data.
- Existing installs must configure the network port and pair their desktop client; the Ingress panel is removed.

## 0.1.4

- Patch T3 Code environment descriptor requests for Home Assistant Ingress.

## 0.1.3

- Patch T3 Code client API, WebSocket, and router paths for Home Assistant Ingress.

## 0.1.2

- Use relative T3 Code web asset URLs so the UI loads behind Home Assistant Ingress.

## 0.1.1

- Add build dependencies needed to compile npm native modules on arm64.

## 0.1.0

- Initial local add-on packaging for T3 Code and OpenAI Codex CLI.
