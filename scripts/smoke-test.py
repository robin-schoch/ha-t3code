#!/usr/bin/env python3
"""Exercise the packaged T3 CLI without a provider login or inference request."""

import argparse
import http.cookiejar
import json
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--t3', default=shutil.which('t3'))
    args = parser.parse_args()
    if not args.t3:
        parser.error('Install the pinned T3 version or pass --t3 /path/to/t3')

    # Exercise the launcher's actual validation code without running the add-on.
    launcher = (Path(__file__).resolve().parents[1] / 't3code-codex/run.sh').read_text()
    validator = launcher.split("<<'JS'\n", 1)[1].split('\nJS\n', 1)[0]
    for url, expected in [
        ('http://100.101.102.103:8099', 0),
        ('https://homeassistant.example.ts.net', 0),
        ('http://homeassistant.example.ts.net:9000/', 0),
        ('http://localhost:8099', 1),
        ('http://127.0.0.1:8099', 1),
        ('http://[::1]:8099', 1),
        ('http://0.0.0.0:8099', 1),
        ('file:///tmp/config', 1),
        ('http://100.101.102.103:8099/path', 1),
        ('http://user:password@100.101.102.103:8099', 1),
        ('http://100.101.102.103:8099?token=example', 1),
        ('not a URL', 1),
    ]:
        result = subprocess.run(['node', '-', url], input=validator, text=True,
                                capture_output=True, check=False)
        assert result.returncode == expected, 'Remote URL validation failed'
    print('PASS remote URL validation')

    with tempfile.TemporaryDirectory(prefix='ha-t3-smoke-') as directory:
        root = Path(directory)
        workspace = root / 'homeassistant'
        workspace.mkdir()
        (workspace / 'configuration.yaml').write_text('default_config:\n')
        state = root / 'state'
        with socket.socket() as listener:
            listener.bind(('127.0.0.1', 0))
            port = listener.getsockname()[1]
        base_url = 'http://127.0.0.1:{}'.format(port)

        def cli(*arguments):
            result = subprocess.run([args.t3, *arguments], capture_output=True,
                                    text=True, timeout=30, cwd=workspace)
            # CLI output can contain a pairing secret. Never print it on failure.
            assert result.returncode == 0, 'T3 CLI command failed: {}'.format(arguments[0])
            return result.stdout

        issued = json.loads(cli('auth', 'pairing', 'create', '--base-dir', str(state),
                                '--base-url', base_url, '--ttl', '10m', '--json'))
        assert issued['pairUrl'].startswith(base_url + '/pair#')
        print('PASS pairing creation before server startup')

        cookies = http.cookiejar.CookieJar()
        client = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookies))

        def request(path, payload=None, authenticated=False):
            data = None if payload is None else json.dumps(payload).encode()
            query = urllib.request.Request(base_url + path, data=data, headers={
                'Content-Type': 'application/json', 'Origin': base_url,
            })
            try:
                with (client.open(query, timeout=3) if authenticated else
                      urllib.request.urlopen(query, timeout=3)) as response:
                    return response.status, json.loads(response.read())
            except urllib.error.HTTPError as error:
                return error.code, None

        def start(log):
            server = subprocess.Popen([
                args.t3, 'serve', '--mode', 'web', '--host', '0.0.0.0',
                '--port', str(port), '--base-dir', str(state), '--no-browser',
                '--log-level', 'error',
            ], cwd=workspace, stdout=log, stderr=log)
            try:
                deadline = time.monotonic() + 30
                while time.monotonic() < deadline:
                    assert server.poll() is None, 'Server exited during startup'
                    try:
                        status, descriptor = request('/.well-known/t3/environment')
                        if status == 200:
                            return server, descriptor
                    except (OSError, ValueError):
                        pass
                    time.sleep(0.2)
                raise AssertionError('Server did not become ready')
            except BaseException:
                stop(server)
                raise

        def stop(server):
            server.terminate()
            try:
                server.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=5)

        # All server output stays in temporary storage, including bootstrap tokens.
        with tempfile.TemporaryFile() as log:
            server, descriptor = start(log)
            try:
                assert request('/api/auth/session')[1]['authenticated'] is False
                assert request('/api/auth/pairing-token', {})[0] == 401
                assert request('/api/auth/browser-session', {'credential': 'invalid'})[0] == 401
                assert request('/api/auth/browser-session',
                               {'credential': issued['credential']}, True)[0] == 200
                assert request('/api/auth/session', authenticated=True)[1]['authenticated'] is True
                assert request('/api/auth/browser-session',
                               {'credential': issued['credential']})[0] == 401
                print('PASS unauthenticated access denied, pairing accepted once, session authorized')
            finally:
                stop(server)

            server, restarted_descriptor = start(log)
            try:
                assert descriptor['environmentId'] == restarted_descriptor['environmentId']
                assert request('/api/auth/session', authenticated=True)[1]['authenticated'] is True
                print('PASS environment identity and paired session persist across restart')
            finally:
                stop(server)


if __name__ == '__main__':
    main()
