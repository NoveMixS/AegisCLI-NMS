"""
nmap module — lightweight TCP port scanner mimicking nmap's flag style.

Usage:
    aegis nmap <target> [-p PORTS] [-t THREADS] [--timeout SECONDS]

Examples:
    aegis nmap google.com
    aegis nmap -p 80,443 google.com
    aegis nmap -p 1-1000 -t 300 10.10.10.5
"""
import argparse
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

NAME = "nmap"
DESCRIPTION = "Fast TCP port scanner (nmap-style flags)."

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


def _scan_one(ip: str, port: int, timeout: float) -> tuple[int, bool]:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        return port, s.connect_ex((ip, port)) == 0


def run(argv: list[str]) -> None:
    parser = argparse.ArgumentParser(prog="aegis nmap", add_help=True)
    parser.add_argument("target", help="Hostname or IP address")
    parser.add_argument("-p", "--ports", default="1-1000",
                         help="Port(s): '80,443' or '1-1000' (default: 1-1000)")
    parser.add_argument("-t", "--threads", type=int, default=200,
                         help="Concurrent scan threads (default: 200)")
    parser.add_argument("--timeout", type=float, default=1.0,
                         help="Per-port timeout in seconds (default: 1.0)")
    args = parser.parse_args(argv)

    try:
        ip = socket.gethostbyname(args.target)
    except socket.gaierror as e:
        print(f"[!] Could not resolve {args.target}: {e}")
        return

    ports = _parse_ports(args.ports)
    print(f"[*] Scanning {args.target} ({ip}) — {len(ports)} ports, {args.threads} threads\n")

    open_ports = []
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = [executor.submit(_scan_one, ip, p, args.timeout) for p in ports]
        for fut in as_completed(futures):
            port, is_open = fut.result()
            if is_open:
                open_ports.append(port)

    if not open_ports:
        print("[-] No open ports found.")
        return

    print(f"PORT     STATE  SERVICE")
    for port in sorted(open_ports):
        service = COMMON_SERVICES.get(port, "unknown")
        print(f"{port:<8} open   {service}")

    print(f"\n[+] {len(open_ports)} open port(s) found.")
