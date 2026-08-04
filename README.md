# KL-ctf

**Agentic CTF harness for Aaliya**, running on **Cursor Agent**.

Workshop formula: `LLM + Tools + Loop + Context` + harness.  
Real tools: dig, nmap, curl + scanners **ffuf, sqlmap, nuclei**.

---

## Aaliya (only human operator)

1. Open this folder in Cursor → type `hi` in Agent  
2. **Allow** Mac installs when asked  
3. Paste challenges → Allow → submit `FLAG:`  

Guides: [`OPEN_IN_CURSOR.md`](OPEN_IN_CURSOR.md) · [`AALIYA.md`](AALIYA.md) · [`EXPLAIN.md`](EXPLAIN.md)

```
I am Aaliya. Boot KL-ctf. Install scanners on my Mac if needed. Teach me the 2-minute version, then wait for challenges.
```

---

## Is it agentic?

**Yes.** Cursor Agent is the runtime loop (think → tool → observe → repeat). This repo is the harness (scanners, skills, memory, guardrails). That is what the competition wants — not a chatbot.

---

## AI agents

[`START_HERE.md`](START_HERE.md) → [`AGENTS.md`](AGENTS.md)  
Boot: `bash scripts/first-run.sh` → `bash scripts/install-mac-scanners.sh`

```bash
python3 tools/cypherflag.py scanners
python3 tools/cypherflag.py ffuf 'http://TARGET/FUZZ'
python3 tools/cypherflag.py sqlmap 'http://TARGET/item?id=1'
python3 tools/cypherflag.py nuclei 'http://TARGET/'
python3 tools/cypherflag.py web-hunt 'http://TARGET/'
python3 tools/cypherflag.py autosolve --slug S --text-file challenges/S/README.md
```

---

## Docs

| Role | Doc |
|---|---|
| Judges | [`JUDGE-ONEPAGER.md`](JUDGE-ONEPAGER.md) · [`ARCHITECTURE.md`](ARCHITECTURE.md) |
| Ryan | [`BATTLE.md`](BATTLE.md) |
| Index | [`docs/INDEX.md`](docs/INDEX.md) |

Authorized CTF use only.
