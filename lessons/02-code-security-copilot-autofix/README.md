# Lesson 02 — Copilot Autofix and agentic remediation

Remediate an existing CodeQL alert on the default branch with either a focused
Copilot Autofix suggestion or agentic autofix, which is generally available
since October 15, 2026.

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
- Fall back safely when a control or fix suggestion is unavailable.

## Estimated time

**~15 min demo + 5 min discussion**

## Choose the right flow

| | Copilot Autofix | Agentic autofix (Assign to Copilot) |
| --- | --- | --- |
| Lesson label | **Passive suggestion** | **Agentic remediation** |
| Status | Generally available for eligible CodeQL alerts | **Generally available since October 15, 2026** on GitHub Enterprise Cloud (including data residency) |
| Starts with | **Generate fix** | **Assign to Copilot** — when agentic autofix is enabled it *replaces* **Generate fix** on individual alerts |
| What it does | Generates one targeted patch and explanation for you to evaluate | Starts an agent session that explores the repository, proposes a fix, reruns CodeQL to confirm the alert closes, and iterates if needed |
| Result | **Create PR with fix** commits the suggestion to a new branch from the default branch and opens a draft PR | Opens a draft PR with a summary of the fix, why it closes the alert, and the validation steps taken |
| Iteration | Edit or test the PR yourself | Comment on the PR, or continue the session from the repository's **Agents** tab |
| Licensing and billing | No GitHub Copilot subscription; suggested fixes don't consume AI credits | No Copilot license either, but a Copilot billing method must exist; each session consumes AI credits from the Code Security budget plus GitHub Actions minutes |

“Passive” is a teaching distinction, not a GitHub product name. Autofix still
uses AI, but it proposes a bounded change and waits for you. The agentic path
performs a multi-step task in a GitHub Actions-powered environment. Neither
path makes a fix trustworthy without human review and testing.

> **Facilitator decision:** a repository shows one button or the other. If
> agentic autofix is enabled for this repository (or inherited from the
> organization), **Generate fix** is replaced by **Assign to Copilot**. Decide
> before the session which flow you will show, and confirm the button in the UI.

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

### Agentic autofix (Assign to Copilot)

- **Generally available** (October 15, 2026) for GitHub Code Security and
  GitHub Advanced Security customers on GitHub Enterprise Cloud.
- Access is layered: an enterprise owner or security manager allows it with
  the **Agentic autofix** policy, then an organization owner or security
  manager enables it. Organization enablement turns it on for eligible
  repositories by default; repository administrators can opt out.
- No Copilot license is required, but a **Copilot billing method** must be
  defined. Each agent session consumes **AI credits from the Code Security
  budget** plus GitHub Actions minutes. Check the budget before a workshop run.
- Only alerts on the **default branch** can be assigned. Agentic autofix isn't
  available for repositories owned by Enterprise Managed Users.
- Copilot validates its fix by rerunning CodeQL with the default code scanning
  suite, so it can't confirm fixes for custom queries, the `security-extended`
  suite, or third-party SARIF alerts. This lesson's `py/sql-injection` alert is
  in the default suite, so validation works.

## Hands-on steps

This is the free Copilot Autofix path (shown when agentic autofix is not enabled for the repository) and the safe fallback.

1. Open the repository's **Security and quality → Code scanning** backlog:
   <https://github.com/tkl-enteprises/ghas-demos/security/code-scanning>.
2. Filter to open alerts on the default branch, then open the
   `py/sql-injection` alert for
   `lessons/02-code-security-copilot-autofix/insecure_login.py`. If the alert is not present,
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

## Agentic path: Assign to Copilot

Use this path only if **Assign to Copilot** is visible and the workshop owner
has approved the AI-credit and Actions-minute usage.

1. Return to the open `py/sql-injection` alert.
2. Click **Assign to Copilot**. This starts an agentic autofix session rather
   than generating the single Autofix suggestion above.
3. Follow the session. Copilot explores the repository, proposes a fix,
   reruns CodeQL to confirm the alert closes, and iterates if needed.
4. Open the resulting **draft PR**. Review the summary, validation results,
   session log, and diff.
5. Compare the patch with [`solution.md`](./solution.md). If changes are
   needed, comment on the PR, continue the session from the **Agents** tab, or
   take over manually.

The alert backlog — or a security campaign (lesson 11) — can also assign
**up to 25 alerts** to Copilot in one operation, producing one PR, but keep
this workshop run to the single SQL-injection alert so the scope and billing
are predictable.

## If a control is missing

Do not weaken repository policy, dismiss the alert, or merge an unreviewed
manual change just to complete the demo.

1. **No Assign to Copilot:** treat this as an expected plan, policy, or
   repository-availability difference (GitHub Enterprise Cloud, the
   enterprise policy, organization enablement, and a billing method are all
   required). Use **Generate fix** and **Create PR with fix** instead. Do not
   use an API call to bypass a disabled policy.
2. **No Generate fix:** if **Assign to Copilot** appears in its place, agentic
   autofix is enabled and has replaced the button — use the agentic path or ask
   an administrator to opt the workshop repository out. Otherwise confirm that
   the alert is from CodeQL, is open on the default branch, the latest analysis
   completed, the repository is eligible for Autofix, and you have write
   access. Some queries cannot produce a fix.
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
Agentic assignment also has a REST path—setting the alert's `assignees` to
`["copilot-swe-agent[bot]"]`—but only use it where agentic autofix is already
enabled. It is not a fallback for absent UI or policy.

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
- Policy enablement and AI-credit budgets are prerequisites, not controls to
  bypass; passive Autofix and a manual draft PR are safe fallbacks.

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
- [About autofix for code scanning (agentic autofix and Copilot Autofix)](https://docs.github.com/en/code-security/concepts/code-scanning/autofix-for-code-scanning)
- [Agentic autofix general availability (changelog, 2026-10-15)](https://github.blog/changelog/2026-10-15-agentic-autofix-for-code-scanning-alerts-general-availability/)
- [REST API endpoints for code scanning](https://docs.github.com/en/rest/code-scanning/code-scanning)
- [About Copilot cloud agent](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent)
