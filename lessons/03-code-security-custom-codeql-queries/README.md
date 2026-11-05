# Lesson 03 — Custom CodeQL Queries

Write a custom CodeQL query that enforces an authorization rule the default suites can't know about.

The rule: **every Flask route under `/admin` must use the `@admin_required` decorator** from the organization's shared `auth` module. A route without it is reachable by any visitor (CWE-862: Missing Authorization, part of OWASP's Broken Access Control category). The default CodeQL suites can't flag this, because they don't know which decorator enforces authorization in this codebase or which URL prefix is privileged.

## Goal

You will:

1. Read a custom CodeQL query (`py/tkl/unprotected-admin-route`) that reports `/admin` routes without `@admin_required`.
2. See it fire on `noncompliant.py` and remain silent on `compliant.py`.
3. Learn how repository-specific rules are loaded into CodeQL and tested for both recall and precision.

## Learning objectives

After this lesson you can:

- Identify the imports, predicates, metadata, and select clause in a small CodeQL query.
- Reuse CodeQL's built-in framework models instead of matching source text.
- Configure custom queries through `.github/codeql/codeql-config.yml`.
- Use positive and negative controls to test a custom rule.
- Run a custom query locally before pushing it to CI.

## Estimated time

**~15 min demo + 5 min discussion**

## Prerequisites

- GitHub Code Security enabled. This repository uses the **workflow-based (advanced) CodeQL setup**, so the configuration that loads the query is visible in source. Since August 2026, default setup can also apply a CodeQL configuration file through the `github-codeql-config-file` repository property (add queries, exclude paths, set threat models) — the at-scale option when you don't want a workflow in every repository.
- `.github/codeql/codeql-config.yml` references the custom query pack.
- The `CodeQL` workflow has run after the query and fixtures were committed.
- Optional: the CodeQL CLI for local iteration.

## Where the query lives

The query is [`.github/codeql/custom-queries/UnprotectedAdminRoute.ql`](https://github.com/tkl-enteprises/ghas-demos/blob/main/.github/codeql/custom-queries/UnprotectedAdminRoute.ql). Its rule help, which GitHub shows on the alert page, is in [`UnprotectedAdminRoute.md`](https://github.com/tkl-enteprises/ghas-demos/blob/main/.github/codeql/custom-queries/UnprotectedAdminRoute.md) next to it.

Its metadata gives the result the rule id `py/tkl/unprotected-admin-route`, a security severity of 7.5 (**High**), and the CWE-862 tag. It reports a request handler when all three of these conditions hold:

- CodeQL's Flask model recognizes it as the handler of a route.
- The route's URL is `/admin` or starts with `/admin/`.
- The handler has no `@admin_required` decorator.

## How custom queries get loaded

The [CodeQL configuration](https://github.com/tkl-enteprises/ghas-demos/blob/main/.github/codeql/codeql-config.yml) loads three things: the `security-extended` suite, a one-query suite that adds lesson 01's low-precision `py/hardcoded-credentials`, and the QL pack under `.github/codeql/custom-queries/`. Every `.ql` query in that pack runs during the Python analysis job and reports under its own rule id.

## Hands-on steps

1. **Read the query.** Open `UnprotectedAdminRoute.ql` and locate the `import` lines, the `isAdminProtected` predicate, the `from … where … select` clause, and the `@id`, `@kind`, `@precision`, and `@security-severity` metadata.
2. **Compare the controls.** [`noncompliant.py`](./noncompliant.py) and [`compliant.py`](./compliant.py) define the same three routes: a public `/health` check, `/admin/audit-log`, and `/admin/users/export`. The only code difference is that `export_users` in `noncompliant.py` has no `@admin_required`. Both files import the decorator from [`auth.py`](./auth.py).
3. **Trigger a scan.** Push the change or dispatch the `CodeQL` workflow.
4. **Filter the results.** Open **Security and quality → Code scanning**, select **Tool: CodeQL**, and filter to **Rule: `py/tkl/unprotected-admin-route`**.
5. **Check precision.** Expect exactly one alert, on `export_users` in `noncompliant.py`. `compliant.py` must not appear, and neither may the public `/health` route or the protected `/admin/audit-log` route.
6. **Open the alert.** It shows **High** severity, the CWE-862 tag, and the rule help from `UnprotectedAdminRoute.md`, including the fix.

This lesson has no screenshots yet. Capture the rule list and alert detail after the CodeQL workflow has run.

## Writing your own query

CodeQL queries are declarative. This one doesn't parse decorators as text: it uses CodeQL's Flask model through the `Http::Server::RouteSetup` concept, which already knows that `@app.route("/admin/users/export")` registers `export_users` as the handler for that URL.

```ql
import python
import semmle.python.Concepts

/** Holds if `handler` is decorated with `@admin_required`. */
predicate isAdminProtected(Function handler) {
  handler.getADecorator().(Name).getId() = "admin_required"
}

from Http::Server::RouteSetup route, Function handler
where
  handler = route.getARequestHandler() and
  route.getUrlPattern().regexpMatch("/admin(/.*)?") and
  not isAdminProtected(handler)
select handler, "Admin route '" + route.getUrlPattern() + "' is missing @admin_required."
```

Run it locally from the repository root with the [CodeQL bundle](https://github.com/github/codeql-action/releases) for your platform (it already contains the `codeql/python-all` dependency; with a CLI-only install, run `codeql pack install .github/codeql/custom-queries` first):

```bash
codeql database create py-db --language=python --source-root=.

# Fast iteration loop: prints the raw result table.
codeql query run --database=py-db .github/codeql/custom-queries/UnprotectedAdminRoute.ql

# Precision check: results with file and line.
codeql database analyze py-db .github/codeql/custom-queries/UnprotectedAdminRoute.ql \
  --format=csv --output=admin-routes.csv
cat admin-routes.csv
```

`admin-routes.csv` should contain exactly one row, for `noncompliant.py` line 28, and nothing for `compliant.py` (verified with CodeQL 2.27.4).

## Files

| File | Purpose |
| --- | --- |
| `noncompliant.py` | Positive control: `/admin/users/export` has no `@admin_required` and produces one alert. |
| `compliant.py` | Negative control: the same routes, with every `/admin` route protected, produce no alert. |
| `auth.py` | The shared `admin_required` decorator that both controls import. |
| `solution.md` | Exercises for broadening the rule while preserving precision. |
| `README.md` | Lesson walkthrough. |

## Exit criteria

- Attendees find `py/tkl/unprotected-admin-route` in the code-scanning rule filter.
- Exactly one alert points to `export_users` in `noncompliant.py`.
- `compliant.py` is absent from the results.
- Attendees can identify the config file that loads the custom query pack.
- Attendees can explain why the default suites can't detect this rule.

## Key takeaways

- Custom CodeQL queries turn your organization's security conventions into reviewable, versioned checks.
- Reuse CodeQL's framework models instead of matching source text: the route model already knows which function handles which URL.
- A positive control proves recall; a negative control protects precision.
- Start with an exact rule, then broaden only when tests justify it.
- Custom queries only cover languages CodeQL extracts. For other formats, such as Terraform, use a scanner for that format and upload its SARIF as shown in Lesson 04.

## Discussion questions

1. Which authorization conventions in your codebase could a query like this enforce?
2. `/admin/login` must stay reachable without administrator rights. How would you exempt it without hiding real findings?
3. What happens when `@admin_required` is listed above `@app.route` instead of below it? Does the starter query notice?
4. Should this rule block pull requests, or only report alerts?

## Reset state

```bash
git checkout main && git pull
```

The custom query is intended to stay enabled between cohorts; no additional reset is required.
