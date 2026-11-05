"""
Positive control for the Lesson 03 custom CodeQL query.

Workshop policy: every Flask route under /admin must use @admin_required.
`export_users` is missing the decorator, so `py/tkl/unprotected-admin-route`
reports it. Inert source fixture: nothing here starts a server.
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
def export_users():  # No @admin_required: the custom query flags this handler.
    return {"users": []}
