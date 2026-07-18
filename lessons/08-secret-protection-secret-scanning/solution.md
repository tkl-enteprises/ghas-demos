# Solution / Remediation Runbook — Lesson 08

When a real (non-canary) secret leaks into a repo, treat it as an incident. The order matters: rotate first, *then* clean up history.

## Step 1 — Rotate the secret immediately

Disable the leaked credential at the issuer **before** doing anything else. Removing it from the repo doesn't help — anyone who already cloned, forked, or scraped the repo (including bots) still has the value.

| Provider | Action |
| --- | --- |
| Azure storage / SAS / Key Vault key | Portal → Storage account → *Access keys* → **Rotate key**, or `az storage account keys renew`. For Key Vault: rotate the secret version and update consumers. Federate Actions to Azure via OIDC where possible. |
| AWS IAM access key | IAM → Users → *user* → Security credentials → **Make inactive**, then delete. Rotate via short-lived OIDC if possible. |
| Stripe API key | Dashboard → Developers → API keys → **Roll key**. |
| GitHub PAT | <https://github.com/settings/tokens> → Revoke. Re-issue as fine-grained PAT or replace with a GitHub App. |
| Generic password | Disable the account or force a password reset for every user/service that knew it. |

## Step 2 — Audit access logs

Before assuming "no harm done", check what the leaked credential *did* in the time window between the leak and the rotation:

- Azure: Monitor → Activity log + Storage / Key Vault diagnostic settings — search by AccountKey usage, look for unfamiliar IPs, regions, or operations (especially `Microsoft.Storage/storageAccounts/listKeys/action`, large-blob reads from customer containers, role assignments).
- AWS: CloudTrail → search by access key ID, look for unfamiliar IPs, regions, or service calls (especially `iam:CreateUser`, `s3:GetObject` on customer buckets, `ec2:RunInstances`).
- Stripe: Dashboard → Logs → filter by API key.
- GitHub: org audit log + the PAT's "last used" timestamp.

If anything looks suspicious, escalate to your security team.

## Step 3 — Remove the secret from history

Now (and only now) clean up the repo so the value isn't readable in `git log`. **Removing the secret in a new commit is not enough** — `git log -p` still shows it on the parent commit.

Options:

- **`git filter-repo`** (recommended): <https://github.com/newren/git-filter-repo>
  ```bash
  git filter-repo --replace-text <(echo 'AccountKey=FAKEDEMO…==>REDACTED')
  ```
- **BFG Repo-Cleaner** (older but simpler): <https://rtyley.github.io/bfg-repo-cleaner/>
- After rewriting, force-push and ask everyone with a clone to re-clone (their old clone still has the secret).

## Step 4 — Replace with a real secret-management pattern

Hard-coding is the disease; rotating is the cure for the symptom. Don't re-introduce the disease.

- **GitHub Actions secrets** for CI: Settings → Secrets and variables → Actions. Reference as `${{ secrets.AZURE_STORAGE_CONNECTION_STRING }}` in workflow YAML.
- **Org-level secrets** for sharing across many repos: Org → Settings → Secrets and variables → Actions → "New organization secret".
- **OIDC federation (best for cloud)** — no long-lived secret in GitHub at all. Federate Actions to Azure / AWS / GCP using their OIDC trust:
  - Azure: <https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-azure>
  - AWS: <https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services>
  - GCP: <https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-google-cloud-platform>
- **Cloud secrets managers** for runtime: Azure Key Vault, AWS Secrets Manager, GCP Secret Manager, HashiCorp Vault. The app reads the secret at startup (or on demand) using its workload identity.
- **`.env` for local dev only** — see `.env.example` in this lesson; ensure `.env` is in `.gitignore`.

## Why "removing it in the next commit" isn't enough

Git is content-addressable: every commit object references the previous tree, and the leaked value lives in the blob attached to that tree. A diff that *removes* the line creates a new commit, but the old blob (and therefore the old value) is still reachable via `git log -p`, `git show <old-sha>`, GitHub's commit history UI, the GitHub REST API's `/commits/{sha}/files`, every clone, every fork, and every cache (e.g. archive.softwareheritage.org). The secret has to be considered public the moment the push lands. Rotation is non-negotiable.

## Quick reference

- AI-detected generic secrets: <https://docs.github.com/en/enterprise-cloud@latest/code-security/how-tos/secure-your-secrets/detect-secret-leaks/enabling-secret-scanning-for-ai-detected-secrets>
- About push protection (including GitHub MCP server coverage): <https://docs.github.com/en/enterprise-cloud@latest/code-security/concepts/secret-security/about-push-protection>
- Delegated bypass: <https://docs.github.com/en/enterprise-cloud@latest/code-security/secret-scanning/using-advanced-secret-scanning-and-push-protection-features/delegated-bypass-for-push-protection/about-delegated-bypass-for-push-protection>
- Public monitoring: <https://docs.github.com/en/enterprise-cloud@latest/code-security/concepts/secret-security/public-monitoring>
- GitHub Secret Protection plans and features: <https://docs.github.com/en/enterprise-cloud@latest/get-started/learning-about-github/about-github-advanced-security>
