# Source-only preview fixture. This function is intentionally never called.
preview_path() {
  local requested_path="$1"
  sh -c "printf 'Would inspect: %s\n' '$requested_path'"
}
