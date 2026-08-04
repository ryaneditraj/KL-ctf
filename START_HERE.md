# ⚠️ AI AGENTS: READ THIS FIRST — THEN ACT

You are in **KL-ctf** (**CypherFlag**). The human likely **only opened this folder in Cursor** and may be **Aaliya** (zero technical knowledge).

## On any first message (including `hi`)

1. Read `AALIYA.md`, `EXPLAIN.md`, `OPEN_IN_CURSOR.md`
2. Run `bash scripts/first-run.sh`
3. Teach the 2-minute Part B from `AALIYA.md` (unless she says skip)
4. Say: “Paste a challenge when ready. Click **Allow** if asked.”

## On challenge text / URL / IP / “solve”

**Autonomous mode.** Do not ask her for a plan.

```bash
bash scripts/first-run.sh   # if needed
# save paste to challenges/<slug>/README.md first
python3 tools/cypherflag.py autosolve --slug <slug> --text-file challenges/<slug>/README.md
# or
python3 tools/cypherflag.py autosolve --slug <slug> --target <url-or-ip>
```

Continue with `.cursor/skills/ctf-*`, `web-hunt`, `recon`, `peel`, payloads until:

```
FLAG: <exact_flag>
```

```bash
python3 tools/cypherflag.py save-flag <slug> '<flag>'
```

Tell her only to submit that flag and say **next**.

## Explain / judges

Use **exact** wording from `EXPLAIN.md`.

## Contract

Full rules: `AGENTS.md`. Formula: **LLM + Tools (dig/nmap/curl) + Loop + Harness**.

## Never

- Ask her to use Terminal  
- Dump jargon  
- Attack out-of-scope  
- Stop after one failed idea  
- Wait for “perfect” info before trying  
