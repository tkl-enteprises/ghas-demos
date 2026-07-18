#!/usr/bin/env bash

set -euo pipefail

repository="${GITHUB_REPOSITORY:?GITHUB_REPOSITORY is required}"
default_branch="${DEFAULT_BRANCH:-main}"
manual_alert="${AUTOFIX_ALERT_NUMBER:-}"
codeql_run_id="${CODEQL_RUN_ID:-}"
max_alerts="${MAX_AUTOFIX_ALERTS:-5}"

warn() {
  printf '::warning::%s\n' "$*"
}

summarize() {
  if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
    printf '%s\n' "$*" >>"$GITHUB_STEP_SUMMARY"
  fi
}

delete_branch() {
  local branch="$1"
  if ! gh api --method DELETE "repos/${repository}/git/refs/heads/${branch}" >/dev/null; then
    warn "Could not clean up branch ${branch}."
  fi
}

process_alert() {
  local alert_number="$1"
  local alert branch existing_pr alert_sha status description
  local attempt pr_url

  if ! alert="$(gh api "repos/${repository}/code-scanning/alerts/${alert_number}")"; then
    warn "Could not read code scanning alert #${alert_number}."
    return
  fi

  if [[ "$(jq -r '.state' <<<"$alert")" != "open" ]]; then
    warn "Skipping alert #${alert_number}: alert is not open."
    return
  fi
  if [[ "$(jq -r '.tool.name' <<<"$alert")" != "CodeQL" ]]; then
    warn "Skipping alert #${alert_number}: only CodeQL alerts support Autofix."
    return
  fi
  if [[ "$(jq -r '.most_recent_instance.ref' <<<"$alert")" != "refs/heads/${default_branch}" ]]; then
    warn "Skipping alert #${alert_number}: alert is not on ${default_branch}."
    return
  fi

  branch="autofix/codeql-alert-${alert_number}"
  existing_pr="$(
    gh pr list \
      --repo "$repository" \
      --state open \
      --head "$branch" \
      --json url \
      --jq '.[0].url // empty'
  )"
  if [[ -n "$existing_pr" ]]; then
    summarize "- Alert #${alert_number}: existing draft PR ${existing_pr}"
    return
  fi
  if gh api "repos/${repository}/git/ref/heads/${branch}" --silent >/dev/null 2>&1; then
    warn "Skipping alert #${alert_number}: branch ${branch} already exists."
    return
  fi

  printf 'Requesting Autofix for code scanning alert #%s...\n' "$alert_number"
  if ! gh api \
    --method POST \
    "repos/${repository}/code-scanning/alerts/${alert_number}/autofix" \
    >/dev/null; then
    warn "GitHub could not start Autofix for alert #${alert_number}."
    return
  fi

  status="pending"
  for attempt in $(seq 1 18); do
    status="$(
      gh api \
        "repos/${repository}/code-scanning/alerts/${alert_number}/autofix" \
        --jq '.status'
    )"
    case "$status" in
      success)
        break
        ;;
      error | outdated)
        warn "Autofix for alert #${alert_number} finished with status ${status}."
        return
        ;;
      pending)
        sleep 10
        ;;
      *)
        warn "Autofix for alert #${alert_number} returned unexpected status ${status}."
        return
        ;;
    esac
  done
  if [[ "$status" != "success" ]]; then
    warn "Timed out waiting for Autofix on alert #${alert_number}."
    return
  fi

  alert_sha="$(jq -r '.most_recent_instance.commit_sha' <<<"$alert")"
  if ! gh api \
    --method POST \
    "repos/${repository}/git/refs" \
    -f "ref=refs/heads/${branch}" \
    -f "sha=${alert_sha}" \
    >/dev/null; then
    warn "Could not create branch ${branch} for alert #${alert_number}."
    return
  fi

  if ! gh api \
    --method POST \
    "repos/${repository}/code-scanning/alerts/${alert_number}/autofix/commits" \
    -f "target_ref=refs/heads/${branch}" \
    -f "message=fix: apply Autofix for CodeQL alert #${alert_number}" \
    >/dev/null; then
    warn "Could not commit Autofix for alert #${alert_number}."
    delete_branch "$branch"
    return
  fi

  description="$(
    gh api \
      "repos/${repository}/code-scanning/alerts/${alert_number}/autofix" \
      --jq '.description // "GitHub generated a suggested fix for this alert."'
  )"
  if ! pr_url="$(
    gh pr create \
      --repo "$repository" \
      --base "$default_branch" \
      --head "$branch" \
      --draft \
      --title "fix: Autofix CodeQL alert #${alert_number}" \
      --body "$(printf '%s\n\n%s\n\n%s\n' \
        "Automated draft for code scanning alert #${alert_number}." \
        "$description" \
        "Review the generated patch and required checks before merging.")"
  )"; then
    warn "Could not open a draft PR for alert #${alert_number}."
    delete_branch "$branch"
    return
  fi

  summarize "- Alert #${alert_number}: opened ${pr_url}"

  # GITHUB_TOKEN-created pull requests do not trigger ordinary PR workflows.
  # Explicit dispatches attach the repository's tests and CodeQL checks to the
  # Autofix commit without introducing a recursive Autofix run.
  for workflow in tests.yml codeql.yml; do
    if ! gh workflow run "$workflow" --repo "$repository" --ref "$branch"; then
      warn "Could not dispatch ${workflow} for ${branch}."
    fi
  done
}

if ! [[ "$max_alerts" =~ ^[1-9][0-9]*$ ]]; then
  printf 'MAX_AUTOFIX_ALERTS must be a positive integer.\n' >&2
  exit 1
fi

alerts=()
if [[ -n "$manual_alert" ]]; then
  if ! [[ "$manual_alert" =~ ^[1-9][0-9]*$ ]]; then
    printf 'AUTOFIX_ALERT_NUMBER must be a positive integer.\n' >&2
    exit 1
  fi
  alerts=("$manual_alert")
else
  if ! [[ "$codeql_run_id" =~ ^[1-9][0-9]*$ ]]; then
    printf 'CODEQL_RUN_ID must be provided for automatic runs.\n' >&2
    exit 1
  fi

  scan_started_at="$(
    gh api \
      "repos/${repository}/actions/runs/${codeql_run_id}" \
      --jq '.run_started_at'
  )"
  open_alerts="$(
    gh api \
      --paginate \
      "repos/${repository}/code-scanning/alerts?state=open&ref=refs/heads/${default_branch}&tool_name=CodeQL&per_page=100" |
      jq -s 'add'
  )"
  mapfile -t alerts < <(
    jq -r \
      --arg started "$scan_started_at" \
      --argjson limit "$max_alerts" \
      '[.[] | select(.created_at >= $started)]
       | sort_by(.created_at)
       | .[:$limit][]
       | .number' \
      <<<"$open_alerts"
  )
fi

if (( ${#alerts[@]} == 0 )); then
  summarize "No newly created CodeQL alerts were eligible for Autofix."
  exit 0
fi

for alert_number in "${alerts[@]}"; do
  process_alert "$alert_number"
done
