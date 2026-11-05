# Admin route missing @admin_required

Every Flask route under `/admin` must use the `@admin_required` decorator from the organization's shared `auth` module. A route without it skips the administrator check, so any visitor can call the endpoint.

The default CodeQL suites can't find this on their own: they don't know which decorator enforces authorization in this codebase, or which URL prefix is privileged.

## Recommendation

Add `@admin_required` directly below `@app.route`. Flask registers the function that `@app.route` receives, so the authorization decorator must be the innermost one.

## Example

This route is missing the decorator:

```python
@app.route("/admin/users/export")
def export_users():
    return {"users": []}
```

The fixed route:

```python
@app.route("/admin/users/export")
@admin_required
def export_users():
    return {"users": []}
```

## References

- Flask: [View Decorators](https://flask.palletsprojects.com/en/stable/patterns/viewdecorators/)
- Common Weakness Enumeration: [CWE-862: Missing Authorization](https://cwe.mitre.org/data/definitions/862.html)
