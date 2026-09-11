#!/usr/bin/env python3
"""
AegisCLI Hub v2.1 - Enhanced with history, search, favorites, and more.
"""

import os
import sys
import json
import argparse
import importlib.util
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich import box
from rich.markdown import Markdown
from rich.text import Text

# ----------------------------------------------------------------------
# Configuration & Constants
# ----------------------------------------------------------------------
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aegis_config.json")
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aegis.log")
HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aegis_history.txt")
VERSION = "2.1"

console = Console()
# Global store for the last tool result per tool (Phase 2 AI engine will read this)
_LAST_RESULT: dict = {}
# Updated Banner with version
BANNER = """
[bold cyan]
  █████╗ ███████╗ ██████╗ ██╗███████╗    ██████╗██╗     ██╗
 ██╔══██╗██╔════╝██╔════╝ ██║██╔════╝   ██╔════╝██║     ██║
 ███████║█████╗  ██║  ███╗██║███████╗   ██║     ██║     ██║
 ██╔══██║██╔══╝  ██║   ██║██║╚════██║   ██║     ██║     ██║
 ██║  ██║███████╗╚██████╔╝██║███████║   ╚██████╗███████╗██║
 ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝╚══════╝    ╚═════╝╚══════╝╚═╝
[/bold cyan]
[bold yellow]⚔️  AI-Powered Modular Security CLI Toolkit[/bold yellow]
[dim]├─ Version: {}[/dim]
[dim]├─ Developed by Md Siyam Mahmud[/dim]
[dim]├─ GitHub: github.com/siyam201  |  Org: github.com/novemixs[/dim]
[dim]└─ Type 'help' for commands, 'exit' to quit.[/dim]
""".format(VERSION)

DEFAULT_CONFIG = {
    "last_tool": None,
    "auto_clear": True,
    "log_errors": True,
    "favorites": [],
}

# ----------------------------------------------------------------------
# Logger & History
# ----------------------------------------------------------------------
def log_error(message: str):
    if not load_config().get("log_errors", True):
        return
    try:
        with open(LOG_FILE, "a") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {message}\n")
    except:
        pass

def add_history(command: str):
    """Add command to history file (last 50 entries)."""
    try:
        # Read existing history
        history = []
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                history = [line.strip() for line in f.readlines() if line.strip()]
        # Append new command
        history.append(command)
        # Keep last 50
        if len(history) > 50:
            history = history[-50:]
        # Write back
        with open(HISTORY_FILE, "w") as f:
            f.write("\n".join(history) + "\n")
    except:
        pass

def get_history():
    """Return list of last commands."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    return []

# ----------------------------------------------------------------------
# Config Manager
# ----------------------------------------------------------------------
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            return DEFAULT_CONFIG.copy()
    else:
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

def save_config(config):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
    except:
        pass

# ----------------------------------------------------------------------
# Tool Loader (with metadata and category)
# ----------------------------------------------------------------------
def load_tools():
    tools = {}
    tools_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools")
    if not os.path.exists(tools_dir):
        os.makedirs(tools_dir)
        console.print("[yellow]📁 Created 'tools/' directory. Please add tool modules.[/yellow]")
        return tools

    for filename in os.listdir(tools_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = filename[:-3]
            filepath = os.path.join(tools_dir, filename)
            try:
                spec = importlib.util.spec_from_file_location(module_name, filepath)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                if hasattr(module, "run") and hasattr(module, "description"):
                    tools[module_name] = {
                        "module": module,
                        "description": module.description,
                        "version": getattr(module, "__version__", "1.0"),
                        "author": getattr(module, "__author__", "Unknown"),
                        "category": getattr(module, "__category__", "General"),
                    }
                else:
                    console.print(f"[dim]⚠️  Skipping {filename}: missing 'run()' or 'description'[/dim]")
            except Exception as e:
                err_msg = f"Error loading {module_name}: {e}"
                console.print(f"[red]❌ {err_msg}[/red]")
                log_error(err_msg)
    return tools

# ----------------------------------------------------------------------
# Command Handlers
# ----------------------------------------------------------------------
def display_menu(tools, config):
    if config.get("auto_clear", True):
        console.clear()

    console.print(Panel(BANNER, border_style="blue", box=box.DOUBLE_EDGE))

    tool_count = len(tools)
    status_color = "green" if tool_count > 0 else "red"
    console.rule(f"[bold] MAIN HUB MENU  |  Tools Loaded: [{status_color}]{tool_count}[/{status_color}] [/bold]")

    if not tools:
        console.print("[red]No tools found in the 'tools/' directory.[/red]")
        console.print("[dim]Add a Python file with 'run()' and 'description' in 'tools/'[/dim]")
        console.print("\n[bold]Available commands:[/bold]")
        console.print("[cyan]  help[/cyan]  - Show this menu again")
        console.print("[cyan]  reload[/cyan] - Reload all tools without restart")
        console.print("[cyan]  info <tool>[/cyan] - Show tool details")
        console.print("[cyan]  search <keyword>[/cyan] - Search tools by description")
        console.print("[cyan]  favorite <tool>[/cyan] - Mark/unmark tool as favorite")
        console.print("[cyan]  favlist[/cyan] - List favorite tools")
        console.print("[cyan]  history[/cyan] - Show command history")
        console.print("[cyan]  clear[/cyan] - Clear screen")
        console.print("[cyan]  set <key> <value>[/cyan] - Change config (e.g., set auto_clear false)")
        console.print("[cyan]  config[/cyan]  - Show current configuration")
        console.print("[cyan]  exit/q[/cyan]  - Quit AegisCLI")
        return

    # Table with category
    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("SL", style="dim", width=4, justify="center")
    table.add_column("Tool Name", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")
    table.add_column("Version", style="green", width=10, justify="center")
    table.add_column("Category", style="yellow", width=12, justify="center")

    tool_list = list(tools.keys())
    config_favs = config.get("favorites", [])
    for i, tool_name in enumerate(tool_list, 1):
        is_fav = "⭐" if tool_name in config_favs else ""
        table.add_row(
            str(i),
            f"{is_fav} {tool_name}",
            tools[tool_name]["description"],
            tools[tool_name]["version"],
            tools[tool_name]["category"],
        )

    console.print(table)
    console.rule("[bold] COMMANDS [/bold]")
    console.print(
        "[dim]  Run: Enter SL number or Tool Name  |  "
        "reload  |  info <tool>  |  search <kw>  |  favorite <tool>  |  favlist  |  history  |  clear  |  set  |  config  |  exit/q[/dim]"
    )
    console.print()

# ----------------------------------------------------------------------
# Search Tools
# ----------------------------------------------------------------------
def search_tools(tools, keyword):
    """Search tools by description or name."""
    keyword = keyword.lower()
    matches = []
    for name, data in tools.items():
        if keyword in name.lower() or keyword in data["description"].lower():
            matches.append((name, data["description"]))
    if not matches:
        console.print(f"[yellow]No tools found matching '{keyword}'.[/yellow]")
    else:
        table = Table(title=f"🔍 Search Results for '{keyword}'", box=box.ROUNDED)
        table.add_column("Tool", style="cyan")
        table.add_column("Description", style="white")
        for name, desc in matches:
            table.add_row(name, desc)
        console.print(table)

# ----------------------------------------------------------------------
# Favorites Management
# ----------------------------------------------------------------------
def toggle_favorite(config, tool_name, tools):
    if tool_name not in tools:
        console.print(f"[red]Tool '{tool_name}' not found.[/red]")
        return config
    favs = config.get("favorites", [])
    if tool_name in favs:
        favs.remove(tool_name)
        console.print(f"[yellow]➖ Removed '{tool_name}' from favorites.[/yellow]")
    else:
        favs.append(tool_name)
        console.print(f"[green]➕ Added '{tool_name}' to favorites.[/green]")
    config["favorites"] = favs
    save_config(config)
    return config

def list_favorites(tools, config):
    favs = config.get("favorites", [])
    if not favs:
        console.print("[yellow]No favorite tools.[/yellow]")
        return
    table = Table(title="⭐ Favorite Tools", box=box.ROUNDED)
    table.add_column("Tool", style="cyan")
    table.add_column("Description", style="white")
    for name in favs:
        if name in tools:
            table.add_row(name, tools[name]["description"])
        else:
            table.add_row(name, "[red]Tool not loaded[/red]")
    console.print(table)

# ----------------------------------------------------------------------
# Config Set Command
# ----------------------------------------------------------------------
def config_set(config, key, value):
    """Update a configuration value."""
    if key not in config:
        console.print(f"[red]Unknown config key '{key}'. Valid keys: {list(config.keys())}[/red]")
        return config
    # Convert value to appropriate type
    if isinstance(config[key], bool):
        if value.lower() in ["true", "1", "yes", "on"]:
            value = True
        elif value.lower() in ["false", "0", "no", "off"]:
            value = False
        else:
            console.print("[red]Invalid boolean value. Use true/false.[/red]")
            return config
    elif isinstance(config[key], int):
        try:
            value = int(value)
        except:
            console.print("[red]Invalid integer value.[/red]")
            return config
    elif isinstance(config[key], list):
        # For simplicity, we treat as string, but we don't support setting list from CLI easily.
        console.print("[red]Setting list values is not supported via 'set'. Use config file.[/red]")
        return config
    config[key] = value
    save_config(config)
    console.print(f"[green]✅ Config '{key}' set to '{value}'.[/green]")
    return config

# ----------------------------------------------------------------------
# Tool Runner
# ----------------------------------------------------------------------
def run_tool(tools, tool_name):
    if tool_name not in tools:
        console.print(f"[red]✖ Tool '{tool_name}' not found.[/red]")
        return

    console.print(f"\n[bold cyan]▶ Loading tool:[/bold cyan] {tool_name} "
                  f"[dim](v{tools[tool_name]['version']})[/dim]\n")
    try:
        result = tools[tool_name]["module"].run()
        # Phase 2 hook: store last result for the AI engine
        if isinstance(result, dict):
            _LAST_RESULT[tool_name] = result
    except KeyboardInterrupt:
        console.print("\n[yellow]⏹️  Tool execution interrupted by user.[/yellow]")
    except Exception as e:
        err_msg = f"Execution error in {tool_name}: {e}"
        console.print(f"[red]❌ {err_msg}[/red]")
        log_error(err_msg)

    # Hub owns the pause — tools should NOT prompt
    console.print("\n[dim]Press Enter to return to the main menu...[/dim]")
    input()

# ----------------------------------------------------------------------
# Main Loop
# ----------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AegisCLI - Modern Security Toolkit")
    parser.add_argument("--run", help="Run a specific tool directly", metavar="TOOL_NAME")
    parser.add_argument("--list", action="store_true", help="List all available tools")
    parser.add_argument("--version", action="version", version=f"AegisCLI v{VERSION}")
    args = parser.parse_args()

    config = load_config()
    tools = load_tools()

    if args.list:
        if not tools:
            console.print("[red]No tools found.[/red]")
            return
        console.print("[bold]Available Tools:[/bold]")
        for name, data in tools.items():
            console.print(f"  [cyan]{name}[/cyan] - {data['description']} [dim](v{data['version']}, {data['category']})[/dim]")
        return

    if args.run:
        run_tool(tools, args.run)
        return

    # Interactive
    while True:
        display_menu(tools, config)
        # Show last used tool in prompt
        last_tool = config.get("last_tool")
        prompt_suffix = f" [dim](last: {last_tool})[/dim]" if last_tool and last_tool in tools else ""
        choice = Prompt.ask(f"[bold magenta]aegis-hub>[/bold magenta]{prompt_suffix}").strip()
        add_history(choice)
        choice_lower = choice.lower()

        # Exit
        if choice_lower in ["exit", "quit", "q", "0"]:
            console.print("\n[bold green]✅ GOOD BYE! Exiting Aegis-CLI Hub...[/bold green]\n")
            sys.exit(0)

        # Reload
        if choice_lower == "reload":
            console.print("[yellow]🔄 Reloading tools...[/yellow]")
            tools = load_tools()
            console.print("[green]✅ Tools reloaded successfully![/green]")
            continue

        # Help
        if choice_lower == "help":
            # Display help (will be shown in menu, but we can show a detailed help panel)
            console.print(Panel(
                "[bold]Available Commands:[/bold]\n"
                "  [cyan]<SL>[/] or [cyan]<tool_name>[/] - Run a tool\n"
                "  [cyan]reload[/] - Reload all tools\n"
                "  [cyan]info <tool>[/] - Show tool details\n"
                "  [cyan]search <keyword>[/] - Search tools by description\n"
                "  [cyan]favorite <tool>[/] - Toggle favorite status\n"
                "  [cyan]favlist[/] - List favorite tools\n"
                "  [cyan]history[/] - Show command history\n"
                "  [cyan]clear[/] - Clear screen\n"
                "  [cyan]set <key> <value>[/] - Change config setting\n"
                "  [cyan]config[/] - Show current configuration\n"
                "  [cyan]exit[/], [cyan]quit[/], [cyan]q[/] - Exit hub",
                title="Help", border_style="green"
            ))
            input("[dim]Press Enter to continue...[/dim]")
            continue

        # Clear
        if choice_lower == "clear":
            console.clear()
            continue

        # History
        if choice_lower == "history":
            hist = get_history()
            if not hist:
                console.print("[yellow]No command history.[/yellow]")
            else:
                table = Table(title="Command History", box=box.ROUNDED)
                table.add_column("#", style="dim")
                table.add_column("Command", style="white")
                for i, cmd in enumerate(hist, 1):
                    table.add_row(str(i), cmd)
                console.print(table)
            input("[dim]Press Enter to continue...[/dim]")
            continue

        # Config
        if choice_lower == "config":
            show_config(config)
            input("[dim]Press Enter to continue...[/dim]")
            continue

        # Set config
        if choice_lower.startswith("set "):
            parts = choice.split(maxsplit=2)
            if len(parts) == 3:
                _, key, value = parts
                config = config_set(config, key, value)
            else:
                console.print("[red]Usage: set <key> <value>[/red]")
            input("[dim]Press Enter to continue...[/dim]")
            continue

        # Search
        if choice_lower.startswith("search "):
            keyword = choice[7:].strip()
            if keyword:
                search_tools(tools, keyword)
            else:
                console.print("[red]Usage: search <keyword>[/red]")
            input("[dim]Press Enter to continue...[/dim]")
            continue

        # Info
        if choice_lower.startswith("info "):
            tool = choice[5:].strip()
            if tool:
                show_tool_info(tools, tool)
            else:
                console.print("[red]Usage: info <tool>[/red]")
            input("[dim]Press Enter to continue...[/dim]")
            continue

        # Favorite
        if choice_lower.startswith("favorite "):
            tool = choice[9:].strip()
            if tool:
                config = toggle_favorite(config, tool, tools)
            else:
                console.print("[red]Usage: favorite <tool>[/red]")
            input("[dim]Press Enter to continue...[/dim]")
            continue

        # Favlist
        if choice_lower == "favlist":
            list_favorites(tools, config)
            input("[dim]Press Enter to continue...[/dim]")
            continue

        # Run by SL or name
        selected_tool = None
        if choice.isdigit() and 1 <= int(choice) <= len(tools):
            selected_tool = list(tools.keys())[int(choice)-1]
        elif choice in tools:
            selected_tool = choice

        if selected_tool:
            run_tool(tools, selected_tool)
            config["last_tool"] = selected_tool
            save_config(config)
        else:
            console.print("[bold red]✖ Invalid selection! Use SL number, Tool Name, or a valid command.[/bold red]")
            input("[dim]Press Enter to continue...[/dim]")

# ----------------------------------------------------------------------
# Show config (helper)
# ----------------------------------------------------------------------
def show_config(config):
    table = Table(title="⚙️  Current Configuration", box=box.HEAVY_EDGE)
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="white")
    for key, val in config.items():
        table.add_row(key, str(val))
    console.print(table)
    if Confirm.ask("[yellow]Reset configuration to defaults?[/yellow]"):
        save_config(DEFAULT_CONFIG)
        console.print("[green]✅ Configuration reset to defaults. Restart hub to apply.[/green]")

def show_tool_info(tools, tool_name):
    if tool_name not in tools:
        console.print(f"[red]Tool '{tool_name}' not found.[/red]")
        return
    data = tools[tool_name]
    info_table = Table(title=f"📊 Tool Info: {tool_name}", box=box.HEAVY_EDGE)
    info_table.add_column("Property", style="cyan", width=15)
    info_table.add_column("Value", style="white")
    info_table.add_row("Description", data["description"])
    info_table.add_row("Version", data["version"])
    info_table.add_row("Author", data["author"])
    info_table.add_row("Category", data["category"])
    info_table.add_row("Module Path", f"tools/{tool_name}.py")
    console.print(info_table)

# ----------------------------------------------------------------------
# Entry Point
# ----------------------------------------------------------------------
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[bold red]⏹️  Session Interrupted. GOOD BYE![/bold red]\n")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]💥 Fatal Error: {e}[/bold red]")
        log_error(f"FATAL: {e}")
        sys.exit(1)