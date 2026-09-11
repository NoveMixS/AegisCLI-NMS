#!/usr/bin/env python3
"""
tools/nmap.py — Fast TCP port scanner for AegisCLI hub.

AegisCLI hub module. Exposes:
    description  : str
    SCHEMA       : dict  -- machine-readable manifest for the AI engine
    run(args)    : dict  -- structured results (also prints Rich table)

Behavior:
    * Called with no args  -> interactive prompts.
    * Called with a dict   -> fully non-interactive, no prompts.
    * args["json"] == True -> prints JSON, suppresses tables.

Returned dict shape:
    {
        "target":     "example.com",
        "resolved":   ["93.184.216.34"],
        "family":     "IPv4",
        "open_ports": [22, 80, 443],
        "services":   {22: "ssh", 80: "http", 443: "https"},
        "banners":    {22: "SSH-2.0-OpenSSH_8.9"},
        "scanned":    1000,
        "elapsed":    4.21,
    }
"""

import os
import sys
import json
import socket
import time
import argparse
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
description = "Fast multi-threaded TCP port scanner (IPv4/IPv6)"
__version__ = "2.0"
__author__ = "Md Siyam Mahmud"
__category__ = "Recon"

# ----------------------------------------------------------------------
# Machine-readable schema (for the future AI command engine)
# ----------------------------------------------------------------------
SCHEMA = {
    "name": "nmap",
    "description": "Scan TCP ports on a target host; identifies common services.",
    "args": {
        "target":  {"type": "string", "required": True,
                    "help": "Hostname or IP to scan."},
        "ports":   {"type": "string", "required": False, "default": "1-1000",
                    "help": "Port spec: '80,443' or '1-1000' or mixed '22,80,8000-8100'."},
        "threads": {"type": "int",    "required": False, "default": 200,
                    "help": "Max concurrent workers."},
        "timeout": {"type": "float",  "required": False, "default": 1.0,
                    "help": "Per-port connect timeout in seconds."},
        "banner":  {"type": "bool",   "required": False, "default": True,
                    "help": "Attempt to grab service banner on open ports."},
        "json":    {"type": "bool",   "required": False, "default": False,
                    "help": "Emit JSON instead of a Rich table."},
    },
    "returns": {
        "target":     "string",
        "resolved":   "list[ip]",
        "family":     "string",
        "open_ports": "list[int]",
        "services":   "dict[port -> service]",
        "banners":    "dict[port -> banner]",
        "scanned":    "int",
        "elapsed":    "float",
    },
}

# ----------------------------------------------------------------------
# Common service name map (port -> service)
# ----------------------------------------------------------------------
COMMON_SERVICES = {
    20: "ftp-data", 21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp",
    53: "dns", 67: "dhcp", 68: "dhcp", 69: "tftp",
    80: "http", 88: "kerberos", 110: "pop3", 111: "rpcbind",
    123: "ntp", 135: "msrpc", 137: "netbios-ns", 138: "netbios-dgm",
    139: "netbios-ssn", 143: "imap", 161: "snmp", 162: "snmptrap",
    179: "bgp", 194: "irc", 389: "ldap", 443: "https", 445: "smb",
    465: "smtps", 500: "isakmp", 514: "syslog", 515: "printer",
    543: "klogin", 544: "kshell", 548: "afp", 554: "rtsp",
    587: "smtp-submission", 631: "ipp", 636: "ldaps",
    646: "ldp", 873: "rsync", 990: "ftps", 993: "imaps", 995: "pop3s",
    1025: "nfs-or-iis", 1080: "socks", 1194: "openvpn",
    1433: "mssql", 1434: "mssql-browser", 1521: "oracle",
    1701: "l2tp", 1723: "pptp", 1883: "mqtt", 1900: "upnp",
    2049: "nfs", 2082: "cpanel", 2083: "cpanel-ssl",
    2181: "zookeeper", 2222: "ssh-alt", 2375: "docker",
    2376: "docker-ssl", 3000: "node/grafana", 3128: "squid",
    3260: "iscsi", 3306: "mysql", 3389: "rdp", 3690: "svn",
    4000: "icq", 4369: "epmd", 4443: "https-alt", 5000: "flask/upnp",
    5432: "postgresql", 5601: "kibana", 5672: "amqp",
    5900: "vnc", 5938: "teamviewer", 5984: "couchdb",
    6000: "x11", 6379: "redis", 6443: "k8s-api",
    6667: "irc", 7001: "weblogic", 7002: "weblogic-ssl",
    8000: "http-alt", 8008: "http-alt", 8080: "http-proxy",
    8081: "http-alt", 8086: "influxdb", 8088: "http-alt",
    8443: "https-alt", 8888: "http-alt", 8983: "solr",
    9000: "php-fpm", 9001: "tor", 9042: "cassandra",
    9090: "prometheus", 9092: "kafka", 9200: "elasticsearch",
    9300: "elasticsearch-cluster", 9418: "git",
    9999: "http-alt", 10000: "webmin", 11211: "memcached",
    27017: "mongodb", 27018: "mongodb", 50000: "sap",
    50070: "hadoop-namenode", 61616: "activemq",
}

# ----------------------------------------------------------------------
# Parsing helpers
# ----------------------------------------------------------------------
def _parse_ports(port_str: str) -> list[int]:
    """
    Parse a port spec like '80,443' or '1-1000' or '22,80,8000-8100'
    into a sorted, deduplicated list of ints.
    """
    ports: set[int] = set()
    for part in port_str.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_s, end_s = part.split("-", 1)
            start, end = int(start_s), int(end_s)
            if start > end:
                start, end = end, start
            ports.update(range(start, end + 1))
        else:
            ports.add(int(part))
    return sorted(p for p in ports if 1 <= p <= 65535)

# ----------------------------------------------------------------------
# DNS resolution (IPv4 + IPv6 via getaddrinfo)
# ----------------------------------------------------------------------
def _resolve(target: str):
    """
    Return (list_of_ips, family_label) or (None, None) on failure.
    Tries both IPv4 and IPv6 if the OS returns them.
    """
    try:
        infos = socket.getaddrinfo(target, None, proto=socket.IPPROTO_TCP)
    except socket.gaierror:
        return None, None

    v4, v6 = [], []
    for info in infos:
        family, _, _, _, sockaddr = info
        ip = sockaddr[0]
        if family == socket.AF_INET and ip not in v4:
            v4.append(ip)
        elif family == socket.AF_INET6 and ip not in v6:
            v6.append(ip)

    if v4:
        return v4, "IPv4"
    if v6:
        return v6, "IPv6"
    return None, None

# ----------------------------------------------------------------------
# Port scan
# ----------------------------------------------------------------------
def _scan_one(ip: str, port: int, timeout: float, family: int) -> bool:
    """Try TCP connect to (ip, port). Return True if open, False otherwise."""
    try:
        with socket.socket(family, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            return s.connect_ex((ip, port)) == 0
    except Exception:
        return False

# ----------------------------------------------------------------------
# Banner grab (best-effort, short timeout)
# ----------------------------------------------------------------------
def _grab_banner(ip: str, port: int, family: int, timeout: float = 1.5) -> str | None:
    """
    Try to read a short banner from an open port.
    Many services won't send anything until they receive input, so this is
    best-effort. For HTTP-ish ports we send a HEAD request to trigger a reply.
    """
    try:
        with socket.socket(family, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((ip, port))

            # For HTTP-ish ports, send a minimal HEAD request
            if port in (80, 8000, 8008, 8080, 8081, 8088, 8888, 9999, 3000, 5000):
                try:
                    s.sendall(b"HEAD / HTTP/1.0\r\nHost: " + ip.encode() + b"\r\n\r\n")
                except Exception:
                    pass

            data = s.recv(256)
            if not data:
                return None
            # Decode; strip control chars; keep it to one line
            text = data.decode("utf-8", errors="replace").strip()
            text = text.splitlines()[0] if text else ""
            return text[:120] if text else None
    except Exception:
        return None

# ----------------------------------------------------------------------
# Public scan orchestrator
# ----------------------------------------------------------------------
def _scan(ip: str, ports: list[int], threads: int, timeout: float,
          family: int, grab_banner: bool, show_progress: bool):
    """Return (open_ports, banners)."""
    open_ports: list[int] = []
    banners: dict[int, str] = {}

    if show_progress:
        with Progress(
            SpinnerColumn(),
            TextColumn("[cyan]Scanning ports..."),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("scan", total=len(ports))
            with ThreadPoolExecutor(max_workers=threads) as pool:
                futures = {pool.submit(_scan_one, ip, p, timeout, family): p
                           for p in ports}
                for fut in as_completed(futures):
                    port = futures[fut]
                    if fut.result():
                        open_ports.append(port)
                    progress.advance(task)
    else:
        with ThreadPoolExecutor(max_workers=threads) as pool:
            futures = {pool.submit(_scan_one, ip, p, timeout, family): p
                       for p in ports}
            for fut in as_completed(futures):
                port = futures[fut]
                if fut.result():
                    open_ports.append(port)

    open_ports.sort()

    # Banner grabbing is done sequentially to avoid exhausting sockets
    if grab_banner and open_ports:
        for port in open_ports:
            b = _grab_banner(ip, port, family)
            if b:
                banners[port] = b

    return open_ports, banners

# ----------------------------------------------------------------------
# Interactive prompts
# ----------------------------------------------------------------------
def _prompt_inputs():
    target = console.input("[cyan]Target (host or IP): [/cyan]").strip()
    if not target:
        console.print("[red]No target given.[/red]")
        return None

    port_str = console.input("[cyan]Ports (default 1-1000): [/cyan]").strip() or "1-1000"
    threads_str = console.input("[cyan]Threads (default 200): [/cyan]").strip() or "200"
    timeout_str = console.input("[cyan]Timeout per port sec (default 1.0): [/cyan]").strip() or "1.0"
    banner_str = console.input("[cyan]Grab service banners? (y/N): [/cyan]").strip().lower()
    grab_banner = banner_str in ("y", "yes")

    try:
        threads = int(threads_str)
        timeout = float(timeout_str)
        ports = _parse_ports(port_str)
    except ValueError as e:
        console.print(f"[red]Invalid input: {e}[/red]")
        return None

    return {
        "target": target,
        "ports": port_str,
        "threads": threads,
        "timeout": timeout,
        "banner": grab_banner,
        "json": False,
        "_parsed_ports": ports,
    }

# ----------------------------------------------------------------------
# Public entry point
# ----------------------------------------------------------------------
def run(args: dict | None = None) -> dict:
    """
    Run a TCP port scan.

    Interactive when args is None; otherwise non-interactive using the
    provided dict. Recognized keys: target, ports, threads, timeout,
    banner, json.
    """
    empty = {
        "target": None, "resolved": [], "family": None,
        "open_ports": [], "services": {}, "banners": {},
        "scanned": 0, "elapsed": 0.0,
    }

    if args is None:
        args = _prompt_inputs()
        if not args:
            return empty

    target = (args.get("target") or "").strip()
    if not target:
        console.print("[red]No target given.[/red]")
        return empty

    emit_json = bool(args.get("json", False))
    grab_banner = bool(args.get("banner", True))

    # Parse ports (or reuse pre-parsed list from interactive path)
    try:
        ports = args.get("_parsed_ports") or _parse_ports(args.get("ports", "1-1000"))
    except (ValueError, TypeError) as e:
        console.print(f"[red]Invalid port spec: {e}[/red]")
        return empty

    threads = int(args.get("threads", 200))
    timeout = float(args.get("timeout", 1.0))

    # Resolve
    ips, family_label = _resolve(target)
    if not ips:
        console.print(f"[red]Could not resolve {target}[/red]")
        return empty

    ip = ips[0]
    family = socket.AF_INET if family_label == "IPv4" else socket.AF_INET6

    if not emit_json:
        console.print(
            f"\n[*] Scanning [bold]{target}[/bold] ({ip}, {family_label}) — "
            f"{len(ports)} ports, {threads} threads, {timeout}s timeout\n"
        )

    start = time.time()
    open_ports, banners = _scan(
        ip, ports, threads, timeout, family,
        grab_banner=grab_banner,
        show_progress=not emit_json,
    )
    elapsed = time.time() - start

    services = {p: COMMON_SERVICES.get(p, "unknown") for p in open_ports}

    result = {
        "target": target,
        "resolved": ips,
        "family": family_label,
        "open_ports": open_ports,
        "services": services,
        "banners": banners,
        "scanned": len(ports),
        "elapsed": round(elapsed, 2),
    }

    # Output
    if emit_json:
        print(json.dumps(result, indent=2))
    else:
        if not open_ports:
            console.print("[yellow]No open ports found.[/yellow]")
        else:
            table = Table(title=f"Open ports on {target} ({ip})")
            table.add_column("Port", style="cyan", justify="right")
            table.add_column("Service", style="green")
            table.add_column("Banner", style="dim")
            for port in open_ports:
                table.add_row(
                    str(port),
                    services[port],
                    banners.get(port, "")[:60],
                )
            console.print(table)
            console.print(
                f"[bold green]{len(open_ports)} open port(s) found "
                f"in {elapsed:.1f}s.[/bold green]"
            )

    return result

# ----------------------------------------------------------------------
# Standalone entry point
#
# NOTE: The hub owns the "press enter to return" pause. This block only
# runs when the file is executed directly (python tools/nmap.py).
# ----------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AegisCLI TCP port scanner")
    parser.add_argument("target", nargs="?", help="Host or IP")
    parser.add_argument("-p", "--ports", default="1-1000",
                        help="Port spec, e.g. '22,80,443' or '1-1000'")
    parser.add_argument("-t", "--threads", type=int, default=200)
    parser.add_argument("--timeout", type=float, default=1.0)
    parser.add_argument("--no-banner", action="store_true",
                        help="Skip banner grabbing")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    opts = parser.parse_args()

    if opts.target:
        run({
            "target": opts.target,
            "ports": opts.ports,
            "threads": opts.threads,
            "timeout": opts.timeout,
            "banner": not opts.no_banner,
            "json": opts.json,
        })
        if not opts.json:
            input("\nPress Enter to exit...")
    else:
        run()
        input("\nPress Enter to exit...")