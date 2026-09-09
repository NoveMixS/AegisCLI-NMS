"""
tools/subfinder.py — DNS brute-force subdomain enumeration, interactive.
"""
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from rich.console import Console
from rich.table import Table

console = Console()

description = "DNS brute-force subdomain discovery"

FALLBACK_WORDLIST = [
    "www", "mail", "ftp", "api", "dev", "staging", "test", "admin",
    "portal", "vpn", "shop", "blog", "app", "cdn", "static", "beta",
    "ns1", "ns2", "smtp", "webmail", "dashboard", "support", "docs",
    "custom",
]


def _load_wordlist(path: str) -> list[str]:
    if path and Path(path).exists():
        return [l.strip() for l in Path(path).read_text().splitlines() if l.strip()]
    return FALLBACK_WORDLIST


def _check(sub: str, domain: str):
    fqdn = f"{sub}.{domain}"
    try:
        return fqdn, socket.gethostbyname(fqdn)
    except socket.gaierror:
        return None


def run():
    domain = console.input("[cyan]Domain (e.g. example.com): [/cyan]").strip()
    if not domain:
        console.print("[red]No domain given.[/red]")
        return

    wordlist_path = console.input("[cyan]Custom wordlist path (blank = built-in): [/cyan]").strip()
    threads_str = console.input("[cyan]Threads (default 200): [/cyan]").strip() or "200"

    try:
        threads = int(threads_str)
    except ValueError:
        console.print("[red]Invalid thread count.[/red]")
        return

    wordlist = _load_wordlist(wordlist_path)
    console.print(f"\n[*] Testing {len(wordlist)} candidates against {domain}\n")

    found = []
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(_check, sub, domain) for sub in wordlist]
        for fut in as_completed(futures):
            result = fut.result()
            if result:
                found.append(result)

    if not found:
        console.print("[yellow]No subdomains found.[/yellow]")
        return

    table = Table(title=f"Subdomains of {domain}")
    table.add_column("Subdomain", style="cyan")
    table.add_column("IP", style="green")
    for fqdn, ip in sorted(found):
        table.add_row(fqdn, ip)

    console.print(table)
    console.print(f"[bold green]{len(found)} subdomain(s) found.[/bold green]")
