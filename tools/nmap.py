"""
tools/nmap.py — Fast TCP port scanner, interactive version for aegis-hub.
Loaded automatically by aegis-hub.py. Must expose: description, run()
"""
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.console import Console
from rich.table import Table

console = Console()

description = "Fast multi-threaded TCP port scanner"

COMMON_SERVICES = {
    21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp", 53: "dns",
    80: "http", 110: "pop3", 111: "rpcbind", 135: "msrpc",
    139: "netbios-ssn", 143: "imap", 443: "https", 445: "microsoft-ds",
    3306: "mysql", 3389: "rdp", 5432: "postgresql", 8080: "http-proxy",
}


def _parse_ports(port_str: str) -> list[int]:
    ports = []
    for part in port_str.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-")
            ports.extend(range(int(start), int(end) + 1))
        else:
            ports.append(int(part))
    return sorted(set(ports))


def _scan_one(ip: str, port: int, timeout: float):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        return port, s.connect_ex((ip, port)) == 0


def run():
    target = console.input("[cyan]Target (host or IP): [/cyan]").strip()
    if not target:
        console.print("[red]No target given.[/red]")
        return

    port_str = console.input("[cyan]Ports (default 1-1000): [/cyan]").strip() or "1-1000"
    threads_str = console.input("[cyan]Threads (default 200): [/cyan]").strip() or "200"
    timeout_str = console.input("[cyan]Timeout per port sec (default 1.0): [/cyan]").strip() or "1.0"

    try:
        threads = int(threads_str)
        timeout = float(timeout_str)
        ports = _parse_ports(port_str)
    except ValueError as e:
        console.print(f"[red]Invalid input: {e}[/red]")
        return

    try:
        ip = socket.gethostbyname(target)
    except socket.gaierror as e:
        console.print(f"[red]Could not resolve {target}: {e}[/red]")
        return

    console.print(f"\n[*] Scanning [bold]{target}[/bold] ({ip}) — {len(ports)} ports, {threads} threads\n")

    open_ports = []
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(_scan_one, ip, p, timeout) for p in ports]
        for fut in as_completed(futures):
            port, is_open = fut.result()
            if is_open:
                open_ports.append(port)

    if not open_ports:
        console.print("[yellow]No open ports found.[/yellow]")
        return

    table = Table(title=f"Open ports on {target}")
    table.add_column("Port", style="cyan")
    table.add_column("Service", style="green")
    for port in sorted(open_ports):
        table.add_row(str(port), COMMON_SERVICES.get(port, "unknown"))

    console.print(table)
    console.print(f"[bold green]{len(open_ports)} open port(s) found.[/bold green]")
