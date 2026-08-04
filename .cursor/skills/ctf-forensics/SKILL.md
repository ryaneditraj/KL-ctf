---
name: ctf-forensics
description: >
  Forensics CTF: PCAP, disk/memory, carving, stego, EXIF. Use for .pcap, disk
  images, memory dumps, stego media, or hidden-data challenges.
---

# CTF Forensics

```bash
file evidence.*
strings -n 8 evidence.* | python3 tools/cypherflag.py extract-flags -
exiftool evidence.* 2>/dev/null
binwalk -e evidence.* 2>/dev/null
```

PCAP: `tshark`/`tcpdump` — follow HTTP/FTP/DNS for flags.  
Stego: `zsteg`, `steghide`.  
Always run `extract-flags` on any carved output. `save-flag` when found.
