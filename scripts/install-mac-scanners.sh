#!/usr/bin/env bash
# Install real CTF scanners on Aaliya's Mac (Homebrew).
# AI agents: run this during first-run. Operator should only click Allow / enter Mac password if asked.
set -euo pipefail

echo "=== KL-ctf scanner install (macOS / Aaliya) ==="

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "Not macOS — use scripts/bootstrap.sh / apt instead."
  exit 0
fi

if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew missing. Installing Homebrew (may need Aaliya to Approve / password)..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" || {
    echo "ERROR: Homebrew install failed. Ask Ryan / click Allow and re-run."
    exit 1
  }
  # Apple Silicon path
  if [[ -x /opt/homebrew/bin/brew ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
  fi
fi

# Ensure brew in PATH for this shell
if [[ -x /opt/homebrew/bin/brew ]]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
elif [[ -x /usr/local/bin/brew ]]; then
  eval "$(/usr/local/bin/brew shellenv)"
fi

echo "Updating brew (best effort)..."
brew update 2>/dev/null || true

# Workshop + scanners (idempotent)
PKGS=(
  nmap
  curl
  bind          # dig
  whois
  ffuf
  gobuster
  sqlmap
  nuclei
  jq
  ripgrep
  exiftool
  binwalk
  steghide
  radare2
  netcat
)

echo "Installing packages: ${PKGS[*]}"
for p in "${PKGS[@]}"; do
  if brew list "$p" >/dev/null 2>&1; then
    echo "  OK already: $p"
  else
    echo "  INSTALL: $p"
    brew install "$p" 2>/dev/null || echo "  WARN: failed $p (continue)"
  fi
done

# nuclei templates (first time)
if command -v nuclei >/dev/null 2>&1; then
  echo "Updating nuclei templates (best effort)..."
  nuclei -update-templates 2>/dev/null || true
fi

echo
echo "=== Scanner versions ==="
for c in nmap dig curl ffuf gobuster sqlmap nuclei whois; do
  if command -v "$c" >/dev/null 2>&1; then
    echo "  OK  $c → $(command -v "$c")"
  else
    echo "  MISS $c"
  fi
done

echo
echo "DONE. Aaliya: you only needed to Approve installs. Continue pasting challenges in Cursor Agent."
