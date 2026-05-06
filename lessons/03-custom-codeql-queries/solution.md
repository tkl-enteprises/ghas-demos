# Lesson 03 — Evolving the Query

The starter `HardcodedDebugFlag.ql` flags the literal pattern:

```python
DEBUG = True
```

That is a useful baseline, but production codebases use a few near-equivalents that bypass the strict `True`-literal check. This document walks through three concrete extensions, ordered from easy to ambitious.

## 1. Broaden the truthy check

`DEBUG = 1` (or `DEBUG = "yes"`) is functionally identical to `DEBUG = True` from Python's truthiness rules. Extend the predicate to match any literal that Python evaluates as truthy:

```ql
import python

from Assign a, Name target, Expr value
where
    a.getATarget() = target and
    target.getId() = "DEBUG" and
    target.getScope() instanceof Module and
    value = a.getValue() and
    (
        // True
        value.(NameConstant).getValue() = true
        or
        // Non-zero int literal: 1, 2, ...
        value.(IntegerLiteral).getValue() != 0
        or
        // Non-empty string literal: "yes", "on", ...
        exists(StringLiteral s | s = value | s.getText().length() > 0)
    )
select target, "Module-level DEBUG flag is hard-coded to a truthy literal."
```

Push this and confirm `target.py` still fires — and add a third file `target_one.py` with `DEBUG = 1` to verify the new branch.

## 2. Catch always-true conditional bodies

Some teams "hide" a debug flag by guarding it with a constant expression, e.g.:

```python
if 1 == 1:
    DEBUG = True
```

CodeQL's data-flow library lets you trace back through such conditions. The shape is roughly:

```ql
import python
import semmle.python.dataflow.new.DataFlow

from If i, Assign a, Name target
where
    a.getEnclosingNode+() = i and
    target = a.getATarget() and
    target.getId() = "DEBUG" and
    forex(Expr cond | cond = i.getTest() | cond.(Compare).getOp(0) instanceof Eq and …)
select target, "DEBUG is set to True under a guard whose condition is always true."
```

Refining the guard predicate is the interesting part of the exercise — start by detecting the simplest constant-comparison case and grow from there.

## 3. Reduce false positives

Right now the query flags any module-level `DEBUG = True`. A few legitimate cases get caught:

- Test-only modules under `tests/` or `conftest.py`.
- Files that immediately overwrite `DEBUG` from the environment a few lines later (`DEBUG = True` then `DEBUG = bool(os.environ.get(...))`).
- `DEBUG` that is `__all__`-private and used only inside the module.

Exclude them with location/context filters:

```ql
where
    not target.getLocation().getFile().getRelativePath().regexpMatch(".*/(tests?|conftest)\\.py")
    and not exists(Assign later |
        later.getATarget().(Name).getId() = "DEBUG" and
        later.getLocation().getStartLine() > target.getLocation().getStartLine() and
        later.getEnclosingModule() = target.getEnclosingModule() and
        later.getValue() instanceof Call
    )
```

Re-run on the workshop repo. `bypass.py` already passes; the broadened query should keep it green.

## How to test query changes locally

```bash
# Build a database from the repo (run in repo root).
codeql database create py-db --language=python --source-root=.

# Run just your custom query.
codeql query run \
    --database=py-db \
    .github/codeql/custom-queries/HardcodedDebugFlag.ql

# Or run the whole workshop config the same way Actions does.
codeql database analyze py-db \
    --format=sarif-latest \
    --output=results.sarif \
    --sarif-category=python \
    .github/codeql/custom-queries/
```

Open `results.sarif` in VS Code with the CodeQL extension to step through every alert before pushing.

## Recap

- **Start strict, broaden later.** A query that fires once on a known-bad pattern is more useful than a perfect query you never ship.
- **Always have a negative control.** `bypass.py` is your regression test — if it ever shows up in the alert list, your last QL change lost precision.
- **Iterate locally with the CLI**, then promote to the workflow once results are stable.
