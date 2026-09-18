#!/usr/bin/env python3
"""DNS Reconnaissance tool for AegisCLI."""

from datetime import datetime
import dns.resolver
import dns.zone
import dns.query
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

description = "DNS records enumerator (A, AAAA, MX, TXT, NS, SOA, CNAME, SRV)"
__version__ = "1.0"
__author__  = "Md Siyam Mahmud"
__category__ = "Recon"

SCHEMA = {
    "action": {"type": "choice", "choices": ["enum", "json"], "default": "enum"},
    "domain": {"type": "string", "required": True},
    "zone_transfer": {"type": "bool", "default": True},
}

RECORD_TYPES = ["A", "AAAA", "MX", "TXT", "NS", "SOA", "CNAME", "SRV", "CAA"]
FALLBACK_RESOLVERS = ["1.1.1.1", "8.8.8.8", "9.9.9.9"]


def _clean_domain(domain):
    return domain.strip().lower().replace("https://", "").replace("http://", "").split("/")[0]


def _query_record(resolver, domain, rtype):
    try:
        answers = resolver.resolve(domain, rtype)
        return [str(r) for r in answers]
    except Exception:
        return []


def _try_zone_transfer(nameserver, domain):
    try:
        zone = dns.zone.from_xfr(dns.query.xfr(nameserver, domain, timeout=5))
        records = []
        for name, node in zone.nodes.items():
            for rdataset in node.rdatasets:
                for rdata in rdataset:
                    records.append(f"{name}.{domain} {rdataset.rdtype} {rdata}")
        return {"nameserver": nameserver, "ok": True, "records": records[:100]}
    except Exception as e:
        return {"nameserver": nameserver, "ok": False, "error": str(e)[:100]}


def _action_enum(domain, zone_transfer=True):
    domain = _clean_domain(domain)
    if not domain:
        return {"ok": False, "action": "enum", "error": "no domain"}

    resolver = dns.resolver.Resolver()
    resolver.timeout = 5
    resolver.lifetime = 8

    records = {}
    for rtype in RECORD_TYPES:
        answers = _query_record(resolver, domain, rtype)
        if answers:
            records[rtype] = answers

    if not records:
        for ns in FALLBACK_RESOLVERS:
            resolver.nameservers = [ns]
            for rtype in RECORD_TYPES:
                answers = _query_record(resolver, domain, rtype)
                if answers:
                    records[rtype] = answers
            if records:
                break

    if not records:
        return {"ok": False, "action": "enum", "domain": domain, "error": "No DNS records"}

    zt_results = []
    if zone_transfer and "NS" in records:
        for ns in records["NS"]:
            zt_results.append(_try_zone_transfer(ns.rstrip(".").lower(), domain))

    spf = [t for t in records.get("TXT", []) if "v=spf1" in t.lower()]

    return {
        "ok": True, "action": "enum", "domain": domain,
        "records": records, "zone_transfers": zt_results, "spf": spf,
        "queried_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }


def _render_result(result):
    if not result.get("ok"):
        console.print(f"[red]✖ {result.get('error')}[/red]")
        return
    console.print(Panel(
        f"[bold]Domain:[/bold] {result['domain']}\n"
        f"[bold]Record types:[/bold] {len(result['records'])}",
        title=f"🌐 DNS Recon · {result['domain']}", border_style="cyan"))
    for rtype in RECORD_TYPES:
        values = result["records"].get(rtype)
        if not values:
            continue
        t = Table(title=f"{rtype} Records", box=box.ROUNDED, show_header=False)
        t.add_column("Value", style="cyan")
        for v in values:
            t.add_row(v)
        console.print(t)
    if result.get("spf"):
        console.print("\n[bold]📧 SPF:[/bold]")
        for s in result["spf"]:
            console.print(f"  • [green]{s}[/green]")
    if result.get("zone_transfers"):
        console.print("\n[bold]🔓 Zone Transfer Attempts:[/bold]")
        for entry in result["zone_transfers"]:
            if entry.get("ok"):
                console.print(f"  [red]⚠️ {entry['nameserver']} — VULNERABLE![/red]")
            else:
                console.print(f"  [green]✓ {entry['nameserver']} — refused[/green]")


def _interactive():
    domain = console.input("[cyan]Domain to enumerate[/cyan] (e.g. example.com): ").strip()
    if not domain:
        return {"ok": False, "action": "enum", "error": "no domain"}
    zt = console.input("[cyan]Attempt zone transfer?[/cyan] [Y/n]: ").strip().lower() != "n"
    console.print(f"\n[dim]Enumerating DNS records for {domain}...[/dim]\n")
    result = _action_enum(domain, zt)
    _render_result(result)
    return result


def run(args=None):
    if args is None:
        return _interactive()
    action = (args.get("action") or "enum").lower()
    domain = args.get("domain", "")
    zt = bool(args.get("zone_transfer", True))
    if action in ("enum", "json"):
        result = _action_enum(domain, zt)
        if action == "json":
            console.print_json(data=result)
        else:
            _render_result(result)
        return result
    return {"ok": False, "action": action, "error": f"Unknown action: {action}"}