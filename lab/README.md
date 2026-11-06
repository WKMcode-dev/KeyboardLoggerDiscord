# KeyboardLoggerDiscord v2.0 — Authorized Telemetry Lab

This branch preserves the original project while introducing a safe, opt-in client/server learning environment. **It does not record keystrokes, clipboard data, screenshots, or execute remote commands.** No hidden persistence or security bypasses are used.

## Quick start (Windows PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r lab/requirements-dev.txt
$env:LAB_API_KEY = "replace-with-a-long-random-secret"
uvicorn lab.server:app --host 127.0.0.1 --port 8000
```

In a second PowerShell window, activate the same environment and set the same `LAB_API_KEY`, then run:

```powershell
python -m lab.client --label "Test PC A" --message "Hello from A"
python -m lab.client --label "Test PC B" --message "Hello from B"
```

Each run generates a new UUID unless `--id` is explicitly supplied. To reuse a session, pass the same UUID on subsequent invocations.

Visit `http://127.0.0.1:8000/docs` to inspect the API. Protected endpoints require the `X-Lab-Key` header.

## Optional Discord read-only interface

Set `DISCORD_TOKEN` and `LAB_API_KEY`, install requirements, and run `python -m lab.discord_view`. Use `!agents` in your test server. This does not create channels or publish event contents.

## Tests

```powershell
python -m pytest lab/tests -q
```

## Security

Keep the server bound to loopback unless you configure TLS, firewall restrictions, and per-client credentials. Never commit secrets. Rotate any Discord token previously committed to the original repository. Shared lab API keys are intended only for isolated local testing.
