#!/usr/bin/env python3
"""Directory Brute-Forcer for AegisCLI."""

import re
import urllib3
from collections import Counter
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

description = "Directory/path brute-forcer (finds hidden files & endpoints)"
__version__ = "1.0"
__author__  = "Md Siyam Mahmud"
__category__ = "Web"

SCHEMA = {
    "action": {"type": "choice", "choices": ["scan", "json"], "default": "scan"},
    "url": {"type": "string", "required": True},
    "wordlist": {"type": "path", "required": False},
    "threads": {"type": "int", "default": 20},
    "timeout": {"type": "int", "default": 8},
    "extensions": {"type": "string", "required": False},
}

BUILTIN_WORDLIST = [
    "admin", "admin/", "administrator", "admin.php", "admin.html",
    "login", "login/", "login.php", "wp-admin", "wp-login.php",
    "dashboard", "panel", "cpanel", "manage", "manager",
    "api", "api/", "api/v1", "api/v2", "api/v3",
    "graphql", "rest", "json", "swagger", "swagger.json",
    "openapi.json", "api-docs", "docs",
    ".env", ".env.local", ".env.production", ".env.backup",
    "config", "config/", "config.php", "config.json", "config.yml",
    "settings", "settings.php", "settings.json",
    "wp-config.php", "wp-config.php.bak",
    "backup", "backups", "backup.zip", "backup.tar.gz",
    "db.sql", "database.sql", "dump.sql", "site.zip",
    "old", "old-site", "old/", "archive", "archive.zip",
    ".git", ".git/", ".git/config", ".gitignore",
    ".svn", ".svn/", ".hg", ".hg/",
    ".DS_Store", ".htaccess", ".htpasswd",
    "uploads", "upload", "files", "media", "images", "img",
    "assets", "static", "public", "private", "downloads",
    "cache", "tmp", "temp", "logs", "log",
    "test", "tests", "dev", "development", "staging",
    "beta", "demo", "sandbox", "playground",
    "index.php", "index.html", "index.htm", "home",
    "robots.txt", "sitemap.xml", "humans.txt", "security.txt",
    "favicon.ico", "crossdomain.xml",
    "status", "health", "healthz", "ping", "version",
    "info", "phpinfo.php", "server-status", "server-info",
    "wp-content", "wp-includes", "wordpress",
    "joomla", "drupal", "magento",
    "phpmyadmin", "pma", "mysql", "myadmin",
    "console", "shell", "cmd", "exec", "debug",
    "readme", "README.md", "CHANGELOG.md", "LICENSE",
]


def _normalize_url(url):
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url.rstrip("/")


def _load_wordlist(custom_path):
    if custom_path:
        try:
            with open(custom_path, "r", encoding="utf-8", errors="ignore") as f:
                return list(dict.fromkeys(l.strip() for l in f if l.strip() and not l.startswith("#")))
        except Exception as e:
            console.print(f"[yellow]⚠️ {e}[/yellow]")
    return BUILTIN_WORDLIST


def _apply_extensions(words, extensions):
    if not extensions:
        return words
    exts = [e.strip().lstrip(".") for e in extensions.split(",") if e.strip()]
    if not exts:
        return words
    expanded = set(words)
    for w in words:
        if "/" in w or w.endswith(tuple(f".{e}" for e in exts)):
            continue
        for e in exts:
            expanded.add(f"{w}.{e}")
    return sorted(expanded)


def _probe_path(base_url, path, timeout):
    url = f"{base_url}/{path.lstrip('/')}"
    try:
        resp = requests.get(url, timeout=timeout, allow_redirects=False,
                            verify=False, headers={"User-Agent": "AegisCLI/1.0"})
        snippet = resp.text[:500] if resp.text else ""
        title = None
        m = re.search(r"<title[^>]*>(.*?)</title>", snippet, re.IGNORECASE | re.DOTALL)
        if m:
            title = re.sub(r"\s+", " ", m.group(1)).strip()[:60]
        return {"path": path, "url": url, "status": resp.status_code,
                "length": len(resp.content),
                "content_type": resp.headers.get("Content-Type", "").split(";")[0],
                "title": title, "redirect_to": resp.headers.get("Location")}
    except requests.exceptions.Timeout:
        return {"path": path, "url": url, "error": "timeout"}
    except requests.exceptions.ConnectionError:
        return {"path": path, "url": url, "error": "connection error"}
    except Exception as e:
        return {"path": path, "url": url, "error": str(e)[:60]}


def _action_scan(url, wordlist, threads=20, timeout=8):
    url = _normalize_url(url)
    if not wordlist:
        return {"ok": False, "action": "scan", "error": "empty wordlist"}
    results = []
    with Progress(SpinnerColumn(),
                  TextColumn("[progress.description]{task.description}"),
                  BarColumn(), TextColumn("{task.completed}/{task.total}"),
                  console=console, transient=True) as progress:
        task = progress.add_task("Scanning", total=len(wordlist))
        with ThreadPoolExecutor(max_workers=threads) as pool:
            futures = {pool.submit(_probe_path, url, p, timeout): p for p in wordlist}
            for fut in as_completed(futures):
                try:
                    results.append(fut.result())
                except Exception as e:
                    results.append({"path": futures[fut], "error": str(e)[:60]})
                progress.update(task, advance=1)

    INTERESTING = {200, 201, 204, 301, 302, 307, 308, 401, 403, 500, 502, 503}
    found = [r for r in results if r.get("status") in INTERESTING]
    errors = [r for r in results if r.get("error")]

    sizes = [r.get("length", 0) for r in found if r.get("length")]
    false_positive_size = None
    if sizes:
        common_size, common_count = Counter(sizes).most_common(1)[0]
        if common_count > len(found) * 0.5 and len(found) > 3:
            false_positive_size = common_size
            found = [r for r in found if r.get("length") != false_positive_size]

    found.sort(key=lambda r: (r["status"], r["path"]))
    by_status = {}
    for r in found:
        by_status.setdefault(r["status"], []).append(r)

    return {"ok": True, "action": "scan", "target": url,
            "total_paths": len(wordlist), "found_count": len(found),
            "error_count": len(errors), "false_positive_size": false_positive_size,
            "results": found, "by_status": by_status,
            "scanned_at": datetime.utcnow().isoformat(timespec="seconds") + "Z"}


def _render_result(result):
    if not result.get("ok"):
        console.print(f"[red]✖ {result.get('error')}[/red]")
        return
    text = (f"[bold]Target:[/bold] {result['target']}\n"
            f"[bold]Paths:[/bold] {result['total_paths']} tested\n"
            f"[bold]Found:[/bold] [green]{result['found_count']}[/green] interesting\n"
            f"[bold]Errors:[/bold] [yellow]{result['error_count']}[/yellow]")
    if result.get("false_positive_size"):
        text += f"\n[dim]Filtered false-positive size={result['false_positive_size']}[/dim]"
    console.print(Panel(text, title="📁 Directory Brute-Force", border_style="cyan"))

    status_colors = {200: "green", 201: "green", 204: "green",
                     301: "cyan", 302: "cyan", 307: "cyan", 308: "cyan",
                     401: "yellow", 403: "yellow", 500: "red", 502: "red", 503: "red"}
    for status in sorted(result["by_status"].keys()):
        entries = result["by_status"][status]
        color = status_colors.get(status, "white")
        t = Table(title=f"{status} — {len(entries)} path(s)",
                  title_style=f"bold {color}", box=box.ROUNDED)
        t.add_column("Path", style="cyan", width=30)
        t.add_column("Size", style="dim", width=8, justify="right")
        t.add_column("Type", style="dim", width=16)
        t.add_column("Title / Info", style="white", overflow="fold")
        for r in entries:
            info = r.get("title") or ""
            if r.get("redirect_to"):
                info = f"→ {r['redirect_to'][:40]}"
            if not info:
                info = "—"
            t.add_row(r["path"], f"{r.get('length', 0)}",
                     r.get("content_type") or "—", info)
        console.print(t)

    if result["found_count"] == 0:
        console.print("[yellow]No interesting paths found.[/yellow]")


def _interactive():
    url = console.input("[cyan]Target URL[/cyan] (e.g. https://example.com): ").strip()
    if not url:
        return {"ok": False, "action": "scan", "error": "no URL"}
    wl = console.input("[cyan]Wordlist path[/cyan] (blank = built-in): ").strip() or None
    exts = console.input("[cyan]Extensions[/cyan] (comma-separated): ").strip() or None
    threads_str = console.input("[cyan]Threads[/cyan] [20]: ").strip() or "20"
    try:
        threads = int(threads_str)
    except ValueError:
        threads = 20
    wordlist = _apply_extensions(_load_wordlist(wl), exts)
    console.print(f"\n[dim]Scanning {len(wordlist)} paths on {url}...[/dim]\n")
    result = _action_scan(url, wordlist, threads=threads)
    _render_result(result)
    return result


def run(args=None):
    if args is None:
        return _interactive()
    action = (args.get("action") or "scan").lower()
    url = args.get("url", "")
    wl = args.get("wordlist")
    threads = int(args.get("threads", 20))
    timeout = int(args.get("timeout", 8))
    exts = args.get("extensions")
    wordlist = _apply_extensions(_load_wordlist(wl), exts)
    if action in ("scan", "json"):
        result = _action_scan(url, wordlist, threads=threads, timeout=timeout)
        if action == "json":
            console.print_json(data=result)
        else:
            _render_result(result)
        return result
    return {"ok": False, "action": action, "error": f"Unknown action: {action}"}