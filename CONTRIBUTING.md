# 🤝 Contributing to AegisCLI

First of all — **thank you** for considering a contribution to AegisCLI!
This project exists because of people like you who care about open-source
security tooling.

This document explains how to contribute effectively: how to report bugs,
suggest features, write code, and get your Pull Request merged.

---

## 📖 Table of Contents

- [Code of Conduct](#-code-of-conduct)
- [Ways to Contribute](#-ways-to-contribute)
- [Getting Started](#-getting-started)
- [Development Setup](#-development-setup)
- [Module Development Guide](#-module-development-guide)
- [Coding Standards](#-coding-standards)
- [Testing](#-testing)
- [Commit Message Convention](#-commit-message-convention)
- [Pull Request Process](#-pull-request-process)
- [Reporting Bugs](#-reporting-bugs)
- [Suggesting Features](#-suggesting-features)
- [Security Disclosures](#-security-disclosures)
- [Legal & Ethical Requirements](#-legal--ethical-requirements)
- [Recognition](#-recognition)

---

## 📜 Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:

1. **Be respectful** — treat everyone with courtesy, regardless of
   experience level, background, or identity.
2. **Be constructive** — critique ideas, not people. Focus on solutions.
3. **Be patient** — maintainers are volunteers. Responses may take days.
4. **Be honest** — no plagiarism, no fake claims, no misrepresentation.
5. **Be collaborative** — this is a community project, not a competition.
6. **Be ethical** — see [LEGAL.md](LEGAL.md). Do not contribute malicious
   code, attack payloads, or unauthorized-access tooling.

Unacceptable behavior includes harassment, discrimination, doxxing,
spam, and any form of abuse. Violations may result in permanent ban.

---

## 🎯 Ways to Contribute

You don't need to be a Python expert. Every contribution helps:

| Type | Examples |
|---|---|
| 🐛 **Bug reports** | Crash, incorrect output, edge case failure |
| 💡 **Feature ideas** | New module, UX improvement, integration |
| 📝 **Documentation** | Fix typos, improve clarity, add examples |
| 🌍 **Translations** | README / LEGAL in other languages |
| 🧪 **Testing** | Try AegisCLI on your OS, report results |
| 🎨 **Design** | CLI layout, banners, color schemes |
| 🔐 **Security review** | Review code for vulnerabilities |
| 🔧 **Code** | New modules, bug fixes, refactors |
| 📢 **Advocacy** | Share the project, write blog posts |
| 💰 **Sponsorship** | See README's "Support" section |

---

## 🚀 Getting Started

### 1. Fork the repository

Click the **Fork** button at
[github.com/novemixs/AegisCLI-NMS](https://github.com/novemixs/AegisCLI-NMS).

### 2. Clone your fork

```bash
git clone https://github.com/YOUR-USERNAME/AegisCLI-NMS.git
cd AegisCLI-NMS
```

### 3. Add upstream remote

```bash
git remote add upstream https://github.com/novemixs/AegisCLI-NMS.git
git fetch upstream
```

### 4. Create a feature branch

```bash
git checkout -b feature/your-feature-name
# or for bug fixes:
git checkout -b fix/short-description
```

---

## 🛠️ Development Setup

### Requirements

- **Python 3.10 or newer** (uses `dict | None` union syntax)
- `pip` and `venv`
- Git
- (Optional) `git` CLI, `docker`, `make`

### Setup

```bash
# 1. Create virtual environment
python -m venv .venv

# 2. Activate
# Linux/macOS:
source .venv/bin/activate
# Windows (PowerShell):
.venv\Scripts\Activate.ps1

# 3. Upgrade pip
python -m pip install --upgrade pip

# 4. Install runtime dependencies
pip install -r requirements.txt

# 5. (Optional) Install development tools
pip install ruff black mypy pytest pytest-cov
```

### Run the hub

```bash
python aegis-hub.py
```

### Run a tool standalone

```bash
python tools/nmap.py --help
python tools/subfinder.py --help
```

---

## 🧩 Module Development Guide

AegisCLI's power comes from its **module system**. Every tool in `tools/`
must follow the same interface contract.

### Required module interface

```python
#!/usr/bin/env python3
"""
tools/your_module.py — Short description.

AegisCLI hub module. Exposes:
    description  : str
    SCHEMA       : dict
    run(args)    : dict
"""

from rich.console import Console
console = Console()

# ---- 1. Metadata (required) ----------------------------------------
description = "Short, one-line description of what this tool does"
__version__ = "1.0"
__author__  = "Your Name"
__category__ = "Recon"   # Recon / Cryptography / System / Analysis / AI

# ---- 2. Machine-readable schema (required) -------------------------
SCHEMA = {
    "name": "your_module",
    "description": "Longer description for the AI engine.",
    "args": {
        "target":  {"type": "string", "required": True,
                    "help": "What this argument is."},
        "option":  {"type": "bool", "required": False, "default": False},
    },
    "returns": {
        "target":  "string",
        "results": "list",
    },
}

# ---- 3. Entry point (required) -------------------------------------
def run(args: dict | None = None) -> dict:
    """
    Run the module.

    Interactive when args is None. Non-interactive otherwise.
    Return a structured dict — always.
    """
    if args is None:
        # Ask user for inputs via console.input()
        target = console.input("[cyan]Target: [/cyan]").strip()
        args = {"target": target, "json": False}

    target = args.get("target")
    emit_json = args.get("json", False)

    # ... do the work ...

    result = {
        "target": target,
        "results": [],
    }

    if emit_json:
        import json
        print(json.dumps(result, indent=2))
    else:
        console.print(f"[green]Done: {target}[/green]")

    return result

# ---- 4. Standalone CLI (optional but recommended) ------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("target", nargs="?")
    parser.add_argument("--json", action="store_true")
    opts = parser.parse_args()

    if opts.target:
        run({"target": opts.target, "json": opts.json})
        if not opts.json:
            input("\nPress Enter to exit...")
    else:
        run()
        input("\nPress Enter to exit...")
```

### Module rules

1. **Never call `input()` inside `run()`** — the hub owns the pause.
   Only the `if __name__ == "__main__":` block may pause.
2. **Always return a `dict`** — this is the contract with the future AI
   engine. Even on error, return a structured dict (with `"error": "..."`).
3. **Expose `SCHEMA`** — the AI engine reads it to select tools.
4. **Support `--json`** — needed for scripting and pipelines.
5. **Handle `KeyboardInterrupt`** — never crash the hub.
6. **Log errors gracefully** — never `sys.exit()` inside `run()`.

### Testing your module

```bash
# Standalone interactive
python tools/your_module.py

# Standalone non-interactive
python tools/your_module.py example.com --json

# Via hub
python aegis-hub.py
# → select your module by number
```

---

## 📐 Coding Standards

### Style

- **PEP 8** compliance
- **Line length:** 88 characters (Black default)
- **Type hints** on all public functions
- **Docstrings** on all public functions (Google or NumPy style)
- **f-strings** over `.format()` or `%`
- **`pathlib`** over `os.path` where practical

### Naming

| Element | Convention | Example |
|---|---|---|
| Modules | `snake_case` | `subfinder.py` |
| Functions | `snake_case` | `enumerate_subdomains` |
| Classes | `PascalCase` | `ScanResult` |
| Constants | `UPPER_SNAKE` | `DEFAULT_TIMEOUT` |
| Private | `_leading_underscore` | `_scan_one` |

### Formatting tools

```bash
# Format
black .

# Lint
ruff check .

# Type check
mypy tools/ aegis-hub.py
```

Install pre-commit hooks (recommended):

```bash
pip install pre-commit
pre-commit install
```

### Rich usage

- Use `console.print()` instead of `print()` for user-facing output
- Use `[bold]`, `[cyan]`, `[red]` markup — but keep it minimal
- Prefer `Table` for structured results
- Use `Progress` for long operations

---

## 🧪 Testing

Currently AegisCLI has minimal automated tests. Help us change that!

### Running existing tests

```bash
pytest
```

### Writing tests

- Place tests in `tests/` directory
- One test file per module: `test_nmap.py`, `test_subfinder.py`
- Use `pytest` fixtures for common setup
- Mock network calls — **never** hit real targets in tests
- Aim for **>80% coverage** on new modules

Example:

```python
# tests/test_subfinder.py
from tools.subfinder import _parse_ports, resolve

def test_parse_ports_range():
    assert _parse_ports("1-5") == [1, 2, 3, 4, 5]

def test_resolve_localhost():
    assert resolve("localhost", timeout=1) is not None
```

---

## 💬 Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/).

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

| Type | Use for |
|---|---|
| `feat` | A new feature |
| `fix` | A bug fix |
| `docs` | Documentation only |
| `style` | Formatting (no code change) |
| `refactor` | Code change without behavior change |
| `perf` | Performance improvement |
| `test` | Adding or fixing tests |
| `chore` | Build, deps, tooling |
| `security` | Security-related change |

### Examples

```bash
feat(nmap): add IPv6 support via getaddrinfo

fix(subfinder): replace active_count busy-wait with ThreadPoolExecutor

docs(readme): add live demo section

chore(deps): bump rich to 13.9.4

security(hash): raise PBKDF2 iterations to 100000
```

---

## 🔀 Pull Request Process

### Before you open a PR

1. ✅ Code follows the module contract (see above)
2. ✅ `black .` and `ruff check .` pass
3. ✅ `pytest` passes
4. ✅ Your module works both interactively and with `--json`
5. ✅ You've added tests (if code)
6. ✅ You've updated `CHANGELOG.md` under `[Unreleased]`
7. ✅ You've updated `README.md` if user-facing

### PR title

Use the same convention as commit messages:

```
feat(audit): add Windows registry check
fix(hub): handle empty tool list gracefully
docs(legal): add EU AI Act section
```

### PR description template

```markdown
## What does this PR do?
Brief description.

## Why?
Motivation / linked issue (e.g. "Closes #42").

## How to test
```bash
python tools/your_module.py example.com --json
```

## Checklist
- [ ] Follows module contract (description, SCHEMA, run(args))
- [ ] Handles KeyboardInterrupt
- [ ] Returns structured dict
- [ ] Supports --json
- [ ] Added tests
- [ ] Updated CHANGELOG.md
- [ ] Ran black + ruff + pytest

## Screenshots (if UI)
```

### Review process

1. A maintainer will review within **7 days** (usually faster)
2. Address feedback by pushing new commits (do **not** force-push
   during review)
3. Once approved, a maintainer will squash-merge your PR

### What gets rejected

- Code that violates the module contract
- Modules targeting third-party systems by default
- Attack payloads or exploit code
- Code without tests (for non-trivial features)
- PRs that don't update `CHANGELOG.md`
- Anything violating [LEGAL.md](LEGAL.md)

---

## 🐛 Reporting Bugs

### Before filing

1. Search [existing issues](https://github.com/novemixs/AegisCLI-NMS/issues)
2. Try the **latest `main` branch** — the bug may be fixed
3. Reproduce on a **clean environment** (fresh venv)

### Bug report template

```markdown
## Bug description
Clear, concise description.

## Steps to reproduce
1. Run `python aegis-hub.py`
2. Select tool `3` (nmap)
3. Enter target `example.com`
4. Observe ...

## Expected behavior
What you expected to happen.

## Actual behavior
What actually happened. Include the full traceback.

## Environment
- AegisCLI version: v0.1.0
- OS: Ubuntu 22.04 / Windows 11 / macOS 14
- Python: 3.11.4
- Install method: git clone / pip

## Logs
Paste relevant lines from `aegis.log` (redact sensitive info).
```

---

## 💡 Suggesting Features

Open an issue with the `enhancement` label. Include:

- **Use case** — what problem does this solve?
- **Proposed solution** — how would you like it to work?
- **Alternatives** — what else did you consider?
- **Scope** — is this Phase 2/3 territory or urgent?

We prioritize features that:

1. Align with the [roadmap](README.md#-roadmap)
2. Help the widest range of users
3. Are feasible to maintain long-term
4. Don't require proprietary services

---

## 🔐 Security Disclosures

**Do NOT open a public issue for security vulnerabilities.**

Instead:

1. Email **[novemixs@gmail.com](mailto:novemixs@gmail.com)**
2. Subject: `[AEGISCLI SECURITY] <short summary>`
3. Include:
   - Affected version(s)
   - Reproduction steps
   - Impact assessment
   - Suggested fix (if any)
   - Your disclosure timeline preference (default: 90 days)

We will:

- Acknowledge receipt within **72 hours**
- Provide a preliminary assessment within **7 days**
- Credit you in the release notes (unless you prefer anonymity)
- Coordinate public disclosure with you

---

## ⚖️ Legal & Ethical Requirements

By contributing, you agree that:

1. Your contribution is your **original work** or properly licensed
2. You grant the project a **perpetual, worldwide, royalty-free license**
   to use, modify, and distribute your contribution under the project's
   [MIT License](LICENSE)
3. Your code complies with [LEGAL.md](LEGAL.md) — no unauthorized-access
   tooling, no attack payloads, no targeted exploitation
4. You will **not** contribute code that enables illegal activity

Contributions that violate these requirements will be rejected and may
result in a permanent ban from the project.

---

## 🏆 Recognition

Every contributor is credited in:

- The **release notes** for the version that includes their work
- The **"Contributors"** section of the README (once we have one)
- The GitHub **Contributors** graph

Significant contributors may be invited to become **maintainers**.

---

## 📬 Contact

| Platform | Handle |
|---|---|
| 📧 Email | [novemixs@gmail.com](mailto:novemixs@gmail.com) |
| 🐙 GitHub | [@siyam201](https://github.com/siyam201) |
| 📁 Repo | [novemixs/AegisCLI-NMS](https://github.com/novemixs/AegisCLI-NMS) |
| 💬 Discussions | [GitHub Discussions](https://github.com/novemixs/AegisCLI-NMS/discussions) |

---

<div align="center">

**⚔️ AegisCLI**

*«One CLI. Modular Security. Built in the open.»*

Thank you for contributing. 🛡️

[← Back to README](README.md) · [LEGAL](LEGAL.md) · [CHANGELOG](CHANGELOG.md)

</div>
