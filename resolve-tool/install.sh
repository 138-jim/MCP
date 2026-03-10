#!/usr/bin/env bash
set -euo pipefail

# ──────────────────────────────────────────────────────────────
# resolve-tool installer
# Sets up the MCP server for DaVinci Resolve control via Claude
# ──────────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC_DIR="$SCRIPT_DIR/src"
MIN_PYTHON="3.10"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

info()  { echo -e "${BLUE}▸${NC} $*"; }
ok()    { echo -e "${GREEN}✓${NC} $*"; }
warn()  { echo -e "${YELLOW}!${NC} $*"; }
fail()  { echo -e "${RED}✗${NC} $*"; exit 1; }

# ── Find Python ──────────────────────────────────────────────

find_python() {
    for cmd in python3 python; do
        if command -v "$cmd" &>/dev/null; then
            local ver
            ver="$("$cmd" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
            if "$cmd" -c "import sys; exit(0 if sys.version_info >= (3,10) else 1)" 2>/dev/null; then
                PYTHON="$cmd"
                PYTHON_PATH="$(command -v "$cmd")"
                PYTHON_VER="$ver"
                return 0
            fi
        fi
    done
    return 1
}

if ! find_python; then
    fail "Python ${MIN_PYTHON}+ is required but not found. Install it from https://python.org"
fi
ok "Found Python ${PYTHON_VER} at ${PYTHON_PATH}"

# ── Check Resolve scripting module ───────────────────────────

check_resolve_module() {
    case "$(uname -s)" in
        Darwin)
            RESOLVE_MODULES="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules"
            ;;
        Linux)
            RESOLVE_MODULES="/opt/resolve/Developer/Scripting/Modules"
            ;;
        MINGW*|MSYS*|CYGWIN*)
            RESOLVE_MODULES="${PROGRAMDATA:-C:\\ProgramData}/Blackmagic Design/DaVinci Resolve/Support/Developer/Scripting/Modules"
            ;;
        *)
            RESOLVE_MODULES=""
            ;;
    esac

    if [ -n "$RESOLVE_MODULES" ] && [ -d "$RESOLVE_MODULES" ]; then
        ok "Resolve scripting modules found at ${RESOLVE_MODULES}"
        return 0
    else
        warn "Resolve scripting modules not found at default path"
        warn "Make sure DaVinci Resolve is installed. The MCP server will fail to connect without it."
        return 1
    fi
}

check_resolve_module || true

# ── Install Python package ───────────────────────────────────

echo ""
info "Installing resolve-tool with MCP dependencies..."
"$PYTHON" -m pip install -e "${SCRIPT_DIR}[mcp]" --quiet 2>&1 | tail -5
ok "Python package installed"

# Verify it works
if "$PYTHON" -c "import resolve_mcp" 2>/dev/null; then
    ok "resolve_mcp module imports successfully"
else
    fail "Failed to import resolve_mcp after install"
fi

# ── Configure MCP clients ────────────────────────────────────

MCP_CONFIG="{
  \"mcpServers\": {
    \"resolve\": {
      \"command\": \"${PYTHON_PATH}\",
      \"args\": [\"-m\", \"resolve_mcp\"],
      \"cwd\": \"${SCRIPT_DIR}\",
      \"env\": {
        \"PYTHONPATH\": \"${SRC_DIR}\"
      }
    }
  }
}"

echo ""
echo -e "${BOLD}Configure MCP clients${NC}"
echo ""
echo "Which clients do you want to configure?"
echo ""
echo "  1) Claude Code  (adds .mcp.json to current project)"
echo "  2) Claude Desktop"
echo "  3) Cursor"
echo "  4) All detected"
echo "  5) None (just print the config)"
echo ""
read -rp "Choice [1-5]: " choice

write_mcp_json() {
    local dest="$1"
    local label="$2"
    local dir
    dir="$(dirname "$dest")"

    if [ -f "$dest" ]; then
        # Merge into existing config
        if "$PYTHON" -c "
import json, sys
with open('$dest') as f:
    cfg = json.load(f)
server = json.loads('''$MCP_CONFIG''')['mcpServers']['resolve']
cfg.setdefault('mcpServers', {})['resolve'] = server
with open('$dest', 'w') as f:
    json.dump(cfg, f, indent=2)
    f.write('\n')
" 2>/dev/null; then
            ok "${label}: updated ${dest}"
        else
            warn "${label}: failed to update ${dest} — write it manually"
        fi
    else
        mkdir -p "$dir"
        echo "$MCP_CONFIG" | "$PYTHON" -c "
import json, sys
cfg = json.load(sys.stdin)
with open('$dest', 'w') as f:
    json.dump(cfg, f, indent=2)
    f.write('\n')
"
        ok "${label}: created ${dest}"
    fi
}

configure_claude_code() {
    local dest
    read -rp "Project directory for .mcp.json [$(pwd)]: " dest
    dest="${dest:-$(pwd)}"
    write_mcp_json "${dest}/.mcp.json" "Claude Code"
}

configure_claude_desktop() {
    local dest
    case "$(uname -s)" in
        Darwin)  dest="$HOME/Library/Application Support/Claude/claude_desktop_config.json" ;;
        Linux)   dest="$HOME/.config/Claude/claude_desktop_config.json" ;;
        *)       dest="$APPDATA/Claude/claude_desktop_config.json" ;;
    esac
    write_mcp_json "$dest" "Claude Desktop"
}

configure_cursor() {
    local dest
    read -rp "Project directory for .cursor/mcp.json [$(pwd)]: " dest
    dest="${dest:-$(pwd)}"
    write_mcp_json "${dest}/.cursor/mcp.json" "Cursor"
}

case "${choice:-5}" in
    1) configure_claude_code ;;
    2) configure_claude_desktop ;;
    3) configure_cursor ;;
    4)
        configure_claude_code
        if [ -d "$HOME/Library/Application Support/Claude" ] || [ -d "$HOME/.config/Claude" ]; then
            configure_claude_desktop
        fi
        configure_cursor
        ;;
    5)
        echo ""
        echo -e "${BOLD}Add this to your MCP client config:${NC}"
        echo ""
        echo "$MCP_CONFIG" | "$PYTHON" -m json.tool
        ;;
    *)
        warn "Invalid choice, printing config instead"
        echo "$MCP_CONFIG" | "$PYTHON" -m json.tool
        ;;
esac

# ── Done ─────────────────────────────────────────────────────

echo ""
echo -e "${GREEN}${BOLD}Installation complete!${NC}"
echo ""
echo "  To test manually:  PYTHONPATH=${SRC_DIR} ${PYTHON_PATH} -m resolve_mcp"
echo "  Make sure DaVinci Resolve is running before using the MCP tools."
echo ""
