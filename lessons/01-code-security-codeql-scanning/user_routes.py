"""
⚠️ INTENTIONALLY VULNERABLE — for educational use only.
Part of GHAS workshop demos: https://github.com/tkl-enteprises/ghas-demos
Do not deploy or use in production. Every issue here is detected by GHAS.

Flask route handlers that pass remote request data directly to sqlite3.
"""

import sqlite3

from flask import Flask, request


app = Flask(__name__)


@app.get("/users/search")
def search_users() -> list[tuple]:
    """Search users by partial name match.

    ⚠️ The `q` parameter is concatenated straight into the SQL string, so
    `?q=%' OR '1'='1` dumps the whole table. CodeQL flags this as
    py/sql-injection (CWE-89) with a taint path from `request.args[...]`
    into `cursor.execute`.
    """
    q = request.args.get("q", "")
    conn = sqlite3.connect("workshop.db")
    cursor = conn.cursor()
    sql = "SELECT id, username, email FROM users WHERE username LIKE '%" + q + "%'"
    cursor.execute(sql)
    return cursor.fetchall()


@app.get("/users/orders")
def list_user_orders() -> list[tuple]:
    """List orders for a given user_id.

    ⚠️ Same pattern, different sink — useful for showing CodeQL's per-route
    detection.
    """
    user_id = request.args.get("user_id", "")
    conn = sqlite3.connect("workshop.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, total FROM orders WHERE user_id = " + user_id)
    return cursor.fetchall()
