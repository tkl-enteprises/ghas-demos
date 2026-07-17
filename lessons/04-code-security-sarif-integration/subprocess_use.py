"""
⚠️ INTENTIONALLY VULNERABLE — for educational use only.
Part of GHAS workshop demos: https://github.com/tkl-enteprises/ghas-demos
Do not deploy or use in production. Bandit detects every issue here.
"""
import subprocess  # noqa: F401  ⚠️ B404 — `subprocess` import flagged for review.


def list_files(path: str) -> str:
    # ⚠️ B602 — shell=True with user input → command injection.
    return subprocess.check_output(f"ls -la {path}", shell=True).decode()


def run_pipeline(user_filter: str) -> str:
    # ⚠️ B602 — Popen with shell=True is the canonical command-injection sink.
    proc = subprocess.Popen(
        f"cat /etc/passwd | grep {user_filter}",
        shell=True,
        stdout=subprocess.PIPE,
    )
    out, _ = proc.communicate()
    return out.decode()


def run_no_shell(target: str) -> str:
    # ⚠️ B603 — even without shell=True, untrusted input as argv is risky.
    return subprocess.check_output(["ping", "-c", "1", target]).decode()
