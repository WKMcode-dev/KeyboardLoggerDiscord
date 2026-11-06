# KeyboardLoggerDiscord v2.0 — Authorized Telemetry Lab

This branch preserves the original project while introducing a safe, opt-in client/server learning environment. It does **not** capture global keystrokes, clipboard data, screenshots, or other applications' activity. It does not create hidden copies or startup persistence.

## Windows 11 — setup

In PowerShell, from the repository root:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r lab/requirements-dev.txt
$env:LAB_API_KEY = "replace-with-a-long-random-secret"
uvicorn lab.server:app --host 127.0.0.1 --port 8000
```

In another PowerShell window, activate the environment, set the **same** `LAB_API_KEY`, and run the visible keyboard test window:

```powershell
python -m lab.gui_client
```

Type test text in its text field. The client sends the current text after a short typing pause; only that field is monitored. It creates a unique UUID for each launch. You can also run `python -m lab.client --message "Hello"` for explicit API checks.

Visit `http://127.0.0.1:8000/docs` to inspect the API. Protected endpoints require the `X-Lab-Key` header.

## Optional Discord status

Set `DISCORD_TOKEN` and `LAB_API_KEY`, then run `python -m lab.discord_view`. Use `!agents` in your private test server. The bot exposes a read-only session list; it does not yet forward text events or create per-agent channels.

## Tests

```powershell
python -m pytest lab/tests -q
```

## Cleanup / uninstall

Close the GUI, Discord bot and server. Then:

```powershell
python -m lab.uninstall --db lab.sqlite3
python -m lab.uninstall --db lab.sqlite3 --confirm
```

The first command previews the removal; the second deletes the selected local SQLite database (including SQLite sidecar files). Delete the downloaded project directory or any packaged test executable to finish. This lab does not register scheduled tasks, Windows services, Run keys or hidden copies.

## Security

Keep the server bound to loopback unless you configure TLS, firewall restrictions, and per-client credentials. Never commit secrets. Rotate any Discord token previously committed to the original repository. The shared lab API key is only for isolated local testing.
