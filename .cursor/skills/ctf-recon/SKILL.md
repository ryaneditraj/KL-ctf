---
name: ctf-recon
description: >
  Network and host reconnaissance for CTF using workshop tools dig, nmap, curl,
  and whois via cypherflag.py. Maps ports/services/DNS then hands off to web/pwn.
  Use for IPs, hostnames, recon labs, and unknown network targets.
---

# CTF Recon

Workshop tools: **dig · nmap · curl · whois**

## Canonical command

```bash
python3 tools/cypherflag.py recon <ip-or-url>
```

Or stepwise:

```bash
python3 tools/cypherflag.py dig <host>
python3 tools/cypherflag.py whois <host>
python3 tools/cypherflag.py nmap <host>
python3 tools/cypherflag.py nmap <host> --full
python3 tools/cypherflag.py http http://<host>/
```

## After recon

- HTTP open → `ctf-web`
- Weird binary port → `ctf-pwn`
- Check DNS TXT / http headers / robots for free flags
- Save output excerpt to `notes/<slug>/recon.md`
