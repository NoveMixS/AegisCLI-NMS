#!/usr/bin/env python3
"""
audit.py – Local system security audit: weak permissions & listening services
Cross-platform (Windows & Linux)
"""

import os
import platform
import stat
import subprocess
import socket
from rich.console import Console
from rich.table import Table

console = Console()

description = "Local system security audit: weak permissions & listening services"
__version__ = "1.1"
__author__ = "Md Siyam Mahmud"
__category__ = "System"

# ----------------------------------------------------------------------
# Helper: World-writable files (Linux only; Windows -> simple check)
# ----------------------------------------------------------------------
def _world_writable_linux(paths):
    """Find world-writable files on Linux (using os.walk)."""
    findings = []
    for path in paths:
        if not os.path.exists(path):
            continue
        try:
            for root, dirs, files in os.walk(path):
                for name in files:
                    fpath = os.path.join(root, name)
                    try:
                        # Check if 'other' has write permission
                        if os.stat(fpath).st_mode & stat.S_IWOTH:
                            findings.append(fpath)
                    except (PermissionError, FileNotFoundError):
                        continue
                # Limit subdirs to avoid long scans (optional)
                dirs[:] = dirs[:10]
        except PermissionError:
            continue
    return findings[:50]  # Show first 50

def _world_writable_windows(paths):
    """Simplified check on Windows: look for files with 'read-only' off? Actually, 
    Windows doesn't have a global world-writable concept. We'll check if file is 
    writable by 'Everyone' or if it's not read-only, but that's not accurate.
    We'll just return a warning message instead of scanning."""
    return ["[yellow]World-writable scan not supported on Windows. Use Linux for full audit.[/yellow]"]

def _world_writable(paths):
    """Cross-platform dispatcher."""
    if platform.system() == "Linux":
        return _world_writable_linux(paths)
    else:
        return _world_writable_windows(paths)

# ----------------------------------------------------------------------
# Helper: Listening ports (cross-platform)
# ----------------------------------------------------------------------
def _listening_ports():
    """Get listening TCP/UDP ports using platform-specific commands or Python."""
    system = platform.system()
    try:
        if system == "Linux":
            # Use ss (preferred) or netstat
            try:
                out = subprocess.run(["ss", "-tulnp"], capture_output=True, text=True, timeout=5)
                if out.returncode == 0:
                    return out.stdout.strip().splitlines()
            except:
                pass
            # Fallback to netstat
            try:
                out = subprocess.run(["netstat", "-tulnp"], capture_output=True, text=True, timeout=5)
                if out.returncode == 0:
                    return out.stdout.strip().splitlines()
            except:
                pass
            return ["No port listing command available (try installing net-tools)."]
        elif system == "Windows":
            # Use netstat -an
            try:
                out = subprocess.run(["netstat", "-an"], capture_output=True, text=True, timeout=5)
                if out.returncode == 0:
                    lines = out.stdout.strip().splitlines()
                    # Filter lines containing 'LISTENING' or 'UDP' with listening state
                    # On Windows, netstat -an shows TCP with state LISTENING, UDP with just port.
                    # We'll show all lines that have 'LISTENING' or 'UDP' and a port.
                    # Also filter out lines with no port (e.g., headers)
                    filtered = []
                    for line in lines:
                        if "LISTENING" in line or ("UDP" in line and ":" in line):
                            # Remove duplicate empty lines
                            if line.strip():
                                filtered.append(line)
                    return filtered if filtered else lines[:20]  # fallback to first 20
                else:
                    return ["netstat command failed."]
            except FileNotFoundError:
                # Try using PowerShell Get-NetTCPConnection (available on newer Windows)
                try:
                    ps_cmd = 'powershell -Command "Get-NetTCPConnection | Where-Object {$_.State -eq \'Listen\'} | Format-Table LocalAddress, LocalPort, State"'
                    out = subprocess.run(ps_cmd, capture_output=True, text=True, timeout=5, shell=True)
                    if out.returncode == 0:
                        return out.stdout.strip().splitlines()
                except:
                    pass
                return ["Could not retrieve listening ports. Please run as Administrator or install netstat."]
        else:
            return ["Unsupported OS for listening ports."]
    except Exception as e:
        return [f"Error listing ports: {str(e)}"]

# ----------------------------------------------------------------------
# Main audit function (interactive)
# ----------------------------------------------------------------------
def run():
    system = platform.system()
    console.print(f"[bold cyan]🔍 System Security Audit[/bold cyan]")
    console.print(f"[dim]OS: {system} {platform.release()}[/dim]\n")

    if system == "Linux":
        paths_str = console.input("[cyan]Paths to scan for world-writable files (space-separated, default /tmp /var/tmp): [/cyan]").strip()
        paths = paths_str.split() if paths_str else ["/tmp", "/var/tmp"]
    else:
        paths = []  # not used on Windows

    # ---- World-writable files ----
    console.print("[bold]== World-writable files ==[/bold]")
    if system == "Linux":
        findings = _world_writable(paths)
        if findings:
            for f in findings:
                console.print(f"[red]  [!] {f}[/red]")
        else:
            console.print("[green]  No world-writable files found.[/green]")
    else:
        console.print("[yellow]  World-writable scan is not supported on Windows.[/yellow]")

    # ---- Listening ports ----
    console.print("\n[bold]== Listening Services (TCP/UDP) ==[/bold]")
    port_lines = _listening_ports()
    if port_lines:
        # Display in a table if possible (for better readability)
        if system == "Linux" and len(port_lines) > 1:
            # Try to parse ss output into a table (optional)
            table = Table(title="Listening Ports")
            table.add_column("Data", style="white")
            for line in port_lines[:20]:  # show first 20 lines
                table.add_row(line)
            console.print(table)
        else:
            for line in port_lines[:20]:
                console.print(f"  {line}")
        if len(port_lines) > 20:
            console.print(f"[dim]... and {len(port_lines)-20} more lines[/dim]")
    else:
        console.print("[yellow]  No listening services found or could not retrieve.[/yellow]")

    console.print("\n[dim]Audit complete. Press Enter to return.[/dim]")
    input()

# ----------------------------------------------------------------------
# For standalone test
# ----------------------------------------------------------------------
if __name__ == "__main__":
    run()