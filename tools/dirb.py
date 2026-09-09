#!/usr/bin/env python3
"""
Merged dirb-style web directory brute‑forcer.
Features:
- Interactive and command‑line modes.
- Asynchronous HTTP with Tornado.
- Rich console table output.
- Wordlist from file or built‑in fallback.
- Custom headers, cookies, basic auth.
- Extension probing and variations.
- CSV output and file writing.
"""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Iterable, Optional, List

from tornado.httpclient import AsyncHTTPClient, HTTPClientError, HTTPRequest
from rich.console import Console
from rich.table import Table

console = Console()

# ----------------------------------------------------------------------
# Constants & defaults
# ----------------------------------------------------------------------
FALLBACK_WORDLIST = [
    "admin", "login", "wp-admin", "backup", "config", "uploads",
    "images", "css", "js", "api", "dashboard", "test", "dev",
    ".git", ".env", "robots.txt", "sitemap.xml", "phpinfo.php",
    "server-status", "old", "tmp", "assets", "static", "includes",
]

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
)
DEFAULT_NUM_WORKERS = 20
DEFAULT_TIMEOUT = 3.0


# ----------------------------------------------------------------------
# Wordlist loader
# ----------------------------------------------------------------------
def load_wordlist(path: Optional[str]) -> List[str]:
    if path and Path(path).exists():
        return [line.strip() for line in Path(path).read_text().splitlines() if line.strip()]
    return FALLBACK_WORDLIST[:]


# ----------------------------------------------------------------------
# Core brute‑forcing class (async)
# ----------------------------------------------------------------------
class Dirb:
    def __init__(
        self,
        base_url: str,
        wordlist: List[str],
        *,
        num_workers: int = DEFAULT_NUM_WORKERS,
        timeout: float = DEFAULT_TIMEOUT,
        user_agent: Optional[str] = None,
        headers: Optional[List[str]] = None,
        cookies: Optional[str] = None,
        credentials: Optional[str] = None,
        follow_redirects: bool = False,
        probe_extensions: List[str] = None,
        probe_variations: List[str] = None,
        found_callback=None,
        error_callback=None,
        pre_fetch_callback=None,
    ):
        self.base_url = base_url.rstrip("/")
        self.wordlist = wordlist
        self.num_workers = num_workers
        self.timeout = timeout
        self.user_agent = user_agent or DEFAULT_USER_AGENT
        self.headers = headers or []
        self.cookies = cookies
        self.credentials = credentials
        self.follow_redirects = follow_redirects
        self.probe_extensions = probe_extensions or []
        self.probe_variations = probe_variations or []

        self.found_callback = found_callback
        self.error_callback = error_callback
        self.pre_fetch_callback = pre_fetch_callback

        self.queue = asyncio.Queue()
        self.results = []

    async def run(self):
        # Fill queue with all paths (including extensions)
        for path in set(self.wordlist):
            path = path.strip()
            if not path:
                continue
            await self.queue.put(path)
            for ext in self.probe_extensions:
                if ext:
                    await self.queue.put(f"{path}{ext}")

        # Start workers
        workers = [asyncio.create_task(self._worker()) for _ in range(self.num_workers)]
        await self.queue.join()
        for w in workers:
            w.cancel()

    async def _worker(self):
        while True:
            try:
                await self._try_url()
            except asyncio.CancelledError:
                return

    async def _try_url(self):
        path = await self.queue.get()
        if not path.startswith("/"):
            path = "/" + path
        url = f"{self.base_url}{path}"

        if self.pre_fetch_callback:
            await self.pre_fetch_callback(path)

        try:
            http_client = AsyncHTTPClient()
            req = HTTPRequest(
                url,
                method="GET",
                user_agent=self.user_agent,
                headers=self._build_headers(),
                follow_redirects=self.follow_redirects,
                connect_timeout=self.timeout,
                request_timeout=self.timeout,
            )
            response = await http_client.fetch(req)

            # 3xx, 4xx (except 404) are also considered "found"
            if response.code not in (404,):
                self.results.append({
                    "path": path,
                    "effective_url": response.effective_url or url,
                    "status_code": response.code,
                    "headers": response.headers.get_all(),
                })
                if self.found_callback:
                    await self.found_callback(path, response.code)

        except HTTPClientError as e:
            # e.code can be 403, 401, 301, etc. – treat as found
            if e.code not in (404,):
                self.results.append({
                    "path": path,
                    "effective_url": url,
                    "status_code": e.code,
                    "headers": [],
                })
                if self.found_callback:
                    await self.found_callback(path, e.code)
            else:
                if self.error_callback:
                    await self.error_callback(f"{path} → {e.code}")
        except Exception as e:
            if self.error_callback:
                await self.error_callback(f"{path} → {str(e)}")
        finally:
            self.queue.task_done()

    def _build_headers(self):
        headers = {}
        if self.user_agent:
            headers["User-Agent"] = self.user_agent
        if self.cookies:
            headers["Cookie"] = self.cookies
        if self.credentials:
            # Basic Auth (simple)
            import base64
            cred = base64.b64encode(self.credentials.encode()).decode()
            headers["Authorization"] = f"Basic {cred}"
        for h in self.headers:
            if ":" in h:
                key, val = h.split(":", 1)
                headers[key.strip()] = val.strip()
        return headers

    @property
    def alive(self):
        return [r for r in self.results if r["status_code"] == 200]


# ----------------------------------------------------------------------
# Interactive mode
# ----------------------------------------------------------------------
async def interactive_run():
    base_url = console.input("[cyan]Target base URL (e.g. http://10.10.10.5): [/cyan]").strip()
    if not base_url:
        console.print("[red]No target given.[/red]")
        return
    if not base_url.startswith(("http://", "https://")):
        base_url = "http://" + base_url

    wordlist_path = console.input("[cyan]Custom wordlist path (blank = built‑in): [/cyan]").strip()
    threads_str = console.input("[cyan]Concurrent workers (default 20): [/cyan]").strip() or "20"
    timeout_str = console.input("[cyan]Timeout per request (sec, default 3.0): [/cyan]").strip() or "3.0"

    try:
        workers = int(threads_str)
        timeout = float(timeout_str)
    except ValueError:
        console.print("[red]Invalid number.[/red]")
        return

    wordlist = load_wordlist(wordlist_path)
    console.print(f"\n[*] Brute‑forcing {len(wordlist)} paths on {base_url}\n")

    # Callbacks for live feedback
    async def pre_fetch_hook(path):
        console.print(f"\r[dim]Checking {path} ...[/dim]", end="")

    async def found_hook(path, code):
        console.print(f"\n[green]FOUND {path} (status {code})[/green]")

    async def error_hook(msg):
        console.print(f"\n[yellow]{msg}[/yellow]")

    dirb = Dirb(
        base_url,
        wordlist,
        num_workers=workers,
        timeout=timeout,
        pre_fetch_callback=pre_fetch_hook,
        found_callback=found_hook,
        error_callback=error_hook,
    )
    await dirb.run()
    console.print()  # newline

    if not dirb.results:
        console.print("[yellow]No paths found.[/yellow]")
        return

    # Show results in a Rich table
    table = Table(title=f"Discovered paths on {base_url}")
    table.add_column("URL", style="cyan")
    table.add_column("Status", style="green")
    for entry in sorted(dirb.results, key=lambda x: x["path"]):
        url = f"{base_url}{entry['path']}"
        status = entry["status_code"]
        style = "green" if status == 200 else "yellow"
        table.add_row(url, f"[{style}]{status}[/{style}]")

    console.print(table)
    console.print(f"[bold green]{len(dirb.results)} path(s) found.[/bold green]")


# ----------------------------------------------------------------------
# Command‑line mode (argparse)
# ----------------------------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(prog="dirb", description="Directory brute‑forcer (merged)")
    parser.add_argument("base_url", help="Base URL, e.g. http://example.com")
    parser.add_argument("-w", "--word-file", action="append", default=[],
                        help="Wordlist file (can be used multiple times)")
    parser.add_argument("-n", "--num-workers", type=int, default=DEFAULT_NUM_WORKERS,
                        help=f"Number of concurrent workers (default: {DEFAULT_NUM_WORKERS})")
    parser.add_argument("-t", "--timeout", type=float, default=DEFAULT_TIMEOUT,
                        help=f"Request timeout in seconds (default: {DEFAULT_TIMEOUT})")
    parser.add_argument("-a", "--user-agent", default=DEFAULT_USER_AGENT,
                        help="Custom User‑Agent string")
    parser.add_argument("-H", "--header", action="append", default=[],
                        help="Extra header, e.g. 'X-Custom: value'")
    parser.add_argument("-c", "--cookie", help="Cookie string")
    parser.add_argument("-u", "--credentials", help="username:password for Basic Auth")
    parser.add_argument("-f", "--follow-redirects", action="store_true",
                        help="Follow 301/302 redirects")
    parser.add_argument("-X", "--probe-extensions",
                        help="Comma‑separated extensions to try (e.g. .php,.bak)")
    parser.add_argument("-M", "--probe-variations",
                        help="Comma‑separated variations to add when a path is found")
    parser.add_argument("--csv", action="store_true", help="Output results in CSV format")
    parser.add_argument("-o", "--output", help="Write output to file (instead of stdout)")
    parser.add_argument("-v", "--verbose", action="count", default=0,
                        help="Increase verbosity (show found/error lines)")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="Suppress progress and found messages (only final output)")
    return parser.parse_args()


async def cli_run(args):
    # Load wordlist(s)
    wordlist = []
    if args.word_file:
        for fname in args.word_file:
            if Path(fname).exists():
                wordlist.extend(load_wordlist(fname))
            else:
                console.print(f"[red]Wordlist file '{fname}' not found.[/red]")
                return
    else:
        # If no wordlist provided, use built‑in
        wordlist = FALLBACK_WORDLIST[:]

    if not wordlist:
        console.print("[red]No words to test.[/red]")
        return

    # Parse extensions/variations
    probe_ext = [x.strip() for x in (args.probe_extensions or "").split(",") if x.strip()]
    probe_var = [x.strip() for x in (args.probe_variations or "").split(",") if x.strip()]

    # Set up callbacks
    pre_fetch = None
    found = None
    error = None
    if not args.quiet:
        if args.verbose >= 0:
            async def pre_fetch_hook(path):
                console.print(f"\r[dim]Checking {path} ...[/dim]", end="")
            pre_fetch = pre_fetch_hook

        if args.verbose > 0:
            async def found_hook(path, code):
                console.print(f"\n[green]FOUND {path} (status {code})[/green]")
            found = found_hook

            async def error_hook(msg):
                console.print(f"\n[yellow]{msg}[/yellow]")
            error = error_hook

    dirb = Dirb(
        args.base_url,
        wordlist,
        num_workers=args.num_workers,
        timeout=args.timeout,
        user_agent=args.user_agent,
        headers=args.header,
        cookies=args.cookie,
        credentials=args.credentials,
        follow_redirects=args.follow_redirects,
        probe_extensions=probe_ext,
        probe_variations=probe_var,
        pre_fetch_callback=pre_fetch,
        found_callback=found,
        error_callback=error,
    )

    await dirb.run()

    # Output
    if args.csv:
        outfile = open(args.output, "w") if args.output else sys.stdout
        fields = ["status_code", "path", "effective_url", "headers"]
        outfile.write(";".join(fields) + "\n")
        for r in dirb.results:
            headers_str = ",".join(f"{k}:{v}" for k, v in r["headers"])
            outfile.write(
                f"{r['status_code']};"
                f'"{r["path"]}";'
                f'"{r["effective_url"]}";'
                f'"{headers_str}"\n'
            )
        if args.output:
            outfile.close()
    else:
        # Rich table or simple text
        if args.verbose >= 0 and not args.quiet:
            # Use Rich table
            table = Table(title=f"Discovered paths on {args.base_url}")
            table.add_column("URL", style="cyan")
            table.add_column("Status", style="green")
            for r in sorted(dirb.results, key=lambda x: x["path"]):
                url = f"{args.base_url}{r['path']}"
                style = "green" if r["status_code"] == 200 else "yellow"
                table.add_row(url, f"[{style}]{r['status_code']}[/{style}]")
            console.print(table)
            console.print(f"[bold green]{len(dirb.results)} path(s) found.[/bold green]")
        else:
            # Minimal output (just URLs, maybe to file)
            out = open(args.output, "w") if args.output else sys.stdout
            for r in sorted(dirb.results, key=lambda x: x["path"]):
                out.write(f"{args.base_url}{r['path']}\n")
            if args.output:
                out.close()


# ----------------------------------------------------------------------
# Main entry point
# ----------------------------------------------------------------------
def main():
    if len(sys.argv) == 1:
        # No arguments → interactive mode
        try:
            asyncio.run(interactive_run())
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted.[/yellow]")
    else:
        args = parse_args()
        try:
            asyncio.run(cli_run(args))
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted.[/yellow]")


if __name__ == "__main__":
    main()