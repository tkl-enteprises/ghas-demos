# Lesson 02 — Copilot Autofix and agentic remediation

Remediate an existing CodeQL alert on the default branch with either a focused
Copilot Autofix suggestion or, when the public preview is available, Copilot
cloud agent.

## Goal

Start from the code scanning **backlog**, not a pull request. Review the
`py/sql-injection` alert for [`insecure_login.py`](./insecure_login.py), create
a draft fix PR, and explain which Copilot remediation mode produced it.

## Learning objectives

After this lesson you can:

- Use **Generate fix** and **Create PR with fix** on an existing default-branch
  alert.
- Distinguish a Copilot Autofix suggestion from **Assign to Copilot** agentic
  remediation.
- Review either draft PR against the manual fix in [`solution.md`](./solution.md).
- Identify the access, product, availability, and billing differences.
- Fall back safely when a preview control or fix suggestion is unavailable.

## Estimated time

**~15 min demo + 5 min discussion**

## Choose the right flow

| | Copilot Autofix | Assign to Copilot |
| --- | --- | --- |
| Lesson label | **Passive suggestion** | **Agentic remediation** |
| Status | Generally available for eligible CodeQL alerts | **Public preview; subject to change** |
| Starts with | **Generate fix** | **Assign to Copilot** |
| What it does | Generates one targeted patch and explanation for you to evaluate | Starts a cloud-agent session that explores the repository, edits code, and validates on a best-effort basis |
| Result | **Create PR with fix** commits the suggestion to a new branch from the default branch and opens a draft PR | Typically opens a Copilot-authored draft PR with a summary and validation results |
| Iteration | Edit or test the PR yourself | Review the session log and mention Copilot in PR comments to request changes |
| Copilot plan and billing | No GitHub Copilot subscription is required; the alert-resolution docs do not bill this as a cloud-agent session | Requires an eligible paid Copilot plan and consumes GitHub Actions minutes plus AI credits as a cloud-agent session |

“Passive” is a teaching distinction, not a GitHub product name. Autofix still
uses AI, but it proposes a bounded change and waits for you. The agentic path
performs a multi-step task in a GitHub Actions-powered environment. Neither
path makes a fix trustworthy without human review and testing.

## Prerequisites

### Both paths

- The alert must be an open **CodeQL** code scanning alert on the repository's
  default branch. This lesson expects rule `py/sql-injection`.
- You need **write** access to resolve the alert and create the PR.
- Autofix supports only a subset of queries in supported CodeQL languages and
  works on a best-effort basis, so a button or suggestion is not guaranteed.

### Copilot Autofix

- Available for public repositories on GitHub.com.
- For private or internal repositories, the owning organization or enterprise
  needs a **GitHub Code Security** license.
- A GitHub Copilot subscription is **not** required.

### Assign to Copilot

- The code-scanning assignment experience is in **public preview** and may not
  appear in every repository or GitHub deployment.
- Both Copilot Autofix and Copilot cloud agent must be available in the
  repository.
- Copilot cloud agent requires a paid Copilot plan. For Copilot Business or
  Enterprise, an administrator must enable the relevant policy; repository
  owners can also opt repositories out.
- Each assignment is billed as a cloud-agent session. Usage consumes GitHub
  Actions minutes and AI credits based on the selected model and tokens used.
  Included allowances may cover it; budget policy can permit additional
  charges or block further usage. Some legacy personal annual plans may still
  display **premium requests** instead of current AI-credit terminology.
  Check the account's current plan and budget before starting a workshop run.

## Hands-on steps

This is the stable path and the safe fallback for the preview.

1. Open the repository's **Security and quality → Code scanning** backlog:
   <https://github.com/tkl-enteprises/ghas-demos/security/code-scanning>.
2. Filter to open alerts on the default branch, then open the
   `py/sql-injection` alert for
   `lessons/02-copilot-autofix/insecure_login.py`. If the alert is not present,
   wait for the default-branch CodeQL workflow to complete before troubleshooting
   Autofix.
3. Review the source-to-sink path ending at `cursor.execute(query)`.
4. Click **Generate fix**. This asks Copilot Autofix to generate a suggested
   patch for this historical/default-branch alert.
5. Read the explanation and every changed line. Confirm that both untrusted
   values become SQLite bound parameters.
6. Click **Create PR with fix**. GitHub creates a branch from the default
   branch, commits the suggestion, and opens a **draft pull request**.
7. Review and test the draft PR as normal. Compare its diff with
   [`solution.md`](./solution.md). Do not mark it ready or merge it merely
   because it was generated by Autofix.

## Optional public-preview path: Assign to Copilot

Use this path only if **Assign to Copilot** is visible and the workshop owner
has approved cloud-agent usage.

1. Return to the open `py/sql-injection` alert.
2. Click **Assign to Copilot**. This starts an agentic autofix session rather
   than generating the single Autofix suggestion above.
3. Follow the session. Copilot cloud agent explores the repository, proposes a
   fix, and attempts to run relevant validation.
4. Open the resulting **draft PR**. Review the summary, validation results,
   session log, and diff.
5. Compare the patch with [`solution.md`](./solution.md). If changes are
   needed, comment on the PR and mention Copilot, or take over manually.

The alert backlog can also assign **1–25 alerts** to Copilot in one operation,
producing one PR, but keep this workshop run to the single SQL-injection alert
so the scope and billing are predictable.

## If a control is missing

Do not weaken repository policy, dismiss the alert, or merge an unreviewed
manual change just to complete the demo.

1. **No Assign to Copilot:** treat this as an expected preview, plan, policy,
   or repository-availability difference. Use **Generate fix** and
   **Create PR with fix** instead. Do not use an API call to bypass a disabled
   policy.
2. **No Generate fix:** confirm that the alert is from CodeQL, is open on the
   default branch, the latest analysis completed, the repository is eligible
   for Autofix, and you have write access. Some queries cannot produce a fix.
3. **Still no suggestion:** create a normal branch and draft PR using the
   parameterized query in [`solution.md`](./solution.md). Run the same tests,
   request review, and let a subsequent CodeQL scan verify that the alert
   closes.

## Optional automation: Autofix REST API

The UI is preferred for the workshop. For automation, GitHub exposes endpoints
for historical/default-branch alerts to create an Autofix, poll its status, and
commit it:

```bash
OWNER=tkl-enteprises
REPO=ghas-demos
ALERT=<alert-number>

gh api --method POST \
  "repos/$OWNER/$REPO/code-scanning/alerts/$ALERT/autofix"

gh api \
  "repos/$OWNER/$REPO/code-scanning/alerts/$ALERT/autofix"

# The target branch must already exist. Committing does not replace PR review.
gh api --method POST \
  "repos/$OWNER/$REPO/code-scanning/alerts/$ALERT/autofix/commits" \
  -f target_ref="refs/heads/autofix/alert-$ALERT" \
  -f message="Fix code scanning alert $ALERT"
```

Use a token with the permissions documented for these endpoints, protect the
target branch, inspect the generated diff, run tests, and open a draft PR.
Agentic assignment also has a REST path—updating the alert assignee to
`copilot-swe-agent[bot]`—but only use it where the preview and cloud-agent
policy are already enabled. It is not a fallback for absent UI or policy.

## Review checklist

- [ ] Both `username` and `password` are passed as bound parameters.
- [ ] The function signature, return behavior, and connection cleanup remain
      unchanged.
- [ ] The patch is limited to the vulnerable query unless a broader change is
      clearly justified.
- [ ] Tests pass and the PR's CodeQL scan reports no new alerts.
- [ ] The PR remains draft until a human has reviewed the diff and validation.
- [ ] The alert closes on the default branch only after the reviewed fix lands
      and code scanning runs again.

Copilot Autofix and cloud-agent validation are both best effort. A missing fix,
failed test, or “possible false positive” note is a prompt for human triage,
not a reason to dismiss the finding.

## Key takeaways

- **Generate fix** is a bounded Autofix suggestion; **Assign to Copilot** starts
  a metered, multi-step cloud-agent session.
- Both routes produce draft PRs that require normal human review and testing.
- Public-preview availability and billing policy are prerequisites, not
  controls to bypass; passive Autofix and a manual draft PR are safe fallbacks.

## Files

| File | Purpose |
| --- | --- |
| `insecure_login.py` | Intentionally vulnerable demo with one `py/sql-injection` alert. |
| `solution.md` | Correct parameterized-query reference and review guidance. |
| `README.md` | This lesson. |

## Exit criteria

- Attendees can identify whether a draft PR came from passive Autofix or an
  agentic session.
- They can explain why the patch is equivalent to the manual solution.
- They know the safe fallback when either UI control is unavailable.
- They do not merge the generated PR without review and tests.

## Discussion questions

1. Which backlog alerts are sufficiently localized for a one-step Autofix, and
   which justify an agent session?
2. What branch protection, required checks, approval, and AI-usage budget would
   you require before enabling agentic remediation at scale?

## Reset state

Close the workshop draft PR without merging and delete its branch. If a fix was
merged, revert that PR so `insecure_login.py` remains intentionally vulnerable
for the next cohort; do not copy the vulnerable code into production.

## References

- [Resolving code scanning alerts](https://docs.github.com/en/code-security/code-scanning/managing-code-scanning-alerts/resolving-code-scanning-alerts)
- [About Copilot Autofix for code scanning](https://docs.github.com/en/code-security/code-scanning/managing-code-scanning-alerts/about-autofix-for-codeql-code-scanning)
- [REST API endpoints for code scanning](https://docs.github.com/en/rest/code-scanning/code-scanning)
- [About Copilot cloud agent](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent)
