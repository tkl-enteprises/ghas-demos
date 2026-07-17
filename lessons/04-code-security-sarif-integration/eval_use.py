"""
⚠️ INTENTIONALLY VULNERABLE — for educational use only.
Part of GHAS workshop demos: https://github.com/tkl-enteprises/ghas-demos
Do not deploy or use in production. Bandit detects every issue here.
"""


def evaluate(expression: str):
    # ⚠️ B307 — eval on user input → code injection.
    return eval(expression)


def execute(code: str) -> None:
    # ⚠️ Same family — exec is equally dangerous.
    exec(code)
