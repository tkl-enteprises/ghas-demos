"""
⚠️ INTENTIONALLY VULNERABLE — for educational use only.
Part of GHAS workshop demos: https://github.com/tkl-enteprises/ghas-demos
Do not deploy or use in production. Bandit detects every issue here.
"""
import sqlite3


def find_user(conn: sqlite3.Connection, username: str):
    cur = conn.cursor()
    # ⚠️ B608 — SQL built via string formatting → SQL injection.
    cur.execute("SELECT * FROM users WHERE username = '%s'" % username)
    return cur.fetchone()


def search_orders(conn: sqlite3.Connection, status: str):
    cur = conn.cursor()
    # ⚠️ B608 — f-string concatenation is the same anti-pattern.
    cur.execute(f"SELECT id, total FROM orders WHERE status = '{status}'")
    return cur.fetchall()
