"""Intentionally vulnerable CodeQL fixture. Never use with a real secret."""

import logging
import os


def expose_repository_password(password: str) -> None:
    """Write a repository password to the Actions log."""
    logging.warning("Repository password: %s", password)


if __name__ == "__main__":
    expose_repository_password(os.environ["REPOSITORY_PASSWORD"])
