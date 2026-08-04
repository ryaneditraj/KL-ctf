# KL-ctf

**CypherFlag** — autonomous CTF / cybersecurity hackathon agent harness.

Built for the UCSI / Cypherly-style **Cybersecurity Hackathon** track: an AI agent that uses real tools (`dig`, `nmap`, `curl`) in a loop to find **flags**, with a harness layer (skills, memory, guardrails) for both **scoreboard wins** and **architecture judging**.

Designed so a **non-technical on-site operator (Aaliya)** can compete by pasting challenges into Cursor / Claude Code / similar — the agent runs the technical work.

Workshop contract:

> `Agent = LLM + Tools + Loop + Context` · Harness = body around the brain

---

## Quick start

```bash
git clone https://github.com/ryaneditraj/KL-ctf.git
cd KL-ctf
bash scripts/first-run.sh
source .venv/bin/activate
```

Open this folder in **Cursor** (Agent mode) or **Claude Code**.

### Operator (Aaliya) — send this once

```
I am Aaliya. Read START_HERE.md and AALIYA.md. Run first-run setup yourself. Teach me the 2-minute version, then wait for challenges.
```

Then for every CTFd challenge: **paste → click Allow → copy `FLAG:` → submit**.

Full operator guide: [`AALIYA.md`](AALIYA.md)

---

## Who reads what

| Audience | Start here |
|---|---|
| **AI coding agents** | [`START_HERE.md`](START_HERE.md) → [`AGENTS.md`](AGENTS.md) |
| **On-site operator** | [`AALIYA.md`](AALIYA.md) |
| **Remote tech / Ryan** | [`BATTLE.md`](BATTLE.md) |
| **Judges / architecture round** | [`JUDGE-ONEPAGER.md`](JUDGE-ONEPAGER.md) → [`ARCHITECTURE.md`](ARCHITECTURE.md) |
| **Workshop notes** | [`WORKSHOP-KB.md`](WORKSHOP-KB.md) |

Claude Code also loads [`CLAUDE.md`](CLAUDE.md). Copilot uses [`.github/copilot-instructions.md`](.github/copilot-instructions.md).

---

## Repository layout

```
KL-ctf/
├── START_HERE.md          # AI agents: read first, then act
├── AGENTS.md              # Full autonomous solve contract
├── AALIYA.md              # Teach + operate (zero knowledge)
├── ARCHITECTURE.md        # 9 harness components (judging)
├── JUDGE-ONEPAGER.md      # 30-second pitch
├── BATTLE.md              # Live CTF playbook
├── CLAUDE.md              # Claude Code entry
├── .cursor/
│   ├── rules/             # Always-on competition rules
│   └── skills/ctf-*       # Triage, web, recon, crypto, pwn, …
├── tools/
│   ├── cypherflag.py      # dig/nmap/curl/recon/web-hunt/autosolve
│   ├── payloads/          # Web + crypto cheatsheets
│   └── wordlists/         # CTF paths
├── scripts/
│   ├── first-run.sh       # One-shot bootstrap
│   ├── bootstrap.sh       # Full tool install
│   ├── check-tools.sh     # Preflight
│   └── solve.sh           # doctor / init / autosolve helpers
├── challenges/            # Per-challenge CTFd text (gitignored bodies)
├── notes/                 # Triage + traces (gitignored bodies)
└── flags/FOUND.md         # Flag ledger
```

---

## Toolkit (workshop tools)

Prefer the CLI wrappers (same tools taught in the workshop):

```bash
python3 tools/cypherflag.py dig <host>
python3 tools/cypherflag.py nmap <host> [--quick|--full]
python3 tools/cypherflag.py whois <host>
python3 tools/cypherflag.py curl <url>
python3 tools/cypherflag.py http <url>
python3 tools/cypherflag.py recon <target>
python3 tools/cypherflag.py web-hunt <url>
python3 tools/cypherflag.py autosolve --slug <slug> --text-file challenges/<slug>/README.md
python3 tools/cypherflag.py autosolve --slug <slug> --target http://TARGET/
python3 tools/cypherflag.py save-flag <slug> 'flag{...}'
```

Helpers:

```bash
bash scripts/solve.sh doctor
bash scripts/solve.sh init my-chal --title "Challenge Name"
bash scripts/solve.sh autosolve my-chal
```

---

## How a challenge is solved

1. Operator pastes CTFd text into the AI agent  
2. Agent scaffolds `challenges/<slug>/` + `notes/<slug>/`  
3. **`autosolve`** — parse targets → dig / web-hunt / quick nmap → extract flags  
4. If needed — category **skills** (web SQLi/SSTI/SSRF/…, crypto, pwn, forensics, …)  
5. Print `FLAG: …` and append `flags/FOUND.md`  
6. Operator submits on CTFd  

One challenge per chat. Don’t mix threads.

---

## Win conditions

1. **Primary:** most flags on the scoreboard  
2. **Secondary:** architecture / technical round — show harness design (`JUDGE-ONEPAGER.md`)

---

## Safety

- Only attack **in-scope** CTF targets  
- No DoS / no real-world systems  
- Human **Allow** prompts for tool execution  
- Non-technical operator never runs the terminal  

---

## Requirements

- Python 3.10+  
- macOS (Homebrew) or Debian/Ubuntu preferred  
- Cursor, Claude Code, or another agent that can run shell tools  
- Network access to CTF targets  

Optional: `pwntools` for binary pwn (may need extra build deps on some Macs).

---

## License / use

For authorized CTF / hackathon use only. Do not use against systems you do not own or lack permission to test.
