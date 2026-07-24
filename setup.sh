#!/usr/bin/env bash
#
# DailyAndacht — one-shot setup for a fresh Mac.
#
# Run once after `git clone`, from anywhere:
#     ./setup.sh
#
# It assumes NOTHING is installed and makes the authoring tool runnable:
#   1. Xcode Command Line Tools (compilers/git) — needed by Homebrew
#   2. Homebrew (the macOS package manager)
#   3. A modern Python (3.12) via Homebrew
#   4. A project virtualenv at ./.venv
#   5. All Python packages from requirements.txt
#   6. Playwright's bundled WebKit engine (for PNG promo images)
#
# The script is idempotent: re-running it just verifies/repairs each step,
# so it's safe to run again any time.

set -euo pipefail

# --- pretty output ----------------------------------------------------------
BOLD=$'\033[1m'; GREEN=$'\033[32m'; YELLOW=$'\033[33m'; RED=$'\033[31m'; RESET=$'\033[0m'
step() { printf '\n%s==> %s%s\n' "$BOLD" "$1" "$RESET"; }
ok()   { printf '%s   ✓ %s%s\n' "$GREEN" "$1" "$RESET"; }
info() { printf '     %s\n' "$1"; }
warn() { printf '%s   ! %s%s\n' "$YELLOW" "$1" "$RESET"; }
die()  { printf '%s   ✗ %s%s\n' "$RED" "$1" "$RESET" >&2; exit 1; }

# Always work from the directory this script lives in (the repo root).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PYTHON_FORMULA="python@3.12"

[[ "$(uname -s)" == "Darwin" ]] || die "This setup script is for macOS only."

# --- 1. Xcode Command Line Tools -------------------------------------------
step "Checking Xcode Command Line Tools"
if xcode-select -p >/dev/null 2>&1; then
  ok "Command Line Tools already installed"
else
  warn "Not installed — launching Apple's installer (a GUI window will open)."
  xcode-select --install || true
  info "Complete the install in the popup, then press RETURN here to continue."
  read -r _
  xcode-select -p >/dev/null 2>&1 || die "Command Line Tools still missing. Re-run ./setup.sh after they finish installing."
  ok "Command Line Tools installed"
fi

# --- 2. Homebrew ------------------------------------------------------------
step "Checking Homebrew"
if ! command -v brew >/dev/null 2>&1; then
  # brew may already be installed but not on PATH in this shell.
  for cand in /opt/homebrew/bin/brew /usr/local/bin/brew; do
    [[ -x "$cand" ]] && eval "$("$cand" shellenv)" && break
  done
fi

if command -v brew >/dev/null 2>&1; then
  ok "Homebrew already installed"
else
  warn "Installing Homebrew (you may be prompted for your macOS password)…"
  NONINTERACTIVE=1 /bin/bash -c \
    "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  # Load brew into this shell for the rest of the script.
  for cand in /opt/homebrew/bin/brew /usr/local/bin/brew; do
    [[ -x "$cand" ]] && eval "$("$cand" shellenv)" && break
  done
  command -v brew >/dev/null 2>&1 || die "Homebrew install did not complete."
  ok "Homebrew installed"
fi

# Make brew persist in future terminal sessions (append once to the profile).
BREW_PREFIX="$(brew --prefix)"
SHELL_PROFILE="${HOME}/.zprofile"   # zsh is the macOS default
BREW_LINE="eval \"\$(${BREW_PREFIX}/bin/brew shellenv)\""
if [[ -w "$SHELL_PROFILE" || ! -e "$SHELL_PROFILE" ]]; then
  if ! grep -qsF "$BREW_LINE" "$SHELL_PROFILE" 2>/dev/null; then
    printf '\n# Homebrew\n%s\n' "$BREW_LINE" >> "$SHELL_PROFILE"
    info "Added Homebrew to $SHELL_PROFILE for future terminals."
  fi
fi

# --- 3. Python --------------------------------------------------------------
step "Checking Python ($PYTHON_FORMULA)"
if brew list --formula "$PYTHON_FORMULA" >/dev/null 2>&1; then
  ok "$PYTHON_FORMULA already installed"
else
  warn "Installing $PYTHON_FORMULA…"
  brew install "$PYTHON_FORMULA"
  ok "$PYTHON_FORMULA installed"
fi

PY_BIN="$(brew --prefix "$PYTHON_FORMULA")/bin/python3.12"
[[ -x "$PY_BIN" ]] || PY_BIN="$(command -v python3.12 || true)"
[[ -x "$PY_BIN" ]] || die "Could not locate the python3.12 binary after install."
ok "Using $("$PY_BIN" --version) at $PY_BIN"

# --- 4. Virtualenv ----------------------------------------------------------
step "Setting up virtualenv (./.venv)"
# If an old venv exists built against a different Python, rebuild it cleanly.
if [[ -x .venv/bin/python ]] && .venv/bin/python -c 'import sys; sys.exit(0 if sys.version_info[:2]==(3,12) else 1)' 2>/dev/null; then
  ok "Existing .venv is Python 3.12 — reusing it"
else
  [[ -e .venv ]] && { warn "Recreating .venv with Python 3.12…"; rm -rf .venv; }
  "$PY_BIN" -m venv .venv
  ok "Created .venv"
fi

VENV_PY="$SCRIPT_DIR/.venv/bin/python"

# --- 5. Python packages -----------------------------------------------------
step "Installing Python packages (requirements.txt)"
"$VENV_PY" -m pip install --upgrade pip >/dev/null
"$VENV_PY" -m pip install -r requirements.txt
ok "Installed: $(tr '\n' ' ' < requirements.txt)"

# --- 6. Playwright browser engine ------------------------------------------
step "Installing Playwright's WebKit engine (for promo-image PNG export)"
if "$VENV_PY" -m playwright install webkit; then
  ok "WebKit engine ready"
else
  warn "WebKit download failed — the tool still works, but PNG export will fall"
  warn "back to a system browser. Re-run: ./.venv/bin/playwright install webkit"
fi

# --- done -------------------------------------------------------------------
step "Setup complete 🎉"
cat <<EOF

You're ready. Start the authoring tool with:

  ${BOLD}./.venv/bin/python src/creator/create_sermon.py -manual${RESET}
  ${BOLD}./.venv/bin/python src/creator/create_sermon.py -assisted${RESET}

Notes:
  • Open a NEW terminal (or run: source ~/.zprofile) so 'brew' is on your PATH.
  • Assisted mode also needs Ollama running locally (https://ollama.com) with a
    model pulled, e.g.:  ollama pull llama3   — this script does not install it.
EOF
