# Lesson 04 — Copilot Autofix

Use Copilot Autofix to convert a real CodeQL alert into a one-click pull request.

## Goal

Experience the **Copilot Autofix** flow end-to-end on a real CodeQL alert: read the AI-suggested patch, evaluate it, then commit it (or open it as a PR) without leaving the GitHub UI.

## Prerequisites

- This repository is in an enterprise org with **GitHub Advanced Security** enabled.
- **Copilot is enabled** on the org so Autofix can call the model. See [Managing GitHub Copilot in your organization](https://docs.github.com/en/copilot/managing-copilot/managing-github-copilot-in-your-organization).
- You have at least **read** access to the repo's Code scanning alerts. Most workshop attendees only need read; committing the suggestion needs write.

## Hands-on steps

1. **Open the lesson file** [`insecure_login.py`](./insecure_login.py) in the GitHub UI. The file is intentionally short (<60 lines) so the Autofix diff is easy to read.
2. **Wait for the CodeQL alert** to appear in [Security → Code scanning](https://github.com/tkl-enteprises/ghas-demos/security/code-scanning). The rule id is `py/sql-injection`. The alert points at the `cursor.execute(query)` line in `authenticate`.
3. **Open the alert page.** The **Copilot Autofix** panel is pinned at the top of the alert. If it has not generated a fix yet, you'll see a *Generate fix* button.
4. **Click "Generate fix".** Autofix reads the data-flow path CodeQL produced, generates a patch, and shows it as an inline diff with a short rationale ("converted concatenation into a parameterised query because…").
5. **Apply the fix.** You have three choices:
   - **Commit suggestion** — commits the patch directly to the branch the alert is on.
   - **Open as pull request** — best for protected branches and for workshop demos; opens a PR titled `Potential fix for code scanning alert no. N`.
   - **Edit before committing** — tweak the patch in-place if you'd like to change identifiers or add a comment.
6. **Compare the AI patch with the manual fix** in [`solution.md`](./solution.md). The two should be functionally equivalent — both use parameter binding via `?` placeholders. Note any stylistic differences (variable names, query string layout, error handling).

## What good Autofix looks like

A high-quality Autofix output should (1) **fix the actual sink** that CodeQL flagged — not a cosmetic neighbour, (2) **preserve the function's externally observable behaviour** — same return type, same exceptions, same SQL semantics, and (3) **leave the rest of the file alone**. After applying the fix, re-run your tests: the CodeQL alert should auto-close on the next scan and your unit tests should still pass against the parameterised query.

## Where Autofix struggles

Autofix is purpose-built for *localised* security fixes — single-file, single-function patterns where the safe API is a near drop-in replacement. It is weaker on **cross-file refactors** (e.g. introducing a new helper that has to be wired through five callers), on **business-logic-aware fixes** (e.g. "this path traversal is intentional because the file is in a sandboxed tenant directory — just tighten the resolver"), and on **performance-sensitive trade-offs** where the safe API is materially slower and you need a tailored cache. Treat Autofix as a fast first draft on those cases and iterate manually.

## Files

| File | Purpose |
| --- | --- |
| `insecure_login.py` | Single-vulnerability demo file — exactly one `py/sql-injection` alert. |
| `solution.md` | Reference manual fix to compare against the Autofix suggestion. |
| `README.md` | This file. |
