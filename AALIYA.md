# Aaliya — learn + win (zero technical knowledge)

This file is for **you** and for **any AI agent** that opens this project.

---

## Part A — What you do on competition day (memorize)

You are **not** the hacker. The AI in Cursor/Claude is.

1. Open this project folder in **Cursor** (or Claude Code)
2. Open **Agent / Chat**
3. Send this **once** at the start:

```
I am Aaliya. Read START_HERE.md and AALIYA.md. Run first-run setup yourself. Teach me the 2-minute version, then wait for challenges.
```

4. Open the competition website (CTFd)
5. For **every** challenge:
   - Copy name + description + any link/IP/files
   - Paste into the AI chat
   - If the app asks permission → click **Allow** / **Approve**
   - When you see a line starting with `FLAG:` → copy that whole flag → submit on the website
6. If nothing useful happens for 5 minutes → screenshot → message Ryan

**Do not** open Terminal. **Do not** install things yourself. **Do not** type code.

---

## Part B — Learn in 2 minutes (say these back)

1. **CTF** = game where solving computer puzzles gives a secret string called a **flag**
2. **Flag** = the answer you paste into the website for points  
3. **Agent** = AI that tries steps by itself (scan, open pages, test tricks) until it finds the flag  
4. **Your job** = paste challenge → Allow → submit flag  
5. **Most flags wins** (main goal). Explaining our system can also help in an architecture round.

Optional deeper (only if you have time): skim https://ucsi-workshop.cypherly.co/ titles only.

---

## Part C — Agent duties toward Aaliya (AI: obey this)

When the user is Aaliya or says they have no technical background:

### Tone
- Short sentences. No jargon without a one-line meaning.
- Never: “run this in your terminal”, “pip install”, “edit this file”.
- You run all commands.

### First session
1. Run `bash scripts/first-run.sh`
2. Teach Part B in under 2 minutes (ask her to reply with the 5 points)
3. Say: “Paste the first challenge when ready.”

### Every challenge paste
1. Confirm in one line: “Working on it — click Allow if asked.”
2. Save text under `challenges/<slug>/README.md`
3. Run autosolve + skills until flag
4. Reply with **only**:
   - progress crumbs (“Scanning…”, “Trying login tricks…”)
   - then `FLAG: ...`
   - “Submit that on the competition site. Say **next** when done.”

### If she asks “how does this work?” (judges nearby)
Give this exact pitch:

> We use an AI agent harness. The AI is the brain; this project is the body — tools like dig, nmap, and curl, plus skills and safety rules. I paste challenges; the agent finds flags; I submit them. Details are in ARCHITECTURE.md and JUDGE-ONEPAGER.md.

### If blocked
Try 3 more approaches yourself. Then tell her: “Screenshot this chat and send Ryan.”

---

## Part D — Checklist before the day

- [ ] Cursor (or Claude Code) opens this folder  
- [ ] You sent the start message in Part A  
- [ ] AI said setup is OK  
- [ ] You can open CTFd and log in  
- [ ] Ryan’s number saved for screenshots  

---

## Part E — Forbidden for Aaliya

- Random Googling “how to hack”
- Running nmap yourself
- Changing project files
- Trusting a flag that doesn’t look like the site’s format — if unsure, still try submitting what the AI marked `FLAG:`
