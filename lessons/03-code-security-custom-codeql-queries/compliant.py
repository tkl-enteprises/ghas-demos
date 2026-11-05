"""
Negative control for the Lesson 03 custom CodeQL query.

Identical to noncompliant.py except that `export_users` uses @admin_required.
/health is public by design and outside /admin, so this file must not produce
an alert.
"""

from flask import Flask

from auth import admin_required

app = Flask(__name__)


@app.route("/health")
def health():
    return {"status": "ok"}


@app.route("/admin/audit-log")
@admin_required
def audit_log():
    return {"events": []}


@app.route("/admin/users/export")
@admin_required
def export_users():
    return {"users": []}
