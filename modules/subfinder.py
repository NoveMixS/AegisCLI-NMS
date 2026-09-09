"""
subfinder module — DNS brute-force subdomain discovery.

Usage:
    aegis subfinder <domain> [-w WORDLIST] [-t THREADS]

Examples:
    aegis subfinder google.com
    aegis subfinder -w mylist.txt -t 300 example.com
"""
import argparse
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

NAME = "subfinder"
DESCRIPTION = "DNS brute-force subdomain enumeration."

FALLBACK_WORDLIST = [
    "www", "mail", "ftp", "api", "dev", "staging", "test", "admin",
    "portal", "vpn", "shop", "blog", "app", "cdn", "static", "beta",
    "ns1", "ns2", "smtp", "webmail", "dashboard", "support", "docs",
]


def _load_wordlist(path: str | None) -> list[str]:
    if path and Path(path).exists():
        return [l.strip() for l in Path(path).read_text().splitlines() if l.strip()]
    return FALLBACK_WORDLIST


def _check(sub: str, domain: str):
    fqdn = f"{sub}.{domain}"
    try:
        return fqdn, socket.gethostbyname(fqdn)
    except socket.gaierror:
        return None


def run(argv: list[str]) -> None:
    parser = argparse.ArgumentParser(prog="aegis subfinder", add_help=True)
    parser.add_argument("domain", help="Root domain, e.g. example.com")
    parser.add_argument("-w", "--wordlist", help="Path to custom wordlist file")
    parser.add_argument("-t", "--threads", type=int, default=200, help="Concurrent threads")
    args = parser.parse_args(argv)

    wordlist = _load_wordlist(args.wordlist)
    print(f"[*] Testing {len(wordlist)} candidates against {args.domain}\n")

    found = []
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = [executor.submit(_check, sub, args.domain) for sub in wordlist]
        for fut in as_completed(futures):
            result = fut.result()
            if result:
                found.append(result)

    if not found:
        print("[-] No subdomains found.")
        return

    for fqdn, ip in sorted(found):
        print(f"{fqdn:<30} {ip}")
    print(f"\n[+] {len(found)} subdomain(s) found.")
