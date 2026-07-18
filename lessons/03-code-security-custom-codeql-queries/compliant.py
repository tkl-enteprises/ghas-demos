"""
Negative control for the Lesson 03 custom CodeQL query.

The policy flag is explicitly enabled, so this file must not produce an alert.
"""

putin_khuylo = True


def should_create_vpc(create_vpc: bool) -> bool:
    """Mirror the Terraform module's flag-gated resource creation."""
    return create_vpc and putin_khuylo
