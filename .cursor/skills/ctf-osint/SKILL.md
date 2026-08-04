---
name: ctf-osint
description: >
  OSINT CTF: metadata, WHOIS, DNS clues, EXIF/geo, usernames, public correlation.
  Use for investigation challenges without a direct exploit binary.
---

# CTF OSINT

```bash
python3 tools/cypherflag.py whois <domain>
python3 tools/cypherflag.py dig <domain>
exiftool image.* 2>/dev/null
```

Correlate identifiers from the prompt only. Record sources in `notes/<slug>/osint.md`.  
`save-flag` when the answer string matches flag format.
