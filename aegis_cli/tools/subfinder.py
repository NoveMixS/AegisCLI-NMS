#!/usr/bin/env python3
"""
tools/subfinder.py — Subdomain enumeration using DNS resolution.

AegisCLI hub module. Exposes:
    description  : str
    SCHEMA       : dict  -- machine-readable manifest for the AI engine
    run(args)    : dict  -- structured results (also prints Rich table)

Behavior:
    * Called with no args  -> interactive prompts (original UX).
    * Called with a dict   -> fully non-interactive, no prompts.
    * args["json"] == True -> prints JSON, suppresses tables/progress.

Returned dict shape:
    {
        "domain":   "example.com",
        "found":    {"www": ["1.2.3.4"], "api": ["1.2.3.5"]},
        "count":    2,
        "elapsed":  3.41,
    }
"""

import os
import sys
import json
import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from rich.console import Console
from rich.table import Table
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeElapsedColumn,
)

console = Console()

# ----------------------------------------------------------------------
# Module metadata
# ----------------------------------------------------------------------
description = "DNS brute-force subdomain discovery"
__version__ = "2.0"
__author__ = "Md Siyam Mahmud"
__category__ = "Recon"

# ----------------------------------------------------------------------
# Machine-readable schema (for the future AI command engine).
# ----------------------------------------------------------------------
SCHEMA = {
    "name": "subfinder",
    "description": "Enumerate subdomains of a domain via DNS brute-force.",
    "args": {
        "domain":   {"type": "string", "required": True,
                     "help": "Target base domain, e.g. example.com"},
        "wordlist": {"type": "string", "required": False,
                     "help": "Path to a custom wordlist file. Omit for built-in."},
        "threads":  {"type": "int",    "required": False, "default": 200,
                     "help": "Max concurrent workers."},
        "timeout":  {"type": "float",  "required": False, "default": 5.0,
                     "help": "Per-lookup DNS timeout in seconds."},
        "json":     {"type": "bool",   "required": False, "default": False,
                     "help": "Emit JSON instead of a Rich table."},
    },
    "returns": {
        "domain":  "string",
        "found":   "dict[subdomain -> list[ip]]",
        "count":   "int",
        "elapsed": "float",
    },
}

# ----------------------------------------------------------------------
# Built-in wordlist (~250 common subdomains)
# ----------------------------------------------------------------------
FALLBACK_WORDLIST = [
    # common web / infra
    "www", "mail", "ftp", "webmail", "smtp", "pop", "pop3", "imap",
    "ns1", "ns2", "ns3", "ns4", "dns", "dns1", "dns2",
    "cpanel", "whm", "autodiscover", "autoconfig", "m", "mobile",
    "test", "dev", "staging", "stage", "beta", "alpha", "demo",
    "admin", "administrator", "panel", "cp", "dashboard", "manage",
    "forum", "blog", "news", "wiki", "docs", "help", "support",
    "vpn", "remote", "git", "gitlab", "github", "jenkins", "ci",
    "mysql", "sql", "db", "database", "mssql", "oracle", "postgres",
    "old", "new", "legacy", "backup", "bak", "archive",
    "lists", "newsletter", "email", "webmail2", "mail2",
    "mx", "mx1", "mx2", "relay",
    "static", "assets", "img", "images", "cdn", "media",
    "shop", "store", "cart", "checkout", "payment", "pay",
    "secure", "ssl", "login", "signin", "auth", "sso", "oauth",
    "api", "api2", "api-v1", "api-v2", "rest", "graphql",
    "app", "apps", "web", "webapp", "portal", "my",
    "play", "live", "stream", "video", "tv",
    "local", "localhost", "internal", "intranet", "extranet",
    "info", "status", "monitor", "metrics", "grafana", "prometheus",
    "kibana", "elastic", "elasticsearch", "log", "logs", "splunk",
    "start", "go", "link", "links", "url", "redirect",
    "file", "files", "upload", "uploads", "download", "downloads",
    "cloud", "aws", "azure", "gcp", "s3", "storage",
    "k8s", "kubernetes", "kube", "cluster", "node", "nodes",
    "proxy", "gateway", "edge", "lb", "loadbalancer",
    "id", "identity", "account", "accounts", "user", "users",
    "profile", "profiles", "member", "members",
    "search", "find", "query", "explore",
    "chat", "im", "slack", "teams", "meet", "zoom",
    "calendar", "calendar2", "schedule",
    "photo", "photos", "gallery", "pic", "pics",
    "doc", "docs2", "pdf", "ebook",
    "game", "games", "play2",
    "payment2", "billing", "invoice", "invoices",
    "report", "reports", "analytics", "stats", "statistics",
    "marketing", "sales", "crm", "erp", "hr",
    "training", "learn", "education", "edu",
    "partner", "partners", "affiliate", "affiliates",
    "vendor", "vendors", "supplier", "suppliers",
    "feedback", "survey", "form", "forms",
    "translate", "translate2", "language",
    "customer", "customers", "client", "clients",
    "employee", "employees", "staff", "team", "teams2",
    "server", "server1", "server2", "host", "host1",
    "vm", "vm1", "vm2", "instance", "instances",
    "staging2", "qa", "uat", "preprod", "prod", "production",
    "preview", "sandbox", "lab", "labs", "research",
    "beta2", "beta3", "alpha2",
    "test2", "test3", "testing",
    "dev2", "dev3",
    "demo2", "trial",
    "sandbox2",
    "tmp", "temp", "temporary",
    "hidden", "secret", "private", "internal2",
    "vpn2", "tunnel",
    "mailer", "sendmail", "postfix", "exim",
    "spam", "antispam", "filter",
    "access", "login2", "portal2",
    "aws2", "aws-console", "console",
    "smartsheet", "jira", "confluence", "bitbucket",
    "trello", "asana", "monday",
    "zabbix", "nagios", "icinga", "sensu",
    "n8n", "zapier", "ifttt",
    "chat2", "discord", "telegram",
    "custom", "custom2",
    "old2", "old3",
    "new2", "new3",
    "backup2", "backup3",
    "archive2", "archive3",
    "mirror", "mirror1", "mirror2",
    "v1", "v2", "v3",
    "api3", "api4", "api5",
    "web1", "web2", "web3",
    "app1", "app2", "app3",
    "site", "site1", "site2",
    "server3", "server4",
    "client1", "client2",
    "demo3", "demo4",
    "sample", "samples",
    "test-api", "test-api2", "api-test", "api-test2",
    "test-app", "test-app2", "app-test", "app-test2",
    "dev-api", "dev-api2", "api-dev", "api-dev2",
    "stage-api", "stage-api2", "api-stage", "api-stage2",
    "prod-api", "prod-api2", "api-prod", "api-prod2",
    "internal-api", "internal-api2", "api-internal", "api-internal2",
    "external-api", "external-api2", "api-external", "api-external2",
    "public-api", "public-api2", "api-public", "api-public2",
    "private-api", "private-api2", "api-private", "api-private2",
    "secure-api", "secure-api2", "api-secure", "api-secure2",
    "rest-api", "rest-api2", "api-rest", "api-rest2",
    "graphql-api", "graphql-api2", "api-graphql", "api-graphql2",
]

# ----------------------------------------------------------------------
# DNS resolver
#
# socket.getaddrinfo() has NO built-in timeout and ignores
# socket.setdefaulttimeout().  To guarantee a hard per-lookup timeout we
# run the lookup in a daemon thread and join with a deadline.  If the
# thread is stuck, we return None and let the daemon die with the process.
# ----------------------------------------------------------------------
def resolve(host: str, timeout: float = 5.0):
    """Resolve host to a sorted list of unique IPs, or None on failure."""
    result = [None]

    def _do_lookup():
        try:
            infos = socket.getaddrinfo(host, None)
            ips = sorted({info[4][0] for info in infos})
            if ips:
                result[0] = ips
        except (socket.gaierror, socket.timeout, UnicodeError, OSError):
            pass
        except Exception:
            pass

    worker = threading.Thread(target=_do_lookup, daemon=True)
    worker.start()
    worker.join(timeout=timeout)
    return result[0]

# ----------------------------------------------------------------------
# Enumeration
# ----------------------------------------------------------------------
def enumerate_subdomains(domain, wordlist, max_workers=200, timeout=5.0,
                         show_progress=True):
    """Return dict[subdomain -> list[ip]] for all resolving candidates."""
    found = {}
    lock = threading.Lock()

    def worker(sub):
        full = domain if sub == "@" else f"{sub}.{domain}"
        ips = resolve(full, timeout=timeout)
        if ips:
            with lock:
                found[sub] = ips

    if not show_progress:
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = [pool.submit(worker, s) for s in wordlist]
            for _ in as_completed(futures):
                pass
        return found

    with Progress(
        SpinnerColumn(),
        TextColumn("[cyan]Enumerating subdomains..."),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("enum", total=len(wordlist))
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = [pool.submit(worker, s) for s in wordlist]
            for _ in as_completed(futures):
                progress.advance(task)

    return found

# ----------------------------------------------------------------------
# Interactive prompts (only used when args is None)
# ----------------------------------------------------------------------
def _prompt_inputs():
    console.print("\n[bold cyan]🔎 Subdomain Enumerator[/bold cyan]")
    console.print("[dim]DNS brute-force with hard per-lookup timeout[/dim]\n")

    domain = console.input("[cyan]Domain (e.g. example.com): [/cyan]").strip()
    if not domain:
        console.print("[red]No domain provided.[/red]")
        return None

    wordlist_path = console.input(
        "[cyan]Custom wordlist path (blank = built-in ~250): [/cyan]"
    ).strip()

    threads_str = console.input("[cyan]Max threads (default 200): [/cyan]").strip() or "200"
    timeout_str = console.input("[cyan]Per-lookup timeout sec (default 5.0): [/cyan]").strip() or "5.0"

    try:
        threads = int(threads_str)
        timeout = float(timeout_str)
    except ValueError:
        console.print("[yellow]Invalid number, falling back to defaults (200 threads, 5.0s).[/yellow]")
        threads, timeout = 200, 5.0

    return {
        "domain": domain,
        "wordlist": wordlist_path or None,
        "threads": threads,
        "timeout": timeout,
        "json": False,
    }

# ----------------------------------------------------------------------
# Public entry point
# ----------------------------------------------------------------------
def run(args: dict | None = None) -> dict:
    """
    Run subdomain enumeration.

    Interactive when args is None; otherwise non-interactive using the
    provided dict. Recognized keys: domain, wordlist, threads, timeout, json.
    """
    if args is None:
        args = _prompt_inputs()
        if not args:
            return {"domain": None, "found": {}, "count": 0, "elapsed": 0.0}

    domain = (args.get("domain") or "").strip()
    if not domain:
        console.print("[red]No domain provided.[/red]")
        return {"domain": None, "found": {}, "count": 0, "elapsed": 0.0}

    emit_json = bool(args.get("json", False))
    interactive = args.get("_interactive", args is not None and not emit_json and False)

    # Load wordlist
    wordlist_path = args.get("wordlist")
    if wordlist_path:
        try:
            with open(wordlist_path, "r") as f:
                wordlist = [line.strip() for line in f if line.strip()]
            if not wordlist:
                raise ValueError("empty wordlist")
        except Exception:
            console.print("[red]Could not read wordlist, using built-in.[/red]")
            wordlist = FALLBACK_WORDLIST
    else:
        wordlist = FALLBACK_WORDLIST

    threads = int(args.get("threads", 200))
    timeout = float(args.get("timeout", 5.0))

    if not emit_json:
        console.print(
            f"\n[bold]Testing {len(wordlist)} candidates against "
            f"{domain} ({threads} workers, {timeout}s timeout)...[/bold]\n"
        )

    start = time.time()
    found = enumerate_subdomains(
        domain, wordlist,
        max_workers=threads,
        timeout=timeout,
        show_progress=not emit_json,
    )
    elapsed = time.time() - start

    result = {
        "domain": domain,
        "found": {sub: ips for sub, ips in sorted(found.items())},
        "count": len(found),
        "elapsed": round(elapsed, 2),
    }

    # Output
    if emit_json:
        # Clean, machine-parseable line on stdout
        print(json.dumps(result, indent=2))
    else:
        if found:
            table = Table(title=f"Subdomains for {domain}")
            table.add_column("Subdomain", style="cyan")
            table.add_column("IP(s)", style="green")
            for sub, ips in sorted(found.items()):
                full = domain if sub == "@" else f"{sub}.{domain}"
                table.add_row(full, ", ".join(ips))
            console.print(table)
            console.print(
                f"[bold green]Found {len(found)} subdomain(s) "
                f"in {elapsed:.1f}s.[/bold green]"
            )
        else:
            console.print(f"[yellow]No subdomains found in {elapsed:.1f}s.[/yellow]")
            console.print(
                "[dim]Tip: use a bigger wordlist from SecLists "
                "(e.g. subdomains-top1million-5000.txt)[/dim]"
            )

    return result

# ----------------------------------------------------------------------
# Standalone entry point
#
# NOTE: The hub owns the "press enter to return" pause.  This block only
# runs when the file is executed directly (python tools/subfinder.py).
# ----------------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AegisCLI subdomain enumerator")
    parser.add_argument("domain", nargs="?", help="Target domain")
    parser.add_argument("-w", "--wordlist", help="Path to custom wordlist")
    parser.add_argument("-t", "--threads", type=int, default=200)
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    opts = parser.parse_args()

    if opts.domain:
        run({
            "domain": opts.domain,
            "wordlist": opts.wordlist,
            "threads": opts.threads,
            "timeout": opts.timeout,
            "json": opts.json,
        })
        if not opts.json:
            input("\nPress Enter to exit...")
    else:
        # Interactive fallback
        run()
        input("\nPress Enter to exit...")