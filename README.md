# KL-ctf

**CypherFlag** — drop this folder into **Cursor** (or Claude Code). That’s the product.

Autonomous CTF agent harness for UCSI / Cypherly-style hackathons:  
`LLM + dig/nmap/curl + loop + harness` → find **flags**.

Built for a **zero-knowledge operator (Aaliya)**: she pastes challenges; the agent does the rest.

---

## Aaliya (start here)

1. Open this folder in Cursor → Agent chat → type `hi`  
2. Read **[`OPEN_IN_CURSOR.md`](OPEN_IN_CURSOR.md)**  
3. Practice saying **[`EXPLAIN.md`](EXPLAIN.md)** (judges)  
4. Full guide: **[`AALIYA.md`](AALIYA.md)**

```
I am Aaliya. Boot KL-ctf. Teach me the 2-minute version from AALIYA.md, then wait for challenges.
```

---

## AI agents

Read **[`START_HERE.md`](START_HERE.md)** on any message, then **[`AGENTS.md`](AGENTS.md)**.  
Boot: `bash scripts/first-run.sh`. Challenge → `autosolve` → skills → `FLAG:`.

---

## Everyone else

| Role | Doc |
|---|---|
| Ryan / live ops | [`BATTLE.md`](BATTLE.md) |
| Judges | [`JUDGE-ONEPAGER.md`](JUDGE-ONEPAGER.md) · [`ARCHITECTURE.md`](ARCHITECTURE.md) |
| Doc index | [`docs/INDEX.md`](docs/INDEX.md) |

---

## Setup (agent usually runs this)

```bash
git clone https://github.com/ryaneditraj/KL-ctf.git
cd KL-ctf
bash scripts/first-run.sh
```

## Toolkit

```bash
python3 tools/cypherflag.py autosolve --slug S --text-file challenges/S/README.md
python3 tools/cypherflag.py web-hunt http://TARGET/
python3 tools/cypherflag.py recon TARGET
python3 tools/cypherflag.py peel 'base64orhex...'
python3 tools/cypherflag.py dig|nmap|curl|whois|http ...
```

## Safety

Authorized CTF targets only. No DoS. Operator clicks Allow; agent runs tools.
