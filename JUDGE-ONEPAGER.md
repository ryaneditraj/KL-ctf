# Judge one-pager — CypherFlag

**Entry:** Cursor-based **agent harness** for cybersecurity CTF.

**Workshop alignment:** `Agent = LLM + Tools + Loop + Context`  
**Tools (as taught):** dig · nmap · curl (+ whois/http helpers) via `tools/cypherflag.py`  
**Harness:** skills, memory (`notes/`, `flags/`), guardrails/HITL, observability traces  

**Solve path:** triage by signals → specialist skill → tool loop → `FLAG:` + ledger  

**Coverage:** web vulns (SQLi/SSTI/SSRF/LFI/IDOR/JWT/upload/RCE), recon, crypto, pwn, forensics, reverse, misc, OSINT  

**Human:** non-technical operator pastes challenges and approves tool runs  

**Full map:** `ARCHITECTURE.md`
