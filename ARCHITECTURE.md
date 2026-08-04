# CypherFlag Harness — Architecture

**Goal:** maximize flags on CTFd **and** win architectural/technical judging.

**Runtime:** Cursor Agent (LLM + tools + loop) + this repo as the control plane.

Aligned to the UCSI / Cypherly workshop stack: `Agent = LLM + Tools + Loop + Context`, wrapped in a full harness.

---

## Concrete implementation (what exists in-repo)

| Need (from workshop) | Implementation |
|---|---|
| dig / nmap / curl | `tools/cypherflag.py` |
| Real scanners | `ffuf`, `sqlmap`, `nuclei` (+ `install-mac-scanners.sh` for Aaliya’s Mac) |
| WHOIS / HTTP enrichment | `whois` + `http` / `web-hunt` |
| Agent loop (agentic) | **Cursor Agent** runtime + `AGENTS.md` |
| Skills | `.cursor/skills/ctf-*` |
| Memory | `notes/`, `flags/FOUND.md` |
| Operator | **Aaliya only** — `AALIYA.md` / `OPEN_IN_CURSOR.md` |

## Why this beats a bare chatbot

| Layer | Chatbot | CypherFlag |
|---|---|---|
| Reasoning | LLM only | LLM (Cursor / Claude) |
| Actions | None | dig/nmap/curl + shell + python toolkit |
| Autonomy | One-shot | While-loop until flag or budget |
| Specialization | Generic | Category skills (web/pwn/crypto/…) |
| Safety | None | Scope rules + HITL on dangerous cmds |
| Memory | Chat only | `notes/`, `flags/`, triage artefacts |
| Observability | None | Traces in `notes/<challenge>/trace.md` |

---

## Nine harness components (workshop map)

| # | Component | Implementation here |
|---|---|---|
| 1 | **While loop** | Cursor Agent loop (think → tool → observe → repeat) |
| 2 | **Context management** | Triage first; load only matching skill; write notes so context can be rebuilt |
| 3 | **Tools** | Host toolchain: nmap, curl, dig, python, … (`scripts/check-tools.sh`) |
| 4 | **Sub-agents / specialists** | Category skills act as playbooks; agent switches skill by signals |
| 5 | **Built-in skills** | `.cursor/skills/ctf-*` |
| 6 | **Session persistence** | `notes/`, `flags/FOUND.md`, challenge folders |
| 7 | **System prompt assembly** | `AGENTS.md` + `.cursor/rules` + skill descriptions |
| 8 | **Lifecycle hooks** | Operator Allow/Deny in Cursor; bootstrap/check scripts pre-flight |
| 9 | **Guardrails & approvals** | In-scope only; no DoS; human approves shell; never attack out-of-scope |

---

## Control flow (flag hunter)

```
Challenge text / URL / files
        │
        ▼
   ctf-triage          ← classify by signals (not by challenge name)
        │
        ├─► ctf-web / ctf-recon / ctf-crypto / ctf-pwn /
        │   ctf-forensics / ctf-reverse / ctf-misc / ctf-osint
        │
        ▼
   Exploit loop        ← tools + scripts, max iterations, pivot on failure
        │
        ▼
   FLAG: …             ← print clearly + append flags/FOUND.md
        │
        ▼
   Operator submits on CTFd
```

**Mechanics-first routing** (industry pattern used by strong CTF agents): inspect artefacts → dispatch skill → focused attack loop. Do not guess category from the title alone.

---

## Wide bug / challenge coverage

| Category | Typical bugs / tasks the harness hunts |
|---|---|
| **Web** | SQLi, XSS, SSTI, SSRF, LFI/RFI, IDOR, auth bypass, JWT, file upload, command injection, path traversal, XXE, mass assignment |
| **Recon** | DNS, WHOIS, ports, services, dirs, tech fingerprint, subdomain clues |
| **Crypto** | Encoding layers, XOR, classic ciphers, RSA footguns, padding oracles, weak PRNG |
| **Pwn** | Buffer overflow, format string, ROP hints, libc leaks, simple heap (tooling-dependent) |
| **Reverse** | Strings, static analysis, decompile clues, keygen-ish logic, packed binaries |
| **Forensics** | PCAP, disk images, memory dumps, stego, file carving, metadata |
| **Misc** | Pyjails, encodings, esoteric langs, LLM/prompt challenges |
| **OSINT** | Public metadata, DNS history clues, image EXIF, linked artefacts |

---

## Dual win condition

### A. Most flags (primary)
- Fast triage → correct skill → tool-heavy loop
- Persist partial progress so retries don’t restart from zero
- Operator UX so a non-technical teammate can submit flags quickly

### B. Architectural / technical round
Judges should see a **documented production-shaped harness**, not a prompt:
- Explicit 9-component mapping (this doc)
- Skill registry with schemas of *when* each skill fires
- Observability (`notes/`), memory (`flags/`), guardrails (rules)
- Separable model (Cursor) vs control plane (this repo) — swap models without rewriting tools

Talking points for Aaliya / demo:
1. “LLM is the brain; this repo is the body (harness).”
2. “We triage by evidence, then load a specialist skill.”
3. “Every run leaves a trace and stored flags.”
4. “Dangerous actions need human approval; scope is enforced.”

---

## Operator model

- **Remote builder (Ryan):** maintains skills, tools, dry-runs.
- **On-site operator (Aaliya):** paste challenge → Allow tools → copy `FLAG:` → CTFd.
- Agent must never require her to write code or interpret stack traces.

---

## Extensibility

- Add a skill under `.cursor/skills/ctf-<name>/SKILL.md`
- Register signals in `ctf-triage`
- Add tools to `scripts/bootstrap.sh` + `check-tools.sh`
- Keep skills lean; put long cheat sheets in `reference.md` beside the skill
