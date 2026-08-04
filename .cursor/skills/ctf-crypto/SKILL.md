---
name: ctf-crypto
description: >
  Cryptography CTF solving: encodings, XOR, classical ciphers, RSA common
  mistakes (small e, shared p, Fermat, Wiener), PRNG abuse, ECB/CBC oracles,
  hashing footguns. Use when ciphertext, keys, RSA numbers, or decrypt tasks appear.
---

# CTF Crypto

Follow `tools/payloads/crypto.md` first.

## Loop

1. Peel encodings (b64/hex/url) until binary/text stable
2. XOR single-byte brute / frequency
3. Classical ciphers
4. RSA footguns if `n,e,c` present
5. Script in `notes/<slug>/solve.py` — iterate fast

```bash
python3 tools/cypherflag.py extract-flags notes/<slug>/solve_out.txt
python3 tools/cypherflag.py save-flag <slug> '<flag>'
```
