"""
⚠️ INTENTIONALLY VULNERABLE — for educational use only.
Part of GHAS workshop demos: https://github.com/tkl-enteprises/ghas-demos
Do not deploy or use in production. Every issue here is detected by GHAS.

A deliberately tiny login route with exactly ONE vulnerability so the
Copilot Autofix UI stays uncluttered for the workshop demo:

    py/sql-injection (CWE-89) — string-concatenated SQL on cursor.execute.
"""

import sqlite3

from flask import Flask, request

DB_PATH = "workshop.db"
app = Flask(__name__)


@app.get("/login")
def login() -> tuple[str, int]:
    """Authenticate credentials supplied as remote query parameters.

    ⚠️ The query is built by string concatenation, so a username like
    `admin' --` lets the attacker bypass the password check entirely.
    """
    username = request.args.get("username", "")
    password = request.args.get("password", "")
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        query = (
            "SELECT 1 FROM users "
            "WHERE username = '" + username + "' "
            "AND password = '" + password + "'"
        )
        cursor.execute(query)
        if cursor.fetchone() is not None:
            return "authenticated", 200
        return "denied", 401
    finally:
        conn.close()
