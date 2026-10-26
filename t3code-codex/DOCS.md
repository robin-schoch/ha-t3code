# T3 Code server for Home Assistant

The add-on runs T3 Code and Codex on Home Assistant OS. Your desktop app connects over Tailscale and controls work on the server's files.

```text
T3 Code desktop -> Tailscale -> Home Assistant port 8099
                                  -> T3 Code server -> Codex -> /homeassistant
```

## Upgrade from 0.1.x

Version 0.2.0 removes the Ingress panel and the patched web client. Existing private T3 and Codex data remain under `/data`; back up the add-on before upgrading because newer T3 versions may migrate their database. Follow the pairing steps below after upgrading. Use a desktop version compatible with the packaged T3 server (0.0.45).

## Connect your desktop

1. Confirm Home Assistant and your desktop are on the same tailnet. In the Home Assistant Tailscale add-on, use `userspace_networking: false` so the host has a Tailscale network interface. Check that your tailnet access rules allow your desktop to reach the Home Assistant host on TCP port `8099`.
2. In this add-on's **Configuration**, enter Home Assistant's reachable Tailscale address in **Tailscale server URL** (`remote_url`), including the `http://` prefix and port. Find the Home Assistant node's `100.x.y.z` address in the Tailscale app or admin console. For example:

   ```yaml
   remote_url: "http://100.101.102.103:8099"
   openai_api_key: ""
   t3code_log_level: "Info"
   ```

   Replace that example IP with your Home Assistant node's Tailscale IP. You can also use its full MagicDNS name, such as `http://homeassistant.your-tailnet.ts.net:8099`. Use the host address, not an add-on container IP or `localhost`. The setting accepts an HTTP(S) origin without a path, query, or credentials.

   If you see **Invalid configuration: expected a URL** on version 0.2.0, click **Go to configuration**, enter a complete `remote_url` as above, and save. If the field is hidden, enable **Show unused optional configuration options**, or open the configuration menu and choose **Edit in YAML**. This is an add-on option; do not put it in Home Assistant's `configuration.yaml`. Version 0.2.1 also fixes the invalid empty default so you can leave it blank while setting up.
3. In the add-on's **Network** settings, enable the disabled `8099/tcp` mapping and set its host port to `8099`. You may need to show disabled ports. If you choose another host port, use that port in `remote_url` too. Save and start the add-on.
4. Open the add-on's **Log** tab. Copy the URL under **Desktop pairing link for ...**. It is valid for one use and expires after ten minutes. Keep the token private. Ignore any additional automatically generated link that uses a container or loopback address.
5. In your T3 Code desktop app, open **Settings > Connections > Add environment** and paste the pairing URL. Select the Home Assistant environment. The client stores its authorization for future connections, so you do not need to pair again after ordinary restarts.
6. Add a project on that remote environment with the path `/homeassistant`. This is the live Home Assistant configuration, including `configuration.yaml`, `automations.yaml`, and `custom_components`.
7. To use your ChatGPT account, leave `openai_api_key` empty. In **Settings > Providers**, select the Home Assistant environment and choose **Connect with ChatGPT**. Complete the OpenAI sign-in in your desktop browser. Your desktop's existing local Codex login does not automatically authenticate the server.

For a fresh pairing link, restart the add-on and copy the new labeled link. Restarting interrupts active work, so wait for running tasks to finish first. If you already have a terminal inside this add-on container, you can issue a link without restarting:

```sh
t3 auth pairing create --base-dir /data/t3code --base-url http://100.101.102.103:8099 --ttl 10m
```

Run that command inside the T3 add-on, not another Home Assistant terminal container. Replace the address and port with your own.

## Rename a server

In add-on **Configuration**, set **Server name** (`server_name`), then save and restart the add-on. This option is available in version 0.2.5 and later. Give each installation its own name, for example:

```yaml
server_name: "Home Assistant Home"
```

On your second installation, use `server_name: "Home Assistant Rofka"`. Add this alongside the other add-on options, or use the Server name field in the configuration form. If it is hidden, enable **Show unused optional configuration options**.

Reconnect or refresh your T3 client after restarting. The server advertises the new name. If an existing client keeps showing its cached connection name, create a fresh pairing link and use **Add environment** on that client again to refresh its saved label. The server's identity, project files, and Tailscale address are unchanged. Leave the setting empty to return to the container hostname.

T3 Code 0.1.2 reads the Linux `PRETTY_HOSTNAME` from `/etc/machine-info`. The launcher writes this inside the add-on container on every start, using the saved option; it does not rename the Home Assistant host. See the [upstream name resolver](https://github.com/pingdotgg/t3code/blob/v0.1.2/apps/server/src/environment/ServerEnvironmentLabel.ts).

## Codex authentication

### Use your ChatGPT account (no API key)

1. Leave `openai_api_key: ""` in the add-on options. If you previously entered a key, clear it and restart the add-on before connecting your account.
2. Pair your desktop with the add-on, then open **Settings > Providers** and select the **Home Assistant** remote environment.
3. Choose **Connect with ChatGPT**, sign in with your OpenAI/ChatGPT account in your desktop browser, and approve the connection. Access and usage depend on your ChatGPT plan and workspace permissions.
4. Return to T3 Code and select the connected account for a thread in the remote `/homeassistant` project.

If remote sign-in ends on a localhost page that cannot load, paste that page's full URL into T3 Code's sign-in panel. Do not change the URL to your Home Assistant address. T3 handles completion on the remote environment. See [T3 Code's ChatGPT sign-in instructions](https://github.com/pingdotgg/t3code/blob/v0.1.2/docs/user/providers-codex.md#connect-with-chatgpt).

This connection is separate from the Codex CLI login. T3 stores its managed account state in its persistent data, and your desktop's local login stays unchanged. No API key or copied authentication file is required for this flow.

### Optional: API-key authentication

Only set `openai_api_key` if you intentionally want API billing. With it set, startup passes the key on standard input to `codex login --with-api-key` and stores that CLI login in `/data/.codex/auth.json`. Keys are not passed as command-line arguments. An explicitly configured API key takes precedence over a previously saved CLI login.

With the option empty, the server still starts and existing saved CLI credentials are preserved. You can also authenticate the installed Codex CLI from a terminal inside this add-on using `codex login --device-auth` if you prefer a CLI login over T3's managed ChatGPT connection.

See the [official OpenAI authentication documentation](https://developers.openai.com/codex/auth) and [CLI login reference](https://developers.openai.com/codex/cli/reference#codex-login).

## Network access

The server listens inside the container on port `8099`, with T3's own pairing and session authentication enabled. The host port mapping is disabled by default. Publishing it can make it reachable on the LAN as well as Tailscale: setting `remote_url` controls the pairing link, not which interfaces may connect. Restrict access with your host/network policy as needed. Do not forward this port from your internet router.

For the desktop app, direct HTTP over the Tailscale route is sufficient; Tailscale encrypts the traffic between its nodes. Both devices must be connected to Tailscale, and the pairing URL must use the Tailscale address.

The add-on does not bundle Tailscale or share the other add-on's daemon socket. Do not add `--tailscale-serve` to its launcher. If you later want HTTPS for the hosted web client, configure a separate Tailscale Serve/Services endpoint to forward to the published server port, then set `remote_url` to that HTTPS origin. `remote_url` does not create a proxy or certificate.

Upstream references: [T3 Code remote access](https://github.com/pingdotgg/t3code/blob/v0.1.2/docs/user/remote-access.md), [Home Assistant Tailscale configuration](https://github.com/hassio-addons/addon-tailscale/blob/main/tailscale/DOCS.md), and [Home Assistant app port mappings](https://developers.home-assistant.io/docs/apps/configuration/).

## Editing Home Assistant files

Select the remote Home Assistant project before starting a thread. Work directly in `/homeassistant` when you want edits to affect the live configuration directory. Changes in a separate Git worktree will not affect Home Assistant until you explicitly apply them to the live directory.

Use Git and Home Assistant backups to keep changes recoverable. Review the diff, validate the configuration with Home Assistant, and then reload or restart the affected functionality. This add-on mounts files but does not grant Supervisor API access or install the `ha` CLI, so do not assume `ha core check` is available inside it.

Create an `AGENTS.md` file in your Home Assistant configuration root with project instructions such as:

```markdown
# Home Assistant Configuration Instructions

- Prefer small, reviewable changes.
- Do not edit secrets.yaml or .storage/ unless explicitly asked.
- Do not delete backups, database files, or generated caches.
- Validate Home Assistant configuration after YAML changes when possible.
- Explain changed files before suggesting a restart.
```

## Persistent storage

```text
/homeassistant  Home Assistant configuration, read-write
/config         Public add-on config directory
/data           Private persistent add-on data
/data/t3code    T3 Code state (runtime data under userdata/)
/data/.codex    Codex credentials and state
```

Protect add-on backups as they can contain credentials. Changing the network address does not require moving any project files or credentials.

## Troubleshooting

- **Startup fails with a schema error at T3CODE_LOG_LEVEL:** Update/rebuild the add-on to version 0.2.2 or later. Earlier launchers incorrectly converted `Info` to `info` before creating a pairing link. Keep `t3code_log_level: "Info"`; changing the option alone does not fix that launcher bug.
- **Cannot connect:** Check the enabled host port, `remote_url`, both Tailscale connections, tailnet access rules, and `userspace_networking: false` on the Home Assistant Tailscale add-on. A changed option requires restarting the T3 add-on.
- **Pairing expired or already used:** Generate a fresh link. Existing paired clients can reconnect without the original link.
- **No Home Assistant files:** Select the remote environment and add `/homeassistant`; a project on your laptop uses your laptop's files.
- **Provider not authenticated:** Select Home Assistant in provider settings and authenticate there, or set `openai_api_key` and restart.
- **Changes do not appear in Home Assistant:** Confirm the task edited `/homeassistant` rather than a separate worktree, then validate and reload the affected configuration.

## Updating packaged versions

The Dockerfile pins T3 Code at `0.0.45` and Codex CLI at `0.159.0`, matching T3's [bundled provider compatibility recommendation](https://github.com/pingdotgg/t3code/blob/v0.1.2/apps/server/src/provider/model-manifest.json). Update the build arguments, bump the add-on version in `config.yaml` and the Dockerfile, rebuild, and test startup and desktop pairing. Keep the desktop and server versions compatible. There are no client bundle patches to maintain.

For a local server/authentication smoke test, install the pinned T3 CLI and run:

```sh
python3 scripts/smoke-test.py --t3 /path/to/t3
```

The test uses temporary state and a temporary project. It runs T3 with the launcher's actual option-loading environment and checks remote URL validation, one-time pairing, rejection of unauthenticated access to protected endpoints, and session persistence after restart. It does not run a model or modify Home Assistant files. A Home Assistant container build and a desktop connection over your tailnet still need to be tested on your deployment.
