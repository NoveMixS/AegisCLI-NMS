<div align="center">

<svg width="220" height="220" viewBox="0 0 220 220" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="shieldSteel" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#f5f7fa"/>
      <stop offset="45%" stop-color="#c8d2dc"/>
      <stop offset="100%" stop-color="#7c8a99"/>
    </linearGradient>
    <linearGradient id="shieldBlue" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#4fa8ff"/>
      <stop offset="55%" stop-color="#1462c9"/>
      <stop offset="100%" stop-color="#062a63"/>
    </linearGradient>
    <linearGradient id="bladeGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="50%" stop-color="#b9c4cf"/>
      <stop offset="100%" stop-color="#5c6b7a"/>
    </linearGradient>
    <filter id="softShadow" x="-30%" y="-30%" width="160%" height="160%">
      <feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#0a1d3d" flood-opacity="0.35"/>
    </filter>
  </defs>

  <g filter="url(#softShadow)">
    <path d="M110 12 L188 40 C188 100 176 150 110 200 C44 150 32 100 32 40 Z"
          fill="url(#shieldSteel)" stroke="#3a4652" stroke-width="2"/>
    <path d="M110 24 L174 47 C174 98 164 142 110 186 C56 142 46 98 46 47 Z"
          fill="url(#shieldBlue)"/>
    <path d="M110 24 L174 47 C174 98 164 142 110 186 Z" fill="#ffffff" opacity="0.06"/>
  </g>

  <g filter="url(#softShadow)">
    <rect x="104" y="28" width="12" height="92" rx="3" fill="url(#bladeGrad)"/>
    <path d="M110 20 L124 34 L110 44 L96 34 Z" fill="url(#bladeGrad)"/>
    <rect x="86" y="100" width="48" height="10" rx="2" fill="#dfe6ec"/>
    <rect x="100" y="108" width="20" height="46" rx="4" fill="#1c2733"/>
    <rect x="107" y="108" width="6" height="46" fill="#4fa8ff" opacity="0.7"/>
  </g>
</svg>

# ⚔️ AegisCLI

### All-in-One Modular Security CLI Toolkit

*«One CLI. Modular Security. Built in the open.»*

![Release](https://img.shields.io/badge/Release-v0.1%20%E2%80%94%20Sep%2012%2C%202026-2ea44f?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-2ea44f?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active%20Development-orange?style=for-the-badge)
![Roadmap](https://img.shields.io/badge/Roadmap-630%2B%20Tools-1462c9?style=for-the-badge)

**🎉 v0.1 is live — 4 working modules + interactive Hub CLI.**

</div>

---

> **⚡ Fast Release — September 12, 2026**
> AegisCLI **v0.1** ships with four fully working native modules and a Rich-powered interactive Hub. The AI command engine and 630+ external tool integrations remain on the roadmap.

<br>

## 🚀 What's Available Now (v0.1)

<table>
<tr><td width="40">✅</td><td><b>Interactive Hub CLI</b><br>Rich terminal UI · numbered tool menu · search · favorites · command history · JSON output for scripting.</td></tr>
<tr><td>✅</td><td><b>Port Scanner</b> <code>nmap</code><br>Multi-threaded TCP scan · IPv4 &amp; IPv6 · service detection · banner grabbing.</td></tr>
<tr><td>✅</td><td><b>Subdomain Enumerator</b> <code>subfinder</code><br>DNS brute-force · 250+ built-in wordlist · custom wordlists · per-lookup hard timeout.</td></tr>
<tr><td>✅</td><td><b>Hash Analyzer</b> <code>hash</code><br>Identify hash format · compute MD5/SHA family · AES encrypt/decrypt (Fernet + PBKDF2).</td></tr>
<tr><td>✅</td><td><b>System Security Auditor</b> <code>audit</code><br>World-writable file scan · listening-services enumeration · cross-platform (Linux / Windows).</td></tr>
</table>

<br>

### 🎬 Live Demo

```text
⚔️  Aegis-CLI — AI-Powered Modular Security CLI Toolkit
    Version: 2.1  |  Tools Loaded: 4

  SL   Tool Name     Description                                Version   Category
 ───  ────────────  ─────────────────────────────────────────  ────────  ─────────
  1   audit         Local system security audit                1.1       System
  2   hash          Identify · compute · encrypt/decrypt       1.2       Cryptography
  3   nmap          Fast multi-threaded TCP port scanner       2.0       Recon
  4   subfinder     DNS brute-force subdomain discovery        2.0       Recon

aegis-hub> 3
▶ Loading tool: nmap (v2.0)

Target (host or IP): scanme.nmap.org
Ports (default 1-1000):
Threads (default 200):
Timeout per port sec (default 1.0):
Grab service banners? (y/N): y

[*] Scanning scanme.nmap.org (45.33.32.156, IPv4) — 1000 ports, 200 threads

      Open ports on scanme.nmap.org (45.33.32.156)
 ┏━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
 ┃ Port ┃ Service ┃ Banner                      ┃
 ┡━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
 │   22 │ ssh     │ SSH-2.0-OpenSSH_6.6.1p1     │
 │   80 │ http    │ HTTP/1.1 200 OK             │
 └──────┴─────────┴─────────────────────────────┘
3 open port(s) found in 5.2s.
```

<br>

## 🔍 What is AegisCLI?

Modern security workflows often require many different tools. Instead of juggling them, AegisCLI gives you **one unified CLI** with a numbered menu, consistent output, and a modular plugin system.

**Before — juggling multiple tools:**

```bash
nmap -sV -p 80,443 target.com
subfinder -d target.com
hashid "5f4dcc3b5aa765d61d8327deb882cf99"
```

**After — one hub:**

```bash
python aegis-hub.py
# → pick a tool by number
# → answer 2–3 prompts
# → get structured results
```

<br>

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/novemixs/AegisCLI-NMS.git
cd AegisCLI-NMS

# Install dependencies
pip install -r requirements.txt

# Launch the Hub
python aegis-hub.py
```

**`requirements.txt`:**

```
rich
cryptography
prompt-toolkit
```

**Requirements:** Python 3.10+ · pip · Linux / macOS / Windows

<br>

## 🛠️ Usage

### Interactive Hub (recommended)

```bash
python aegis-hub.py
```

Inside the hub:

| Command | What it does |
|---|---|
| `<number>` or `<tool-name>` | Run a tool (e.g. `3` or `nmap`) |
| `info <tool>` | Show module details |
| `search <keyword>` | Find tools by name/description |
| `favorite <tool>` | Star / unstar a tool |
| `favlist` | List favorites |
| `history` | Show recent commands |
| `reload` | Hot-reload all tools (no restart) |
| `set <key> <value>` | Change config |
| `config` | Show current config |
| `clear` | Clear screen |
| `help` | Show help panel |
| `exit` / `q` | Quit |

### Non-interactive / Scripting

Each module can also be run standalone with `--json` for pipelines:

```bash
# Port scan with JSON output
python tools/nmap.py scanme.nmap.org --json > scan.json

# Subdomain enumeration
python tools/subfinder.py example.com --json -t 100

# Custom port range, no banner
python tools/nmap.py 127.0.0.1 -p 22,80,443,8080 --no-banner
```

<br>

## 🧩 Modules — v0.1 Detail

### 🌐 `nmap` — TCP Port Scanner
- Multi-threaded (`ThreadPoolExecutor`, default 200 workers)
- IPv4 **and** IPv6 via `getaddrinfo`
- 100+ common-service name map
- Best-effort banner grabbing (SSH, HTTP, FTP, SMTP…)
- Hard per-port timeout

### 🔎 `subfinder` — Subdomain Enumerator
- Built-in ~250 common subdomain wordlist
- Custom wordlist support
- Per-lookup **hard timeout** (no hangs on dead DNS)
- Bounded concurrency via `ThreadPoolExecutor`
- `@` marker for apex domain

### #️⃣ `hash` — Hash Analyzer & Crypto
- Identify: MD5, SHA-1/224/256/384/512, NTLM, bcrypt, sha512crypt, md5crypt
- Compute: MD5, SHA-1/224/256/384/512
- **AES encrypt/decrypt** via Fernet + PBKDF2 (100k iterations)
- Failed-attempt lockout protection

### 🔒 `audit` — System Security Auditor
- World-writable file scan (Linux)
- Listening-services enumeration (Linux `ss`/`netstat`, Windows `netstat`/PowerShell)
- Cross-platform dispatcher

<br>

## 🗺️ Roadmap

| Phase | Timeline | Target | Status |
|---|---|---|---|
| **Phase 0 — Foundation** | Sep 1 → Sep 11, 2026 | Setup | ✅ Done |
| **Phase 1 — Core Modules** | **Sep 12, 2026** | **v0.1** | ✅ **Released** |
| **Phase 2 — AI Engine** | Oct 2026 → Jan 2027 | v0.5 Beta | 🟡 In Development |
| **Phase 3 — Expanded Platform** | Feb → Jun 2027 | v1.0 | 🔵 Planned |
| **Phase 4 — Community** | Q3 2027+ | — | 🔵 Planned |

<details>
<summary><b>📋 Detailed roadmap (click to expand)</b></summary>

<br>

**Phase 0 — Foundation** *(Sep 1 → Sep 11, 2026)* ✅
- [x] Project planning
- [x] Repository setup
- [x] Architecture planning
- [x] Development environment
- [x] Core CLI skeleton
- [x] Initial documentation

**Phase 1 — Core Modules — v0.1** ✅ *(Released Sep 12, 2026)*
- [x] Interactive Hub CLI (Rich)
- [x] Port Scanner module
- [x] Subdomain Enumerator module
- [x] Hash Analyzer module
- [x] System Security Auditor module
- [x] `SCHEMA` manifest on modules
- [x] Structured `dict` return from every module
- [x] `--json` output for scripting
- [x] Command history · favorites · search · reload

**Phase 2 — AI & Tool Integration** *(Oct 2026 → Jan 2027 · v0.5 Beta)*
- [ ] AI Command Engine (LangChain + Ollama)
- [ ] Natural-language → tool selection
- [ ] Tool-selection layer using `SCHEMA`
- [ ] 100+ external tool integrations
- [ ] Configuration system expansion
- [ ] Structured logging

**Phase 3 — Expanded Platform** *(Feb → Jun 2027 · v1.0)*
- [ ] 400+ tool integrations
- [ ] Threat detection module
- [ ] Malware analysis capabilities
- [ ] Plugin ecosystem (third-party modules)
- [ ] Stable CLI API

**Phase 4 — Community & Ecosystem** *(Q3 2027+)*
- [ ] 630+ tools/modules
- [ ] Community plugin registry
- [ ] Bug-bounty workflow support
- [ ] Enterprise features

</details>

<br>

## 🏗️ Architecture (v0.1)

```
                    ┌──────────────────┐
                    │   aegis-hub.py   │   ← Interactive hub
                    │   (Rich UI)      │
                    └────────┬─────────┘
                             │  dynamic import
                             ▼
                    ┌──────────────────┐
                    │  tools/          │
                    │  ├── nmap.py     │   ← each exposes:
                    │  ├── subfinder.py│      description
                    │  ├── hash.py     │      SCHEMA
                    │  └── audit.py    │      run(args) -> dict
                    └──────────────────┘
                             │
                             ▼
                    Structured dict result
                             │
                             ▼
              (Phase 2) AI Engine reads _LAST_RESULT
```

<br>

## 🤝 Contributing

Contributions are welcome — Python dev · security research · module development · tool integrations · AI engineering · docs · CLI/UX · testing.

```bash
git clone https://github.com/novemixs/AegisCLI-NMS.git
cd AegisCLI-NMS
git checkout -b feature/your-feature

# Make your changes

git add .
git commit -m "Add: your feature"
git push origin feature/your-feature
```

Then open a Pull Request.

**Every module must expose:**

```python
description = "Short description"
__version__ = "x.y"
__author__  = "Your Name"
__category__ = "Recon"          # Recon / Cryptography / System / …
SCHEMA      = { ... }           # args manifest for the AI engine

def run(args: dict | None = None) -> dict:
    """Interactive if args is None. Return a structured dict."""
```

See existing modules in `tools/` for the reference pattern.

<br>

## 🔐 Responsible Use

AegisCLI is intended **only** for:

- Authorized security testing
- Security research
- CTF / lab environments
- Defensive security & system auditing
- Educational purposes

> **⚠️ Do not use AegisCLI against systems or networks without explicit authorization.**

You are responsible for complying with all applicable laws. The maintainers are not responsible for misuse.

<br>

## 📊 Project Status

| Component | Status |
|---|---|
| Interactive Hub CLI | 🟢 Available |
| Port Scanner (`nmap`) | 🟢 Available |
| Subdomain Enum (`subfinder`) | 🟢 Available |
| Hash Analyzer (`hash`) | 🟢 Available |
| System Auditor (`audit`) | 🟢 Available |
| AI Engine | 🔵 Planned |
| 100+ Tool Integrations | 🔵 Planned |
| 630+ Tools | 🔵 Long-term Goal |

**Legend:** 🟢 Available &nbsp;·&nbsp; 🟡 In Development &nbsp;·&nbsp; 🔵 Planned

<br>

## 💰 Support the Project

AegisCLI is free and open source. Development costs:

| Item | Estimated |
|---|---|
| Development PC | $1,500 |
| Cloud Server — 1 year | $300 |
| Domain & SSL | $50 |
| Testing / Dev Tools | $150 |
| **Total** | **$2,000** |

⭐ Star · 🐛 Report bugs · 💡 Suggest features · 🤝 Contribute · 📢 Share · 💖 Sponsor (soon)

<br>

## 📬 Contact

**Md Siyam Mahmud**

📧 [novemixs@gmail.com](mailto:novemixs@gmail.com) &nbsp;·&nbsp;
🐙 [@siyam201](https://github.com/siyam201) &nbsp;·&nbsp;
📁 [AegisCLI-NMS](https://github.com/novemixs/AegisCLI-NMS)

<br>

## 📄 License

Released under the **MIT License** — Copyright © 2026 Md Siyam Mahmud. See [LICENSE](LICENSE).

<br>

<div align="center">

### ⚔️ AegisCLI v0.1

*«One CLI. Modular Security. Built in the open.»*

**Released September 12, 2026**

⭐ **Star the repository if you want to follow development.**

[**→ GitHub Repository**](https://github.com/novemixs/AegisCLI-NMS)

</div>
