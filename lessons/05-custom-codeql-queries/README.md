# Lesson 05 — Custom CodeQL Queries

Write your own CodeQL query to enforce an organisation-specific rule the default suite does not catch.

## Goal

You will:

1. Read a small custom CodeQL query (`py/tkl/hardcoded-debug-true`) that flags a module-level `DEBUG = True` constant — a common cause of leaking stack traces to end users.
2. See it fire on `target.py` and stay silent on `bypass.py`, demonstrating query *precision*.
3. Learn how custom queries are loaded into the CodeQL workflow and how to evolve them.

## Where the query lives

The query file lives in the repository at:

[`.github/codeql/custom-queries/HardcodedDebugFlag.ql`](https://github.com/tkl-enteprises/ghas-demos/blob/main/.github/codeql/custom-queries/HardcodedDebugFlag.ql)

It is owned by the GHAS-config track of the workshop, but you can read and edit it freely.

## How custom queries get loaded

CodeQL discovers custom queries through the workflow's config file:

[`.github/codeql/codeql-config.yml`](https://github.com/tkl-enteprises/ghas-demos/blob/main/.github/codeql/codeql-config.yml)

That config tells the `github/codeql-action/init` step to load the default Python query suite **plus** every `.ql` file under `.github/codeql/custom-queries/`. Each query produces alerts under its own rule id (`py/tkl/hardcoded-debug-true` here), so you can filter the Code Scanning view by rule id.

If you fork this repo and add a new `.ql` file in that directory, it is picked up automatically on the next workflow run — no workflow edits needed.

## Hands-on steps

1. **Read the query.** Open `HardcodedDebugFlag.ql` and identify (a) the `import` line that pulls in the Python library, (b) the `from … where … select` clause, (c) the `@id` and `@kind` metadata that determine where alerts surface in the UI.
2. **Read both targets.** [`target.py`](./target.py) sets `DEBUG = True` at module level — the query should fire here. [`bypass.py`](./bypass.py) computes `DEBUG` from `os.environ`, so the right-hand side is *not* a constant `True` literal — the query should stay silent. Comparing the two is the precision check.
3. **Trigger a scan.** Push a small change to either file (or open a PR) so the `CodeQL` workflow runs.
4. **Filter for the custom rule.** In **Security → Code scanning**, set the filters to:
   - **Tool:** `CodeQL`
   - **Rule:** `py/tkl/hardcoded-debug-true`
   You should see exactly one alert, on `lessons/05-custom-codeql-queries/target.py` at the `DEBUG = True` line. `bypass.py` should not appear.

## Writing your own query

CodeQL queries are written in QL, a declarative logic language. The fastest path to your first useful query:

- Start at the [CodeQL documentation portal](https://codeql.github.com/docs/) — read *About CodeQL* and *CodeQL for Python*.
- Browse the [Python query help pages](https://codeql.github.com/codeql-query-help/python/) to see how the built-in queries are structured. Most are 20–60 lines of QL with a handful of taint-tracking helpers — readable even on day one.
- Install the [CodeQL CLI](https://github.com/github/codeql-cli-binaries/releases) and run a query against a local database with:

  ```bash
  codeql database create py-db --language=python --source-root=.
  codeql query run \
    --database=py-db \
    .github/codeql/custom-queries/HardcodedDebugFlag.ql
  ```

  The CLI prints results to your terminal, so you can iterate locally without waiting for the GitHub Actions workflow.
- Use the [CodeQL extension for VS Code](https://marketplace.visualstudio.com/items?itemName=GitHub.vscode-codeql) — it gives you autocomplete, hover docs and an interactive Quick Eval mode for ad-hoc QL snippets.

## Files

| File | Purpose |
| --- | --- |
| `target.py` | Positive control — should produce one alert from the custom query. |
| `bypass.py` | Negative control — should not produce any alert from the custom query. |
| `solution.md` | Ideas for evolving the query (broaden the truthy check, raise precision, reduce false positives). |
| `README.md` | This file. |
