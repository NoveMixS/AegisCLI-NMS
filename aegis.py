import os
import sys
import importlib.util
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

# বড় ASCII আর্ট ব্যানার
BANNER = """
[bold cyan]
  ███    ███████   ██████  ███████   ██████ 
██   ██  ██       ██          ██    ██      
███████  █████    ██  ███     ██    █████   
██   ██  ██       ██   ██     ██         ██ 
██   ██  ███████   ██████  ███████  ██████  
[/bold cyan]
[dim]All-in-One AI-Powered Modular Security CLI Toolkit[/dim]
[dim]Phase 1 Core | Developed by Md Siyam Mahmud[/dim]
[dim]GitHub: github.com/siyam201  |  Org: github.com/novemixs[/dim]
"""

def load_tools():
    """tools/ All TOOLS LOAD"""
    tools = {}
    tools_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tools')

    if not os.path.exists(tools_dir):
        os.makedirs(tools_dir)
        return tools

    for filename in os.listdir(tools_dir):
        if filename.endswith('.py') and not filename.startswith('__'):
            module_name = filename[:-3]
            filepath = os.path.join(tools_dir, filename)
            try:
                # dynamick load
                spec = importlib.util.spec_from_file_location(module_name, filepath)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # per file tool 'run' funtion and 'description' vruable
                if hasattr(module, 'run') and hasattr(module, 'description'):
                    tools[module_name] = {
                        'module': module,
                        'description': module.description
                    }
            except Exception as e:
                console.print(f"[red]Error loading tool {module_name}: {e}[/red]")
    return tools

def display_menu(tools):
    """MAIN MENU"""
    console.print(BANNER)
    console.print("\n[bold yellow]═══════════════ Main Hub Menu ═══════════════[/bold yellow]")

    if not tools:
        console.print("[red]No tools found in the 'tools/' directory.[/red]")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("SL", style="dim", width=4)
    table.add_column("Tool Name", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")

    tool_list = list(tools.keys())
    for i, tool_name in enumerate(tool_list, 1):
        table.add_row(str(i), tool_name, tools[tool_name]['description'])

    console.print(table)
    console.print("[bold yellow]═══════════════════════════════════════════════[/bold yellow]")
    console.print("[dim]Type the Tool Name or SL number to run. Type 'exit' to quit.[/dim]\n")

def main():
    tools = load_tools()

    while True:
        display_menu(tools)
        choice = console.input("[bold magenta]aegis-hub>[/bold magenta] ").strip().lower()

        if choice in ['exit', 'quit', '0']:
            console.print("\n[bold green]GOOD BYE! Exiting Aegis-CLI Hub...[/bold green]\n")
            sys.exit(0)

        # name and serile number tools select
        selected_tool = None
        if choice.isdigit() and 1 <= int(choice) <= len(tools):
            selected_tool = list(tools.keys())[int(choice) - 1]
        elif choice in tools:
            selected_tool = choice

        if selected_tool:
            console.print(f"\n[bold cyan]▶ Loading tool:[/bold cyan] {selected_tool}\n")
            try:
                # select tool run funtion call
                tools[selected_tool]['module'].run()
            except Exception as e:
                console.print(f"[red]Error executing tool: {e}[/red]")
            console.print("\n[dim]Press Enter to return to the main menu...[/dim]")
            input()
            os.system('cls' if os.name == 'nt' else 'clear')
        else:
            console.print("[bold red]✖ Invalid selection! Please enter a valid Tool Name or SL number.[/bold red]\n")
            console.input("[dim]Press Enter to continue...[/dim]")
            os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[bold red]Session Interrupted. GOOD BYE![/bold red]\n")
        sys.exit(0)
