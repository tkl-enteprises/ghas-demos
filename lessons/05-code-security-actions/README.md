# Lesson 05 — CodeQL for GitHub Actions

Use CodeQL to find vulnerabilities in workflow YAML before an attacker turns CI automation into a privileged execution path.

> **Safety boundary:** the examples in `fixtures/` end in `.txt`. GitHub only loads workflow files from `.github/workflows/*.yml` or `.yaml`, so these fixtures cannot run in this repository. The live [vulnerable workflow](../../.github/workflows/lesson-05-vulnerable.yml) has a job-level `if: ${{ false }}` guard: CodeQL analyzes it, but GitHub Actions never executes it or reads a repository secret. Do not remove that guard or use a real secret with this demo.

## Goal

Recognize four high-signal workflow findings, explain the trust-boundary failure behind each one, and choose a remediation that preserves the workflow's purpose:

- untrusted pull-request checkout in a privileged `pull_request_target` workflow;
- direct interpolation of attacker-controlled context into a shell script;
- action dependencies referenced by mutable tags instead of full commit SHAs.
- extraction of a password from a structured repository secret, which creates a derived value that GitHub cannot automatically mask.

## Learning objectives

After this lesson you can:

- Explain why `pull_request_target` plus checkout of the PR head can become a "pwn request."
- Identify contexts such as a pull request title as untrusted input.
- Pass untrusted values through environment variables rather than splicing them into generated shell source.
- Pin actions to verified, full-length commit SHAs.
- Explain why values extracted from a JSON secret are not automatically masked.
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

For an end-to-end alert exercise, use a disposable fork, copy the fixture to `.github/workflows/lesson-05-vulnerable.yml` on a short-lived branch, and let the existing `pull_request` CodeQL scan inspect the proposed file. Never merge it, and delete the branch afterward. A newly proposed `pull_request_target` file does not run from the PR branch because that event uses the workflow definition from the base branch.

## Detectable secret-exposure example

The repository also contains a deliberately vulnerable but disabled workflow that directly tries to print a password extracted from the repository secret `LESSON_05_CREDENTIALS`:

```yaml
if: ${{ false }}
# ...
run: echo "${{ fromJSON(secrets.LESSON_05_CREDENTIALS).password }}"
```

The secret does not need to exist. The job-level false condition prevents secret access and command execution. CodeQL still analyzes the YAML and reports `actions/unmasked-secret-exposure` on the expression in `.github/workflows/lesson-05-vulnerable.yml`.

A direct `${{ secrets.NAME }}` value is normally masked by the runner. A property extracted with `fromJSON(secrets.NAME).password` is a new value the runner does not know, so printing it may expose clear text.

## Hands-on steps

1. **Confirm Actions analysis is enabled.** Open `.github/workflows/codeql.yml` and find the job whose `languages` input is `actions`. It uses `build-mode: none`, because workflow YAML is interpreted, and adds `security-extended` so the medium-precision unpinned-tag query runs alongside the default high-precision security queries.
2. **Inspect the trust boundary.** In the vulnerable fixture, find `on: pull_request_target`, the checkout of `github.event.pull_request.head.sha`, and the subsequent `pytest` command. The event supplies base-repository privileges while the checkout supplies attacker-controlled executable code.
3. **Trace script injection.** Follow `github.event.pull_request.title` into the `run:` block. GitHub expands `${{ ... }}` before the runner invokes Bash, so a crafted title can alter the generated script.
4. **Audit action references.** Find `actions/checkout@v4` and `actions/setup-python@v5`. Tags are mutable names; a full commit SHA makes the selected action content immutable.
5. **Trace secret exposure.** Open the disabled vulnerable workflow and find the derived password directly interpolated into `run: echo`. Confirm that `if: ${{ false }}` is on the job, not merely on one step.
6. **Compare the repaired design.** Open [`fixtures/remediated-workflow.yml.txt`](fixtures/remediated-workflow.yml.txt), then use [`solution.md`](solution.md) to map each vulnerable line to its fix.
7. **Review the GitHub Actions alert.** Open [critical alert #93: Unmasked Secret Exposure](https://github.com/tkl-enteprises/ghas-demos/security/code-scanning/93) directly. To find it from the alert list, clear the current query and enter `is:open branch:main "Unmasked Secret Exposure"`. Do not use `path:.github/workflows/`; GitHub does not treat that value as a directory-prefix search. Workflow files must live under the repository-root `.github/workflows/` directory, so the lesson-directory path filter cannot return a GitHub Actions alert. The two critical `.txt` fixture findings appear only if you completed the disposable-fork exercise above. Useful rule IDs include:
   - `actions/untrusted-checkout/critical`
   - `actions/code-injection/critical`
   - `actions/unpinned-tag`
   - `actions/unmasked-secret-exposure`

## Files

| File | Purpose |
| --- | --- |
| `fixtures/vulnerable-workflow.yml.txt` | Non-executable text fixture containing all three findings. |
| `fixtures/remediated-workflow.yml.txt` | Non-executable, hardened comparison fixture. |
| `.github/workflows/lesson-05-vulnerable.yml` | Vulnerable YAML extracted by CodeQL, permanently skipped at runtime. |
| `solution.md` | Finding-by-finding explanation and remediation guidance. |

## Exit criteria

The lesson is complete when attendees can:

- identify the privileged event and untrusted checkout as separate ingredients whose combination is dangerous;
- replace direct expression interpolation with an environment variable and native shell expansion;
- explain why a version tag is not an immutable pin;
- explain why a password extracted from a structured secret may be unmasked;
- locate the `actions` analysis job and the `security-extended` suite configuration.

## Key takeaways

- **Privilege and trust must agree.** Never execute untrusted PR code in a privileged workflow.
- **Expressions are code generation.** Put untrusted context in `env`, then quote the shell variable.
- **Pin what executes.** Full commit SHAs reduce action supply-chain risk; verify that each SHA belongs to the expected upstream repository.
- **Mask derived secrets explicitly.** Prefer separate plain secrets; otherwise register a derived value with `::add-mask::` before any command could emit it.
- **Scanning is preventive.** CodeQL can flag dangerous workflow structure during review, before it reaches the default branch.

## Discussion questions

1. When is `pull_request_target` actually necessary, and can the privileged task avoid checkout entirely?
2. Which event contexts in your workflows can contributors control indirectly?
3. Who owns action-SHA updates, and how will Dependabot keep immutable pins current?
4. Should critical Actions findings block merge through a repository ruleset?

## Reset state

Nothing in this lesson executes or changes repository state. If you used a disposable fork for the optional alert exercise, close the pull request and delete its branch without merging.
