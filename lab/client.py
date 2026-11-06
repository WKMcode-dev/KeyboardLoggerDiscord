"""Visible, opt-in test client. Sends only explicitly supplied test messages."""
import argparse
import os
import socket
import uuid
import requests

def main():
    parser = argparse.ArgumentParser(description="Authorized lab telemetry client")
    parser.add_argument("--server", default="http://127.0.0.1:8000")
    parser.add_argument("--id", default=str(uuid.uuid4()))
    parser.add_argument("--label", default=socket.gethostname())
    parser.add_argument("--message", default="Hello from the test client")
    args = parser.parse_args()
    key = os.getenv("LAB_API_KEY", "")
    if not key:
        parser.error("Set LAB_API_KEY before running")
    headers = {"X-Lab-Key": key}
    base = args.server.rstrip("/")
    for route, payload in (
        ("/heartbeat", {"agent_id": args.id, "label": args.label}),
        ("/events", {"agent_id": args.id, "kind": "test", "message": args.message}),
    ):
        r = requests.post(base + route, json=payload, headers=headers, timeout=10)
        r.raise_for_status()
    print(f"Test event delivered. Agent ID: {args.id}")

if __name__ == "__main__":
    main()
