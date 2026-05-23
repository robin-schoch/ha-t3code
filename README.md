# T3 Code Codex

Run T3 Code inside Home Assistant and use OpenAI Codex to inspect and edit the Home Assistant configuration directory.

This add-on exposes the T3 Code web UI through Home Assistant Ingress. The Home Assistant configuration folder is mounted read-write at `/homeassistant` inside the container.

This is experimental and intentionally admin-only. Codex can modify files such as `configuration.yaml`, `automations.yaml`, and `custom_components`.
