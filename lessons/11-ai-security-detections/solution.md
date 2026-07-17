# Lesson 11 — Reference solutions

These are review references, not files to deploy. Keep the original fixtures unchanged so future pull requests can exercise the preview. If Autofix proposes a patch, compare the security property—not just its formatting—with the corresponding solution below.

## Terraform/HCL: restrict network exposure

The fixture allows SSH from the entire internet. Preserve its inert `count = 0` guard and replace the public CIDR with a deliberately supplied trusted network:

```hcl
variable "trusted_admin_cidr" {
  description = "Approved administrator network in CIDR notation"
  type        = string

  validation {
    condition     = can(cidrnetmask(var.trusted_admin_cidr)) && var.trusted_admin_cidr != "0.0.0.0/0"
    error_message = "Use a valid, non-public administrator CIDR."
  }
}

resource "aws_security_group" "preview_only" {
  count = 0
  name  = "ai-detection-preview-only"

  ingress {
    description = "SSH from the approved administrator network"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.trusted_admin_cidr]
  }
}
```

In production, prefer private connectivity, identity-aware access, or a managed session service over exposing SSH. Validate the architecture and Terraform plan; changing a CIDR alone is not a deployment approval.

## PHP: bind SQL parameters

Prepare a constant query and bind attacker-controlled values as data:

```php
<?php

function findUser(mysqli $database, string $username): array
{
    $statement = $database->prepare(
        "SELECT id, username FROM users WHERE username = ?"
    );
    $statement->bind_param("s", $username);
    $statement->execute();

    return $statement->get_result()->fetch_all(MYSQLI_ASSOC);
}
```

The important property is that `$username` never changes SQL syntax. A patch that escapes quotes manually or uses a different interpolation form is not an adequate fix.

## Bash: remove the shell interpreter

The sample does not need a shell command at all:

```bash
preview_path() {
  local requested_path="$1"
  printf 'Would inspect: %s\n' "$requested_path"
}
```

If a real task must invoke a program, pass arguments as an array and avoid `sh -c`, `bash -c`, or `eval`. Validate input against the application's expected format rather than trying to blacklist metacharacters.

## Dockerfile: pin and drop privileges

Use an approved image pinned by immutable digest and select a numeric non-root identity explicitly:

```dockerfile
FROM alpine:3.21@sha256:<approved-digest>

USER 10001:10001
```

`<approved-digest>` is intentionally a placeholder, not a fake working digest. Resolve and approve the digest through the organization's dependency process before building. A real image may also need ownership changes, read-only filesystems, dropped capabilities, and a vulnerability scan.

## Autofix review checklist

- [ ] Does the patch remove the actual injection, exposure, or supply-chain property?
- [ ] Does it preserve intended behavior without introducing a new execution path?
- [ ] Does it avoid invented credentials, hosts, package digests, or network ranges?
- [ ] Is the change narrowly scoped and understandable to a human reviewer?
- [ ] Can project tests and policy checks validate it?
- [ ] If no Autofix patch is present, did the reviewer use the remediation text and manual reference instead of assuming no fix exists?

Autofix availability and output vary by finding. A suggested patch is a review candidate, not evidence that the issue is resolved; resolution requires applying, testing, and rescanning the change.
