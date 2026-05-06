# Solution / Remediation Runbook — Lesson 02

When a real (non-canary) secret leaks into a repo, treat it as an incident. The order matters: rotate first, *then* clean up history.

## Step 1 — Rotate the secret immediately

Disable the leaked credential at the issuer **before** doing anything else. Removing it from the repo doesn't help — anyone who already cloned, forked, or scraped the repo (including bots) still has the value.

| Provider | Action |
| --- | --- |
| AWS IAM access key | IAM → Users → *user* → Security credentials → **Make inactive**, then delete. Rotate via short-lived OIDC if possible. |
| Stripe API key | Dashboard → Developers → API keys → **Roll key**. |
| GitHub PAT | <https://github.com/settings/tokens> → Revoke. Re-issue as fine-grained PAT or replace with a GitHub App. |
| Generic password | Disable the account or force a password reset for every user/service that knew it. |

## Step 2 — Audit access logs

Before assuming "no harm done", check what the leaked credential *did* in the time window between the leak and the rotation:

- AWS: CloudTrail → search by access key ID, look for unfamiliar IPs, regions, or service calls (especially `iam:CreateUser`, `s3:GetObject` on customer buckets, `ec2:RunInstances`).
- Stripe: Dashboard → Logs → filter by API key.
- GitHub: org audit log + the PAT's "last used" timestamp.

If anything looks suspicious, escalate to your security team.

## Step 3 — Remove the secret from history

Now (and only now) clean up the repo so the value isn't readable in `git log`. **Removing the secret in a new commit is not enough** — `git log -p` still shows it on the parent commit.

Options:

- **`git filter-repo`** (recommended): <https://github.com/newren/git-filter-repo>
  ```bash
  git filter-repo --replace-text <(echo 'AKIA…==>REDACTED')
  ```
- **BFG Repo-Cleaner** (older but simpler): <https://rtyley.github.io/bfg-repo-cleaner/>
- After rewriting, force-push and ask everyone with a clone to re-clone (their old clone still has the secret).

## Step 4 — Replace with a real secret-management pattern

Hard-coding is the disease; rotating is the cure for the symptom. Don't re-introduce the disease.

- **GitHub Actions secrets** for CI: Settings → Secrets and variables → Actions. Reference as `${{ secrets.AWS_ACCESS_KEY_ID }}` in workflow YAML.
- **Org-level secrets** for sharing across many repos: Org → Settings → Secrets and variables → Actions → "New organization secret".
- **OIDC federation (best for cloud)** — no long-lived secret in GitHub at all. Federate Actions to AWS / Azure / GCP using their OIDC trust:
  - AWS: <https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services>
  - Azure: <https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-azure>
  - GCP: <https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-google-cloud-platform>
- **Cloud secrets managers** for runtime: AWS Secrets Manager, Azure Key Vault, GCP Secret Manager, HashiCorp Vault. The app reads the secret at startup (or on demand) using its workload identity.
- **`.env` for local dev only** — see `.env.example` in this lesson; ensure `.env` is in `.gitignore`.

## Why "removing it in the next commit" isn't enough

Git is content-addressable: every commit object references the previous tree, and the leaked value lives in the blob attached to that tree. A diff that *removes* the line creates a new commit, but the old blob (and therefore the old value) is still reachable via `git log -p`, `git show <old-sha>`, GitHub's commit history UI, the GitHub REST API's `/commits/{sha}/files`, every clone, every fork, and every cache (e.g. archive.softwareheritage.org). The secret has to be considered public the moment the push lands. Rotation is non-negotiable.

## Quick reference

- Working with push protection: <https://docs.github.com/en/code-security/secret-scanning/working-with-push-protection>
- Secret scanning patterns: <https://docs.github.com/en/code-security/secret-scanning/secret-scanning-patterns>
- About GitHub Advanced Security: <https://docs.github.com/en/get-started/learning-about-github/about-github-advanced-security>
