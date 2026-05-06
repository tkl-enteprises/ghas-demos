#!/usr/bin/env bash
# preflight.sh — workshop facilitator pre-flight check for tkl-enteprises/ghas-demos.
#
# Run this ~24 hours before a delivery to catch GHAS / repo-config drift while you
# still have time to fix it. It is read-only — it only inspects the repo via the
# GitHub API; it never writes settings.
#
# Usage:
#   scripts/preflight.sh
#
# Required gh auth scopes (token used by `gh auth login`):
#   - repo
#   - read:org
#   plus admin permission on the demo repo (tkl-enteprises/ghas-demos) for the
#   active account, so we can read security_and_analysis fields and rulesets.
#
# Exit codes:
#   0   all checks passed
#   1   one or more checks failed (see red ✗ lines above the summary)

set -u
set -o pipefail

REPO="${PREFLIGHT_REPO:-tkl-enteprises/ghas-demos}"

# ANSI colors, but only if stdout is a terminal.
if [ -t 1 ]; then
  GREEN=$'\033[32m'
  RED=$'\033[31m'
  YELLOW=$'\033[33m'
  BOLD=$'\033[1m'
  RESET=$'\033[0m'
else
  GREEN=""
  RED=""
  YELLOW=""
  BOLD=""
  RESET=""
fi

PASS=0
FAIL=0
WARN=0

ok()   { printf "  ${GREEN}✓${RESET} %s\n" "$1"; PASS=$((PASS+1)); }
fail() { printf "  ${RED}✗${RESET} %s\n" "$1"; FAIL=$((FAIL+1)); }
warn() { printf "  ${YELLOW}!${RESET} %s\n" "$1"; WARN=$((WARN+1)); }
hdr()  { printf "\n${BOLD}%s${RESET}\n" "$1"; }

printf "${BOLD}GHAS workshop preflight — %s${RESET}\n" "$REPO"
printf "  (read-only checks; safe to re-run)\n"

# ----------------------------------------------------------------------------
# 1. gh auth status
# ----------------------------------------------------------------------------
hdr "1. gh CLI authentication"
if ! command -v gh >/dev/null 2>&1; then
  fail "gh CLI not on PATH — install from https://cli.github.com"
elif ! gh auth status >/dev/null 2>&1; then
  fail "gh not authenticated — run 'gh auth login' (need scopes: repo, read:org)"
else
  ACTIVE_USER="$(gh api user --jq '.login' 2>/dev/null || echo "?")"
  ok "gh authenticated as ${ACTIVE_USER}"
fi

# Bail early if gh is unusable — every later check needs it.
if [ "$FAIL" -gt 0 ]; then
  printf "\n${RED}${BOLD}Aborting: gh CLI is required for the rest of the checks.${RESET}\n"
  exit 1
fi

# ----------------------------------------------------------------------------
# 2. Admin permission on the repo
# ----------------------------------------------------------------------------
hdr "2. Repo admin permission"
ADMIN="$(gh api "repos/${REPO}" --jq '.permissions.admin // false' 2>/dev/null || echo "error")"
case "$ADMIN" in
  true)  ok "active account has admin on ${REPO}" ;;
  false) fail "active account does NOT have admin on ${REPO} — security_and_analysis fields will be hidden" ;;
  *)     fail "could not query repos/${REPO} — token missing 'repo' scope or repo not accessible" ;;
esac

# ----------------------------------------------------------------------------
# 3. security_and_analysis toggles
# ----------------------------------------------------------------------------
hdr "3. security_and_analysis toggles"
SA_JSON="$(gh api "repos/${REPO}" --jq '.security_and_analysis // {}' 2>/dev/null || echo '{}')"
check_sa() {
  local field="$1"
  local label="$2"
  local status
  status="$(printf '%s' "$SA_JSON" | jq -r --arg f "$field" '.[$f].status // "missing"' 2>/dev/null || echo "missing")"
  if [ "$status" = "enabled" ]; then
    ok "${label} (${field}.status = enabled)"
  else
    fail "${label} — expected 'enabled', got '${status}'"
  fi
}
check_sa "secret_scanning"                       "Secret scanning"
check_sa "secret_scanning_push_protection"       "Push protection"
check_sa "secret_scanning_ai_detection"          "Secret scanning AI detection"
check_sa "secret_scanning_validity_checks"       "Secret scanning validity checks"
check_sa "secret_scanning_non_provider_patterns" "Non-provider patterns"
check_sa "dependabot_security_updates"           "Dependabot security updates"

# ----------------------------------------------------------------------------
# 4. Default-setup CodeQL must be off (advanced workflow conflicts with it)
# ----------------------------------------------------------------------------
hdr "4. CodeQL default-setup state"
CQ_STATE="$(gh api "repos/${REPO}/code-scanning/default-setup" --jq '.state // "unknown"' 2>/dev/null || echo "error")"
case "$CQ_STATE" in
  not-configured)
    ok "default-setup CodeQL is not-configured (advanced workflow owns SARIF upload)"
    ;;
  configured)
    fail "default-setup CodeQL is CONFIGURED — turn it off in Settings → Code security, otherwise the advanced workflow can't upload SARIF"
    ;;
  error)
    warn "could not read default-setup state — likely a permissions blip; verify in Settings UI"
    ;;
  *)
    warn "default-setup state = '${CQ_STATE}' — expected 'not-configured'"
    ;;
esac

# ----------------------------------------------------------------------------
# 5. main-branch ruleset exists
# ----------------------------------------------------------------------------
hdr "5. main-branch-protection ruleset"
RS_NAME="$(gh api "repos/${REPO}/rulesets" --jq '.[] | select(.name=="main-branch-protection") | .name' 2>/dev/null || echo "")"
if [ -n "$RS_NAME" ]; then
  ok "ruleset 'main-branch-protection' is present"
else
  fail "ruleset 'main-branch-protection' NOT found — required-status-check gate is missing"
fi

# ----------------------------------------------------------------------------
# 6. Open alert counts
# ----------------------------------------------------------------------------
hdr "6. Open alert counts"
count_alerts() {
  # Uses paginate + length to get full count without trusting per-page caps.
  local endpoint="$1"
  gh api --paginate "repos/${REPO}/${endpoint}" --jq 'length' 2>/dev/null \
    | awk '{s+=$1} END {print s+0}'
}

CS_COUNT="$(count_alerts 'code-scanning/alerts?state=open&per_page=100')"
DB_COUNT="$(count_alerts 'dependabot/alerts?state=open&per_page=100')"
SS_COUNT="$(count_alerts 'secret-scanning/alerts?state=open&per_page=100')"

check_count() {
  local label="$1" actual="$2" expected_min="$3"
  if [ -z "$actual" ] || ! [ "$actual" -ge 0 ] 2>/dev/null; then
    fail "${label}: could not read alert count (token scope?)"
  elif [ "$actual" -ge "$expected_min" ]; then
    ok "${label}: ${actual} open (expected ≥ ${expected_min})"
  else
    warn "${label}: ${actual} open (expected ≥ ${expected_min}) — workshop demos may show fewer alerts than expected"
  fi
}
check_count "Code-scanning alerts" "$CS_COUNT" 25
check_count "Dependabot alerts"    "$DB_COUNT" 50
check_count "Secret-scanning alerts" "$SS_COUNT" 1

# ----------------------------------------------------------------------------
# 7. Latest CodeQL Analyze run on main was successful
# ----------------------------------------------------------------------------
hdr "7. Latest CodeQL run on main"
CQ_RUN_JSON="$(gh run list --repo "${REPO}" --workflow=codeql.yml --branch=main --limit=1 --json conclusion,status,createdAt,displayTitle 2>/dev/null || echo '[]')"
CQ_CONCLUSION="$(printf '%s' "$CQ_RUN_JSON" | jq -r '.[0].conclusion // "none"' 2>/dev/null || echo "none")"
CQ_STATUS="$(printf '%s' "$CQ_RUN_JSON" | jq -r '.[0].status // "none"' 2>/dev/null || echo "none")"

case "$CQ_CONCLUSION" in
  success)
    ok "latest CodeQL run on main = success"
    ;;
  none)
    fail "no CodeQL run found on main — workflow has never run, lesson 1 will be empty"
    ;;
  "")
    if [ "$CQ_STATUS" = "in_progress" ] || [ "$CQ_STATUS" = "queued" ]; then
      warn "latest CodeQL run on main is still ${CQ_STATUS} — re-run preflight after it completes"
    else
      fail "latest CodeQL run on main has no conclusion (status=${CQ_STATUS})"
    fi
    ;;
  *)
    fail "latest CodeQL run on main = '${CQ_CONCLUSION}' (status=${CQ_STATUS}) — fix before workshop"
    ;;
esac

# ----------------------------------------------------------------------------
# Summary
# ----------------------------------------------------------------------------
TOTAL=$((PASS+FAIL+WARN))
hdr "Summary"
printf "  %d total checks: ${GREEN}%d passed${RESET}, ${RED}%d failed${RESET}, ${YELLOW}%d warnings${RESET}\n" \
  "$TOTAL" "$PASS" "$FAIL" "$WARN"

if [ "$FAIL" -eq 0 ]; then
  printf "${GREEN}${BOLD}ALL CHECKS PASSED${RESET}\n"
  exit 0
else
  printf "${RED}${BOLD}%d CHECKS FAILED — review above${RESET}\n" "$FAIL"
  exit 1
fi
