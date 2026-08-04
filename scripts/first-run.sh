#!/usr/bin/env bash
# One-shot setup for Aaliya's machine / any AI agent boot.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "CypherFlag first-run"
echo "Repo: $ROOT"

chmod +x "$ROOT/scripts/"*.sh "$ROOT/tools/cypherflag.py" 2>/dev/null || true

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q -U pip
pip install -q -r requirements.txt

# OS tools — best effort (agents: keep going even if brew/apt needs password)
if command -v brew >/dev/null 2>&1; then
  brew list nmap >/dev/null 2>&1 || brew install nmap curl bind whois 2>/dev/null || true
elif [[ -f /etc/debian_version ]]; then
  sudo -n true 2>/dev/null && sudo apt-get install -y nmap curl dnsutils whois 2>/dev/null || true
fi

mkdir -p challenges notes flags
[[ -f flags/FOUND.md ]] || echo -e "# Flags found\n" > flags/FOUND.md

echo
bash scripts/check-tools.sh || true
echo
echo "READY. Operator: open Agent chat and paste challenges."
echo "Start message for Aaliya is in AALIYA.md Part A."
