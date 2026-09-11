# ⚖️ Legal Notice & Responsible Use

<div align="center">

**AegisCLI — Network & Modular Security Toolkit**

*Read this document carefully before using AegisCLI.*

</div>

---

## 📖 Overview

AegisCLI is an **open-source, modular security toolkit** intended for
legitimate security professionals, researchers, students, and system
administrators. It provides network reconnaissance, subdomain enumeration,
hashing utilities, and system-audit capabilities through a unified
command-line interface.

Because security tooling can be misused, this document explains:

- Who may use AegisCLI
- What activities are **permitted**
- What activities are **strictly prohibited**
- Your responsibilities as a user
- Limitations of the software
- How to report misuse or security issues

**By downloading, installing, or using AegisCLI, you acknowledge that you
have read, understood, and agreed to the terms in this document.**

---

## ✅ Permitted Use

AegisCLI may be used **only** in the following scenarios:

### 1. Authorized Security Testing
You have **explicit, written permission** from the owner of the target
system or network to perform security testing. This includes:

- Penetration testing engagements with a signed scope-of-work (SOW)
- Red-team exercises authorized by the target organization
- Bug-bounty programs where the target is *within published scope*

### 2. Systems You Own or Control
You are testing:

- Your own personal devices, servers, or networks
- Systems provisioned specifically for your use (e.g. VPS, lab VMs)
- Publicly designated testing targets (e.g. `scanme.nmap.org`)

### 3. Security Research & Education
You are using AegisCLI:

- In an academic course with instructor approval
- In a formal security training program
- For personal learning **against isolated lab environments only**
- For CTF (Capture The Flag) competitions and lab platforms

### 4. Defensive Security Operations
You are using AegisCLI:

- To audit systems you are responsible for
- To detect misconfigurations or exposed services on your own assets
- As part of a SOC (Security Operations Center) monitoring workflow
  within your organization's authorized scope

---

## ❌ Prohibited Use

AegisCLI **must not** be used for any of the following. These activities
may violate local, national, or international law, and may result in
**criminal and civil liability**.

### 1. Unauthorized Access
- Scanning or probing systems you do **not** own and **have not** been
  authorized to test
- Attempting to gain unauthorized access to any system, network, or data
- Bypassing authentication, access controls, or security mechanisms

### 2. Denial-of-Service (DoS / DDoS)
- Flooding a target with traffic
- Overloading a service to cause degradation or outage
- Using AegisCLI's multithreaded features to exhaust a target's resources

### 3. Malicious Reconnaissance
- Gathering information about a target with intent to attack
- Mapping networks for the purpose of exploitation
- Enumerating assets without authorization

### 4. Data Interception & Privacy Violation
- Intercepting communications without authorization
- Accessing, copying, or exfiltrating data you are not authorized to access
- Violating any individual's privacy or data-protection rights

### 5. Illegal Activity
- Any activity that violates the laws of your jurisdiction
- Any activity that violates the laws of the target's jurisdiction
- Any activity that violates international treaties or conventions

### 6. Weaponization
- Integrating AegisCLI into malware or offensive tooling
- Automating attacks against third parties
- Using AegisCLI to facilitate any crime

### 7. Bypassing Restrictions
- Circumventing rate limits, firewalls, or other protective controls
  without authorization
- Evading detection on systems you do not own

---

## 🌍 Legal Frameworks You Should Know

AegisCLI users are subject to **all applicable laws**. Depending on your
location and the location of the target system, the following may apply:

| Region | Key Legislation | Notes |
|---|---|---|
| **United States** | Computer Fraud and Abuse Act (CFAA), 18 U.S.C. § 1030 | Unauthorized access is a federal crime |
| **United Kingdom** | Computer Misuse Act 1990 | Up to 10 years imprisonment for serious offenses |
| **European Union** | Directive 2013/40/EU on attacks against information systems | Member-state implementation varies |
| **Germany** | StGB § 202a–202c | Hacking and data espionage provisions |
| **India** | Information Technology Act, 2000 (§ 43, § 66) | Civil and criminal penalties |
| **Bangladesh** | Cyber Security Act, 2023; Digital Security Act (repealed) | Unauthorized access is punishable |
| **Australia** | Criminal Code Act 1995, Part 10.7 | Computer offenses |
| **Canada** | Criminal Code § 342.1 | Unauthorized use of computer |
| **Japan** | Act on Prohibition of Unauthorized Computer Access (2011) | Strict prohibitions |

> **This list is not exhaustive.** Even scanning a public IP address may
> constitute a criminal offense in some jurisdictions if the target did
> not consent. **When in doubt, do not scan.**

Additionally, port scanning and enumeration may violate:

- **Terms of Service** of cloud providers (AWS, Azure, GCP, DigitalOcean)
- **Acceptable Use Policies** of ISPs and hosting providers
- **Contractual obligations** with clients or employers
- **University or corporate IT policies**

---

## 👤 User Responsibility

**You, the user, are solely responsible for your actions.**

By using AegisCLI, you agree that:

1. You will only use AegisCLI against systems you own or have **explicit
   written authorization** to test.
2. You will comply with **all applicable laws** in your jurisdiction and
   the jurisdiction of any target system.
3. You will **not hold** the developers, contributors, maintainers, or
   distributors of AegisCLI liable for any consequences of your use.
4. You understand that **unauthorized use may result in criminal
   prosecution**, civil lawsuits, and permanent damage to your career and
   reputation.
5. You will **obtain written permission** before testing any third-party
   system, and you will retain that documentation.
6. You will respect the **Terms of Service** of every platform, network,
   and service you interact with.

---

## 📄 Disclaimer of Warranty

```
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.

IN NO EVENT SHALL THE AUTHORS, COPYRIGHT HOLDERS, OR CONTRIBUTORS BE LIABLE
FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT, OR OTHERWISE, ARISING FROM, OUT OF, OR IN CONNECTION WITH THE SOFTWARE
OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```

AegisCLI is provided as-is. The maintainers:

- **Do not guarantee** that the software is bug-free, accurate, or fit for
  any particular purpose
- **Do not guarantee** that scan results are complete or correct
- **Are not responsible** for any damage caused by the software
- **Are not responsible** for any legal consequences resulting from its use
- **Do not endorse** any specific use case beyond authorized security work

---

## 🛡️ Ethical Principles

AegisCLI is built in the spirit of the security community's long-standing
ethical norms. Users are expected to uphold:

1. **Authorization first** — never test without permission
2. **Minimal impact** — do not disrupt or damage target systems
3. **Confidentiality** — treat findings as confidential unless authorized
   to disclose
4. **Responsible disclosure** — report vulnerabilities privately to the
   affected party before public disclosure
5. **Respect for privacy** — do not access data beyond what is necessary
6. **No harm** — do not weaponize findings for personal gain
7. **Legal compliance** — follow the law, even when inconvenient

These principles align with recognized codes of ethics including:

- [(ISC)² Code of Ethics](https://www.isc2.org/Ethics)
- [EC-Council Code of Ethics](https://www.eccouncil.org/code-of-ethics/)
- [ACM Code of Ethics](https://www.acm.org/code-of-ethics)
- [SANS Security Ethics](https://www.sans.org/)

---

## 🚨 Reporting Misuse

If you become aware of AegisCLI being used for malicious or unauthorized
purposes, please report it:

- **Email:** [novemixs@gmail.com](mailto:novemixs@gmail.com)
- **Subject line:** `[AEGISCLI MISUSE]`
- **Include:** evidence of misuse (screenshots, logs, URLs)

We take reports of misuse seriously. Where appropriate, we may:

- Remove or restrict access to the project
- Cooperate with law enforcement
- Notify affected parties

---

## 🐛 Reporting Security Issues in AegisCLI

If you discover a **vulnerability in AegisCLI itself**, please:

1. **Do not** open a public GitHub issue
2. Email details to [novemixs@gmail.com](mailto:novemixs@gmail.com)
3. Include:
   - Affected version
   - Reproduction steps
   - Impact assessment
   - Your preferred disclosure timeline (default: 90 days)

We will acknowledge receipt within **72 hours** and work with you on a
coordinated disclosure.

---

## 🤝 Contributing to Legal Safety

Contributors adding new modules to AegisCLI must ensure their code:

- Does **not** include hardcoded attack payloads
- Does **not** target specific third-party systems by default
- Does **not** bypass authorization controls
- Includes warnings where operations could be destructive
- Follows the responsible-use principles in this document

Maintainers reserve the right to reject contributions that facilitate
unethical or illegal use.

---

## 📚 Educational Resources

If you are new to security testing, start here **before** using AegisCLI:

- **TryHackMe** — [tryhackme.com](https://tryhackme.com) (beginner-friendly labs)
- **Hack The Box** — [hackthebox.com](https://hackthebox.com) (CTF + labs)
- **PortSwigger Web Security Academy** — [portswigger.net/web-security](https://portswigger.net/web-security) (free)
- **OWASP** — [owasp.org](https://owasp.org)
- **SANS Cyber Aces** — [cyberaces.org](https://www.cyberaces.org)

Always practice on **authorized lab environments**, not on live systems.

---

## 📝 Final Words

Security is a **privilege and a responsibility**. The tools we build are
neutral; how they are used determines their impact. AegisCLI exists to
help defenders, researchers, and students — not to enable harm.

If you are unsure whether a particular use is legal or ethical:

> **Stop. Ask. Get written permission. If you cannot, do not proceed.**

The open-source community thrives because its members respect the trust
placed in them. Please be one of them.

---

<div align="center">

**⚔️ AegisCLI**

*«One CLI. Modular Security. Built in the open.»*

[← Back to README](README.md) &nbsp;·&nbsp; [LICENSE](LICENSE) &nbsp;·&nbsp; [Report Misuse](mailto:novemixs@gmail.com)

</div>
