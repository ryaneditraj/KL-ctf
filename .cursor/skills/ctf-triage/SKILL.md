---
name: ctf-triage
description: >
  Mechanics-first CTF challenge triage. Classifies challenges from observable
  signals (URL, binary, pcap, ciphertext, images, jail prompts) and dispatches
  the correct ctf-* skill. Use at the start of every CTF challenge, when the
  category is unclear, or before switching attack paths.
---

# CTF Triage

## Goal

Pick **one** primary skill fast. Write triage. Start tools.

## Steps

1. Read challenge text + files under `challenges/<slug>/`.
2. Quick probes:
   ```bash
   file challenges/<slug>/*
   python3 tools/cypherflag.py extract-flags challenges/<slug>/README.md
   ```
3. If host/URL present:
   ```bash
   python3 tools/cypherflag.py recon <target>
   ```
4. Match signals → skill (table below).
5. Write `notes/<slug>/triage.md`, then load that skill.

## Signal → skill

| Signals | Skill |
|---|---|
| http(s), HTML/JS, forms, API, cookies | `ctf-web` |
| IP/host, ports, DNS, dig, nmap | `ctf-recon` (then hand off) |
| ciphertext, RSA, XOR, decrypt | `ctf-crypto` |
| ELF/PE, overflow, libc, nc binary | `ctf-pwn` |
| pcap, disk, memory, stego | `ctf-forensics` |
| reverse, crackme, keycheck | `ctf-reverse` |
| jail, eval, esolang, LLM puzzle | `ctf-misc` |
| OSINT, EXIF, WHOIS-only story | `ctf-osint` |

## triage.md template

```md
# Triage: <name>
- Signals:
- Category:
- Primary skill:
- Target:
- Plan:
  1.
  2.
  3.
- Tools already run:
```
