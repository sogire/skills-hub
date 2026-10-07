#!/usr/bin/env bash
# ==============================================================================
# Antigravity Skills & Plugins Hub - Setup & Installation Script
# ==============================================================================
# Usage:
#   ./install.sh
#
# This script:
#   1. Validates Python 3 (3.10+ recommended)
#   2. Initializes and checks Git submodules (external repositories)
#   3. Symlinks bin/agyhub to ~/.local/bin/agyhub
#   4. Verifies PATH configuration
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_SRC="${SCRIPT_DIR}/bin/agyhub"
TARGET_DIR="${HOME}/.local/bin"
TARGET_LINK="${TARGET_DIR}/agyhub"
LEGACY_LINK="${TARGET_DIR}/ag-hub"

COLOR_GREEN="\033[32m"
COLOR_CYAN="\033[36m"
COLOR_YELLOW="\033[33m"
COLOR_RED="\033[31m"
COLOR_BOLD="\033[1m"
COLOR_RESET="\033[0m"

echo -e "\n${COLOR_BOLD}=== Antigravity Skills Hub Installer ===${COLOR_RESET}\n"

# 1. Validate Python
if ! command -v python3 &>/dev/null; then
    echo -e "${COLOR_RED}Error: python3 is not installed.${COLOR_RESET}" >&2
    echo "Please install Python 3 (3.10 or higher) and re-run this script." >&2
    exit 1
fi

PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_CHECK=$(python3 -c 'import sys; print(1 if sys.version_info >= (3, 10) else 0)')

if [ "${PY_CHECK}" -eq 1 ]; then
    echo -e "${COLOR_GREEN}✓${COLOR_RESET} Python ${PY_VER} detected (Standard Library only - zero pip dependencies required)."
else
    echo -e "${COLOR_YELLOW}!${COLOR_RESET} Python ${PY_VER} detected. Python 3.10+ is recommended."
fi

# 2. Check / Initialize Git Submodules
if [ -f "${SCRIPT_DIR}/.gitmodules" ]; then
    echo -e "\nChecking Git submodules in external/..."
    if command -v git &>/dev/null; then
        git -C "${SCRIPT_DIR}" submodule update --init --recursive
        echo -e "${COLOR_GREEN}✓${COLOR_RESET} Submodules initialized."
    else
        echo -e "${COLOR_YELLOW}!${COLOR_RESET} Git is not installed or not in PATH; skipping submodule init."
    fi
fi

# 3. Create ~/.local/bin and symlink agyhub (strict cutover from ag-hub)
mkdir -p "${TARGET_DIR}"
chmod +x "${BIN_SRC}"

# Remove legacy ag-hub symlink or binary if present
if [ -L "${LEGACY_LINK}" ] || [ -f "${LEGACY_LINK}" ]; then
    rm -f "${LEGACY_LINK}"
    echo -e "${COLOR_YELLOW}!${COLOR_RESET} Removed legacy executable link: ${LEGACY_LINK}"
fi

if [ -L "${TARGET_LINK}" ] || [ -f "${TARGET_LINK}" ]; then
    rm -f "${TARGET_LINK}"
fi

ln -s "${BIN_SRC}" "${TARGET_LINK}"
echo -e "${COLOR_GREEN}✓${COLOR_RESET} CLI executable symlinked:"
echo -e "  ${COLOR_CYAN}${TARGET_LINK}${COLOR_RESET} -> ${BIN_SRC}"

# 4. PATH Verification
echo ""
case ":${PATH}:" in
    *":${TARGET_DIR}:"*)
        echo -e "${COLOR_GREEN}✓${COLOR_RESET} ${TARGET_DIR} is already in your PATH."
        ;;
    *)
        echo -e "${COLOR_YELLOW}! Notice:${COLOR_RESET} ${TARGET_DIR} is not currently in your shell's PATH."
        echo "To run 'agyhub' from anywhere, add this directory to your shell configuration:"
        echo ""
        echo "  # For Bash (~/.bashrc):"
        echo "  echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc && source ~/.bashrc"
        echo ""
        echo "  # For Zsh (~/.zshrc):"
        echo "  echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.zshrc && source ~/.zshrc"
        echo ""
        ;;
esac

echo -e "${COLOR_BOLD}=== Installation Complete! ===${COLOR_RESET}\n"
echo "You can now run:"
echo "  agyhub list          # Overview of available skill suites and active skills"
echo "  agyhub list <query>  # Search 200+ skills by keyword"
echo "  agyhub enable -g ... # Enable a group into your project"
echo "  agyhub --help        # View all CLI commands"
echo ""
