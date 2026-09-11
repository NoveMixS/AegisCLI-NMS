# 📋 Changelog

All notable changes to **AegisCLI** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- AI Command Engine (LangChain + Ollama)
- Natural-language → tool selection
- 100+ external tool integrations (Phase 2)
- Threat detection module (Phase 3)
- Plugin ecosystem (Phase 3)

---

## [0.1.0] — 2026-09-12

### 🎉 Initial Public Release — Fast Release

The first public release of AegisCLI. This version ships a working
interactive Hub CLI and four fully functional native modules.

### Added

#### Interactive Hub CLI (`aegis-hub.py`)
- Rich-powered terminal UI with custom ASCII banner
- Numbered tool menu — run tools by index or name
- Dynamic module loader (hot-reload via `reload` command)
- Command history (last 50 commands, persisted to `aegis_history.txt`)
- Favorites system (`favorite`, `favlist`)
- Tool search across names and descriptions (`search <keyword>`)
- Per-tool info panel (`info <tool>`)
- Configuration system with `set <key> <value>` and `config` commands
- Structured error logging to `aegis.log`
- Non-interactive CLI flags: `--run <tool>`, `--list`, `--version`
- Cross-platform support: Linux, macOS, Windows

#### `tools/nmap.py` — TCP Port Scanner (v2.0)
- Multi-threaded scanning via `ThreadPoolExecutor` (default: 200 workers)
- IPv4 **and** IPv6 support via `socket.getaddrinfo`
- Port spec parser: `80`, `1-1000`, `22,80,8000-8100`
- 100+ common-service name map (SSH, HTTP, MySQL, Redis, Kafka, etc.)
- Best-effort **banner grabbing** for open ports
- Hard per-port connect timeout
- Structured `dict` return with `SCHEMA` manifest
- `--json` output mode for scripting and pipelines
- Standalone `argparse` CLI for direct invocation

#### `tools/subfinder.py` — Subdomain Enumerator (v2.0)
- DNS brute-force via `socket.getaddrinfo`
- Built-in wordlist of ~250 common subdomains
- Custom wordlist support (`-w <path>`)
- **Bounded concurrency** via `ThreadPoolExecutor`
- **Per-lookup hard timeout** (no hangs on dead DNS)
- Apex domain marker (`@`) support
- Rich progress bar with ETA
- Structured `dict` return with `SCHEMA` manifest
- `--json` output mode
- Standalone `argparse` CLI

#### `tools/hash.py` — Hash Analyzer & Crypto (v1.2)
- Hash format identification (MD5, SHA-1/224/256/384/512, NTLM,
  bcrypt, sha512crypt, md5crypt)
- Multi-algorithm hash computation
- **AES encryption / decryption** via Fernet + PBKDF2 (100k iterations)
- Failed-attempt lockout protection

#### `tools/audit.py` — System Security Auditor (v1.1)
- World-writable file scan (Linux)
- Listening-services enumeration (Linux `ss` / `netstat`,
  Windows `netstat` / PowerShell `Get-NetTCPConnection`)
- Cross-platform dispatcher

#### Documentation
- `README.md` — full project overview, install, usage, roadmap
- `LICENSE` — MIT License (© 2026 NMS & Md Siyam Mahmud)
- `LEGAL.md` — responsible-use policy and legal disclaimer
- `CHANGELOG.md` — this file
- `CONTRIBUTING.md` — contributor guide

#### Project Infrastructure
- `requirements.txt` — `rich`, `cryptography`, `prompt-toolkit`
- Modular architecture with `SCHEMA` manifest standard
- Structured `dict` return contract for all modules
- `_LAST_RESULT` global hook for future AI integration

### Changed
- All modules now expose `SCHEMA` and support `run(args=None)`
- `run_tool()` in hub no longer double-prompts for "Press Enter"
- Tool modules own their pause only in `__main__` block

### Fixed
- **Subfinder**: replaced unreliable `threading.active_count()` busy-wait
  with `ThreadPoolExecutor`; added hard DNS timeout
- **Nmap**: IPv4-only resolution replaced with dual-stack `getaddrinfo`
- **Nmap**: unused `COMMON_SERVICES` expanded; banner grabbing added
- **Hub**: double "Press Enter" prompt after tool execution
- **Hub**: `_LAST_RESULT` initialization (was missing, caused `NameError`)

### Security
- PBKDF2-HMAC-SHA256 with 100,000 iterations for password-derived keys
- Fernet (AES-128-CBC + HMAC-SHA256) for authenticated encryption

---

## [0.0.0] — 2026-09-01 (Foundation)

### Added
- Initial repository structure
- Architecture planning and design
- Development environment setup
- Core CLI skeleton (`aegis-hub.py` prototype)
- Initial documentation drafts

> This version was never publicly released. It exists only to mark the
> start of the project's development.

---

## 🔗 Version Links

- **Compare 0.1.0 → Unreleased:**
  `https://github.com/novemixs/AegisCLI-NMS/compare/v0.1.0...HEAD`
- **Release v0.1.0:**
  `https://github.com/novemixs/AegisCLI-NMS/releases/tag/v0.1.0`

---

## 📖 Legend

| Type | Meaning |
|---|---|
| **Added** | New features |
| **Changed** | Changes to existing functionality |
| **Deprecated** | Soon-to-be-removed features |
| **Removed** | Removed features |
| **Fixed** | Bug fixes |
| **Security** | Security-related changes |

---

<div align="center">

*Last updated: 2026-09-12*

[← Back to README](README.md) · [LEGAL](LEGAL.md) · [CONTRIBUTING](CONTRIBUTING.md)

</div>
