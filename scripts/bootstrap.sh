#!/usr/bin/env bash
# Install CTF tools + Python deps for CypherFlag.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== Python venv + requirements ==="
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
# Optional pwn stack (skip if build fails — web/recon still win most CTFs)
pip install pwntools 2>/dev/null || echo "pwntools optional install skipped"

echo "=== OS packages ==="
if [[ "$(uname -s)" == "Darwin" ]]; then
  if ! command -v brew >/dev/null 2>&1; then
    echo "Install Homebrew: https://brew.sh"
    exit 1
  fi
  brew install nmap curl bind whois file python3 jq ripgrep \
    exiftool binwalk steghide radare2 2>/dev/null || true
elif [[ -f /etc/debian_version ]]; then
  sudo apt-get update
  sudo apt-get install -y nmap curl dnsutils whois file binutils python3 python3-pip python3-venv \
    jq ripgrep exiftool binwalk steghide radare2 tcpdump tshark netcat-openbsd \
    gdb 2>/dev/null || true
else
  echo "Install nmap curl dig whois manually for your OS"
fi

chmod +x "$ROOT/scripts/"*.sh || true
echo
bash "$ROOT/scripts/solve.sh" doctor || true
echo "Bootstrap finished. Activate: source .venv/bin/activate"
