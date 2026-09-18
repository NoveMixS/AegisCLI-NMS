#!/usr/bin/env python3
"""
WHOIS lookup tool for AegisCLI.
Queries domain registration data and returns structured results.
"""

import os
import re
import sys
import json
import socket
import subprocess
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

# Optional dependency — graceful fallback if not installed
try:
    import whois as _whois_lib
    _HAVE_WHOIS_LIB = True
except ImportError:
    _HAVE_WHOIS_LIB = False

console = Console()

description = "WHOIS domain lookup (registrar, dates, nameservers, contacts)"
__version__ = "1.0"
__author__  = "Md Siyam Mahmud"
__category__ = "Recon"

SCHEMA = {
    "action": {
        "type": "choice",
        "choices": ["lookup", "json"],
        "default": "lookup",
        "help": "Look up domain WHOIS info.",
    },
    "domain": {
        "type": "string",
        "required": True,
        "help": "Domain name (e.g. example.com).",
    },
}


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def _clean_domain(domain: str) -> str:
    """Strip protocol, path, and whitespace from a domain input."""
    domain = domain.strip().lower()
    domain = re.sub(r"^https?://", "", domain)
    domain = domain.split("/")[0]
    domain = domain.split(":")[0]
    return domain


def _validate_domain(domain: str) -> bool:
    """Basic domain validation."""
    if not domain or len(domain) > 253:
        return False
    # Allow letters, digits, hyphens, and dots
    pattern = re.compile(r"^([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}$")
    return bool(pattern.match(domain))


def _whois_via_lib(domain: str) -> dict:
    """Run WHOIS query using python-whois library."""
    try:
        w = _whois_lib.whois(domain)
        return {
            "ok": True,
            "source": "python-whois",
            "domain": domain,
            "registrar": _first(w.get("registrar")),
            "whois_server": _first(w.get("whois_server")),
            "creation_date": _first_date(w.get("creation_date")),
            "expiration_date": _first_date(w.get("expiration_date")),
            "updated_date": _first_date(w.get("updated_date")),
            "name_servers": _listify(w.get("name_servers")),
            "status": _listify(w.get("status")),
            "emails": _listify(w.get("emails")),
            "org": _first(w.get("org")),
            "country": _first(w.get("country")),
            "dnssec": _first(w.get("dnssec")),
        }
    except Exception as e:
        return {"ok": False, "error": f"WHOIS lookup failed: {e}"}


def _whois_via_cli(domain: str) -> dict:
    """Fallback: run system `whois` command if available."""
    try:
        result = subprocess.run(
            ["whois", domain],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode != 0:
            return {"ok": False, "error": result.stderr.strip() or "whois command failed"}
        return _parse_whois_text(result.stdout, domain)
    except FileNotFoundError:
        return {"ok": False, "error": "whois CLI not found and python-whois not installed"}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "whois command timed out"}
    except Exception as e:
        return {"ok": False, "error": f"CLI error: {e}"}


def _parse_whois_text(text: str, domain: str) -> dict:
    """Parse raw WHOIS text into a structured dict."""
    fields = {
        "registrar": r"Registrar:\s*(.+)",
        "whois_server": r"Whois Server:\s*(.+)",
        "creation_date": r"Creation Date:\s*(.+)",
        "expiration_date": r"(?:Registry Expiry Date|Expiration Date):\s*(.+)",
        "updated_date": r"Updated Date:\s*(.+)",
        "status": r"Domain Status:\s*(.+)",
        "dnssec": r"DNSSEC:\s*(.+)",
    }
    out = {"ok": True, "source": "whois-cli", "domain": domain}
    for key, pattern in fields.items():
        matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
        if matches:
            out[key] = matches[0].strip() if key not in ("status",) else [m.strip() for m in matches]

    ns = re.findall(r"Name Server:\s*(.+)", text, re.IGNORECASE)
    if ns:
        out["name_servers"] = [n.strip().lower() for n in ns]

    return out


def _first(val):
    """Return first item if val is a list, else val."""
    if isinstance(val, list):
        return val[0] if val else None
    return val


def _first_date(val):
    """Return first date as ISO string."""
    val = _first(val)
    if val is None:
        return None
    if isinstance(val, datetime):
        return val.isoformat(timespec="seconds")
    return str(val)


def _listify(val) -> list:
    """Ensure val is a list of unique, non-None strings."""
    if val is None:
        return []
    if not isinstance(val, list):
        val = [val]
    cleaned = []
    for v in val:
        if v is None:
            continue
        s = str(v).strip().lower()
        if s and s not in cleaned:
            cleaned.append(s)
    return cleaned


def _resolve_ips(domain: str) -> list:
    """Resolve domain to IPs (A/AAAA)."""
    try:
        infos = socket.getaddrinfo(domain, None)
        ips = sorted({info[4][0] for info in infos})
        return ips
    except Exception:
        return []


# ----------------------------------------------------------------------
# Action
# ----------------------------------------------------------------------
def _action_lookup(domain: str) -> dict:
    domain = _clean_domain(domain)
    if not _validate_domain(domain):
        return {
            "ok": False,
            "action": "lookup",
            "error": f"Invalid domain: {domain}",
        }

    # Try python-whois first, then CLI fallback
    if _HAVE_WHOIS_LIB:
        result = _whois_via_lib(domain)
    else:
        result = _whois_via_cli(domain)

    if not result.get("ok"):
        return result

    # Add resolved IPs
    result["resolved_ips"] = _resolve_ips(domain)
    result["action"] = "lookup"
    result["queried_at"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    return result


# ----------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------
def _render_result(result: dict):
    if not result.get("ok"):
        console.print(f"[red]✖ WHOIS lookup failed: {result.get('error')}[/red]")
        return

    domain = result.get("domain", "?")
    table = Table(title=f"🔎 WHOIS · {domain}", box=box.ROUNDED, show_header=False)
    table.add_column("Field", style="cyan", width=18)
    table.add_column("Value", style="white")

    rows = [
        ("Registrar",       result.get("registrar")),
        ("WHOIS Server",    result.get("whois_server")),
        ("Created",         result.get("creation_date")),
        ("Expires",         result.get("expiration_date")),
        ("Updated",         result.get("updated_date")),
        ("Organization",    result.get("org")),
        ("Country",         result.get("country")),
        ("DNSSEC",          result.get("dnssec")),
        ("Resolved IPs",    ", ".join(result.get("resolved_ips") or []) or None),
        ("Source",          result.get("source")),
    ]
    for key, val in rows:
        if val:
            table.add_row(key, str(val))

    # Expiry warning
    expires = result.get("expiration_date")
    if expires:
        try:
            exp_dt = datetime.fromisoformat(expires.replace("Z", ""))
            days_left = (exp_dt - datetime.utcnow()).days
            if days_left < 30:
                table.add_row("⚠️  Warning", f"[red]Expires in {days_left} days![/red]")
            elif days_left < 90:
                table.add_row("ℹ️  Note", f"[yellow]Expires in {days_left} days[/yellow]")
        except Exception:
            pass

    console.print(table)

    # Name servers
    ns = result.get("name_servers") or []
    if ns:
        console.print("\n[bold]Name Servers:[/bold]")
        for n in ns:
            console.print(f"  • {n}")

    # Status codes
    status = result.get("status") or []
    if status:
        console.print("\n[bold]Domain Status:[/bold]")
        for s in status:
            console.print(f"  • {s}")

    # Emails
    emails = result.get("emails") or []
    if emails:
        console.print("\n[bold]Contact Emails:[/bold]")
        for e in emails:
            console.print(f"  • [cyan]{e}[/cyan]")


# ----------------------------------------------------------------------
# Interactive
# ----------------------------------------------------------------------
def _interactive() -> dict:
    domain = console.input("[cyan]Domain to look up[/cyan] (e.g. example.com): ").strip()
    if not domain:
        console.print("[yellow]No domain given.[/yellow]")
        return {"ok": False, "action": "lookup", "error": "no domain given"}

    console.print(f"\n[dim]Querying WHOIS for {domain}...[/dim]\n")
    result = _action_lookup(domain)
    _render_result(result)
    return result


# ----------------------------------------------------------------------
# Public entry point
# ----------------------------------------------------------------------
def run(args: dict | None = None) -> dict:
    if args is None:
        return _interactive()

    action = (args.get("action") or "lookup").lower()
    domain = args.get("domain", "")

    if action in ("lookup", "json"):
        result = _action_lookup(domain)
        if action == "json":
            console.print_json(data=result)
        else:
            _render_result(result)
        return result

    return {"ok": False, "action": action, "error": f"Unknown action: {action}"}