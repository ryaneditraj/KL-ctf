#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
critical=(nmap curl dig python3 file strings)
optional=(whois ffuf gobuster sqlmap tshark tcpdump exiftool binwalk steghide zsteg checksec radare2 r2 gdb jq rg)
ok=0
miss_c=()

echo "=== Critical (workshop + harness) ==="
for t in "${critical[@]}"; do
  if command -v "$t" >/dev/null 2>&1; then echo "  OK  $t"; else echo "  MISS $t"; miss_c+=("$t"); ok=1; fi
done

PY="$ROOT/.venv/bin/python3"
[[ -x "$PY" ]] || PY="$(command -v python3)"
if "$PY" -c "import requests" 2>/dev/null; then echo "  OK  python-requests"; else echo "  MISS python-requests"; ok=1; fi
if "$PY" "$ROOT/tools/cypherflag.py" --help >/dev/null 2>&1; then echo "  OK  cypherflag.py"; else echo "  MISS cypherflag.py"; ok=1; fi

echo
echo "=== Optional ==="
miss_o=()
for t in "${optional[@]}"; do
  command -v "$t" >/dev/null 2>&1 || miss_o+=("$t")
done
if ((${#miss_o[@]})); then echo "  Missing: ${miss_o[*]}"; else echo "  All optional present"; fi
"$PY" -c "import pwn" 2>/dev/null && echo "  OK  pwntools" || echo "  MISS pwntools (pwn category)"

echo
if ((ok)); then
  echo "RESULT: fix gaps via scripts/bootstrap.sh (missing: ${miss_c[*]})"
  exit 1
fi
echo "RESULT: ready to hunt flags"
exit 0
