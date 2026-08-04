#!/usr/bin/env bash
# One-shot setup for Aaliya's Mac when an AI agent boots this repo in Cursor.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=========================================="
echo " KL-ctf first-run  |  operator: Aaliya"
echo " Agentic runtime: Cursor Agent (or Claude Code)"
echo "=========================================="
echo "Repo: $ROOT"

chmod +x "$ROOT/scripts/"*.sh "$ROOT/tools/cypherflag.py" 2>/dev/null || true

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q -U pip
pip install -q -r requirements.txt

mkdir -p challenges notes flags
[[ -f flags/FOUND.md ]] || printf '%s\n' '# Flags found' '' > flags/FOUND.md

# Real scanners — Mac (Aaliya) preferred path
if [[ "$(uname -s)" == "Darwin" ]]; then
  echo
  echo "Installing / verifying scanners on Aaliya's Mac..."
  bash "$ROOT/scripts/install-mac-scanners.sh" || true
elif [[ -f /etc/debian_version ]]; then
  echo "Debian/Ubuntu best-effort packages..."
  if sudo -n true 2>/dev/null; then
    sudo apt-get update -qq || true
    sudo apt-get install -y nmap curl dnsutils whois ffuf gobuster sqlmap jq ripgrep \
      exiftool binwalk steghide radare2 netcat-openbsd 2>/dev/null || true
  else
    echo "No passwordless sudo — agent should install packages when Allow/password available."
  fi
  # nuclei often via go/brew; try snap or skip
  command -v nuclei >/dev/null 2>&1 || echo "WARN: nuclei not installed"
fi

echo
bash "$ROOT/scripts/check-tools.sh" || true
echo
echo "READY for Aaliya."
echo "She pastes CTFd challenges into Cursor Agent → clicks Allow → submits FLAG: lines."
echo "This system is AGENTIC: Cursor runs the think→tool→observe loop; this repo is the harness."
