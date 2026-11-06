"""Consent-based telemetry lab. No keyboard hooks or remote execution."""
import os
import re
import sqlite3
import time
from contextlib import contextmanager
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

DB_PATH = os.getenv("LAB_DB", "lab.sqlite3")
API_KEY = os.getenv("LAB_API_KEY", "")
app = FastAPI(title="KeyboardLoggerDiscord - Safe Lab", version="2.0.0")

@contextmanager
def database():
    db = sqlite3.connect(DB_PATH, timeout=10)
    try:
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("""CREATE TABLE IF NOT EXISTS agents (
            agent_id TEXT PRIMARY KEY, label TEXT NOT NULL, last_seen REAL NOT NULL)""")
        db.execute("""CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT, agent_id TEXT NOT NULL,
            kind TEXT NOT NULL, message TEXT NOT NULL, created_at REAL NOT NULL)""")
        yield db
        db.commit()
    finally:
        db.close()

class Heartbeat(BaseModel):
    agent_id: str = Field(pattern=r"^[a-f0-9-]{36}$")
    label: str = Field(min_length=1, max_length=80)

class Event(BaseModel):
    agent_id: str = Field(pattern=r"^[a-f0-9-]{36}$")
    kind: str = Field(pattern=r"^(test|status)$")
    message: str = Field(min_length=1, max_length=500)

def authorize(key: str):
    if not API_KEY or key != API_KEY:
        raise HTTPException(401, "Unauthorized")

@app.get("/health")
def health():
    return {"ok": True, "version": "2.0.0"}

@app.post("/heartbeat")
def heartbeat(data: Heartbeat, x_lab_key: str = Header(default="")):
    authorize(x_lab_key)
    with database() as db:
        db.execute("""INSERT INTO agents VALUES (?, ?, ?)
            ON CONFLICT(agent_id) DO UPDATE SET label=excluded.label,
            last_seen=excluded.last_seen""", (data.agent_id, data.label, time.time()))
    return {"ok": True}

@app.post("/events")
def event(data: Event, x_lab_key: str = Header(default="")):
    authorize(x_lab_key)
    with database() as db:
        if not db.execute("SELECT 1 FROM agents WHERE agent_id=?", (data.agent_id,)).fetchone():
            raise HTTPException(404, "Unknown agent")
        db.execute("INSERT INTO events(agent_id,kind,message,created_at) VALUES(?,?,?,?)",
                   (data.agent_id, data.kind, data.message, time.time()))
    return {"ok": True}

@app.get("/agents")
def agents(x_lab_key: str = Header(default="")):
    authorize(x_lab_key)
    with database() as db:
        return [{"agent_id": a, "label": b, "last_seen": c, "online": time.time()-c < 90}
                for a,b,c in db.execute("SELECT agent_id,label,last_seen FROM agents ORDER BY label")]

@app.get("/agents/{agent_id}/events")
def events(agent_id: str, x_lab_key: str = Header(default="")):
    authorize(x_lab_key)
    with database() as db:
        return [{"kind": k, "message": m, "created_at": t}
                for k,m,t in db.execute("""SELECT kind,message,created_at FROM events
                    WHERE agent_id=? ORDER BY id DESC LIMIT 100""", (agent_id,))]
