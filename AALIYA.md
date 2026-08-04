# Aaliya — only operator for KL-ctf

**You:** Aaliya (non-technical)  
**System:** **Agentic** AI on **Cursor** + this harness repo  
**Your jobs:** open folder → Allow installs → paste challenges → Allow tools → submit `FLAG:`

See also: [`OPEN_IN_CURSOR.md`](OPEN_IN_CURSOR.md) · [`EXPLAIN.md`](EXPLAIN.md)

---

## Part A — Day of

1. Open this folder in **Cursor** → **Agent**  
2. Send:

```
I am Aaliya. Boot KL-ctf. Install scanners on my Mac if needed. Teach me the 2-minute version, then wait for challenges.
```

3. If Mac asks password / Allow for Homebrew → **Allow** (installs ffuf, sqlmap, nuclei, nmap, …)  
4. Paste each CTFd challenge → **Allow** → copy `FLAG:` → submit  
5. Stuck 5 min → screenshot Ryan  

No Terminal. No coding.

---

## Part B — 2-minute learn

1. **CTF** = puzzles for points  
2. **Flag** = secret string to submit  
3. **Agentic** = AI that runs tools in a loop by itself (not just chat)  
4. **Your job** = paste → Allow → submit  
5. **Win** = most flags (+ explain with EXPLAIN.md)

---

## Part C — AI duties (agents must obey)

- Operator is **always Aaliya** unless Ryan is clearly driving  
- First boot: `first-run.sh` + `install-mac-scanners.sh` on Darwin  
- Challenge → autosolve + **ffuf/sqlmap/nuclei** + skills until flag  
- Speaks plain English; never asks her to run commands  
- Judges → exact `EXPLAIN.md` text  

---

## Part D — Checklist

- [ ] Cursor opens this repo  
- [ ] Boot message sent; scanners install Allowed  
- [ ] CTFd login  
- [ ] 15-second pitch memorized  
- [ ] Ryan’s number  
