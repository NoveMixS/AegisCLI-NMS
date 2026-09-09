"""
tools/audit.py — Local system security audit (Linux-focused), interactive.
"""
import os
import platform
import stat
import subprocess
from rich.console import Console

console = Console()

description = "Local system security audit: weak permissions & listening services"


def _world_writable(paths: list[str]) -> list[str]:
    findings = []
    for path in paths:
        if not os.path.exists(path):
            continue
        for root, dirs, files in os.walk(path):
            for name in files:
                fpath = os.path.join(root, name)
                try:
                    if os.stat(fpath).st_mode & stat.S_IWOTH:
                        findings.append(fpath)
                except (PermissionError, FileNotFoundError):
                    continue
            dirs[:] = dirs[:5]
    return findings[:50]


def _listening_ports() -> list[str]:
    try:
        out = subprocess.run(["ss", "-tulnp"], capture_output=True, text=True, timeout=5)
        return out.stdout.strip().splitlines()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ["ss command unavailable."]


def run():
    system = platform.system()
    console.print(f"[*] Auditing [bold]{system} {platform.release()}[/bold]\n")

    if system != "Linux":
        console.print("[yellow]Full audit currently supports Linux only.[/yellow]")
        return

    paths_str = console.input("[cyan]Paths to scan, space-separated (default /tmp /var/tmp): [/cyan]").strip()
    paths = paths_str.split() if paths_str else ["/tmp", "/var/tmp"]

    console.print("\n[bold]== World-writable files ==[/bold]")
    ww = _world_writable(paths)
    if ww:
        for f in ww:
            console.print(f"[red]  [!] {f}[/red]")
    else:
        console.print("  None found.")

    console.print("\n[bold]== Listening services (ss -tulnp) ==[/bold]")
    for line in _listening_ports():
        console.print(f"  {line}")
