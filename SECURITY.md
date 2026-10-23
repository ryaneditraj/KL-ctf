# Security policy

KL-ctf is a capture-the-flag harness. It runs reconnaissance commands and
optional scanners against a target the operator supplies. Point it only at a
CTF you joined, a lab you own, or a host inside a written scope.

## Reporting a vulnerability

Please use a private GitHub security advisory:

<https://github.com/ryaneditraj/KL-ctf/security/advisories/new>

Include the version or commit, the command you ran, and the impact. Leave out
live flags, credentials, and data from targets you cannot share. Ryan Editraj
maintains this repository. There is no paid bug-bounty program for the harness
itself.

Do not open a public issue for an unfixed vulnerability.

## Supported versions

Security fixes land on `main`. There are no versioned releases yet.

## Secrets

An audit of the tree and of `git log -S` on 23 October 2026 found **no
committed API keys, passwords, private keys, or cloud tokens**. Nothing in the
history needs to be rotated because of this repository. History was not
rewritten.

The CLI does not ship with a secret. Optional operator settings live in `.env`
(see `.env.example`) and are gitignored.

## Audit, 23 October 2026

| Finding | What we did |
|---|---|
| No hardcoded credentials in the current tree or git history | Recorded here. No rotation list. History left intact. |
| `urllib3>=2.0.0` allowed 2.0.7, which is affected by PYSEC-2026-141, PYSEC-2026-1994, PYSEC-2026-1995, PYSEC-2026-1996, PYSEC-2026-1998, PYSEC-2026-1999, PYSEC-2026-4175, and PYSEC-2026-4177 | Raised the floor to `urllib3>=2.8.0`. `requests`, `beautifulsoup4`, `lxml`, and `pycryptodome` floors were raised to releases that `pip-audit` did not flag on this date. |
| `web_hunt` and `http` disabled TLS verification for every request, and the CLI silenced urllib3 warnings at startup | Certificates are verified by default. A self-signed lab certificate is retried once, and the JSON result includes `tls_verify_fallback`. Set `CYPHERFLAG_TLS_VERIFY=0` only in a lab you trust. |
| `curl` accepted any URL scheme and any string as `-X`, so a method or URL could be read as a curl option. `--data` also treats a leading `@` as a local filename | URLs must be `http` or `https`. Methods are allowlisted. curl is pinned to those protocols with `--proto` and `--proto-redir`. Bodies use `--data-raw`. Values that start with `-` or `@` are rejected. |
| Hosts passed to dig, nmap, whois, ffuf, sqlmap, and nuclei could be parsed as tool flags when they started with `-` or `@` | Those values are rejected. nmap receives the target after `--`. |
| Requests would follow a redirect to a cloud metadata address | Redirects that will actually be followed are checked first. `169.254.169.254`, `169.254.170.2`, `fd00:ec2::254`, decimal and hex forms of those IPv4 addresses, and `metadata.google.internal` are blocked unless `CYPHERFLAG_ALLOW_METADATA=1`. |
| Remote HTML was parsed with lxml | Pages are parsed with the stdlib HTML parser. |
| `scripts/solve.sh` was a syntax error (`case` was missing), so `doctor`, `init`, `recon`, and `autosolve` could not run | The documented commands work again. `recon` calls the existing `cypherflag.py recon` command. |
| A `.env` loader could have been a way to override `PATH` | The loader accepts only `CYPHERFLAG_TLS_VERIFY` and `CYPHERFLAG_ALLOW_METADATA`, and it does not override variables that are already set. |
| Flag ledger lines could be broken by a newline in the challenge name or flag | `save-flag` rejects newlines, NULs, and values that start with `-` or `@`. |

## Left as they are

These are product behavior, not accidents. They stay, with the guardrails above.

- `web-hunt`, `ffuf`, `sqlmap`, and `nuclei` send active checks. Run them only in scope. The cheat sheets in `tools/payloads/` are reference notes for the same setting.
- Private and localhost addresses stay allowed. CTF boxes are often on a lab network.
- `curl -L` can still follow a redirect to a metadata address. The requests-based `http` and `web-hunt` commands block that hop. Dotted-octal IP spellings are not normalized.
- `scripts/first-run.sh` installs Debian packages with `sudo` when passwordless sudo exists. `scripts/install-mac-scanners.sh` runs Homebrew's official install script only when `brew` is missing on macOS. Both are operator-machine setup.
- Packages that happen to be installed on a developer machine (ansible, system pip, setuptools, and similar) are not dependencies of this repo and were not changed.
- Git history was not rewritten. If a secret is ever committed later, rotate it first, then remove it from history in a separate, agreed step.

## Hardening you can turn on

```bash
# default: verify TLS, refuse metadata hosts
export CYPHERFLAG_TLS_VERIFY=1
export CYPHERFLAG_ALLOW_METADATA=0
```
