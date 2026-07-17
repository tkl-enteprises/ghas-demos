# Lesson 06 — AI-powered security detections (optional, public preview)

> **Optional preview lesson.** AI-powered security detections are in public preview and subject to change. Treat the current UI, coverage, licensing, and billing behavior as time-sensitive; verify them against the linked GitHub documentation before presenting.

AI-powered security detections complement CodeQL by reviewing pull request changes in languages and frameworks that CodeQL does not currently cover deeply. Early preview coverage includes **Terraform configuration (HCL), PHP, Shell/Bash, and Dockerfiles**, as well as framework gaps such as JSP and Blazor. They do not replace CodeQL's precise semantic analysis for its supported languages.

## Goal

Open a pull request containing inert, source-only examples and learn how GitHub Code Security presents AI-powered security findings alongside CodeQL results.

## Learning objectives

After this lesson you can:

- Explain where AI-powered detections extend, rather than replace, CodeQL coverage.
- Verify enterprise policy, organization opt-in, repository setup, licenses, and AI credits.
- Identify an AI-powered finding by its **AI** label in a pull request.
- Explain the preview's PR-only, advisory, and ruleset limitations.
- Evaluate a Copilot Autofix suggestion when one is available.
- Run a useful fallback lesson when the preview is unavailable.

## Estimated time

**~10 minutes demo + 5 minutes discussion**

## Prerequisites

All of the following must be true for the live scan:

- The repository is licensed for **GitHub Code Security** through GitHub Advanced Security.
- The organization has a qualifying **GitHub Copilot license**, and the organization or enterprise has **AI credits available**. Preview scans consume AI credits.
- An enterprise owner has allowed the **AI Findings** policy under enterprise **Code Security** settings. It is not allowed by default.
- An organization owner has opted in with the **AI findings** setting under organization **Code scanning** settings. It is disabled by default.
- **CodeQL default setup** is enabled in the repository used for the live exercise.
- The repository-level **AI findings** toggle is enabled or inherited from the organization. Repository administrators can opt out.
- You can create a branch and pull request. Repository administration requires the corresponding owner or administrator role.

No model selection, new workflow, build, or custom prompt file is required. The AI scan uses specialized prompts and does not use files such as `.github/copilot-instructions.md`.

> **Repository compatibility:** `tkl-enteprises/ghas-demos` intentionally uses CodeQL advanced setup for its Python custom queries and lesson 05 Actions analysis, so default setup is off here. Do not replace that shared configuration for this optional lesson. Use a disposable, organization-owned copy that meets the prerequisites above, or run the source-review fallback below.

## Safe sample design

The files under [`samples/`](./samples/) are intentionally vulnerable **source-only teaching fixtures**:

- No workflow references them.
- The PHP and Bash examples only define functions; they never call them.
- The Terraform resource has `count = 0`, so it declares no infrastructure.
- The Dockerfile has no `RUN`, entrypoint, credentials, or deployment configuration.

**Do not execute the Bash/PHP samples, run `terraform apply`, build the Dockerfile, or deploy any sample.** A pull request diff is enough for this lesson. The examples contain no real credentials, hosts, accounts, or destructive operations.

## Hands-on steps

1. **Confirm governance before troubleshooting the repository.**
   1. Enterprise owner: allow **AI Findings** under enterprise `Settings → Code security`.
   2. Organization owner: enable **AI findings** under organization `Settings → Code security → Code scanning`.
   3. Repository administrator: open `Settings → Code security`, confirm **CodeQL default setup**, and confirm **AI findings** is enabled or inherited.
   4. Confirm GitHub Code Security and Copilot licensing and that AI credits are available.

2. **In the eligible disposable repository, create a PR-only copy of the fixtures.** Copying makes every vulnerable line part of the pull request without running it:

   ```bash
   git switch -c workshop/ai-security-detections
   mkdir lessons/06-code-security-ai-detections/pr-demo
   cp lessons/06-code-security-ai-detections/samples/* \
     lessons/06-code-security-ai-detections/pr-demo/
   git add lessons/06-code-security-ai-detections/pr-demo
   git commit -m "Add inert AI detection demo fixtures"
   git push -u origin workshop/ai-security-detections
   gh pr create --fill
   ```

3. **Open the pull request.** A scan starts when the PR is created and after each new commit. It runs independently of CodeQL's status, so results can arrive in either order.

4. **Inspect the `Conversation` and `Files changed` tabs.** AI-powered findings appear alongside code scanning findings and carry an **AI** indicator. Open one finding and identify its category, risk explanation, location, and feedback controls.

5. **Compare coverage.** Look for possible findings around:
   - `main.tf`: overly broad SSH ingress in HCL.
   - `query.php`: string-built SQL.
   - `preview_path.bash`: user input interpolated into a shell command.
   - `Dockerfile`: unpinned base image and root-by-default configuration.

   Preview models and categories evolve, so finding count and wording are intentionally **not** asserted. A missing finding is not proof that the pattern is safe.

6. **Review Autofix if offered.** Most findings include remediation guidance, but not every finding has a code patch. When **Copilot Autofix** is present, compare its proposed change with [`solution.md`](./solution.md). Review and test the patch like any other untrusted code suggestion; do not commit it solely because it was generated by GitHub.

7. **State the enforcement boundary.** These findings are:
   - available only on pull requests, not as full-repository or backlog alerts in the repository security view;
   - advisory and unable to block a merge by themselves; and
   - not currently usable as required findings in rulesets.

## If the preview is unavailable

Do not fabricate a result or enable unrelated products to force the demo.

1. Use the four fixtures and [`solution.md`](./solution.md) as a source-review exercise.
2. Show the [AI-powered security detections documentation](https://docs.github.com/en/code-security/concepts/code-scanning/ai-powered-security-detections) and walk through the enablement chain.
3. Check enterprise policy, organization opt-in, repository opt-out, CodeQL default setup, licenses, and AI-credit availability in that order.
4. Continue using CodeQL for supported languages and an approved SARIF-capable scanner for uncovered ecosystems until the preview is available. Record those results as that tool's findings—not as AI-powered detections.

This fallback preserves the lesson's coverage and governance outcomes without promising preview access or a particular model response.

## Files

| File | Teaching pattern | Runtime safety |
| --- | --- | --- |
| `samples/main.tf` | Public SSH ingress in Terraform/HCL | Resource count is zero. |
| `samples/query.php` | SQL string injection | Defines a function; no call or database credentials. |
| `samples/preview_path.bash` | Shell string injection | Defines a function; no call. |
| `samples/Dockerfile` | Unpinned image and root user | No commands, entrypoint, or deployment. |
| `solution.md` | Safe reference remediations and review checklist | Documentation only. |

## Exit criteria

The lesson is complete when attendees can:

- Name the enterprise, organization, and repository enablement layers.
- Name the Code Security, Copilot, and AI-credit prerequisites.
- Distinguish an AI-labeled PR finding from a CodeQL alert.
- Explain that the preview is PR-only, advisory, absent from the alert backlog, and unavailable to ruleset enforcement.
- Explain that Autofix may be absent and must always be reviewed.
- Describe the fallback when the preview is unavailable.

## Key takeaways

- **Complement, not replacement:** CodeQL remains the high-precision engine for supported languages; AI-powered detections expand PR coverage into additional ecosystems.
- **Governance is layered:** enterprise policy must allow it, the organization must opt in, the repository must use CodeQL default setup, and the repository may opt out.
- **Licensing and metering matter:** GitHub Code Security and Copilot licenses plus available AI credits are required during the preview.
- **Findings are clearly labeled and advisory:** look for the **AI** indicator, then review the finding rather than treating it as a merge gate.
- **Autofix is conditional:** remediation text or a patch may be available, but neither is guaranteed or automatically trustworthy.

## Discussion questions

1. Which repositories in your organization have meaningful PHP, Bash, HCL, or Dockerfile coverage gaps today?
2. How should security teams triage an AI finding differently from a deterministic static-analysis finding?
3. If preview findings cannot enforce a ruleset, what human review or external scanner policy should cover the gap?
4. What evidence would you collect before expanding opt-in from a pilot organization to the enterprise?

## Reset state

In the disposable repository, close the workshop PR without merging and delete its branch:

```bash
gh pr close --delete-branch
git switch main
git branch -D workshop/ai-security-detections
```

The committed `samples/` fixtures remain inert and unchanged for the next cohort.

## References

- [AI-powered security detections in pull requests](https://docs.github.com/en/code-security/concepts/code-scanning/ai-powered-security-detections)
- [Usage-based billing for organizations and enterprises](https://docs.github.com/en/copilot/concepts/billing/usage-based-billing-for-organizations-and-enterprises)
- [CodeQL supported languages and frameworks](https://docs.github.com/en/code-security/concepts/code-scanning/codeql/about-code-scanning-with-codeql#supported-languages-and-frameworks)
