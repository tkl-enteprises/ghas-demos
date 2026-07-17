"""
⚠️ INTENTIONALLY VULNERABLE — for educational use only.
Part of GHAS workshop demos: https://github.com/tkl-enteprises/ghas-demos
Do not deploy or use in production. Every issue here is detected by GHAS.

A deliberately tiny login helper with exactly ONE vulnerability so the
Copilot Autofix UI stays uncluttered for the workshop demo:

    py/sql-injection (CWE-89) — string-concatenated SQL on cursor.execute.
"""

import sqlite3
import sys

DB_PATH = "workshop.db"


def authenticate(username: str, password: str) -> bool:
    """Return True if the username/password pair matches a row in `users`.

    ⚠️ The query is built by string concatenation, so a username like
    `admin' --` lets the attacker bypass the password check entirely.
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        query = (
            "SELECT 1 FROM users "
            "WHERE username = '" + username + "' "
            "AND password = '" + password + "'"
        )
        cursor.execute(query)
        return cursor.fetchone() is not None
    finally:
        conn.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python insecure_login.py <username> <password>")
        sys.exit(1)
    ok = authenticate(sys.argv[1], sys.argv[2])
    print("authenticated" if ok else "denied")
