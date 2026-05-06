# Lesson 03 — Custom CodeQL Queries

Write your own CodeQL query to enforce an organisation-specific rule the default suite does not catch.

## Goal

You will:

1. Read a small custom CodeQL query (`py/tkl/hardcoded-debug-true`) that flags a module-level `DEBUG = True` constant — a common cause of leaking stack traces to end users.
2. See it fire on `target.py` and stay silent on `bypass.py`, demonstrating query *precision*.
3. Learn how custom queries are loaded into the CodeQL workflow and how to evolve them.

## Learning objectives

After this lesson you can:

- Read a small CodeQL `.ql` file and identify imports, predicates, and select clauses.
- Configure custom queries via `.github/codeql/codeql-config.yml` so they load alongside the default suite.
- Verify a custom query has both **recall** (fires on positive control) and **precision** (silent on negative control).
- Run a custom query locally with the CodeQL CLI before pushing to CI.

## Estimated time

**~15 min demo + 5 min discussion**

## Prerequisites

- GHAS enabled, with **workflow-based CodeQL setup** (default setup does not load custom queries).
- `.github/codeql/codeql-config.yml` references the `custom-queries/` directory.
- The `CodeQL` workflow has run after the custom query was committed — check the Actions tab.

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
   You should see exactly one alert, on `lessons/03-custom-codeql-queries/target.py` at the `DEBUG = True` line. `bypass.py` should not appear.

![Code scanning alerts list filtered to rule `py/tkl/hardcoded-debug-true` showing exactly one alert — pointing at `target.py` — with `bypass.py` correctly absent.](../../docs/screenshots/03-custom-codeql-rule-list.png)

*Filtered view proving the custom query has both **recall** (fires on `target.py`) and **precision** (silent on `bypass.py`)._

![Detail page for alert #32 from `py/tkl/hardcoded-debug-true` showing the `DEBUG = True` line, the rule metadata, and the source location.](../../docs/screenshots/03-custom-codeql-alert-detail.png)

*Alert detail surfaces the query's `@id`, `@kind`, and `@description` metadata exactly as the default-suite alerts do — custom queries are first-class citizens in the alerts UI._

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

## Exit criteria

The demo has landed when:

- Attendees find the `py/tkl/hardcoded-debug-true` rule in the **Security → Code scanning** filter.
- The alert list shows exactly one alert (on `target.py`) and `bypass.py` is silent.
- Attendees can name the file in `.github/codeql/` that hooks the custom query into the workflow.

## Key takeaways

- Custom queries are **first-class** in the alerts UI — same dismiss, same Autofix, same severity scoring as default-suite queries.
- **Recall** (does it fire when it should?) and **precision** (does it stay silent when it should?) are the two metrics you tune over time. Both `target.py` and `bypass.py` exist to test the latter.
- You can iterate locally with the CodeQL CLI — no need to round-trip through Actions until you trust the query.

## Discussion questions

1. Where in your team's process would you draft, review, and promote a new custom query — does it live with the security org, the platform team, or alongside production code?
2. The default suite ships hundreds of queries. Would you ever ship a *negative* custom query that **suppresses** a default rule the team has decided not to enforce, or is that always a smell?

## Reset state

```bash
git checkout main && git pull
```

The custom query lives at `.github/codeql/custom-queries/HardcodedDebugFlag.ql` and is intended to remain enabled between cohorts. No reset needed.
