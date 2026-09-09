#!/usr/bin/env python3
"""
AegisCLI core.

Usage:
    python aegis-core.py <tool> [tool-specific args...]

Examples:
    python aegis-core.py nmap -p 80,443 google.com
    python aegis-core.py nmap -p 1-1000 -t 300 10.10.10.5
    python aegis-core.py hash -i 5f4dcc3b5aa765d61d8327deb882cf99
    python aegis-core.py hash -c mypassword
    python aegis-core.py subfinder google.com
    python aegis-core.py audit

How it works:
    Every file in modules/ is a self-contained tool. Each module must
    define:
        NAME        - str, the command name used to invoke it
        DESCRIPTION - str, one-line help text
        run(argv)   - function that receives the remaining argv list
                      (everything after the tool name) and does its own
                      argument parsing + execution.

    Adding a new tool = drop a new file in modules/ that follows this
    contract. No changes needed here.
"""
import sys
import importlib.util
from pathlib import Path

MODULES_DIR = Path(__file__).resolve().parent / "modules"


def _discover_modules() -> dict[str, Path]:
    """Map tool name -> module file path, without importing everything eagerly."""
    tools = {}
    if not MODULES_DIR.exists():
        return tools
    for f in sorted(MODULES_DIR.glob("*.py")):
        if f.stem.startswith("_"):
            continue
        tools[f.stem] = f
    return tools


def _load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _print_help(tools: dict[str, Path]):
    print("AegisCLI — All-in-One Modular Security CLI\n")
    print("Usage: python aegis-core.py <tool> [args...]\n")
    print("Available tools:")
    for name, path in tools.items():
        try:
            mod = _load_module(path)
            desc = getattr(mod, "DESCRIPTION", "")
        except Exception as e:
            desc = f"(failed to load: {e})"
        print(f"  {name:<12} {desc}")
    print("\nRun 'python aegis-core.py <tool> -h' for tool-specific help.")


def main():
    tools = _discover_modules()

    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        _print_help(tools)
        return

    tool_name = sys.argv[1]
    tool_args = sys.argv[2:]

    if tool_name not in tools:
        print(f"[!] Unknown tool: '{tool_name}'")
        print(f"    Available: {', '.join(tools.keys())}")
        sys.exit(1)

    mod = _load_module(tools[tool_name])

    if not hasattr(mod, "run"):
        print(f"[!] Module '{tool_name}' is broken: missing run(argv) function.")
        sys.exit(1)

    try:
        mod.run(tool_args)
    except KeyboardInterrupt:
        print("\n[!] Interrupted.")
        sys.exit(130)


if __name__ == "__main__":
    main()
