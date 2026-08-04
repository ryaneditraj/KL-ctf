# Aaliya — you only open this in Cursor

**Main page for you:** [`OPEN_IN_CURSOR.md`](OPEN_IN_CURSOR.md)  
**What to say to judges:** [`EXPLAIN.md`](EXPLAIN.md)

This file is also for the **AI** (must follow Part C).

---

## Part A — Competition day (only this)

1. Open **this folder** in Cursor  
2. Open **Agent** chat → type `hi` (or the message below)  
3. Open CTFd in a browser  
4. For each challenge: **paste → Allow → copy `FLAG:` → submit**  
5. Stuck 5 min → screenshot Ryan  

```
I am Aaliya. Boot KL-ctf. Teach me the 2-minute version from AALIYA.md, then wait for challenges.
```

Do **not** use Terminal. Do **not** install anything. Do **not** edit code.

---

## Part B — 2-minute learn (AI teaches; you repeat)

1. **CTF** = puzzle game for points  
2. **Flag** = secret string you submit  
3. **Agent** = AI that tries steps alone until it finds the flag  
4. **Your job** = paste → Allow → submit  
5. **Win** = most flags (+ explain harness if asked — use EXPLAIN.md)

---

## Part C — Agent duties (AI: obey)

### Drop-in
Any first message (`hi` included) → run `bash scripts/first-run.sh`, teach Part B briefly, wait for challenges.

### Tone
Short plain English. Never ask her to run commands. You run them.

### Challenge paste
1. “Working — click Allow if asked.”  
2. Save `challenges/<slug>/README.md`  
3. `python3 tools/cypherflag.py autosolve ...` then skills until flag  
4. Show `FLAG: ...` + “Submit on the site. Say next.”

### Judges
Use **exact** scripts in `EXPLAIN.md`. Offer `JUDGE-ONEPAGER.md`.

### Blocked
≥3 techniques, then “Screenshot Ryan.”

---

## Part D — Checklist

- [ ] Folder opens in Cursor  
- [ ] Said hi / boot message; AI ready  
- [ ] CTFd login works  
- [ ] Memorized 15-second pitch in EXPLAIN.md  
- [ ] Ryan’s number saved  
