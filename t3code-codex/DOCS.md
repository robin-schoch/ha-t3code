# T3 Code Codex

## What it does

This add-on packages:

- T3 Code, installed from the `t3` npm package.
- OpenAI Codex CLI, installed from `@openai/codex`.
- Git, ripgrep, jq, and OpenSSH client utilities.

The add-on starts T3 Code in web mode on port `8099` and exposes it through Home Assistant Ingress.

## Configuration

```yaml
openai_api_key: ""
t3code_log_level: "Info"
```

`openai_api_key` is optional in the schema, but you normally need it for non-interactive Codex use inside the container. The launcher exports it as `OPENAI_API_KEY`.

`t3code_log_level` controls T3 Code logging. Keep it at `Info` unless debugging startup issues.

## Mounted paths

```text
/homeassistant  Home Assistant configuration, read-write
/config         Public add-on config directory
/data           Private persistent add-on data
```

T3 Code state is stored in `/data/t3code`. Codex state is stored under `/data/.codex`.

## Recommended project instructions

Create an `AGENTS.md` file in your Home Assistant configuration root with guardrails like:

```markdown
# Home Assistant Configuration Instructions

- Prefer small, reviewable changes.
- Do not edit `secrets.yaml` unless explicitly asked.
- Do not edit files under `.storage/` unless explicitly asked.
- Do not delete backups, database files, or generated caches.
- Run Home Assistant configuration validation after YAML changes when possible.
- Explain changed files before suggesting a restart.
```

## Security notes

This add-on has read-write access to the Home Assistant configuration directory. Keep it admin-only, use Ingress rather than a public port, and leave boot mode as manual unless you are comfortable with it always being available.

Use Git for your Home Assistant configuration before asking Codex to make changes.

## Updating packaged versions

The Dockerfile pins package versions with build arguments:

```dockerfile
ARG T3_VERSION=0.0.24
ARG CODEX_VERSION=0.133.0
```

Update those values, bump `version` in `config.yaml`, rebuild the add-on, and test startup.
