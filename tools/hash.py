"""
tools/hash.py — Hash identifier & computer, interactive version for aegis-hub.
"""
import hashlib
import re
from rich.console import Console
from rich.table import Table

console = Console()

description = "Identify hash algorithm or compute hash digests of text"

HASH_LENGTH_MAP = {
    32: ["MD5", "NTLM", "MD4"],
    40: ["SHA1", "RIPEMD-160"],
    56: ["SHA224", "SHA3-224"],
    64: ["SHA256", "SHA3-256", "BLAKE2s"],
    96: ["SHA384", "SHA3-384"],
    128: ["SHA512", "SHA3-512", "BLAKE2b", "Whirlpool"],
}
HEX_RE = re.compile(r"^[a-fA-F0-9]+$")
BCRYPT_RE = re.compile(r"^\$2[aby]?\$\d{2}\$")
SHA512CRYPT_RE = re.compile(r"^\$6\$")
MD5CRYPT_RE = re.compile(r"^\$1\$")


def identify(value: str) -> list[str]:
    value = value.strip()
    if BCRYPT_RE.match(value):
        return ["bcrypt"]
    if SHA512CRYPT_RE.match(value):
        return ["sha512crypt (Unix)"]
    if MD5CRYPT_RE.match(value):
        return ["md5crypt (Unix)"]
    if HEX_RE.match(value):
        return HASH_LENGTH_MAP.get(len(value), ["Unknown (hex, unrecognized length)"])
    return ["Unknown (non-hex format)"]


def compute(text: str) -> dict:
    algos = ["md5", "sha1", "sha224", "sha256", "sha384", "sha512"]
    return {a: hashlib.new(a, text.encode()).hexdigest() for a in algos}


def run():
    console.print("[cyan]1.[/cyan] Identify a hash")
    console.print("[cyan]2.[/cyan] Compute hashes of text")
    choice = console.input("\n[bold magenta]Select option: [/bold magenta]").strip()

    if choice == "1":
        value = console.input("[cyan]Hash value: [/cyan]").strip()
        if not value:
            console.print("[red]No input given.[/red]")
            return
        candidates = identify(value)
        console.print(f"\n[*] Length: {len(value)} chars")
        console.print(f"[green]Likely algorithm(s): {', '.join(candidates)}[/green]")

    elif choice == "2":
        text = console.input("[cyan]Text to hash: [/cyan]").strip()
        if not text:
            console.print("[red]No input given.[/red]")
            return
        digests = compute(text)
        table = Table(title=f"Hashes for '{text}'")
        table.add_column("Algorithm", style="cyan")
        table.add_column("Digest", style="green")
        for algo, digest in digests.items():
            table.add_row(algo.upper(), digest)
        console.print(table)

    else:
        console.print("[red]Invalid option.[/red]")
