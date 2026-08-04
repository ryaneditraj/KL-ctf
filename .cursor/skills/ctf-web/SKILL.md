---
name: ctf-web
description: >
  Web CTF and bug hunting for SQLi, XSS, SSTI, SSRF, LFI, RFI, IDOR, auth bypass,
  JWT flaws, file upload, command injection, path traversal, XXE, mass assignment,
  open redirect, and deserialization. Use when the target is an HTTP(S) app,
  API, or web challenge.
---

# CTF Web

## Immediate

```bash
python3 tools/cypherflag.py http <url>
python3 tools/cypherflag.py curl <url>
```

Read `tools/payloads/web.md` and fire payloads systematically.

## Order (EV max)

1. Juicy paths from http fingerprint (`/flag`, `/admin`, `/.env`, robots)
2. Auth / IDOR / JWT
3. Injection: SQLi → command → SSTI
4. LFI / upload
5. SSRF / XXE
6. XSS only if it clearly yields flag

## Trace

Log each try in `notes/<slug>/trace.md` (`payload → result`).

## Done

```bash
python3 tools/cypherflag.py save-flag <slug> '<flag>'
```
