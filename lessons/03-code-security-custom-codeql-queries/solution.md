# Lesson 03 — Evolving the Query

The starter `UnprotectedAdminRoute.ql` checks one thing: whether a Flask route under `/admin` has a decorator named `admin_required`. That narrow rule is easy to explain and has a deterministic positive and negative control. The following extensions show how a production policy query could evolve. Each was checked with CodeQL 2.27.4 against the fixtures shown; add the same fixtures to the query's regression corpus before you change the query.

## 1. Exempt endpoints that must stay public

The administrator sign-in page lives under `/admin` but can't require an administrator. The starter query reports it:

```python
@app.route("/admin/login")
def admin_login():
    ...
```

Add an explicit allow-list rather than loosening the URL pattern:

```ql
/** Holds if `url` must stay reachable without administrator rights. */
predicate isPublicByDesign(string url) { url = ["/admin/login"] }
```

Then add `not isPublicByDesign(route.getUrlPattern())` to the `where` clause. Keep the list short and reviewed: the query never checks an allow-listed route again.

## 2. Check the decorator order

Flask registers the function that `@app.route` receives. If `@admin_required` is listed above `@app.route`, Flask registers the unwrapped view and the check never runs. The starter query still sees the decorator and stays silent:

```python
@admin_required
@app.route("/admin/wrong-order")
def wrong_order():
    ...
```

CodeQL represents stacked decorators as nested calls, and the lowest decorator is applied first. Require `@admin_required` to be applied before the route registers the handler:

```ql
/** Holds if decorator `inner` is applied before `outer`, that is, listed below it. */
predicate appliedBefore(Call inner, Call outer) {
  outer.getArg(0) = inner
  or
  appliedBefore(inner, outer.getArg(0))
}

/** Holds if `@admin_required` wraps `handler` before `route` registers it. */
predicate isAdminProtected(Http::Server::RouteSetup route, Function handler) {
  exists(FunctionExpr def, Call registration, Call check |
    def = handler.getDefinition() and
    registration = def.getADecoratorCall() and
    registration.getFunc() = route.asExpr() and
    check = def.getADecoratorCall() and
    check.getFunc().(Name).getId() = "admin_required" and
    appliedBefore(check, registration)
  )
}
```

Replace the starter predicate with these two, and change the `where` clause to `not isAdminProtected(route, handler)`.

## 3. Match the import, not just the name

The starter query accepts any decorator named `admin_required`, including a local function that does nothing:

```python
def admin_required(view):
    return view
```

Use API graphs to accept only the decorator imported from the shared `auth` module:

```ql
import semmle.python.ApiGraphs

/** Holds if `handler` is decorated with `admin_required` imported from the `auth` module. */
predicate isAdminProtected(Function handler) {
  handler.getADecorator() =
    API::moduleImport("auth").getMember("admin_required").getAValueReachableFromSource().asExpr()
}
```

In a real codebase, replace `auth` with the import path of your shared authorization library.

## 4. Know the remaining blind spots

The query only sees routes that CodeQL's Flask model recognizes, and it only checks each route's own URL pattern. With CodeQL 2.27.4 it misses:

- Blueprint routes that get their `/admin` prefix from `url_prefix`, for example `Blueprint("admin", __name__, url_prefix="/admin")` with `@admin.route("/users/export")`. The route's own pattern is `/users/export`.
- Flask's shortcut decorators such as `@app.get` and `@app.post`, which the Flask model doesn't treat as route setups.

Close a gap only when your codebase uses that pattern, and add a positive control for it first.

## Testing query changes locally

```bash
codeql database create py-db --language=python --source-root=.

codeql query run \
  --database=py-db \
  .github/codeql/custom-queries/UnprotectedAdminRoute.ql

codeql database analyze py-db \
  --format=sarif-latest \
  --output=results.sarif \
  --sarif-category=python \
  .github/codeql/custom-queries/
```

The starter query should return one location in `noncompliant.py`. `results.sarif` also embeds the rule help from `UnprotectedAdminRoute.md`, which is the text GitHub shows on the alert page.

## Recap

- Start with an exact, explainable policy.
- Pair every positive fixture with a negative control.
- Broaden predicates only when new test cases justify the additional recall.
- Write down what the query can't see, so a clean result isn't mistaken for full coverage.
