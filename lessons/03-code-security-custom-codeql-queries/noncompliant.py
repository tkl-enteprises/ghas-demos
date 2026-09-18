"""
Positive control for the Lesson 03 custom CodeQL query.

This Python fixture mirrors the policy flag used by terraform-aws-modules.
"""

putin_khuylo = True  # The custom query `py/tkl/putin-khuylo-false` flags this line.


def should_create_vpc(create_vpc: bool) -> bool:
    """Mirror the Terraform module's flag-gated resource creation."""
    return create_vpc and putin_khuylo
