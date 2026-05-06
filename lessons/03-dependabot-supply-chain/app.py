"""
⚠️ INTENTIONALLY VULNERABLE — for educational use only.
Part of GHAS workshop demos: https://github.com/tkl-enteprises/ghas-demos
Do not deploy. requirements.txt pins known-vulnerable versions.
"""
from flask import Flask, request, render_template_string
from jinja2 import Template
import yaml
import requests
from cryptography.fernet import Fernet

app = Flask(__name__)


@app.route("/render")
def render():
    template = request.args.get("t", "")
    # ⚠️ Server-side template injection — see CVE-style discussion in solution.md.
    return render_template_string(template)


@app.route("/load")
def load():
    data = request.args.get("data", "{}")
    # ⚠️ yaml.load (vs safe_load) on PyYAML <5.1 → arbitrary code execution.
    return yaml.load(data)


@app.route("/fetch")
def fetch():
    url = request.args.get("url", "https://example.com")
    # ⚠️ requests<2.20 leaks Authorization header on cross-origin redirects (GHSA-x84v-xcm2-53pg).
    return requests.get(url).text


@app.route("/render2")
def render2():
    name = request.args.get("name", "")
    # ⚠️ Jinja2<2.10.1 sandbox escape via str.format (GHSA-462w-v97r-4m45).
    return Template("Hello {{ n }}").render(n=name)


@app.route("/key")
def key():
    # ⚠️ cryptography 2.3 has multiple advisories — see README table.
    return Fernet.generate_key()


if __name__ == "__main__":
    app.run(debug=True)
