#!/usr/bin/env python3
"""
AegisCLI Hub v2.4
Modern security toolkit hub with animations and rich UI.
"""

import os
import sys

# ======================================================================
# Windows UTF-8 + ANSI fix — MUST run BEFORE importing Rich
# ======================================================================
if os.name == "nt":
    try:
        os.system("chcp 65001 >nul 2>&1")
    except Exception:
        pass
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["PYTHONUTF8"] = "1"
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        kernel32.SetConsoleOutputCP(65001)
        kernel32.SetConsoleCP(65001)
    except Exception:
        pass

# Now safe to import Rich
import json
import time
import argparse
import importlib.util
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.rule import Rule
from rich.text import Text
from rich.align import Align
from rich.live import Live
from rich.spinner import Spinner
from rich import box

# ======================================================================
# Constants
# ======================================================================
CONFIG_FILE  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aegis_config.json")
LOG_FILE     = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aegis.log")
HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aegis_history.txt")

VERSION = "2.4"

# Force Rich to emit ANSI + truecolor even in weird terminals
console = Console(force_terminal=True, color_system="truecolor", legacy_windows=False)

_LAST_RESULT: dict = {}

# Color palette
C = {
    "primary":   "bright_cyan",
    "secondary": "bright_magenta",
    "accent":    "bright_yellow",
    "success":   "bright_green",
    "warning":   "orange1",
    "danger":    "bright_red",
    "muted":     "grey54",
    "text":      "white",
    "link":      "bright_blue",
}

CATEGORY_STYLE = {
    "Recon":        ("🔍", "cyan"),
    "Web":          ("🌐", "magenta"),
    "Cryptography": ("🔐", "yellow"),
    "System":       ("⚙️",  "green"),
    "Network":      ("📡", "blue"),
    "General":      ("📦", "white"),
}

TOOL_ALIASES = {
    "audit":        ["au", "aud"],
    "dirbrute":     ["db", "dir"],
    "dnsrecon":     ["dr", "dns"],
    "hash":         ["h", "ha"],
    "http_headers": ["hh", "hdr", "headers"],
    "httpx_probe":  ["hp", "httpx", "probe"],
    "nmap":         ["nm", "port"],
    "sslscan":      ["ss", "ssl"],
    "subfinder":    ["sf", "sub"],
    "whois":        ["w", "who"],
}

DEFAULT_CONFIG = {
    "last_tool": None,
    "auto_clear": True,
    "log_errors": True,
    "favorites": [],
    "animations": True,
}

BANNER_ART = """
  █████╗ ███████╗ ██████╗ ██╗███████╗     ██████╗██╗     ██╗
 ██╔══██╗██╔════╝██╔════╝ ██║██╔════╝    ██╔════╝██║     ██║
 ███████║█████╗  ██║  ███╗██║███████╗    ██║     ██║     ██║
 ██╔══██║██╔══╝  ██║   ██║██║╚════██║    ██║     ██║     ██║
 ██║  ██║███████╗╚██████╔╝██║███████║    ╚██████╗███████╗██║
 ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝╚══════╝     ╚═════╝╚══════╝╚═╝
"""


# ======================================================================
# Animations
# ======================================================================
def is_animated(config):
    return config.get("animations", True)


def boot_animation(config):
    """Boot sequence with proper markup handling."""
    if not is_animated(config):
        return

    console.clear()
    console.print()

    # Use explicit text + style — no markup inside Text object
    lines = [
        ("⚔️  AegisCLI v" + VERSION, f"bold {C['primary']}", 0.015),
        ("→ Initializing hub...", C['muted'], 0.008),
        ("→ Loading modules...", C['muted'], 0.008),
        ("→ Ready.", C['success'], 0.008),
    ]

    for text_content, style, delay in lines:
        for ch in text_content:
            try:
                console.print(ch, end="", style=style, highlight=False, soft_wrap=True)
            except Exception:
                sys.stdout.write(ch)
                sys.stdout.flush()
            time.sleep(delay)
        console.print()
        time.sleep(0.05)

    time.sleep(0.3)


def loader_spinner(message, duration=1.0, config=None):
    """Show a spinner with a message."""
    if config and not is_animated(config):
        console.print(f"[{C['muted']}]{message}[/{C['muted']}]")
        return
    try:
        with Live(Spinner("dots", text=f"[{C['primary']}] {message}[/{C['primary']}]"),
                  console=console, refresh_per_second=12, transient=True):
            time.sleep(duration)
    except Exception:
        console.print(f"[{C['muted']}]{message}[/{C['muted']}]")
        time.sleep(duration)


def success_toast(message):
    console.print(f"[{C['success']}]✓[/{C['success']}] {message}")


# ======================================================================
# Logger & History
# ======================================================================
def log_error(message):
    if not load_config().get("log_errors", True):
        return
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{ts}] {message}\n")
    except Exception:
        pass


def add_history(command):
    try:
        history = []
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = [l.strip() for l in f.readlines() if l.strip()]
        history.append(command)
        if len(history) > 50:
            history = history[-50:]
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(history) + "\n")
    except Exception:
        pass


def get_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return [l.strip() for l in f.readlines() if l.strip()]
        except Exception:
            return []
    return []


# ======================================================================
# Config
# ======================================================================
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                for k, v in DEFAULT_CONFIG.items():
                    cfg.setdefault(k, v)
                return cfg
        except Exception:
            return DEFAULT_CONFIG.copy()
    save_config(DEFAULT_CONFIG)
    return DEFAULT_CONFIG.copy()


def save_config(config):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
    except Exception:
        pass


# ======================================================================
# Tool Loader
# ======================================================================
def load_tools(config=None):
    tools = {}
    tools_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools")
    if not os.path.exists(tools_dir):
        os.makedirs(tools_dir)
        console.print(f"[{C['warning']}]📁 Created tools/ directory.[/{C['warning']}]")
        return tools

    for filename in sorted(os.listdir(tools_dir)):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = filename[:-3]
            filepath = os.path.join(tools_dir, filename)
            try:
                spec = importlib.util.spec_from_file_location(module_name, filepath)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                if hasattr(module, "run") and hasattr(module, "description"):
                    tools[module_name] = {
                        "module":      module,
                        "description": module.description,
                        "version":     getattr(module, "__version__", "1.0"),
                        "author":      getattr(module, "__author__", "Unknown"),
                        "category":    getattr(module, "__category__", "General"),
                    }
            except Exception as e:
                err = f"Error loading {module_name}: {e}"
                console.print(f"[{C['danger']}]✖ {err}[/{C['danger']}]")
                log_error(err)
    return tools


def resolve_tool(choice, tools):
    """Number, full name, or short alias → tool name."""
    if not choice or not tools:
        return None
    choice_lower = choice.lower().strip()

    if choice_lower.isdigit():
        idx = int(choice_lower) - 1
        tool_list = list(tools.keys())
        if 0 <= idx < len(tool_list):
            return tool_list[idx]
        return None

    if choice_lower in tools:
        return choice_lower

    for tool_name, aliases in TOOL_ALIASES.items():
        if choice_lower in aliases and tool_name in tools:
            return tool_name

    matches = [t for t in tools if t.startswith(choice_lower)]
    if len(matches) == 1:
        return matches[0]

    return None


# ======================================================================
# Menu
# ======================================================================
def print_banner():
    # ASCII art
    banner_text = Text()
    banner_text.append(BANNER_ART, style=f"bold {C['primary']}")

    # Subtitle
    subtitle = Text()
    subtitle.append("  ⚔️  ", style=f"bold {C['accent']}")
    subtitle.append("AI-Powered Modular Security CLI Toolkit", style=f"bold {C['accent']}")
    console.print(Align.center(banner_text))
    console.print(Align.center(subtitle))
    console.print()

    # Author + version + links panel
    info_line1 = Text()
    info_line1.append("Version:  ", style=C['muted'])
    info_line1.append(f"v{VERSION}", style=f"bold {C['success']}")
    info_line1.append("     ·     ", style=C['muted'])
    info_line1.append("Author:  ", style=C['muted'])
    info_line1.append("Md Siyam Mahmud", style=f"bold {C['text']}")

    info_line2 = Text()
    info_line2.append("GitHub:  ", style=C['muted'])
    info_line2.append("@siyam201", style=f"bold {C['link']}")
    info_line2.append("     ·     ", style=C['muted'])
    info_line2.append("Org:  ", style=C['muted'])
    info_line2.append("@novemixs", style=f"bold {C['link']}")

    info_line3 = Text()
    info_line3.append("Repo:  ", style=C['muted'])
    info_line3.append("github.com/novemixs/AegisCLI-NMS", style=f"bold {C['link']}")

    # Panel with info
    from rich.panel import Panel
    info_content = Text()
    info_content.append_text(info_line1)
    info_content.append("\n")
    info_content.append_text(info_line2)
    info_content.append("\n")
    info_content.append_text(info_line3)

    console.print(Align.center(Panel(
        info_content,
        border_style=C['primary'],
        padding=(0, 2),
        width=80,
    )))


def display_menu(tools, config):
    if config.get("auto_clear", True):
        console.clear()

    print_banner()
    console.print()

    tool_count = len(tools)
    fav_count = len(config.get("favorites", []))
    last_tool = config.get("last_tool") or "—"

    status = Text()
    status.append("  ● ", style=C['success'])
    status.append(f"{tool_count}", style=f"bold {C['success']}")
    status.append(" tools", style=C['muted'])
    status.append("   ● ", style=C['accent'])
    status.append(f"{fav_count}", style=f"bold {C['accent']}")
    status.append(" favorites", style=C['muted'])
    status.append("   ● ", style=C['primary'])
    status.append(f"{last_tool}", style=f"bold {C['primary']}")
    status.append(" last used", style=C['muted'])

    console.print(status)
    console.print()

    if not tools:
        console.print(Panel(
            f"[{C['danger']}]No tools found in tools/ directory.[/{C['danger']}]",
            border_style=C['danger'], padding=(1, 2),
        ))
        return

    table = Table(
        show_header=True,
        header_style=f"bold {C['primary']}",
        box=box.ROUNDED,
        border_style=C['muted'],
        padding=(0, 1),
    )
    table.add_column("#",           style=C['muted'],  width=3,  justify="right")
    table.add_column("",            width=2,  justify="center")
    table.add_column("Tool",        style=f"bold {C['text']}", no_wrap=True, width=14)
    table.add_column("Description", style=C['text'],   width=44)
    table.add_column("Ver",         style=C['success'], width=5, justify="center")
    table.add_column("Category",    width=15, justify="center")
    table.add_column("Alias",       style=C['muted'], width=6, justify="center")

    tool_list = list(tools.keys())
    favs = config.get("favorites", [])

    for i, name in enumerate(tool_list, 1):
        cat = tools[name]["category"]
        icon, color = CATEGORY_STYLE.get(cat, ("•", "white"))
        fav_star = f"[{C['accent']}]★[/{C['accent']}]" if name in favs else " "
        aliases = TOOL_ALIASES.get(name, [])
        short = aliases[0] if aliases else "—"

        table.add_row(
            str(i),
            fav_star,
            f"[{color}]{name}[/{color}]",
            tools[name]["description"],
            tools[name]["version"],
            f"[{color}]{icon} {cat}[/{color}]",
            short,
        )

    console.print(table)
    console.print()

    console.print(Rule(style=C['muted']))

    cmd1 = Text()
    cmd1.append("  ▶ ", style=f"bold {C['primary']}")
    cmd1.append("Run", style=f"bold {C['text']}")
    cmd1.append(": number, name, or alias", style=C['muted'])
    console.print(cmd1)

    cmd2 = Text()
    cmd2.append("  │  ", style=C['muted'])
    for c in ["reload", "info <tool>", "search <kw>", "favorite <tool>"]:
        cmd2.append(f"{c}  ", style=C['link'])
    console.print(cmd2)

    cmd3 = Text()
    cmd3.append("  │  ", style=C['muted'])
    for c in ["favlist", "history", "clear", "set", "config", "help", "exit"]:
        cmd3.append(f"{c}  ", style=C['link'])
    console.print(cmd3)
    console.print()


# ======================================================================
# Search / Favorites
# ======================================================================
def search_tools(tools, keyword):
    keyword = keyword.lower()
    matches = [(n, d) for n, d in tools.items()
               if keyword in n.lower() or keyword in d["description"].lower()]

    if not matches:
        console.print(Panel(
            f"[{C['warning']}]No tools matched '{keyword}'[/{C['warning']}]",
            border_style=C['warning'], padding=(0, 2),
        ))
        return

    table = Table(
        title=f"🔍  {len(matches)} match(es) for '{keyword}'",
        title_style=f"bold {C['primary']}",
        box=box.ROUNDED, border_style=C['muted'], padding=(0, 1),
    )
    table.add_column("Tool",        style=f"bold {C['text']}", width=16)
    table.add_column("Description", style=C['text'])
    table.add_column("Category",    width=16, justify="center")

    for name, data in matches:
        icon, color = CATEGORY_STYLE.get(data["category"], ("•", "white"))
        table.add_row(name, data["description"], f"[{color}]{icon} {data['category']}[/{color}]")
    console.print(table)


def toggle_favorite(config, tool_name, tools):
    if tool_name not in tools:
        console.print(f"[{C['danger']}]✖ Tool '{tool_name}' not found.[/{C['danger']}]")
        return config
    favs = config.get("favorites", [])
    if tool_name in favs:
        favs.remove(tool_name)
        console.print(f"[{C['warning']}]★ Removed '{tool_name}' from favorites.[/{C['warning']}]")
    else:
        favs.append(tool_name)
        console.print(f"[{C['success']}]★ Added '{tool_name}' to favorites.[/{C['success']}]")
    config["favorites"] = favs
    save_config(config)
    return config


def list_favorites(tools, config):
    favs = config.get("favorites", [])
    if not favs:
        console.print(f"[{C['muted']}]No favorites yet. Use: favorite <tool>[/{C['muted']}]")
        return
    table = Table(
        title="★  Favorites", title_style=f"bold {C['accent']}",
        box=box.ROUNDED, border_style=C['muted'],
    )
    table.add_column("Tool",        style=f"bold {C['text']}", width=16)
    table.add_column("Description", style=C['text'])
    for name in favs:
        if name in tools:
            table.add_row(name, tools[name]["description"])
        else:
            table.add_row(name, f"[{C['danger']}]not loaded[/{C['danger']}]")
    console.print(table)


# ======================================================================
# Config helpers
# ======================================================================
def config_set(config, key, value):
    if key not in config:
        console.print(f"[{C['danger']}]Unknown key '{key}'.[/{C['danger']}]")
        return config
    if isinstance(config[key], bool):
        if value.lower() in ("true", "1", "yes", "on"):
            value = True
        elif value.lower() in ("false", "0", "no", "off"):
            value = False
        else:
            console.print(f"[{C['danger']}]Use true/false.[/{C['danger']}]")
            return config
    elif isinstance(config[key], int):
        try:
            value = int(value)
        except Exception:
            console.print(f"[{C['danger']}]Invalid integer.[/{C['danger']}]")
            return config
    elif isinstance(config[key], list):
        console.print(f"[{C['danger']}]Use config file for lists.[/{C['danger']}]")
        return config
    config[key] = value
    save_config(config)
    success_toast(f"Config '{key}' = '{value}'")
    return config


def show_config(config):
    table = Table(
        title="⚙️  Configuration",
        title_style=f"bold {C['primary']}",
        box=box.ROUNDED, border_style=C['muted'],
    )
    table.add_column("Setting", style=f"bold {C['text']}", width=18)
    table.add_column("Value",   style=C['text'])
    for k, v in config.items():
        table.add_row(k, str(v))
    console.print(table)
    if Confirm.ask(f"[{C['warning']}]Reset to defaults?[/{C['warning']}]", default=False):
        save_config(DEFAULT_CONFIG)
        success_toast("Reset done.")


def show_tool_info(tools, tool_name):
    if tool_name not in tools:
        console.print(f"[{C['danger']}]✖ Tool '{tool_name}' not found.[/{C['danger']}]")
        return
    data = tools[tool_name]
    icon, color = CATEGORY_STYLE.get(data["category"], ("•", "white"))
    table = Table(
        title=f"{icon}  {tool_name}",
        title_style=f"bold {color}",
        box=box.ROUNDED, border_style=C['muted'], show_header=False,
    )
    table.add_column("Key",   style=C['muted'], width=14)
    table.add_column("Value", style=C['text'])
    table.add_row("Description", data["description"])
    table.add_row("Version",     data["version"])
    table.add_row("Author",      data["author"])
    table.add_row("Category",    f"[{color}]{data['category']}[/{color}]")
    table.add_row("Module Path", f"tools/{tool_name}.py")
    console.print(table)


# ======================================================================
# Tool Runner
# ======================================================================
def run_tool(tools, tool_name, config):
    if tool_name not in tools:
        console.print(f"[{C['danger']}]✖ Tool '{tool_name}' not found.[/{C['danger']}]")
        return
    info = tools[tool_name]
    icon, color = CATEGORY_STYLE.get(info["category"], ("•", "white"))

    console.print()
    console.print(Rule(
        f"[bold {color}]  {icon}  {tool_name}  [/bold {color}]"
        f"[{C['muted']}]v{info['version']}[/{C['muted']}]",
        style=C['muted'],
    ))
    console.print()

    if is_animated(config):
        loader_spinner(f"Launching {tool_name}...", duration=0.3, config=config)

    try:
        result = tools[tool_name]["module"].run()
        if isinstance(result, dict):
            _LAST_RESULT[tool_name] = result
    except KeyboardInterrupt:
        console.print(f"\n[{C['warning']}]⏹  Tool interrupted.[/{C['warning']}]")
    except Exception as e:
        err = f"Error in {tool_name}: {e}"
        console.print(f"[{C['danger']}]✖ {err}[/{C['danger']}]")
        log_error(err)

    console.print()
    console.print(Rule(style=C['muted']))
    console.input(f"[{C['muted']}]Press Enter to return to menu…[/{C['muted']}]")


# ======================================================================
# Main
# ======================================================================
def main():
    parser = argparse.ArgumentParser(description="AegisCLI — Modern Security Toolkit")
    parser.add_argument("--run",     help="Run a specific tool", metavar="TOOL")
    parser.add_argument("--list",    action="store_true", help="List all tools")
    parser.add_argument("--version", action="version", version=f"AegisCLI v{VERSION}")
    parser.add_argument("--no-anim", action="store_true", help="Disable animations")
    args = parser.parse_args()

    config = load_config()
    if args.no_anim:
        config["animations"] = False

    boot_animation(config)
    tools = load_tools(config)

    if args.list:
        if not tools:
            console.print(f"[{C['danger']}]No tools found.[/{C['danger']}]")
            return
        console.print(f"[bold {C['primary']}]Available Tools:[/bold {C['primary']}]")
        for name, data in tools.items():
            icon, color = CATEGORY_STYLE.get(data["category"], ("•", "white"))
            aliases = TOOL_ALIASES.get(name, [])
            alias_str = f" [{C['muted']}]({aliases[0]})[/{C['muted']}]" if aliases else ""
            console.print(
                f"  [{color}]{icon}[/{color}] [{color}]{name:<14}[/{color}]"
                f"{alias_str} [{C['muted']}]v{data['version']} {data['category']}[/{C['muted']}]"
            )
        return

    if args.run:
        run_tool(tools, args.run, config)
        return

    while True:
        display_menu(tools, config)

        last = config.get("last_tool")
        suffix = f" [{C['muted']}]({last})[/{C['muted']}]" if last and last in tools else ""
        try:
            choice = Prompt.ask(f"[bold {C['secondary']}]❯[/bold {C['secondary']}]{suffix}").strip()
        except (KeyboardInterrupt, EOFError):
            console.print()
            break

        if not choice:
            continue

        add_history(choice)
        low = choice.lower()

        if low in ("exit", "quit", "q", "0"):
            console.print()
            if is_animated(config):
                loader_spinner("Shutting down...", duration=0.3, config=config)
            console.print(Panel(
                f"[bold {C['success']}]Goodbye! Thanks for using AegisCLI.[/bold {C['success']}]\n"
                f"[{C['muted']}]github.com/NoveMixS/AegisCLI-NMS[/{C['muted']}]",
                border_style=C['success'], padding=(1, 3),
            ))
            sys.exit(0)

        if low == "reload":
            if is_animated(config):
                loader_spinner("Reloading tools...", duration=0.4, config=config)
            tools = load_tools(config)
            success_toast(f"Reloaded {len(tools)} tools.")
            console.input(f"[{C['muted']}]Press Enter…[/{C['muted']}]")
            continue

        if low == "help":
            console.print(Panel(
                f"[bold {C['primary']}]Navigation[/bold {C['primary']}]\n"
                f"  [{C['link']}]<number>[/{C['link']}] / [{C['link']}]<name>[/{C['link']}] / [{C['link']}]<alias>[/{C['link']}]  Run tool\n"
                f"  [{C['link']}]reload[/{C['link']}]  [{C['link']}]exit[/{C['link']}] / [{C['link']}]q[/{C['link']}]\n\n"
                f"[bold {C['primary']}]Discovery[/bold {C['primary']}]\n"
                f"  [{C['link']}]info <tool>[/{C['link']}]  [{C['link']}]search <kw>[/{C['link']}]  "
                f"[{C['link']}]favlist[/{C['link']}]  [{C['link']}]favorite <tool>[/{C['link']}]\n\n"
                f"[bold {C['primary']}]Session[/bold {C['primary']}]\n"
                f"  [{C['link']}]history[/{C['link']}]  [{C['link']}]clear[/{C['link']}]  "
                f"[{C['link']}]config[/{C['link']}]  [{C['link']}]set <k> <v>[/{C['link']}]",
                title="❓  Help", border_style=C['primary'], padding=(1, 2),
            ))
            console.input(f"[{C['muted']}]Press Enter…[/{C['muted']}]")
            continue

        if low == "clear":
            console.clear()
            continue

        if low == "history":
            hist = get_history()
            if not hist:
                console.print(f"[{C['muted']}]No history yet.[/{C['muted']}]")
            else:
                t = Table(title="Command History", title_style=f"bold {C['primary']}",
                          box=box.ROUNDED, border_style=C['muted'])
                t.add_column("#", style=C['muted'], width=4)
                t.add_column("Command", style=C['text'])
                for i, c in enumerate(hist, 1):
                    t.add_row(str(i), c)
                console.print(t)
            console.input(f"[{C['muted']}]Press Enter…[/{C['muted']}]")
            continue

        if low == "config":
            show_config(config)
            continue

        if low.startswith("set "):
            parts = choice.split(maxsplit=2)
            if len(parts) == 3:
                config = config_set(config, parts[1], parts[2])
            else:
                console.print(f"[{C['danger']}]Usage: set <key> <value>[/{C['danger']}]")
            continue

        if low.startswith("search "):
            kw = choice[7:].strip()
            if kw:
                search_tools(tools, kw)
            else:
                console.print(f"[{C['danger']}]Usage: search <keyword>[/{C['danger']}]")
            console.input(f"[{C['muted']}]Press Enter…[/{C['muted']}]")
            continue

        if low.startswith("info "):
            t = choice[5:].strip()
            if t:
                t_resolved = resolve_tool(t, tools) or t
                show_tool_info(tools, t_resolved)
            else:
                console.print(f"[{C['danger']}]Usage: info <tool>[/{C['danger']}]")
            console.input(f"[{C['muted']}]Press Enter…[/{C['muted']}]")
            continue

        if low.startswith("favorite "):
            t = choice[9:].strip()
            if t:
                t_resolved = resolve_tool(t, tools) or t
                config = toggle_favorite(config, t_resolved, tools)
            else:
                console.print(f"[{C['danger']}]Usage: favorite <tool>[/{C['danger']}]")
            console.input(f"[{C['muted']}]Press Enter…[/{C['muted']}]")
            continue

        if low == "favlist":
            list_favorites(tools, config)
            console.input(f"[{C['muted']}]Press Enter…[/{C['muted']}]")
            continue

        selected = resolve_tool(choice, tools)
        if selected:
            run_tool(tools, selected, config)
            config["last_tool"] = selected
            save_config(config)
        else:
            console.print(f"[{C['danger']}]✖ Unknown: '{choice}'[/{C['danger']}]")
            console.print(f"[{C['muted']}]Try: number, name, or alias (nm, ss, dns)[/{C['muted']}]")
            console.input(f"[{C['muted']}]Press Enter…[/{C['muted']}]")


# ======================================================================
# Entry
# ======================================================================
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print(f"\n[bold {C['danger']}]Session interrupted.[/bold {C['danger']}]\n")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold {C['danger']}]Fatal: {e}[/bold {C['danger']}]")
        log_error(f"FATAL: {e}")
        sys.exit(1)