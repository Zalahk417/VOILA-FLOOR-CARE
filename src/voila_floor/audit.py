from __future__ import annotations

import json
import os
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from typing import Any

def init_db(path: str | None = None) -> str:
    path = path or os.getenv("VOILA_AUDIT_DB", "./voila_audit.sqlite3")
    with closing(sqlite3.connect(path)) as con, con:
        con.execute("""CREATE TABLE IF NOT EXISTS lead_audit (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL, idempotency_key TEXT NOT NULL, source TEXT NOT NULL, human_review_required INTEGER NOT NULL, risk_flags TEXT NOT NULL, missing_fields TEXT NOT NULL, payload_json TEXT NOT NULL)""")
        con.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_lead_audit_idempotency ON lead_audit(idempotency_key)")
    return path

def log_decision(decision: dict[str, Any], path: str | None = None) -> bool:
    path = init_db(path)
    with closing(sqlite3.connect(path)) as con, con:
        try:
            con.execute("INSERT INTO lead_audit (created_at,idempotency_key,source,human_review_required,risk_flags,missing_fields,payload_json) VALUES (?,?,?,?,?,?,?)", (datetime.now(timezone.utc).isoformat(), decision["idempotency_key"], decision["lead"]["source"], 1 if decision["human_review_required"] else 0, json.dumps(decision["risk_flags"], sort_keys=True), json.dumps(decision["missing_fields"], sort_keys=True), json.dumps(decision, sort_keys=True)))
            return True
        except sqlite3.IntegrityError:
            return False
