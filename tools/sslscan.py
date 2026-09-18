#!/usr/bin/env python3
"""
SSL/TLS Scanner for AegisCLI.
Analyzes certificate, protocol versions, cipher suites and known issues.
Uses cryptography lib to decode DER certs (works even without CA verification).
"""

import socket
import ssl
from datetime import datetime, timezone
from urllib.parse import urlparse

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

description = "SSL/TLS scanner — certificates, protocols, ciphers, weaknesses"
__version__ = "1.2"
__author__  = "Md Siyam Mahmud"
__category__ = "Web"

SCHEMA = {
    "action": {
        "type": "choice",
        "choices": ["scan", "json"],
        "default": "scan",
        "help": "Scan SSL/TLS configuration of a host.",
    },
    "host": {
        "type": "string",
        "required": True,
        "help": "Hostname or URL (e.g. github.com).",
    },
    "port": {
        "type": "int",
        "default": 443,
        "help": "TCP port (default 443).",
    },
}


# ----------------------------------------------------------------------
# Parsing helpers
# ----------------------------------------------------------------------
def _clean_host(target: str) -> tuple:
    """Parse a target into (hostname, port)."""
    target = target.strip()
    port = 443
    if target.startswith(("http://", "https://")):
        parsed = urlparse(target)
        host = parsed.hostname or ""
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
    else:
        first = target.split("/")[0]
        if ":" in first:
            host, port_str = first.rsplit(":", 1)
            try:
                port = int(port_str)
            except ValueError:
                port = 443
        else:
            host = first
    return host.lower(), port


def _safe_cipher_name(cipher_raw) -> str:
    """
    Safely extract cipher name from ssl socket's cipher() result.
    Handles 2-tuple, 3-tuple, 4-tuple, or any iterable length.
    """
    if cipher_raw is None:
        return "?"
    if isinstance(cipher_raw, str):
        return cipher_raw
    if isinstance(cipher_raw, (tuple, list)):
        return str(cipher_raw[0]) if len(cipher_raw) >= 1 else "?"
    return str(cipher_raw)


# ----------------------------------------------------------------------
# DER decoding using cryptography lib
# ----------------------------------------------------------------------
def _decode_der_certificate(der: bytes) -> dict:
    """Decode DER cert to a dict using cryptography lib."""
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID

        cert = x509.load_der_x509_certificate(der)

        def attr(name, oid):
            try:
                attrs = name.get_attributes_for_oid(oid)
                return attrs[0].value if attrs else None
            except Exception:
                return None

        def make_name_tuple(name, oid, key):
            val = attr(name, oid)
            if val is None:
                return ()
            return ((key, val),)

        subject = (
            make_name_tuple(cert.subject, NameOID.COMMON_NAME, "commonName") +
            make_name_tuple(cert.subject, NameOID.ORGANIZATION_NAME, "organizationName")
        )
        issuer = (
            make_name_tuple(cert.issuer, NameOID.COMMON_NAME, "commonName") +
            make_name_tuple(cert.issuer, NameOID.ORGANIZATION_NAME, "organizationName")
        )

        # SAN
        sans = []
        try:
            ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
            for name in ext.value:
                if isinstance(name, x509.DNSName):
                    sans.append(("DNS", name.value))
                elif isinstance(name, x509.IPAddress):
                    sans.append(("IP", str(name.value)))
        except Exception:
            pass

        # Handle both new and old cryptography versions
        try:
            nb = cert.not_valid_before_utc
            na = cert.not_valid_after_utc
        except AttributeError:
            nb = cert.not_valid_before
            na = cert.not_valid_after

        return {
            "subject": subject,
            "issuer": issuer,
            "notBefore": nb.strftime("%b %d %H:%M:%S %Y GMT"),
            "notAfter":  na.strftime("%b %d %H:%M:%S %Y GMT"),
            "subjectAltName": sans,
        }
    except Exception as e:
        console.print(f"[dim]DER decode error: {e}[/dim]")
        return {}


# ----------------------------------------------------------------------
# Network helpers
# ----------------------------------------------------------------------
def _fetch_certificate(host: str, port: int = 443, timeout: int = 10) -> dict:
    """Fetch certificate via stdlib ssl. Uses DER parsing for full details."""
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        with socket.create_connection((host, port), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                der = ssock.getpeercert(binary_form=True)
                try:
                    parsed = ssock.getpeercert()
                except Exception:
                    parsed = {}
                cipher = ssock.cipher()
                tls_version = ssock.version()

        cert_dict = parsed if parsed else _decode_der_certificate(der)

        return {
            "ok": True,
            "cert": cert_dict,
            "cipher": cipher,
            "tls_version": tls_version,
        }
    except socket.timeout:
        return {"ok": False, "error": f"Timed out connecting to {host}:{port}"}
    except socket.gaierror:
        return {"ok": False, "error": f"DNS resolution failed for {host}"}
    except ConnectionRefusedError:
        return {"ok": False, "error": f"Connection refused on port {port}"}
    except ssl.SSLError as e:
        return {"ok": False, "error": f"SSL error: {e}"}
    except Exception as e:
        return {"ok": False, "error": f"Unexpected error: {e}"}


def _fetch_cert_verified(host: str, port: int = 443, timeout: int = 10) -> dict:
    """Re-fetch cert with verification enabled."""
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=host):
                pass
        return {"ok": True, "verified": True}
    except ssl.SSLCertVerificationError as e:
        return {"ok": True, "verified": False, "error": str(e)[:200]}
    except Exception as e:
        return {"ok": True, "verified": False, "error": str(e)[:200]}


def _probe_tls_versions(host: str, port: int = 443, timeout: int = 5) -> dict:
    """Test which TLS versions the server supports."""
    results = {}
    versions = [
        ("TLS 1.3", getattr(ssl.TLSVersion, "TLSv1_3", None)),
        ("TLS 1.2", ssl.TLSVersion.TLSv1_2),
        ("TLS 1.1", ssl.TLSVersion.TLSv1_1),
        ("TLS 1.0", ssl.TLSVersion.TLSv1),
    ]

    for name, ver in versions:
        if ver is None:
            results[name] = "unknown"
            continue
        try:
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            ctx.minimum_version = ver
            ctx.maximum_version = ver
            with socket.create_connection((host, port), timeout=timeout) as sock:
                with ctx.wrap_socket(sock, server_hostname=host):
                    results[name] = "supported"
        except (ssl.SSLError, OSError, ValueError):
            results[name] = "not supported"
        except Exception:
            results[name] = "error"

    return results


def _parse_cert_dates(cert: dict) -> dict:
    """Parse notBefore / notAfter strings into datetimes."""
    out = {"notBefore": None, "notAfter": None, "days_left": None, "expired": False}
    if not cert:
        return out

    for key in ("notBefore", "notAfter"):
        raw = cert.get(key)
        if raw:
            try:
                for fmt in ("%b %d %H:%M:%S %Y %Z", "%b %d %H:%M:%S %Y GMT"):
                    try:
                        dt = datetime.strptime(raw, fmt)
                        dt = dt.replace(tzinfo=timezone.utc)
                        out[key] = dt
                        break
                    except ValueError:
                        continue
            except Exception:
                out[key] = None

    if out["notAfter"]:
        delta = out["notAfter"] - datetime.now(timezone.utc)
        out["days_left"] = delta.days
        out["expired"] = delta.total_seconds() < 0

    return out


def _extract_san(cert: dict) -> list:
    """Extract Subject Alternative Names."""
    sans = []
    for entry in cert.get("subjectAltName", []):
        if isinstance(entry, tuple) and len(entry) == 2:
            sans.append(f"{entry[0]}: {entry[1]}")
    return sans


def _extract_subject(cert: dict) -> dict:
    """Flatten subject/issuer entries."""
    def flatten(items):
        out = {}
        for pair in items:
            if isinstance(pair, tuple) and len(pair) == 2:
                k, v = pair
                out[k] = v
        return out
    return {
        "subject": flatten(cert.get("subject", [])),
        "issuer": flatten(cert.get("issuer", [])),
    }


def _compute_grade(tls_matrix: dict, dates: dict, verified: dict) -> str:
    """Rough SSL grade (A+ / A / B / C / D / F)."""
    score = 0
    if verified.get("verified"):
        score += 3
    if not dates.get("expired"):
        score += 2
    if tls_matrix.get("TLS 1.3") == "supported":
        score += 3
    if tls_matrix.get("TLS 1.2") == "supported":
        score += 2
    if tls_matrix.get("TLS 1.0") == "supported":
        score -= 3
    if tls_matrix.get("TLS 1.1") == "supported":
        score -= 2

    if score >= 9:  return "A+"
    if score >= 7:  return "A"
    if score >= 5:  return "B"
    if score >= 3:  return "C"
    if score >= 1:  return "D"
    return "F"


# ----------------------------------------------------------------------
# Action
# ----------------------------------------------------------------------
def _action_scan(target: str, port: int = 443) -> dict:
    host, port = _clean_host(target)

    if not host:
        return {"ok": False, "action": "scan", "error": "no host given"}

    result = _fetch_certificate(host, port)
    if not result.get("ok"):
        return {"ok": False, "action": "scan", "host": host, "port": port,
                "error": result.get("error")}

    cert = result["cert"]
    dates = _parse_cert_dates(cert)
    names = _extract_subject(cert)
    sans = _extract_san(cert)

    verified = _fetch_cert_verified(host, port)
    tls_matrix = _probe_tls_versions(host, port)
    grade = _compute_grade(tls_matrix, dates, verified)

    return {
        "ok": True,
        "action": "scan",
        "host": host,
        "port": port,
        "tls_version": result.get("tls_version"),
        "cipher": _safe_cipher_name(result.get("cipher")),
        "certificate": {
            "subject": names["subject"],
            "issuer": names["issuer"],
            "not_before": dates["notBefore"].isoformat() if dates["notBefore"] else None,
            "not_after":  dates["notAfter"].isoformat() if dates["notAfter"] else None,
            "days_left":  dates["days_left"],
            "expired":    dates["expired"],
            "san":        sans,
        },
        "verified_handshake": {
            "verified": verified.get("verified"),
            "error":    verified.get("error"),
        },
        "tls_versions": tls_matrix,
        "grade": grade,
        "scanned_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }


# ----------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------
def _render_result(result: dict):
    if not result.get("ok"):
        console.print(f"[red]✖ {result.get('error')}[/red]")
        return

    grade = result["grade"]
    grade_color = {
        "A+": "green", "A": "green", "B": "cyan",
        "C": "yellow", "D": "orange1", "F": "red",
    }.get(grade, "white")

    # Cipher is already a safe string from _safe_cipher_name
    cipher_name = result.get("cipher") or "?"

    console.print(Panel(
        f"[bold]Host:[/bold]        {result['host']}:{result['port']}\n"
        f"[bold]TLS version:[/bold] {result.get('tls_version') or '?'}\n"
        f"[bold]Cipher:[/bold]      {cipher_name}\n"
        f"[bold]Grade:[/bold]       [{grade_color}]{grade}[/{grade_color}]",
        title=f"🔒 SSL Scan · {result['host']}",
        border_style=grade_color,
    ))

    # Certificate
    cert = result["certificate"]
    t = Table(title="📜 Certificate", box=box.ROUNDED, show_header=False)
    t.add_column("Field", style="cyan", width=16)
    t.add_column("Value", style="white", overflow="fold")

    subj = cert["subject"]
    iss = cert["issuer"]
    t.add_row("CN",        subj.get("commonName", "—"))
    t.add_row("Org",       subj.get("organizationName", "—"))
    t.add_row("Issuer",    iss.get("organizationName", "—"))
    t.add_row("Issuer CN", iss.get("commonName", "—"))
    t.add_row("Valid from",  cert["not_before"] or "—")
    t.add_row("Valid until", cert["not_after"] or "—")

    days = cert.get("days_left")
    if days is not None:
        if days < 0:
            t.add_row("Expiry", f"[red]EXPIRED {-days} days ago![/red]")
        elif days < 15:
            t.add_row("Expiry", f"[red]{days} days left[/red]")
        elif days < 30:
            t.add_row("Expiry", f"[yellow]{days} days left[/yellow]")
        else:
            t.add_row("Expiry", f"[green]{days} days left[/green]")

    console.print(t)

    # TLS Matrix
    tls = result["tls_versions"]
    t = Table(title="🔐 TLS Protocol Support", box=box.ROUNDED)
    t.add_column("Protocol", style="cyan", width=12)
    t.add_column("Status", style="white")

    for version, status in tls.items():
        if status == "supported":
            color = "green" if version in ("TLS 1.2", "TLS 1.3") else "yellow"
            t.add_row(version, f"[{color}]{status}[/{color}]")
        elif status == "not supported":
            t.add_row(version, f"[dim]{status}[/dim]")
        else:
            t.add_row(version, f"[yellow]{status}[/yellow]")
    console.print(t)

    # Verified handshake
    vh = result["verified_handshake"]
    if vh.get("verified"):
        console.print("[green]✅ Certificate chain verified[/green]")
    else:
        console.print("[red]❌ Certificate verification failed[/red]")
        if vh.get("error"):
            console.print(f"[dim]   {vh['error']}[/dim]")

    # SAN
    sans = cert.get("san", [])
    if sans:
        t = Table(title="🏷️  Subject Alternative Names", box=box.ROUNDED, show_header=False)
        t.add_column("Name", style="cyan")
        for s in sans[:20]:
            t.add_row(s)
        if len(sans) > 20:
            t.add_row(f"[dim]... and {len(sans) - 20} more[/dim]")
        console.print(t)


# ----------------------------------------------------------------------
# Interactive + entry point
# ----------------------------------------------------------------------
def _interactive() -> dict:
    target = console.input("[cyan]Host or URL[/cyan] (e.g. github.com): ").strip()
    if not target:
        console.print("[yellow]No host given.[/yellow]")
        return {"ok": False, "action": "scan", "error": "no host"}
    port_str = console.input("[cyan]Port[/cyan] [443]: ").strip() or "443"
    try:
        port = int(port_str)
    except ValueError:
        port = 443

    console.print(f"\n[dim]Scanning {target}:{port}...[/dim]\n")
    result = _action_scan(target, port)
    _render_result(result)
    return result


def run(args: dict | None = None) -> dict:
    if args is None:
        return _interactive()

    action = (args.get("action") or "scan").lower()
    host = args.get("host", "")
    port = int(args.get("port", 443))

    if action in ("scan", "json"):
        result = _action_scan(host, port)
        if action == "json":
            console.print_json(data=result)
        else:
            _render_result(result)
        return result

    return {"ok": False, "action": action, "error": f"Unknown action: {action}"}