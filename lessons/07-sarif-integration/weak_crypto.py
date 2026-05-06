"""
⚠️ INTENTIONALLY VULNERABLE — for educational use only.
Part of GHAS workshop demos: https://github.com/tkl-enteprises/ghas-demos
Do not deploy or use in production. Bandit detects every issue here.
"""
import hashlib
import random


def hash_password(password: str) -> str:
    # ⚠️ B303 — md5 is broken for security; use bcrypt/argon2/sha256+salt.
    return hashlib.md5(password.encode()).hexdigest()


def generate_session_id() -> str:
    # ⚠️ B311 — `random` is not cryptographically secure; use `secrets`.
    return "".join(str(random.randint(0, 9)) for _ in range(16))


def weak_token(seed: int) -> str:
    # ⚠️ B311 — predictable randomness for a security-sensitive token.
    random.seed(seed)
    return f"{random.random():.16f}"
