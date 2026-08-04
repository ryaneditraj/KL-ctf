---
name: ctf-pwn
description: >
  Binary exploitation CTF: buffer overflows, format strings, ret2win, simple ROP,
  libc leaks, interacting with nc services via pwntools. Use for ELF/PE pwnables,
  overflow, got, rop, or remote binary services.
---

# CTF Pwn

```bash
file ./bin
strings -n 8 ./bin | head -50
python3 tools/cypherflag.py extract-flags <(strings ./bin)
```

## Ladder

1. ret2win / call `win`/`flag`
2. format string leak+write
3. overflow offset (cyclic) → control RIP
4. leak libc → system/one_gadget (if pwntools present)

```python
from pwn import *
# p = remote(HOST, PORT) or process('./bin')
```

Save exploit as `notes/<slug>/exploit.py`. On success `save-flag`.
