---
name: ctf-reverse
description: >
  Reverse engineering CTF: strings, static/dynamic analysis, crackmes, key checks.
  Use for reverse binaries, password finds, or stripped ELFs that are not classic pwn.
---

# CTF Reverse

```bash
file ./bin
strings -n 6 ./bin | python3 tools/cypherflag.py extract-flags -
./bin
```

Find compare logic → patch or reproduce algorithm in Python under `notes/<slug>/`.  
`ltrace`/`strace` if available. Finish with `save-flag`.
