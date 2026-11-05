# Lesson 03 — Custom CodeQL Queries

Write a custom CodeQL query for a repository-specific policy that the default suite does not know about.

This example is inspired by the [`putin_khuylo`](https://github.com/terraform-aws-modules/terraform-aws-vpc/blob/master/variables.tf) flag in `terraform-aws-modules/terraform-aws-vpc`, a project maintained by Anton Babenko. The original module defaults the flag to `true` and includes it in the condition that controls VPC creation.

> CodeQL does not provide a Terraform/HCL extractor. The lesson therefore uses a small Python analogue so attendees can author and run a real CodeQL query. To scan the original Terraform source, use a Terraform-capable scanner and upload its SARIF as shown in Lesson 04.

## Goal

You will:

1. Read a custom CodeQL query (`py/tkl/putin-khuylo-false`) that flags a module-level `putin_khuylo = False` assignment.
2. See it fire on `noncompliant.py` and remain silent on `compliant.py`.
3. Learn how repository-specific rules are loaded into CodeQL and tested for both recall and precision.

## Learning objectives

After this lesson you can:

- Identify the imports, predicates, metadata, and select clause in a small CodeQL query.
- Configure custom queries through `.github/codeql/codeql-config.yml`.
- Use positive and negative controls to test a custom rule.
- Explain when CodeQL is the right engine and when another scanner plus SARIF is required.
- Run a custom query locally before pushing it to CI.

## Estimated time

**~15 min demo + 5 min discussion**

## Prerequisites

- GitHub Code Security enabled. This repository uses the **workflow-based (advanced) CodeQL setup**, so the configuration that loads the query is visible in source. Since August 2026, default setup can also apply a CodeQL configuration file through the `github-codeql-config-file` repository property (add queries, exclude paths, set threat models) — the at-scale option when you don't want a workflow in every repository.
- `.github/codeql/codeql-config.yml` references the custom query pack.
- The `CodeQL` workflow has run after the query and fixtures were committed.
- Optional: the CodeQL CLI for local iteration.

## Where the query lives

The query is [`.github/codeql/custom-queries/PutinKhuyloFalse.ql`](https://github.com/tkl-enteprises/ghas-demos/blob/main/.github/codeql/custom-queries/PutinKhuyloFalse.ql).

Its metadata gives the result the rule id `py/tkl/putin-khuylo-false`. Its predicates require all three of these conditions:

- The assignment target is named `putin_khuylo`.
- The assigned expression is the literal `False`.
- The assignment is at module scope.

## How custom queries get loaded

The [CodeQL configuration](https://github.com/tkl-enteprises/ghas-demos/blob/main/.github/codeql/codeql-config.yml) loads three things: the `security-extended` suite, a one-query suite that adds lesson 01's low-precision `py/hardcoded-credentials`, and the QL pack under `.github/codeql/custom-queries/`. Every `.ql` query in that pack runs during the Python analysis job and reports under its own rule id.

## Hands-on steps

1. **Read the query.** Open `PutinKhuyloFalse.ql` and locate the `import python` line, the `from … where … select` clause, and the `@id`, `@kind`, and `@precision` metadata.
2. **Compare the controls.** [`noncompliant.py`](./noncompliant.py) assigns `putin_khuylo = False`; [`compliant.py`](./compliant.py) assigns it to `True`. Both implement the same flag-gated `should_create_vpc` function.
3. **Trigger a scan.** Push the change or dispatch the `CodeQL` workflow.
4. **Filter the results.** Open **Security and quality → Code scanning**, select **Tool: CodeQL**, and filter to **Rule: `py/tkl/putin-khuylo-false`**.
5. **Check precision.** Expect exactly one alert on `noncompliant.py`. `compliant.py` must not appear.

The previous Lesson 03 screenshots were removed because they showed the superseded `DEBUG = True` query. Capture fresh list and detail views after the new workflow result is available.

## Writing your own query

CodeQL queries are declarative. This example binds an assignment, its target name, and its value, then constrains those objects to the policy violation:

```ql
from Assign a, Name n, Expr v
where
  a.getATarget() = n and
  n.getId() = "putin_khuylo" and
  a.getValue() = v and
  v.toString() = "False" and
  n.getScope() instanceof Module
select a, "`putin_khuylo` must not be set to `False`."
```

Run it locally from the repository root with the [CodeQL bundle](https://github.com/github/codeql-action/releases) for your platform (it already contains the `codeql/python-all` dependency; with a CLI-only install, run `codeql pack install .github/codeql/custom-queries` first):

```bash
codeql database create py-db --language=python --source-root=.

# Fast iteration loop: prints the raw result table.
codeql query run --database=py-db .github/codeql/custom-queries/PutinKhuyloFalse.ql

# Precision check: results with file and line.
codeql database analyze py-db .github/codeql/custom-queries/PutinKhuyloFalse.ql \
  --format=csv --output=putin.csv
cat putin.csv
```

`putin.csv` should contain exactly one row, for `noncompliant.py` line 7, and nothing for `compliant.py` (verified with CodeQL 2.27.4).

## Files

| File | Purpose |
| --- | --- |
| `noncompliant.py` | Positive control: `putin_khuylo = False` produces one alert. |
| `compliant.py` | Negative control: `putin_khuylo = True` produces no alert. |
| `solution.md` | Exercises for broadening the rule while preserving precision. |
| `README.md` | Lesson walkthrough. |

## Exit criteria

- Attendees find `py/tkl/putin-khuylo-false` in the code-scanning rule filter.
- Exactly one alert points to `noncompliant.py`.
- `compliant.py` is absent from the results.
- Attendees can identify the config file that loads the custom query pack.
- Attendees understand why the original Terraform module requires a different extractor.

## Key takeaways

- Custom CodeQL queries turn repository policy into reviewable, versioned checks.
- A positive control proves recall; a negative control protects precision.
- Query only languages CodeQL extracts. Use a language-appropriate scanner and SARIF for unsupported source formats such as Terraform/HCL.
- Start with an exact literal rule, then broaden only when tests justify it.

## Discussion questions

1. Is this rule best described as security, correctness, compliance, or organizational policy?
2. Should the query also flag `0`, `None`, or a computed false value, and what false positives would that introduce?
3. Which repository-specific conventions in your organization deserve a custom query?

## Reset state

```bash
git checkout main && git pull
```

The custom query is intended to stay enabled between cohorts; no additional reset is required.
