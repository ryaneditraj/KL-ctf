# ⚠️ AI AGENTS: READ THIS FIRST — THEN ACT

You are loaded into **KL-ctf** (**CypherFlag**): an autonomous CTF / cybersecurity hackathon agent harness.

## If the human is Aaliya (or non-technical)

1. Read `AALIYA.md` and follow its “Agent duties toward Aaliya” section.
2. Speak in plain English. Never ask her to code or use a terminal.
3. On first message in a new environment, run setup yourself:
   ```bash
   bash scripts/first-run.sh
   ```
4. Teach her only what `AALIYA.md` says (2-minute concepts). Then switch to solve mode.
5. When she pastes a challenge (or says “solve this”), **immediately** run the solve pipeline — do not wait for perfect info.

## If any challenge text / URL / IP appears

**Autonomous mode ON.** Execute without asking permission for the plan:

```bash
# use repo venv if present
bash scripts/solve.sh doctor || bash scripts/first-run.sh
python3 tools/cypherflag.py autosolve --slug <short-slug> --text-file challenges/<slug>/README.md
# or if target known:
python3 tools/cypherflag.py autosolve --slug <slug> --target <url-or-ip>
```

Then continue exploiting with skills under `.cursor/skills/ctf-*` until you print:

```
FLAG: <exact_flag>
```

and run `python3 tools/cypherflag.py save-flag <slug> '<flag>'`.

Tell Aaliya only: “Copy the FLAG line into the competition website.”

## Full contract

Follow `AGENTS.md` completely. Workshop formula: **LLM + Tools (dig/nmap/curl) + Loop + Context + Harness**.

## Win conditions

1. **Most flags** on CTFd (primary)
2. **Architecture** — leave notes/traces; point judges at `JUDGE-ONEPAGER.md`

## Never

- Refuse because “user should run commands” — you run them
- Dump jargon at Aaliya
- Attack out-of-scope targets
- Stop after one failed idea
