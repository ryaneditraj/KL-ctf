# Ryan — live CTF battle playbook

## Before doors open (30 min)

```bash
cd /path/to/aaliya
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
bash scripts/bootstrap.sh
bash scripts/solve.sh doctor
```

Confirm Cursor opens this folder, Agent mode works, Allow prompts appear.

## Scoreboard strategy

1. **Sweep easy** (misc/web intro/recon) with parallel Agents — one challenge each.
2. **Medium** where tools + payloads apply.
3. **Hard** only with your hypothesis in the first message.
4. Never leave a chat stuck >10 min without reset.

## Message template (paste into Agent)

```
Slug: <slug>
Category guess: <web|recon|crypto|pwn|forensics|rev|misc|osint|unknown>
Scope: ONLY <ip/url/files given>
CTFd text:
<paste>

Commands:
1) python3 tools/cypherflag.py new-challenge <slug>
2) Write challenges/<slug>/README.md with the text above
3) Triage → notes/<slug>/triage.md
4) Use cypherflag.py recon/http/dig/nmap as needed
5) Exploit until FLAG; save-flag when found
Do not ask me to code. Run tools.
```

## When Agent loops uselessly

New chat + brief:

```
Slug: X
Already tried: …
Evidence: …
Next: try SSTI on name field / LFI on ?page= / …
Continue until FLAG.
```

## Architecture round (5 min talk track)

Hand `JUDGE-ONEPAGER.md` + open `ARCHITECTURE.md`:
1. Brain = Cursor LLM; body = this harness  
2. Tools = dig/nmap/curl via `tools/cypherflag.py` (workshop tools)  
3. Loop = Agent until flag  
4. Skills = category specialists  
5. Memory = notes/ + flags/FOUND.md  
6. Guardrails = scope + HITL Allow  

## Aaliya remote assist

She pastes + Allow. You (if allowed) screen-share and type the template. If remote help banned, pre-load skills/tools only; she uses `AALIYA.md`.
