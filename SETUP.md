# ⚙️ AegisCLI — Setup Guide

Complete installation and setup instructions for **AegisCLI** on
Windows, Linux, and macOS.

> **New to AegisCLI?** Read the [README](README.md) first for a project
> overview, then come back here.

---

## 📖 Table of Contents

- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
  - [Windows](#-windows)
  - [Linux](#-linux)
  - [macOS](#-macos)
- [Verify Installation](#-verify-installation)
- [Running AegisCLI](#-running-aegiscli)
- [Development Setup](#-development-setup)
- [Troubleshooting](#-troubleshooting)
- [Uninstallation](#-uninstallation)

---

## 📋 Prerequisites

| Requirement | Minimum | Recommended |
|---|---|---|
| **Python** | 3.10 | **3.11 or 3.12** |
| **pip** | Bundled with Python | Latest |
| **Git** | 2.30+ | Latest |
| **OS** | Windows 10, Ubuntu 20.04, macOS 11 | Latest |

### ⚠️ Python Version Warning

**AegisCLI officially supports Python 3.10 – 3.12.**

- ✅ **Python 3.10, 3.11, 3.12** — fully tested, recommended
- ⚠️ **Python 3.13** — should work, mostly tested
- ❌ **Python 3.14+** — may work, but some dependencies (`cryptography`,
  `rich`) may not have prebuilt wheels yet. **Use 3.12 for the smoothest
  experience.**

### Check your Python version

```bash
python --version
```

If you see `Python 3.10.x`, `3.11.x`, or `3.12.x` — you're good.

If you see `3.13.x` or `3.14.x`, consider installing 3.12 alongside
([python.org/downloads](https://www.python.org/downloads/)).

---

## 🚀 Quick Start

**For the impatient** (assumes Python and pip are on PATH):

```bash
git clone https://github.com/novemixs/AegisCLI-NMS.git
cd AegisCLI-NMS
pip install -e .
aegis
```

**If `pip` or `aegis` is not recognized** — jump to
[Troubleshooting](#-troubleshooting).

---

## 💻 Installation

### 🪟 Windows

#### Step 1: Install Python

1. Download **Python 3.12** from [python.org/downloads](https://www.python.org/downloads/)
2. Run the installer
3. ⚠️ **On the FIRST screen, check** ☑️ **"Add Python to PATH"**
4. Click **Install Now**
5. **Close and reopen** your terminal (cmd or PowerShell)

**Verify:**

```cmd
python --version
```

Expected: `Python 3.12.x`

#### Step 2: Install Git (if not installed)

Download from [git-scm.com](https://git-scm.com/download/win) and install
with default options.

**Verify:**

```cmd
git --version
```

#### Step 3: Clone the repository

```cmd
cd %USERPROFILE%\Documents
git clone https://github.com/novemixs/AegisCLI-NMS.git
cd AegisCLI-NMS
```

#### Step 4: Install AegisCLI

```cmd
python -m pip install -e .
```

> **Why `python -m pip` instead of `pip`?**
> On Windows, `pip` is sometimes not on PATH even when Python is. Using
> `python -m pip` guarantees you hit the right pip.

#### Step 5: Add Scripts folder to PATH (one-time)

After install, you'll see a warning like:

```
WARNING: The script aegis.exe is installed in
'C:\Users\<You>\AppData\Local\Python\pythoncore-3.XX-64\Scripts'
which is not on PATH.
```

**Fix:**

1. Press `Win + R`, type `sysdm.cpl`, press Enter
2. Go to **Advanced** → **Environment Variables**
3. Under **User variables**, select **Path** → click **Edit**
4. Click **New** → paste:
   ```
   C:\Users\<You>\AppData\Local\Python\pythoncore-3.XX-64\Scripts
   ```
5. Click **OK** → **OK** → **OK**
6. ⚠️ **Close and reopen** cmd / PowerShell

**Verify:**

```cmd
aegis --version
```

---

### 🐧 Linux

#### Step 1: Install Python and pip

**Debian / Ubuntu:**

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git
```

**Fedora / RHEL:**

```bash
sudo dnf install python3 python3-pip git
```

**Arch:**

```bash
sudo pacman -S python python-pip git
```

**Verify:**

```bash
python3 --version
pip3 --version
```

#### Step 2: Clone and install

```bash
git clone https://github.com/novemixs/AegisCLI-NMS.git
cd AegisCLI-NMS
python3 -m pip install -e .
```

> **Note:** On modern Debian/Ubuntu, you may see
> `error: externally-managed-environment`. Use a virtual environment
> (see [Development Setup](#-development-setup)) or install with
> `pipx install .`.

#### Step 3: Verify

```bash
aegis --version
```

---

### 🍎 macOS

#### Step 1: Install Python

**Option A — Homebrew (recommended):**

```bash
brew install python@3.12 git
```

**Option B — python.org:**

Download from [python.org/downloads](https://www.python.org/downloads/)
and install with default options.

**Verify:**

```bash
python3 --version
```

#### Step 2: Clone and install

```bash
git clone https://github.com/novemixs/AegisCLI-NMS.git
cd AegisCLI-NMS
python3 -m pip install -e .
```

#### Step 3: Verify

```bash
aegis --version
```

---

## ✅ Verify Installation

Run these commands to confirm everything works:

```bash
# 1. Version
aegis --version
# Expected: AegisCLI v2.1

# 2. List tools
aegis --list
# Expected: audit, hash, nmap, subfinder

# 3. Help
aegis --help

# 4. Launch hub (Ctrl+C to quit)
aegis
```

If all four work → **you're done.** 🎉

---

## 🎮 Running AegisCLI

### Method 1 — `aegis` command (after PATH setup)

```bash
aegis                    # interactive hub
aegis --version          # show version
aegis --list             # list tools
aegis --help             # show help
aegis --run nmap         # run a tool directly
```

### Method 2 — Module invocation (works even without PATH)

```bash
python -m aegis_cli
python -m aegis_cli --version
python -m aegis_cli --list
python -m aegis_cli --run nmap
```

### Method 3 — Standalone tool modules

Every module in `aegis_cli/tools/` supports standalone execution:

```bash
python aegis_cli/tools/nmap.py example.com --json
python aegis_cli/tools/subfinder.py example.com -t 100
```

---

## 🛠️ Development Setup

**For contributors** (see [CONTRIBUTING.md](CONTRIBUTING.md) for details).

### Step 1: Create a virtual environment

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (cmd):**

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> **PowerShell error "running scripts is disabled"?** Run once:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### Step 2: Install with dev dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

This installs: `ruff`, `black`, `mypy`, `pytest`, `pytest-cov`,
`pre-commit`, `bandit`, `pip-audit`.

### Step 3: Install pre-commit hooks

```bash
pre-commit install
```

### Step 4: Verify

```bash
pytest
ruff check .
black --check .
```

---

## 🔧 Troubleshooting

### ❌ `pip: command not found`

**Cause:** pip is not on PATH, or not installed.

**Fix (all platforms):** Use the module form:

```bash
python -m pip install -e .
# or
python3 -m pip install -e .
```

**Fix (permanent, Windows):** Add the Python `Scripts/` folder to PATH
(see [Windows Step 5](#step-5-add-scripts-folder-to-path-one-time)).

---

### ❌ `aegis: command not found`

**Cause:** The `Scripts/` folder (Windows) or `bin/` (Linux/macOS) is
not on PATH.

**Fix:** Use the module form instead:

```bash
python -m aegis_cli
```

Or add the Scripts folder to PATH. The location was shown when you
installed (`WARNING: The script aegis.exe is installed in ...`).

---

### ❌ `error: externally-managed-environment`

**Cause:** Modern Linux distros block global pip installs.

**Fix:** Use a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Or install globally with `pipx`:

```bash
pipx install .
```

---

### ❌ `tomllib.TOMLDecodeError: Unescaped '\' in a string`

**Cause:** A `pyproject.toml` with an invalid escape sequence.

**Fix:** This was fixed in v0.1.0. If you see it, you're on an old
commit. Pull the latest:

```bash
git pull origin main
```

---

### ❌ `ModuleNotFoundError: No module named 'cryptography'`

**Cause:** Dependency not installed (or installed in a different Python).

**Fix:**

```bash
python -m pip install -r requirements.txt
```

Or reinstall the package:

```bash
python -m pip install -e . --force-reinstall
```

---

### ❌ Python 3.14 — `cryptography` build error

**Cause:** Some wheels are not yet published for Python 3.14.

**Fix:** Use Python **3.12 or 3.13** instead.

Download from [python.org/downloads](https://www.python.org/downloads/),
then create a venv with the correct interpreter:

```bash
py -3.12 -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Linux/macOS
python -m pip install -e .
```

---

### ❌ `rich 15.x` downgrade warning

**Cause:** AegisCLI pins `rich < 15.0.0` for stability.

**Impact:** If you have other tools depending on `rich 15.x`, they may
break. Use a virtual environment to isolate:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

---

### ❌ Port scan fails / times out

**Cause:** Firewall, ISP, or target blocking.

**Fix:** Try a lower thread count and higher timeout:

```bash
python aegis_cli/tools/nmap.py scanme.nmap.org -p 22,80,443 --timeout 3 -t 50
```

Remember: only scan systems you **own or have permission** to test.
See [LEGAL.md](LEGAL.md).

---

### ❌ `Get-ChildItem : Access to the path is denied` (PowerShell)

**Cause:** Permission issue accessing project folder.

**Fix:** Run PowerShell as a normal user (not admin). Or move the
project out of `C:\Program Files\`.

---

## 🗑️ Uninstallation

### Remove the package

```bash
python -m pip uninstall aegiscli
```

### Remove config and logs

**Linux / macOS:**

```bash
rm -rf ~/.aegis
```

**Windows:**

```cmd
rmdir /s /q "%USERPROFILE%\.aegis"
```

### Remove the repository

```bash
# From the parent folder
rm -rf AegisCLI-NMS
```

---

## 📚 Next Steps

After installation:

1. **Read the [README](README.md)** — project overview, usage, roadmap
2. **Read [CONTRIBUTING](CONTRIBUTING.md)** — if you want to contribute
3. **Read [LEGAL](LEGAL.md)** — responsible use policy
4. **Check [CHANGELOG](CHANGELOG.md)** — version history

### Try these first

```bash
# Launch the hub
aegis

# In the hub:
#   Type "3" or "nmap" to scan a target
#   Type "help" for the full command list
#   Type "q" to quit
```

### Safe practice target

Use `scanme.nmap.org` — a public target maintained by the Nmap project
specifically for testing. **Never scan systems you don't own without
written authorization.**

---

## 🆘 Still Stuck?

If none of the above helps:

1. **Search** [existing issues](https://github.com/novemixs/AegisCLI-NMS/issues)
2. **Open a new issue** with:
   - Your OS and version
   - `python --version` output
   - `python -m pip --version` output
   - Full error message (copy-paste, don't retype)
   - What you tried
3. **Or email:** [novemixs@gmail.com](mailto:novemixs@gmail.com)

---

<div align="center">

**⚔️ AegisCLI**

*«One CLI. Modular Security. Built in the open.»*

[← Back to README](README.md) · [LEGAL](LEGAL.md) · [CONTRIBUTING](CONTRIBUTING.md)

</div>