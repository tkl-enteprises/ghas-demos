"""
Shared authorization decorator used by the Lesson 03 fixtures.

It stands in for an organization's internal auth library. The custom query
`py/tkl/unprotected-admin-route` requires it on every /admin route.
"""

from functools import wraps

from flask import abort, g


def admin_required(view):
    """Return 403 Forbidden unless the signed-in user is an administrator."""

    @wraps(view)
    def wrapper(*args, **kwargs):
        user = getattr(g, "user", None)
        if user is None or not user.is_admin:
            abort(403)
        return view(*args, **kwargs)

    return wrapper
