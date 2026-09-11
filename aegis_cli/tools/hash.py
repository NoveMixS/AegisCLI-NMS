#!/usr/bin/env python3
"""
tools/hash.py — Hash identifier, hash computer, and password encryption/decryption (AES)
Interactive version for aegis-hub.
"""

import hashlib
import re
import json
import os
import base64
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm

console = Console()

description = "Identify hash algorithm, compute hashes, encrypt/decrypt passwords (AES)"
__version__ = "1.2"
__author__ = "Md Siyam Mahmud"
__category__ = "Cryptography"

# ----------------------------------------------------------------------
# Hash identification (as before)
# ----------------------------------------------------------------------
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

# ----------------------------------------------------------------------
# Hash computation (as before)
# ----------------------------------------------------------------------
def compute(text: str) -> dict:
    algos = ["md5", "sha1", "sha224", "sha256", "sha384", "sha512"]
    return {a: hashlib.new(a, text.encode()).hexdigest() for a in algos}

# ----------------------------------------------------------------------
# Encryption / Decryption (AES via Fernet)
# ----------------------------------------------------------------------
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "hash_encrypt_config.json")

def load_lock_config():
    """Load lock configuration (attempts and lock time)"""
    default = {"attempts": 0, "locked_until": None}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            return default
    return default

def save_lock_config(config):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
    except:
        pass

def reset_lock_config():
    save_lock_config({"attempts": 0, "locked_until": None})

def is_locked():
    config = load_lock_config()
    locked_until = config.get("locked_until")
    if locked_until:
        lock_time = datetime.fromisoformat(locked_until)
        if datetime.now() < lock_time:
            remaining = lock_time - datetime.now()
            hours, remainder = divmod(remaining.total_seconds(), 3600)
            mins = remainder // 60
            return True, f"Locked for {int(hours)}h {int(mins)}m (72h cooldown)"
        else:
            # Lock expired, reset attempts
            reset_lock_config()
            return False, None
    return False, None

def record_failed_attempt():
    config = load_lock_config()
    attempts = config.get("attempts", 0) + 1
    if attempts >= 3:
        # Lock for 72 hours
        lock_until = (datetime.now() + timedelta(hours=72)).isoformat()
        config = {"attempts": attempts, "locked_until": lock_until}
        save_lock_config(config)
        return True, "3 failed attempts! Locked for 72 hours."
    else:
        config["attempts"] = attempts
        save_lock_config(config)
        return False, f"Failed attempt {attempts}/3"

def record_success():
    reset_lock_config()  # reset attempts on successful decryption

def derive_key(password: str, salt: bytes = None) -> tuple[bytes, bytes]:
    """Derive a Fernet key from a password and salt. Returns (key, salt)."""
    if salt is None:
        salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt

def encrypt_text(plaintext: str, password: str) -> str:
    """Encrypt text using password-derived key. Returns base64 of salt+ciphertext."""
    key, salt = derive_key(password)
    f = Fernet(key)
    ciphertext = f.encrypt(plaintext.encode())
    # Store salt + ciphertext together (salt 16 bytes + ciphertext)
    combined = salt + ciphertext
    return base64.urlsafe_b64encode(combined).decode()

def decrypt_text(encoded: str, password: str) -> str:
    """Decrypt text using password. Returns plaintext or raises exception."""
    data = base64.urlsafe_b64decode(encoded)
    salt = data[:16]
    ciphertext = data[16:]
    key, _ = derive_key(password, salt)
    f = Fernet(key)
    return f.decrypt(ciphertext).decode()

# ----------------------------------------------------------------------
# Main interactive menu
# ----------------------------------------------------------------------
def run():
    console.print("[cyan]1.[/cyan] Identify a hash")
    console.print("[cyan]2.[/cyan] Compute hashes of text")
    console.print("[cyan]3.[/cyan] Encrypt text (password-based)")
    console.print("[cyan]4.[/cyan] Decrypt text (password-based)")
    choice = Prompt.ask("\n[bold magenta]Select option[/bold magenta]", choices=["1","2","3","4"])

    if choice == "1":
        value = Prompt.ask("[cyan]Hash value[/cyan]").strip()
        if not value:
            console.print("[red]No input given.[/red]")
            return
        candidates = identify(value)
        console.print(f"\n[*] Length: {len(value)} chars")
        console.print(f"[green]Likely algorithm(s): {', '.join(candidates)}[/green]")

    elif choice == "2":
        text = Prompt.ask("[cyan]Text to hash[/cyan]").strip()
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

    elif choice == "3":  # Encrypt
        plaintext = Prompt.ask("[cyan]Text to encrypt[/cyan]").strip()
        if not plaintext:
            console.print("[red]No text given.[/red]")
            return
        password = Prompt.ask("[cyan]Master password (for encryption)[/cyan]", password=True)
        if not password:
            console.print("[red]Password cannot be empty.[/red]")
            return
        try:
            encrypted = encrypt_text(plaintext, password)
            console.print("[green]✅ Encrypted successfully![/green]")
            console.print(f"[bold]Encrypted text (base64):[/bold]\n{encrypted}")
        except Exception as e:
            console.print(f"[red]Encryption failed: {e}[/red]")

    elif choice == "4":  # Decrypt
        # Check if locked
        locked, msg = is_locked()
        if locked:
            console.print(f"[bold red]⛔ {msg}[/bold red]")
            return

        encoded = Prompt.ask("[cyan]Encrypted text (base64)[/cyan]").strip()
        if not encoded:
            console.print("[red]No encrypted text given.[/red]")
            return
        password = Prompt.ask("[cyan]Master password[/cyan]", password=True)
        if not password:
            console.print("[red]Password cannot be empty.[/red]")
            return

        try:
            plaintext = decrypt_text(encoded, password)
            console.print("[green]✅ Decrypted successfully![/green]")
            console.print(f"[bold]Plain text:[/bold] {plaintext}")
            record_success()
        except Exception as e:
            console.print(f"[red]❌ Decryption failed: {e}[/red]")
            # Record failed attempt
            locked, msg = record_failed_attempt()
            if locked:
                console.print(f"[bold red]⛔ {msg}[/bold red]")
            else:
                console.print(f"[yellow]⚠️  {msg}[/yellow]")

    else:
        console.print("[red]Invalid option.[/red]")

    console.print("\n[dim]Press Enter to return.[/dim]")
    input()

# ----------------------------------------------------------------------
# Standalone test
# ----------------------------------------------------------------------
if __name__ == "__main__":
    run()