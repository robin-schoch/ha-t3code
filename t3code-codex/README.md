# T3 Code Codex

Run a headless T3 Code server inside Home Assistant and connect your T3 Code desktop app over Tailscale. OpenAI Codex runs in the add-on and can inspect and edit the Home Assistant configuration directory.

The Home Assistant configuration folder is mounted read-write at `/homeassistant` inside the container. T3 Code and Codex state stay in private persistent add-on storage.

Start with the [desktop and Tailscale setup guide](DOCS.md). You must enable the network port and pair your desktop; this add-on no longer provides a Home Assistant Ingress panel.

This is experimental and intended for administrators. Codex can modify files such as `configuration.yaml`, `automations.yaml`, and `custom_components`.
