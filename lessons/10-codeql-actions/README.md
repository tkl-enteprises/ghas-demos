# Lesson 10 — CodeQL for GitHub Actions

Use CodeQL to find vulnerabilities in workflow YAML before an attacker turns CI automation into a privileged execution path.

> **Safety boundary:** the examples in `fixtures/` end in `.txt`. GitHub only loads workflow files from `.github/workflows/*.yml` or `.yaml`, so these fixtures cannot run in this repository. Do not rename, move, or enable the vulnerable fixture in this live demo repository.

## Goal

Recognize three high-signal workflow findings, explain the trust-boundary failure behind each one, and choose a remediation that preserves the workflow's purpose:

- untrusted pull-request checkout in a privileged `pull_request_target` workflow;
- direct interpolation of attacker-controlled context into a shell script;
- action dependencies referenced by mutable tags instead of full commit SHAs.

## Learning objectives

After this lesson you can:

- Explain why `pull_request_target` plus checkout of the PR head can become a "pwn request."
- Identify contexts such as a pull request title as untrusted input.
- Pass untrusted values through environment variables rather than splicing them into generated shell source.
- Pin actions to verified, full-length commit SHAs.
- Enable the `actions` CodeQL language and the `security-extended` query suite in advanced setup.

## Estimated time

**~15 min demo + 10 min remediation discussion**

## Prerequisites

- GitHub Code Security/code scanning is enabled.
- The repository uses the advanced CodeQL workflow in [`.github/workflows/codeql.yml`](../../.github/workflows/codeql.yml).
- A recent run includes the **Analyze (actions)** job.
- You can view **Security and quality → Code scanning** alerts.

## Why the fixture is inert

[`fixtures/vulnerable-workflow.yml.txt`](fixtures/vulnerable-workflow.yml.txt) is valid-looking workflow text, but its final `.txt` suffix and location outside `.github/workflows/` prevent GitHub Actions from registering it. CodeQL's Actions extractor analyzes active workflow YAML and action metadata, not this inert teaching fixture. The fixture is therefore for side-by-side review; the repository's Actions scan analyzes the real workflows without activating the vulnerable example.

For an end-to-end alert exercise, use a disposable fork, copy the fixture to `.github/workflows/lesson-10-vulnerable.yml` on a short-lived branch, and let the existing `pull_request` CodeQL scan inspect the proposed file. Never merge it, and delete the branch afterward. A newly proposed `pull_request_target` file does not run from the PR branch because that event uses the workflow definition from the base branch.

## Hands-on steps

1. **Confirm Actions analysis is enabled.** Open `.github/workflows/codeql.yml` and find the job whose `languages` input is `actions`. It uses `build-mode: none`, because workflow YAML is interpreted, and adds `security-extended` so the medium-precision unpinned-tag query runs alongside the default high-precision security queries.
2. **Inspect the trust boundary.** In the vulnerable fixture, find `on: pull_request_target`, the checkout of `github.event.pull_request.head.sha`, and the subsequent `pytest` command. The event supplies base-repository privileges while the checkout supplies attacker-controlled executable code.
3. **Trace script injection.** Follow `github.event.pull_request.title` into the `run:` block. GitHub expands `${{ ... }}` before the runner invokes Bash, so a crafted title can alter the generated script.
4. **Audit action references.** Find `actions/checkout@v4` and `actions/setup-python@v5`. Tags are mutable names; a full commit SHA makes the selected action content immutable.
5. **Compare the repaired design.** Open [`fixtures/remediated-workflow.yml.txt`](fixtures/remediated-workflow.yml.txt), then use [`solution.md`](solution.md) to map each vulnerable line to its fix.
6. **Review CodeQL alerts.** In **Security and quality → Code scanning**, filter **Tool: CodeQL** and **Language: GitHub Actions**. The live repository may show `actions/unpinned-tag` findings in its real workflows. The two critical fixture findings appear only if you completed the disposable-fork exercise above; `.txt` fixtures are deliberately not extracted. Useful rule IDs include:
   - `actions/untrusted-checkout/critical`
   - `actions/code-injection/critical`
   - `actions/unpinned-tag`

## Files

| File | Purpose |
| --- | --- |
| `fixtures/vulnerable-workflow.yml.txt` | Non-executable text fixture containing all three findings. |
| `fixtures/remediated-workflow.yml.txt` | Non-executable, hardened comparison fixture. |
| `solution.md` | Finding-by-finding explanation and remediation guidance. |

## Exit criteria

The lesson is complete when attendees can:

- identify the privileged event and untrusted checkout as separate ingredients whose combination is dangerous;
- replace direct expression interpolation with an environment variable and native shell expansion;
- explain why a version tag is not an immutable pin;
- locate the `actions` analysis job and the `security-extended` suite configuration.

## Key takeaways

- **Privilege and trust must agree.** Never execute untrusted PR code in a privileged workflow.
- **Expressions are code generation.** Put untrusted context in `env`, then quote the shell variable.
- **Pin what executes.** Full commit SHAs reduce action supply-chain risk; verify that each SHA belongs to the expected upstream repository.
- **Scanning is preventive.** CodeQL can flag dangerous workflow structure during review, before it reaches the default branch.

## Discussion questions

1. When is `pull_request_target` actually necessary, and can the privileged task avoid checkout entirely?
2. Which event contexts in your workflows can contributors control indirectly?
3. Who owns action-SHA updates, and how will Dependabot keep immutable pins current?
4. Should critical Actions findings block merge through a repository ruleset?

## Reset state

Nothing in this lesson executes or changes repository state. If you used a disposable fork for the optional alert exercise, close the pull request and delete its branch without merging.
