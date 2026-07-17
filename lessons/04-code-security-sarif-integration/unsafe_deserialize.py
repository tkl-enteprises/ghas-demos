"""
⚠️ INTENTIONALLY VULNERABLE — for educational use only.
Part of GHAS workshop demos: https://github.com/tkl-enteprises/ghas-demos
Do not deploy or use in production. Bandit detects every issue here.
"""
import pickle


def load_session(blob: bytes):
    # ⚠️ B301 — pickle.loads on untrusted data → arbitrary code execution.
    return pickle.loads(blob)


def load_session_from_file(path: str):
    # ⚠️ B301 — pickle.load is just as dangerous as pickle.loads.
    with open(path, "rb") as fh:
        return pickle.load(fh)
