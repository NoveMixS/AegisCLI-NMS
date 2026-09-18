#!/usr/bin/env python3
"""HTTP Probe for AegisCLI."""

import re
import urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich import box

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
console = Console()

description = "HTTP/HTTPS prober — detect live hosts, status codes, titles, tech stack"
__version__ = "1.0"
__author__  = "Md Siyam Mahmud"
__category__ = "Recon"

SCHEMA = {
    "action": {"type": "choice", "choices": ["probe", "json"], "default": "probe"},
    "targets": {"type": "list", "required": True},
    "timeout": {"type": "int", "default": 8},
    "threads": {"type": "int", "default": 20},
}

TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
TECH_PATTERNS = [
    (r"nginx", "Nginx"), (r"apache", "Apache"), (r"cloudflare", "Cloudflare"),
    (r"iis", "IIS"), (r"express", "Express.js"),
    (r"wp-content|wordpress", "WordPress"), (r"react", "React"),
    (r"next\.js|__NEXT_DATA__", "Next.js"), (r"vue\.js|vue@", "Vue.js"),
    (r"angular", "Angular"), (r"drupal", "Drupal"), (r"joomla", "Joomla"),
    (r"shopify", "Shopify"), (r"php", "PHP"), (r"asp\.net", "ASP.NET"),
    (r"python", "Python"), (r"gunicorn", "Gunicorn"), (r"node", "Node.js"),
]


def _clean_host(host):
    host = host.strip().lower()
    host = re.sub(r"^https?://", "", host)
    return host.split("/")[0]


def _detect_tech(text, headers):
    blob = text.lower() + " " + " ".join(f"{k}: {v}" for k, v in headers.items()).lower()
    found = []
    for pattern, name in TECH_PATTERNS:
        if re.search(pattern, blob, re.IGNORECASE):
            if name not in found:
                found.append(name)
    return found


def _probe_one(host, timeout=8):
    host = _clean_host(host)
    result = {"host": host, "ok": False, "url": None, "status": None,
              "title": None, "tech": [], "error": None}
    for scheme in ("https", "http"):
        url = f"{scheme}://{host}"
        try:
            resp = requests.get(url, timeout=timeout, allow_redirects=True,
                                verify=False, headers={"User-Agent": "AegisCLI/1.0"})
            result["ok"] = True
            result["url"] = resp.url
            result["status"] = resp.status_code
            m = TITLE_RE.search(resp.text)
            if m:
                result["title"] = re.sub(r"\s+", " ", m.group(1).strip())[:80]
            result["tech"] = _detect_tech(resp.text, dict(resp.headers))
            return result
        except requests.exceptions.SSLError:
            result["error"] = "SSL error"
        except requests.exceptions.ConnectionError:
            result["error"] = "connection failed"
        except requests.exceptions.Timeout:
            result["error"] = "timeout"
        except Exception as e:
            result["error"] = str(e)[:60]
    return result


def _action_probe(targets, timeout=8, threads=20):
    targets = [_clean_host(t) for t in targets if t.strip()]
    if not targets:
        return {"ok": False, "action": "probe", "error": "no targets"}
    results = []
    with Progress(SpinnerColumn(),
                  TextColumn("[progress.description]{task.description}"),
                  BarColumn(), TextColumn("{task.completed}/{task.total}"),
                  console=console, transient=True) as progress:
        task = progress.add_task("Probing", total=len(targets))
        with ThreadPoolExecutor(max_workers=threads) as pool:
            futures = {pool.submit(_probe_one, t, timeout): t for t in targets}
            for fut in as_completed(futures):
                try:
                    results.append(fut.result())
                except Exception as e:
                    results.append({"host": futures[fut], "ok": False, "error": str(e)[:60]})
                progress.update(task, advance=1)
    results.sort(key=lambda r: (not r.get("ok"), r.get("host", "")))
    live = [r for r in results if r.get("ok")]
    dead = [r for r in results if not r.get("ok")]
    return {"ok": True, "action": "probe", "total": len(targets),
            "live": len(live), "dead": len(dead), "results": results,
            "queried_at": datetime.utcnow().isoformat(timespec="seconds") + "Z"}


def _render_result(result):
    if not result.get("ok"):
        console.print(f"[red]✖ {result.get('error')}[/red]")
        return
    console.print(Panel(
        f"[bold]Total:[/bold] {result['total']}\n"
        f"[bold]Live:[/bold] [green]{result['live']}[/green]\n"
        f"[bold]Dead:[/bold] [red]{result['dead']}[/red]",
        title="🌐 HTTP Probe Results", border_style="cyan"))
    live = [r for r in result["results"] if r.get("ok")]
    if live:
        t = Table(title="✅ Live Hosts", box=box.ROUNDED)
        t.add_column("Host", style="cyan", width=24)
        t.add_column("Status", style="green", width=8, justify="center")
        t.add_column("Title", style="white", width=35, overflow="fold")
        t.add_column("Tech", style="yellow", width=25, overflow="fold")
        for r in live:
            sc = r["status"] or 0
            color = "green" if sc < 400 else "yellow" if sc < 500 else "red"
            t.add_row(r["host"], f"[{color}]{sc}[/{color}]",
                     (r.get("title") or "—")[:35],
                     ", ".join(r.get("tech", [])) or "—")
        console.print(t)
    dead = [r for r in result["results"] if not r.get("ok")]
    if dead:
        t = Table(title="❌ Unreachable", box=box.ROUNDED)
        t.add_column("Host", style="dim", width=24)
        t.add_column("Reason", style="red")
        for r in dead:
            t.add_row(r["host"], r.get("error") or "unknown")
        console.print(t)


def _interactive():
    console.print("[cyan]Enter targets[/cyan] (one per line, empty to finish):")
    targets = []
    while True:
        line = console.input("  > ").strip()
        if not line:
            break
        targets.append(line)
    if not targets:
        return {"ok": False, "action": "probe", "error": "no targets"}
    console.print(f"\n[dim]Probing {len(targets)} host(s)...[/dim]\n")
    result = _action_probe(targets)
    _render_result(result)
    return result


def run(args=None):
    if args is None:
        return _interactive()
    action = (args.get("action") or "probe").lower()
    targets = args.get("targets", [])
    timeout = int(args.get("timeout", 8))
    threads = int(args.get("threads", 20))
    if isinstance(targets, str):
        targets = [t.strip() for t in targets.split("\n") if t.strip()]
    if action in ("probe", "json"):
        result = _action_probe(targets, timeout, threads)
        if action == "json":
            console.print_json(data=result)
        else:
            _render_result(result)
        return result
    return {"ok": False, "action": action, "error": f"Unknown action: {action}"}