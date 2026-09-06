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

*«One CLI. Modular Security. AI-assisted automation — coming soon.»*

![License](https://img.shields.io/badge/License-MIT-2ea44f?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active%20Development-orange?style=for-the-badge)
![Goal](https://img.shields.io/badge/Roadmap-630%2B%20Tools-1462c9?style=for-the-badge)

</div>

---

AegisCLI-NMS is an open-source, modular cybersecurity command-line toolkit built with Python.

The goal is simple: provide a **unified CLI** for common security workflows instead of requiring users to manually switch between multiple security utilities.

> ⚠️ **AegisCLI is currently in early development.**
> Several features described below are planned and are not yet available.

<br>

## 🔍 What is AegisCLI?

Modern security workflows often require many different tools for reconnaissance, analysis, auditing, and testing.

**Before — juggling multiple tools:**

```bash
nmap -sV -p 80,443 target.com
subfinder -d target.com
hashid "5f4dcc3b5aa765d61d8327deb882cf99"
```

**After — one unified interface:**

```bash
aegis scan target.com
aegis find subdomains target.com
aegis identify hash 5f4dcc3b5aa765d61d8327deb882cf99
```

The long-term goal is to combine native modules, external security-tool integrations, and an AI-assisted command engine into one modular platform.

<br>

## ✨ Features

<table>
<tr><td width="60">🧩</td><td><b>Modular Architecture</b><br>Independent modules — develop, maintain, enable, or remove freely.</td></tr>
<tr><td>🌐</td><td><b>Network Reconnaissance</b><br>Port scanning, service detection, host discovery, structured results.</td></tr>
<tr><td>🔎</td><td><b>Subdomain Enumeration</b><br>Unified interface across multiple enumeration engines.</td></tr>
<tr><td>#️⃣</td><td><b>Hash Analyzer</b><br>Identify common hash formats with expanding format support.</td></tr>
<tr><td>🔒</td><td><b>System Security Auditor</b><br>Detects misconfigurations, weak settings, exposed services.</td></tr>
<tr><td>🛡️</td><td><b>Threat Detection & Malware Analysis</b><br>Suspicious file analysis, indicators, threat scoring, reports.</td></tr>
<tr><td>🤖</td><td><b>AI Command Engine</b><br>Natural-language task execution via local LLMs (LangChain + Ollama).</td></tr>
</table>

<br>

### 🌐 Network Reconnaissance

Planned functionality: port scanning · service detection · host discovery · basic network enumeration · structured scan results.

```bash
aegis scan target.com
```

---

### 🔎 Subdomain Enumeration

AegisCLI will provide a unified interface for discovering subdomains, with future versions integrating multiple enumeration engines.

```bash
aegis find subdomains target.com
```

---

### #️⃣ Hash Analyzer

The Hash Analyzer is planned to identify common hash formats and provide analysis information. Supported formats will expand over time.

```bash
aegis identify hash 5f4dcc3b5aa765d61d8327deb882cf99
```

---

### 🔒 System Security Auditor

Planned checks include:

- File permissions
- Misconfigurations
- Weak security settings
- Exposed services
- Basic system hardening issues

---

### 🤖 AI Command Engine

> **Planned Feature**

AegisCLI is planned to include an AI-assisted command engine using local AI models.

**Proposed stack:** Python · LangChain · Ollama · Local LLMs

```
User:
Find open web services on target.com

AegisCLI:
→ Interprets the request
→ Selects the appropriate module/tool
→ Executes the permitted operation
→ Presents structured results
```

AI execution will be designed with safety controls and explicit command boundaries rather than allowing unrestricted arbitrary command execution.

---

### 🛠️ Tool Integration

A major long-term goal of AegisCLI is integrating existing security utilities through a common interface — potentially including **Nmap, Subfinder, Wireshark, Burp Suite, Metasploit**, hash analysis utilities, and additional open-source tools.

> **Long-Term Goal:** «630+ security tools/modules» — this is a roadmap target, not the current number of integrated tools.

```
Native Modules
      +
External Tool Integrations
      +
AI Command Engine
      ↓
Unified Security CLI
```

---

### 🛡️ Threat Detection & Malware Analysis

> **Planned Feature**

Potential capabilities: suspicious file analysis · basic malware indicators · hash analysis · file metadata inspection · threat scoring · security reports.

*This module is planned and should not be considered a full antivirus replacement.*

<br>

## 🗺️ Development Roadmap

| Phase | Timeline | Target | Focus |
|---|---|---|---|
| **Phase 0 — Foundation** | Sep 2026 → Feb 2027 | — | Planning, repo setup, architecture ✅ |
| **Phase 1 — Core Modules** | Feb → May 2027 | v0.1 | Recon, Enumeration, Hash Analyzer, Auditor |
| **Phase 2 — AI & Tool Integration** | May → Aug 2027 | v0.5 Beta | AI Engine, Ollama/LangChain, 100+ tools |
| **Phase 3 — Expanded Platform** | Aug → Dec 2027 | v1.0 | 400+ tools, Threat Detection, Plugin ecosystem |
| **Phase 4 — Community & Ecosystem** | 2028+ | — | 630+ tools, community plugins, enterprise features |

<details>
<summary><b>📋 Full detailed roadmap (click to expand)</b></summary>

<br>

**Phase 0 — Foundation** *(September 2026 → February 2027)*
- [x] Project planning
- [x] Repository setup
- [x] Architecture planning
- [ ] Core CLI architecture
- [ ] Development environment
- [ ] Initial documentation

**Phase 1 — Core Modules** *(February → May 2027 · Target: v0.1)*
- [ ] Network Reconnaissance
- [ ] Subdomain Enumeration
- [ ] Hash Analyzer
- [ ] System Security Auditor
- [ ] Modular plugin architecture
- [ ] CLI command structure
- [ ] Basic output formatting
- [ ] Unit tests

**Phase 2 — AI & Tool Integration** *(May → August 2027 · Target: v0.5 Beta)*
- [ ] AI Command Engine
- [ ] Ollama integration
- [ ] LangChain integration
- [ ] Tool-selection layer
- [ ] 100+ tool integrations target
- [ ] Improved result parsing
- [ ] Configuration system
- [ ] Logging system

**Phase 3 — Expanded Platform** *(August → December 2027 · Target: v1.0)*
- [ ] Expanded security modules
- [ ] 400+ tool integrations target
- [ ] Threat detection module
- [ ] Malware analysis capabilities
- [ ] Improved AI workflow
- [ ] Plugin ecosystem
- [ ] Documentation expansion
- [ ] Stable CLI API

**Phase 4 — Community & Ecosystem** *(2028+)*
- [ ] 630+ tools/modules target
- [ ] Community plugins
- [ ] Bug bounty workflow support
- [ ] Security research integrations
- [ ] Performance improvements
- [ ] Enterprise-oriented features
- [ ] Long-term stable releases

</details>

<br>

## ⚙️ Installation

> ⚠️ AegisCLI is currently under active development. Installation instructions may change before the first stable release.

```bash
# Clone the repository
git clone https://github.com/novemixs/AegisCLI-NMS.git

# Enter the project
cd AegisCLI-NMS

# Install dependencies
pip install -r requirements.txt

# Run AegisCLI
python aegis.py --help
```

<br>

## 🧰 Technology Stack

| Component | Technology |
|---|---|
| Language | Python 3.10+ |
| CLI | Click / Typer |
| AI Engine | LangChain + Ollama |
| Containerization | Docker |
| Package Manager | pip |
| Distribution | PyPI |
| Version Control | Git / GitHub |

<br>

## 🏗️ Architecture

```
                    ┌──────────────────┐
                    │     AegisCLI     │
                    │   Command Line   │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │  Command Engine  │
                    └────────┬─────────┘
                             │
             ┌───────────────┼───────────────┐
             │               │               │
        ┌────▼────┐     ┌────▼─────┐    ┌────▼─────┐
        │  Recon  │     │ Analysis │    │   Audit  │
        │ Modules │     │  Modules │    │  Modules │
        └────┬────┘     └────┬─────┘    └────┬─────┘
             │               │               │
             └───────────────┼───────────────┘
                             │
                    ┌────────▼─────────┐
                    │ Tool Integration │
                    └──────────────────┘
```

*The architecture may evolve significantly during development.*

<br>

## 🔐 Responsible Use

AegisCLI is intended for: authorized security testing · security research · CTF environments · lab environments · defensive security · system auditing · educational purposes.

> **Do not use AegisCLI against systems or networks without authorization.**

Users are responsible for complying with all applicable laws and regulations. The project maintainers are not responsible for misuse of the software.

<br>

## 🤝 Contributing

AegisCLI is an open-source project and contributions are welcome — Python development · security research · module development · tool integrations · AI engineering · documentation · CLI/UX design · testing · bug reports.

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

<br>

## 📊 Project Status

| Component | Status |
|---|---|
| Project Architecture | 🟡 Planning |
| Core CLI | 🟡 Development |
| Network Recon | 🔵 Planned |
| Subdomain Enumeration | 🔵 Planned |
| Hash Analyzer | 🔵 Planned |
| System Auditor | 🔵 Planned |
| AI Engine | 🔵 Planned |
| Tool Integrations | 🔵 Planned |
| Threat Detection | 🔵 Planned |
| 630+ Tools | 🔵 Long-term Goal |

**Legend:** 🟢 Available &nbsp;·&nbsp; 🟡 In Development &nbsp;·&nbsp; 🔵 Planned &nbsp;·&nbsp; 🔴 Deprecated

<br>

## 💰 Support the Project

AegisCLI is intended to remain free and open source. Development may require funding for:

| Item | Estimated Cost |
|---|---|
| Development PC | $1,500 |
| Cloud Server — 1 year | $300 |
| Domain & SSL | $50 |
| Testing / Development Tools | $150 |
| **Total** | **$2,000** |

⭐ Star the repository &nbsp;·&nbsp; 🐛 Report bugs &nbsp;·&nbsp; 💡 Suggest features &nbsp;·&nbsp; 🤝 Contribute code &nbsp;·&nbsp; 📢 Share the project &nbsp;·&nbsp; 💖 Sponsor when available

<br>

## 📬 Contact

**Developer:** Md Siyam Mahmud

📧 [novemixs@gmail.com](mailto:novemixs@gmail.com) &nbsp;·&nbsp; 🐙 [@siyam201](https://github.com/siyam201) &nbsp;·&nbsp; 📁 [AegisCLI-NMS](https://github.com/novemixs/AegisCLI-NMS)

<br>

## 📄 License

Released under the **MIT License** — Copyright © 2026 Md Siyam Mahmud. See [LICENSE](LICENSE) for the complete license text.

<br>

<div align="center">

### ⚔️ AegisCLI
*«One CLI. One modular security platform.»*

⭐ **Star the repository if you want to follow the development.**

[**→ GitHub Repository**](https://github.com/novemixs/AegisCLI-NMS)

</div>
