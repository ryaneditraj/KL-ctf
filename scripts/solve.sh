#!/usr/bin/env bash
# Preflight + optional first recon. Usage:
#   scripts/solve.sh init <slug> [--title "Name"]
#   scripts/solve.sh recon <target>
#   scripts/solve.sh doctor
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PY="${ROOT}/.venv/bin/python3"
if [[ ! -x "$PY" ]]; then PY="$(command -v python3)"
fi
CF=("$PY" "$ROOT/tools/cypherflag.py")

cmd="${1:-}"
if [[ $# -gt 0 ]]; then
  shift
fi

case "$cmd" in
  doctor)
    bash "$ROOT/scripts/check-tools.sh" || true
    echo
    echo "=== Python toolkit ==="
    "$PY" -c "import requests,Crypto; print('requests+pycryptodome OK')" 2>/dev/null \
      || echo "MISS: pip install -r requirements.txt"
    "$PY" -c "import pwn; print('pwntools OK')" 2>/dev/null || echo "MISS optional: pwntools"
    echo
    echo "=== cypherflag CLI ==="
    "${CF[@]}" --help
    ;;
  init)
    slug="${1:?slug required}"
    shift || true
    title=""
    if [[ "${1:-}" == "--title" ]]; then title="${2:-}"; fi
    "${CF[@]}" new-challenge "$slug" --title "$title"
    echo
    echo "NEXT (paste into Cursor Agent):"
    cat <<EOF
I am solving challenge: $slug
Read challenges/$slug/README.md after I paste CTFd text there.
Run: python3 tools/cypherflag.py autosolve --slug $slug --text-file challenges/$slug/README.md
Then keep exploiting until FLAG. I am non-technical — you run all commands.
EOF
    ;;
  recon)
    target="${1:?target required}"
    "${CF[@]}" recon "$target"
    ;;
  autosolve)
    slug="${1:?slug}"
    target="${2:-}"
    if [[ -n "$target" ]]; then
      "${CF[@]}" autosolve --slug "$slug" --target "$target"
    else
      "${CF[@]}" autosolve --slug "$slug" --text-file "$ROOT/challenges/$slug/README.md"
    fi
    ;;
  first-run)
    bash "$ROOT/scripts/first-run.sh"
    ;;
  *)
    echo "Usage: $0 {doctor|first-run|init <slug>|recon <target>|autosolve <slug> [target]}"
    exit 2
    ;;
esac
