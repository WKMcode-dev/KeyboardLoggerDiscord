"""Visible, opt-in keyboard test window. Captures only its own text field."""
import os
import socket
import tkinter as tk
import uuid
from tkinter import messagebox
import requests

class LabWindow:
    def __init__(self, root):
        self.root = root
        root.title("KeyboardLoggerDiscord — Keyboard Test Lab")
        root.geometry("680x440")
        self.agent_id = str(uuid.uuid4())
        self.server = tk.StringVar(value=os.getenv("LAB_URL", "http://127.0.0.1:8000"))
        self.label = tk.StringVar(value=socket.gethostname())
        self.status = tk.StringVar(value="Not connected")
        self.last_sent = ""
        tk.Label(root, text="Visible keyboard test — only this window is monitored", font=("Segoe UI", 12, "bold")).pack(pady=12)
        tk.Label(root, text="Server URL").pack()
        tk.Entry(root, textvariable=self.server, width=65).pack(pady=4)
        tk.Label(root, text="Test computer label").pack()
        tk.Entry(root, textvariable=self.label, width=40).pack(pady=4)
        tk.Label(root, text="Type test text below (no passwords or private information)").pack(pady=8)
        self.editor = tk.Text(root, width=75, height=9, wrap="word")
        self.editor.pack(padx=12)
        self.editor.bind("<KeyRelease>", self.schedule_send)
        self.pending = None
        tk.Button(root, text="Send current text to lab server", command=self.send).pack(pady=8)
        tk.Button(root, text="Clear local text", command=self.clear).pack()
        tk.Label(root, textvariable=self.status).pack(pady=6)
        tk.Label(root, text=f"Session ID: {self.agent_id}", fg="gray").pack()
        root.protocol("WM_DELETE_WINDOW", self.close)

    def schedule_send(self, event=None):
        if self.pending:
            self.root.after_cancel(self.pending)
        self.pending = self.root.after(900, self.send)

    def send(self):
        self.pending = None
        key = os.getenv("LAB_API_KEY", "")
        if not key:
            self.status.set("Missing LAB_API_KEY environment variable")
            return
        message = self.editor.get("1.0", "end-1c")
        if not message or message == self.last_sent:
            return
        if len(message) > 500:
            self.status.set("Limit: 500 characters per test event")
            return
        headers = {"X-Lab-Key": key}
        base = self.server.get().rstrip("/")
        try:
            r = requests.post(base + "/heartbeat", headers=headers,
                json={"agent_id": self.agent_id, "label": self.label.get()}, timeout=4)
            r.raise_for_status()
            r = requests.post(base + "/events", headers=headers,
                json={"agent_id": self.agent_id, "kind": "test", "message": message}, timeout=4)
            r.raise_for_status()
            self.last_sent = message
            self.status.set("Sent successfully — check the server and Discord")
        except requests.RequestException as exc:
            self.status.set(f"Delivery failed: {exc.__class__.__name__}")

    def clear(self):
        self.editor.delete("1.0", "end")
        self.last_sent = ""
        self.status.set("Cleared")

    def close(self):
        if self.pending:
            self.root.after_cancel(self.pending)
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    LabWindow(root)
    root.mainloop()
