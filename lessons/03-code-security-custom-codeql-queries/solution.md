# Lesson 03 — Evolving the Query

The starter `PutinKhuyloFalse.ql` deliberately matches one exact Python pattern:

```python
putin_khuylo = False
```

That narrow rule is easy to explain and has a deterministic positive and negative control. The following extensions show how a production policy query could evolve.

## 1. Match equivalent false literals

Python treats `0`, `None`, and empty containers as false. If the policy means that the flag must always be enabled, broaden the value predicate:

```ql
predicate isStaticallyFalse(Expr value) {
  value.toString() = "False"
  or value.toString() = "None"
  or value.(IntegerLiteral).getValue() = 0
  or value.(StringLiteral).getText() = ""
}
```

Replace the literal check with `isStaticallyFalse(v)`, then add one positive fixture for every accepted spelling. Do not broaden the rule without adding controls: Python expressions such as `bool(os.environ.get("FLAG"))` require data-flow or value analysis rather than text matching.

## 2. Detect assignments below module scope

The starter query requires:

```ql
n.getScope() instanceof Module
```

Remove that predicate to find assignments inside functions and classes too. This increases recall but may report harmless local variables. A more precise variant can restrict findings to functions that influence resource creation.

## 3. Reduce false positives

Real repositories may contain examples, generated files, or tests that intentionally set the flag to `False`. Add path exclusions only after confirming those findings are not useful:

```ql
not n.getLocation().getFile().getRelativePath().regexpMatch(
  ".*/(examples?|tests?|generated)/.*"
)
```

Keep `noncompliant.py` and `compliant.py` in the query's regression corpus. The first must continue to fire and the second must remain silent.

## Testing query changes locally

```bash
codeql database create py-db --language=python --source-root=.

codeql query run \
  --database=py-db \
  .github/codeql/custom-queries/PutinKhuyloFalse.ql

codeql database analyze py-db \
  --format=sarif-latest \
  --output=results.sarif \
  --sarif-category=python \
  .github/codeql/custom-queries/
```

The strict starter query should return one location in `noncompliant.py`.

## Applying the policy to Terraform

The upstream flag is Terraform/HCL, which CodeQL does not extract. Preserve the same teaching pattern with a Terraform-capable scanner:

1. Write one rule for `putin_khuylo = false`.
2. Test it against positive and negative `.tf` fixtures.
3. Export the finding as SARIF.
4. Upload the SARIF so it appears beside CodeQL findings in code scanning.

Lesson 04 demonstrates the SARIF integration path.

## Recap

- Start with an exact, explainable policy.
- Pair every positive fixture with a negative control.
- Broaden predicates only when new test cases justify the additional recall.
- Use CodeQL only for supported languages; integrate other analyzers through SARIF.
