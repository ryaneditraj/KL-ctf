# Workshop knowledge base (for Ryan / remote support)

Source: UCSI Cybersecurity Hackathon 2026 workshop recordings + https://ucsi-workshop.cypherly.co/

## Agenda (≈3 hours)

1. **Jarod Tan** — Intro & evolution (LLM → chatbot → tool-calling → agent → harness)
2. **Jarod Tan** — Agent harness deep dive (9 components)
3. **Roheender Singh** — CyberSec Investigator demo + architecture
4. **Hands-on** (~65 min) — build domain investigation agent (DNS / WHOIS / reputation)
5. Security of agents, 8 principles, design challenge, implementation stack

## Core formulas

- `Agent = LLM + Tools + Loop + Context`
- `ReAct = Thought → Action → Observation → repeat`
- Harness = runtime/control layer around the agent (safety, memory, observability, permissions)

## 9 harness components

1. While loop  
2. Context management  
3. Tools (+ schemas / registry; MCP as USB-C for tools)  
4. Sub-agents  
5. Built-in skills  
6. Session persistence (short + long term)  
7. System prompt assembly  
8. Lifecycle hooks  
9. Guardrails & human approvals  

## Hands-on target architecture

```
Agent {
  model: LLM,
  tools: [dns, whois, reputation],
  instructions: "investigate domains",
  loop: while (task not done) { think(); act(); observe(); }
}
```

Demo project seen in recording: VS Code **UCSI DEMO** / `~/ucsi_harness` with `run.py`, `agent.py`, `recon_tools.py`, `.env`, OpenRouter for models.

## Security section (must enforce on site)

- Prompt injection, tool abuse, excessive agency, data leakage, memory poisoning, agent-to-agent trust
- Least privilege; HITL for high-risk actions
- Sandbox tool execution (Docker); max iterations; loop detection
- Sensitive code → local models; sanitized intel → cloud models (workshop guidance)

## Useful links

- Slides: https://ucsi-workshop.cypherly.co/
- Models marketplace demo’d: https://openrouter.ai/
- Skills registry mentioned: https://skills.sh/
- Minimal harness mentioned: https://pi.dev/
- Jarod: https://linkedin.com/in/kahhsingtan
- Roheender: https://linkedin.com/in/roheender-sahota

## Workshop 2 spoken / demo notes (Roheender + Jarod continuation)

- Harness section continues after break; production AI coding tools framed as harnesses.
- **skills.sh** — public skill registry crawled from GitHub; warn: don’t install untrusted skills (agent has machine access).
- **OpenRouter** — create account → Personal → create API key; filter **free** models / free routers for the lab; wire key into the recon agent.
- Live demo stack: `ucsi_harness` with `run.py` (GUI), folders for agent / app / tools; shell tools include `curl`, `dig` (DNS), `nmap`.
- Hands-on ask: build/extend a **recon agent**, implement tools, plug in OpenRouter API key, show results; ~10 min break to start that work.
- Post-workshop: time before the hackathon to keep building; materials also referenced via **Google Drive** + GitHub/Docker backup pull-to-run.
- Alt harness SDKs mentioned: Cursor SDK, **pi.dev** (minimal/bare-bones).

## Local artifacts

- `workshop/workshop1.txt` + `.json` — full transcript part 1  
- `workshop/workshop2.txt` + `.json` — full transcript part 2  
- `workshop/slides1/`, `slides2/` — sampled frames  
- `AALIYA-ONSITE.md` — non-technical facilitator sheet  
