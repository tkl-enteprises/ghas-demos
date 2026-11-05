# Lesson 05 — Solution and remediation

The vulnerable fixture combines three independent weaknesses. Fix all three: removing only one may reduce impact without restoring a sound trust boundary.

## Finding 1: privileged workflow checks out untrusted code

**CodeQL rule:** `actions/untrusted-checkout/critical`  
**Security severity:** critical (9.3)  
**Precision:** very high

`pull_request_target` runs the workflow definition from the base branch in the base repository's privileged context. The fixture then explicitly checks out the contributor-controlled PR head and runs `pytest`. A contributor can modify test hooks, dependencies, or other executable files in the PR; the runner executes those changes with the workflow's token permissions and access to any available secrets.

### Preferred fix

Use `pull_request` for building and testing PR code:

```yaml
on:
  pull_request:

permissions:
  contents: read

steps:
  - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
  - run: python -m pytest
```

The normal checkout behavior uses the PR merge commit, and forked PRs receive a restricted token without repository secrets. The full SHA shown above resolves from the official `actions/checkout` repository's `v7.0.1` tag (verified November 2026); verify upstream ownership and the current release before adopting any pin.

### Platform guardrails are defense in depth, not the fix

`actions/checkout` v7 — and, since July 20, 2026, the floating major tags of earlier supported versions — refuses to fetch fork pull request code in `pull_request_target` and `workflow_run` workflows unless `allow-unsafe-pr-checkout: true` is set. Public repositories also block `pull_request_target` by default from December 2, 2026 unless an Actions event policy allows it. Neither makes the pattern safe to keep: CodeQL still reports it, a `run:` step that does `git fetch origin refs/pull/N/head` bypasses checkout's guard, and private repositories are not covered by the event block.

### If privileged follow-up is required

Keep untrusted execution in a `pull_request` workflow. A separate privileged workflow may comment, label, or publish after completion, but it should use the GitHub API and avoid checking out PR code. Treat artifacts, caches, filenames, and metadata produced by the untrusted workflow as hostile input. Validate their format and contents before a privileged consumer uses them.

Do not "fix" the issue by changing the checkout to the base branch and then running tests: that is safer, but it does not test the proposed code.

## Finding 2: untrusted context is inserted into shell source

**CodeQL rule:** `actions/code-injection/critical`  
**Security severity:** critical (9.0)  
**Precision:** very high

This line is unsafe:

```yaml
run: echo "Reviewing ${{ github.event.pull_request.title }}"
```

GitHub evaluates the expression before Bash starts. A pull request author controls the title, so quotes, substitutions, and shell operators in the title can change the script Bash receives.

### Fix

Move expression evaluation to the step environment and use native, quoted shell expansion:

```yaml
- name: Show pull request title
  env:
    PR_TITLE: ${{ github.event.pull_request.title }}
  run: printf 'Reviewing %s\n' "$PR_TITLE"
```

The title becomes data in the process environment rather than source code in the generated script. Do not reintroduce `${{ env.PR_TITLE }}` inside `run:`; that performs expression interpolation again and recreates the vulnerability.

For complex processing, a JavaScript action that accepts the value through `with:` is another good boundary.

## Finding 3: actions use mutable tags

**CodeQL rule:** `actions/unpinned-tag`  
**Security severity:** 5.0  
**Precision:** medium  
**Suite:** `security-extended`

References such as these resolve a mutable tag each time the job starts:

```yaml
- uses: actions/checkout@v4
- uses: actions/setup-python@v5
```

Pin each action to a verified full commit SHA:

```yaml
- uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
- uses: actions/setup-python@6d4fd22b20465ccc0f7354476588e8df7c9ca0e0 # v7.1.0
```

The version comments are for human and dependency-bot readability; the SHA is the security boundary. Verify a pin against the action's official repository, review updates, and configure Dependabot to propose SHA refreshes.

Two newer alternatives and enforcement levers:

- **Workflow lockfiles** (GA October 28, 2026): keep readable tags in the workflow and run `gh actions-lock` to record exact commits in `.github/workflows/actions.lock`. Dependabot updates the lockfile in its PRs, a **Require lockfile** policy enforces adoption, and CodeQL's `actions/unpinned-tag` no longer reports references pinned by a valid lockfile entry.
- **SHA-pinning policy** (since August 2025): the allowed-actions policy can require full-length SHA pins and block specific actions or versions (prefix an entry with `!`).

## Finding 4: a derived repository secret may be printed unmasked

**CodeQL rule:** `actions/unmasked-secret-exposure`
**Security severity:** critical (9.0)
**Precision:** high

The disabled live example extracts a password from a JSON repository secret:

```yaml
run: echo "${{ fromJSON(secrets.LESSON_05_CREDENTIALS).password }}"
```

GitHub masks the exact value of `${{ secrets.LESSON_05_CREDENTIALS }}`, but it cannot infer that the extracted `password` property is also secret. Echoing that derived value can expose the password in the Actions log.

### Preferred fix

Store the password as a separate plain repository secret and consume it only where authentication is required:

```yaml
env:
  REPOSITORY_PASSWORD: ${{ secrets.LESSON_05_PASSWORD }}
run: ./authenticate-without-logging
```

Never print the value. If a legacy integration requires extracting a field from a structured secret, register the derived value with the runner's masking command before any other command can process it:

```yaml
env:
  CREDENTIALS: ${{ secrets.LESSON_05_CREDENTIALS }}
run: |
  password="$(jq -r '.password' <<<"$CREDENTIALS")"
  echo "::add-mask::$password"
  ./authenticate-without-logging "$password"
```

The job-level `if: ${{ false }}` in the training workflow is a safety control for this repository, not a remediation pattern for production code.

## Least privilege is defense in depth

The repaired fixture declares:

```yaml
permissions:
  contents: read
```

Set permissions at workflow or job scope and grant only what that task requires. Least privilege does not make untrusted checkout or injection safe, but it limits damage if another control fails.

## Why `security-extended` is configured

The default Actions suite includes the very-high-precision critical checkout and injection queries. `actions/unpinned-tag` belongs to the `security-extended` suite, so the repository's dedicated Actions analysis job requests:

```yaml
with:
  languages: actions
  build-mode: none
  queries: security-extended
```

The Python analysis remains separate because it also loads the workshop's Python-only custom query pack.

## Verification checklist

- Trigger is `pull_request` for jobs that build or test PR code.
- No privileged job checks out or executes an untrusted ref.
- Contributor-controlled context reaches scripts only through environment variables or typed action inputs.
- Shell variables are quoted.
- Every external action is pinned to a verified, full-length commit SHA.
- Structured secrets are not decomposed into values that can reach logs or artifacts.
- `GITHUB_TOKEN` permissions are explicitly minimal.
- CodeQL's `actions` analysis completes and reports a distinct `/language:actions` category.

## References

- [GitHub Docs: Secure use reference](https://docs.github.com/en/actions/reference/security/secure-use)
- [CodeQL query help: untrusted checkout](https://codeql.github.com/codeql-query-help/actions/actions-untrusted-checkout-critical/)
- [CodeQL query help: code injection](https://codeql.github.com/codeql-query-help/actions/actions-code-injection-critical/)
- [CodeQL query help: unpinned tag](https://codeql.github.com/codeql-query-help/actions/actions-unpinned-tag/)
- [CodeQL query help: unmasked secret exposure](https://codeql.github.com/codeql-query-help/actions/actions-unmasked-secret-exposure/)
- [GitHub Docs: CodeQL built-in queries for Actions](https://docs.github.com/en/code-security/reference/code-scanning/codeql/codeql-queries/actions-built-in-queries)
