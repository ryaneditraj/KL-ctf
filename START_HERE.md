# ⚠️ AI AGENTS — KL-ctf (for Aaliya)

**Operator:** Aaliya only (zero technical knowledge).  
**Runtime:** **Agentic** on **Cursor Agent** (or Claude Code) — LLM + tools + loop. This repo = harness.  
**Competition:** cybersecurity CTF / agent hackathon — most flags + explainable harness.

## First message (even `hi`)

1. `bash scripts/first-run.sh`  
2. If Mac and scanners missing: `bash scripts/install-mac-scanners.sh`  
3. `python3 tools/cypherflag.py scanners` — install until ffuf/sqlmap/nuclei OK when possible  
4. Teach `AALIYA.md` Part B briefly  
5. “Paste a challenge. Click **Allow** if asked.”

Aaliya must **Approve** Homebrew installs if macOS prompts — that is her only job besides pasting challenges.

## Challenge paste → autonomous solve

```bash
# save text to challenges/<slug>/README.md first
python3 tools/cypherflag.py autosolve --slug <slug> --text-file challenges/<slug>/README.md
python3 tools/cypherflag.py web-hunt <url>      # includes ffuf+nuclei when installed
python3 tools/cypherflag.py ffuf 'http://HOST/FUZZ'
python3 tools/cypherflag.py sqlmap 'http://HOST/path?id=1'
python3 tools/cypherflag.py nuclei 'http://HOST/'
```

Continue with `.cursor/skills/ctf-*` until:

```
FLAG: <exact>
```

```bash
python3 tools/cypherflag.py save-flag <slug> '<exact>'
```

## Why this is agentic

Chatbots only reply. **You** decide next actions, call scanners/tools, read results, loop until flag — inside Cursor’s agent loop. That matches the workshop: `Agent = LLM + Tools + Loop + Context` + harness.

## Never

Ask Aaliya to open Terminal, write code, or pick exploits. In-scope CTF only.
