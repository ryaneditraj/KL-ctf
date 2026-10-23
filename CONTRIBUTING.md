# Contributing to KL-ctf

KL-ctf is an agentic capture-the-flag harness. Contributions that make the
operator loop clearer, the tools safer, or the notes easier to follow are
welcome. Use it only on systems you are allowed to test: a CTF you joined, a
lab you own, or a host covered by a written scope.

## Setup

```bash
git clone https://github.com/ryaneditraj/KL-ctf.git
cd KL-ctf
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
bash scripts/solve.sh doctor
python3 -m unittest discover -s tests -v
```

Python 3.10 or newer. On Windows, use WSL or Git Bash for the shell scripts.
Optional macOS scanners (nmap, ffuf, sqlmap, nuclei, and the workshop tools)
come from `bash scripts/install-mac-scanners.sh`.

Copy `.env.example` to `.env` only if you need to change TLS verification or
the cloud-metadata block. `.env` is gitignored. The CLI ignores every key in
that file except `CYPHERFLAG_TLS_VERIFY` and `CYPHERFLAG_ALLOW_METADATA`.

## Pull requests

1. Branch from `main`.
2. Keep the change focused. A docs fix and a scanner change should be two PRs.
3. Add or update a unit test when you change `tools/cypherflag.py`. Tests must
   stay on localhost. Do not point CI at a public host.
4. Run `python3 -m unittest discover -s tests -v` and `bash -n scripts/*.sh`.
5. Fill in the pull request template, including the security checklist.

Do not commit `.env`, real event flags, challenge downloads, or notes from a
live match. Those paths are gitignored for a reason.

## Security changes

Behavior that stops flag injection, blocks non-HTTP schemes, or verifies TLS
should keep authorized labs working. If a lab box uses a self-signed
certificate, the HTTP helpers already retry once without verification. Say so
in the PR if you change that fallback.

Report vulnerabilities in private. See [SECURITY.md](SECURITY.md).

## Code of conduct

This project uses the [Contributor Covenant](CODE_OF_CONDUCT.md).
