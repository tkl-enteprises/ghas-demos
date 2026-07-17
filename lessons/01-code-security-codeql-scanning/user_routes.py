"""
⚠️ INTENTIONALLY VULNERABLE — for educational use only.
Part of GHAS workshop demos: https://github.com/tkl-enteprises/ghas-demos
Do not deploy or use in production. Every issue here is detected by GHAS.

A pretend "Flask-style" search endpoint. We do not actually depend on Flask
in the workshop image — instead we fake the request with sys.argv so that
CodeQL still sees user input flowing into a sqlite3 query.
"""

import sqlite3
import sys


class FakeRequest:
    """Mimics the parts of a Flask request object that we need."""

    def __init__(self, args: dict[str, str]):
        self.args = args


def search_users(request: FakeRequest) -> list[tuple]:
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


def list_user_orders(request: FakeRequest) -> list[tuple]:
    """List orders for a given user_id.

    ⚠️ Same pattern, different sink — useful for showing CodeQL's per-route
    detection.
    """
    user_id = request.args.get("user_id", "")
    conn = sqlite3.connect("workshop.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, total FROM orders WHERE user_id = " + user_id)
    return cursor.fetchall()


if __name__ == "__main__":
    # Pretend the first argv is the `q` parameter.
    fake = FakeRequest({"q": sys.argv[1] if len(sys.argv) > 1 else ""})
    print(search_users(fake))
