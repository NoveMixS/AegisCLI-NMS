"""
audit module — local system security audit (Linux-focused).

Usage:
    aegis audit [-p PATHS...]

Examples:
    aegis audit
    aegis audit -p /tmp /var/tmp
"""
import argparse
import os
import platform
import stat
import subprocess

NAME = "audit"
DESCRIPTION = "Local system security audit: weak permissions & listening services."


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


def run(argv: list[str]) -> None:
    parser = argparse.ArgumentParser(prog="aegis audit", add_help=True)
    parser.add_argument("-p", "--paths", nargs="+", default=["/tmp", "/var/tmp"],
                         help="Paths to scan for world-writable files")
    args = parser.parse_args(argv)

    system = platform.system()
    print(f"[*] Auditing {system} {platform.release()}\n")

    if system != "Linux":
        print("[!] Full audit currently supports Linux only. Basic info only shown.")
        return

    print("== World-writable files ==")
    ww = _world_writable(args.paths)
    if ww:
        for f in ww:
            print(f"  [!] {f}")
    else:
        print("  None found.")

    print("\n== Listening services (ss -tulnp) ==")
    for line in _listening_ports():
        print(f"  {line}")
