#!/usr/bin/env python3
"""HTTP Security Headers Analyzer for AegisCLI."""

from datetime import datetime
import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

description = "HTTP security headers analyzer with score & recommendations"
__version__ = "1.0"
__author__  = "Md Siyam Mahmud"
__category__ = "Web"

SCHEMA = {
    "action": {"type": "choice", "choices": ["check", "json"], "default": "check"},
    "url": {"type": "string", "required": True},
    "timeout": {"type": "int", "default": 10},
}

SECURITY_HEADERS = [
    ("Strict-Transport-Security", "HSTS", 3, "Forces HTTPS"),
    ("Content-Security-Policy", "CSP", 3, "Restricts resources"),
    ("X-Content-Type-Options", "X-Content-Type-Options", 1, "Prevents MIME sniff"),
    ("X-Frame-Options", "X-Frame-Options", 2, "Prevents clickjacking"),
    ("Referrer-Policy", "Referrer-Policy", 1, "Controls referrer"),
    ("Permissions-Policy", "Permissions-Policy", 1, "Restricts features"),
    ("Cross-Origin-Opener-Policy", "COOP", 2, "Isolates context"),
    ("Cross-Origin-Embedder-Policy", "COEP", 1, "Requires CORS"),
    ("Cross-Origin-Resource-Policy", "CORP", 1, "Restricts embedding"),
]

INFO_LEAK_HEADERS = ["Server", "X-Powered-By", "X-AspNet-Version"]


def _normalize_url(url):
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def _fetch_headers(url, timeout=10):
    try:
        resp = requests.get(url, timeout=timeout, allow_redirects=True,
                            headers={"User-Agent": "AegisCLI/1.0"})
        return {"ok": True, "status_code": resp.status_code,
                "final_url": resp.url, "headers": dict(resp.headers)}
    except Exception as e:
        return {"ok": False, "error": str(e)[:100]}


def _analyze(headers):
    lower = {k.lower(): v for k, v in headers.items()}
    present, missing = [], []
    total_w, earned_w = 0, 0
    for name, friendly, weight, desc in SECURITY_HEADERS:
        total_w += weight
        if name.lower() in lower:
            present.append({"header": name, "value": lower[name.lower()]})
            earned_w += weight
        else:
            missing.append({"header": name, "description": desc})
    leaks = [{"header": h, "value": lower[h.lower()]} for h in INFO_LEAK_HEADERS if h.lower() in lower]
    score = round((earned_w / total_w) * 10, 1) if total_w else 0
    if score >= 9: grade = "A+"
    elif score >= 8: grade = "A"
    elif score >= 7: grade = "B"
    elif score >= 5: grade = "C"
    elif score >= 3: grade = "D"
    else: grade = "F"
    return {"present": present, "missing": missing, "leaks": leaks, "score": score, "grade": grade}


def _action_check(url, timeout=10):
    url = _normalize_url(url)
    fetched = _fetch_headers(url, timeout)
    if not fetched.get("ok"):
        return {"ok": False, "action": "check", "url": url, "error": fetched.get("error")}
    analysis = _analyze(fetched["headers"])
    return {"ok": True, "action": "check", "url": url,
            "final_url": fetched["final_url"], "status_code": fetched["status_code"],
            "score": analysis["score"], "grade": analysis["grade"],
            "present": analysis["present"], "missing": analysis["missing"],
            "leaks": analysis["leaks"],
            "queried_at": datetime.utcnow().isoformat(timespec="seconds") + "Z"}


def _render_result(result):
    if not result.get("ok"):
        console.print(f"[red]✖ {result.get('error')}[/red]")
        return
    grade = result["grade"]
    color = {"A+": "green", "A": "green", "B": "cyan", "C": "yellow",
             "D": "orange1", "F": "red"}.get(grade, "white")
    console.print(Panel(
        f"[bold]URL:[/bold] {result['final_url']}\n"
        f"[bold]Status:[/bold] {result['status_code']}\n"
        f"[bold]Score:[/bold] {result['score']}/10\n"
        f"[bold]Grade:[/bold] [{color}]{grade}[/{color}]",
        title=f"🔒 HTTP Headers · {result['url']}", border_style=color))
    if result["present"]:
        t = Table(title="✅ Present", box=box.ROUNDED)
        t.add_column("Header", style="green", width=32)
        t.add_column("Value", style="white")
        for h in result["present"]:
            v = h["value"][:60] + "..." if len(h["value"]) > 60 else h["value"]
            t.add_row(h["header"], v)
        console.print(t)
    if result["missing"]:
        t = Table(title="❌ Missing", box=box.ROUNDED)
        t.add_column("Header", style="red", width=32)
        t.add_column("Impact", style="white")
        for h in result["missing"]:
            t.add_row(h["header"], h["description"])
        console.print(t)
    if result["leaks"]:
        t = Table(title="⚠️ Information Disclosure", box=box.ROUNDED)
        t.add_column("Header", style="yellow", width=20)
        t.add_column("Value", style="white")
        for leak in result["leaks"]:
            t.add_row(leak["header"], leak["value"])
        console.print(t)


def _interactive():
    url = console.input("[cyan]URL to check[/cyan] (e.g. https://github.com): ").strip()
    if not url:
        return {"ok": False, "action": "check", "error": "no URL"}
    console.print(f"\n[dim]Fetching {url}...[/dim]\n")
    result = _action_check(url)
    _render_result(result)
    return result


def run(args=None):
    if args is None:
        return _interactive()
    action = (args.get("action") or "check").lower()
    url = args.get("url", "")
    timeout = int(args.get("timeout", 10))
    if action in ("check", "json"):
        result = _action_check(url, timeout)
        if action == "json":
            console.print_json(data=result)
        else:
            _render_result(result)
        return result
    return {"ok": False, "action": action, "error": f"Unknown action: {action}"}