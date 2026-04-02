#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# QA Agent Bootstrap — Run once after cloning both repos
# Called by /qa-get-started or manually: bash scripts/bootstrap.sh
# ═══════════════════════════════════════════════════════════════
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

ok()   { echo -e "${GREEN}✅ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
fail() { echo -e "${RED}❌ $1${NC}"; }

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AGENT_DIR="$(dirname "$SCRIPT_DIR")"
AUTOMATION_DIR="${AGENT_DIR}/../Claude_QA_Automation"

echo "═══════════════════════════════════════"
echo " QA Agent Bootstrap"
echo "═══════════════════════════════════════"
echo ""

# ── 1. Check Node.js ──────────────────────────────────────────
echo "Checking prerequisites..."
if command -v node &>/dev/null; then
  NODE_VER=$(node --version)
  ok "Node.js $NODE_VER"
else
  fail "Node.js not found"
  echo "  Install: brew install node"
  exit 1
fi

# ── 2. Check Python ───────────────────────────────────────────
if command -v python3 &>/dev/null; then
  PY_VER=$(python3 --version)
  ok "$PY_VER"
else
  fail "Python3 not found"
  echo "  Install: brew install python3"
  exit 1
fi

# ── 3. Check Git ──────────────────────────────────────────────
if command -v git &>/dev/null; then
  ok "Git $(git --version | cut -d' ' -f3)"
else
  fail "Git not found"
  exit 1
fi

# ── 4. Check sibling repo ────────────────────────────────────
echo ""
echo "Checking repositories..."
if [ -f "$AUTOMATION_DIR/playwright.config.ts" ]; then
  ok "Claude_QA_Automation found"
else
  fail "Claude_QA_Automation not found at $AUTOMATION_DIR"
  echo ""
  echo "  Clone it next to Claude_QA_Agent:"
  echo "    cd $(dirname "$AGENT_DIR")"
  echo "    git clone https://github.com/ApiwatKansaard/Claude_QA_Automation.git"
  exit 1
fi

# ── 5. npm install in QA_Automation ──────────────────────────
echo ""
echo "Installing dependencies..."
cd "$AUTOMATION_DIR"
if [ -d "node_modules" ]; then
  ok "node_modules exists (skipping npm install)"
else
  npm install --silent
  ok "npm install complete"
fi

# ── 6. Playwright browsers ──────────────────────────────────
if npx playwright install --dry-run chromium &>/dev/null 2>&1; then
  ok "Playwright chromium already installed"
else
  npx playwright install --with-deps chromium
  ok "Playwright chromium installed"
fi

# ── 7. Install mcp-atlassian ────────────────────────────────
echo ""
echo "Checking MCP tools..."
if command -v mcp-atlassian &>/dev/null; then
  ok "mcp-atlassian installed"
else
  warn "mcp-atlassian not found — installing..."
  npm install -g mcp-atlassian 2>/dev/null || brew install mcp-atlassian 2>/dev/null || {
    fail "Could not install mcp-atlassian"
    echo "  Try manually: npm install -g mcp-atlassian"
  }
fi

# ── 8. Check ngrok ───────────────────────────────────────────
if command -v ngrok &>/dev/null; then
  ok "ngrok $(ngrok version 2>/dev/null | head -1)"
else
  warn "ngrok not found (optional — needed for webhook E2E tests)"
  echo "  Install: brew install ngrok"
fi

# ── 9. Create .env from template if missing ──────────────────
echo ""
echo "Checking config files..."
cd "$AGENT_DIR"
if [ -f ".env" ]; then
  ok ".env exists"
else
  if [ -f ".env.example" ]; then
    cp .env.example .env
    warn ".env created from template — fill in your credentials!"
  else
    warn ".env not found and no template available"
  fi
fi

# ── 10. Create ~/.claude/.mcp.json if missing ────────────────
CLAUDE_MCP="$HOME/.claude/.mcp.json"
if [ -f "$CLAUDE_MCP" ]; then
  ok "~/.claude/.mcp.json exists"
else
  mkdir -p "$HOME/.claude"
  cat > "$CLAUDE_MCP" << 'MCPJSON'
{
  "mcpServers": {
    "atlassian": {
      "command": "mcp-atlassian",
      "env": {
        "ATLASSIAN_BASE_URL": "https://ekoapp.atlassian.net",
        "ATLASSIAN_EMAIL": "REPLACE_WITH_YOUR_EMAIL",
        "ATLASSIAN_API_TOKEN": "REPLACE_WITH_YOUR_TOKEN",
        "LOG_LEVEL": "error",
        "NODE_ENV": "production"
      }
    }
  }
}
MCPJSON
  warn "~/.claude/.mcp.json created — EDIT IT with your credentials!"
  echo "  File: $CLAUDE_MCP"
fi

# ── Done ─────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════"
echo " Bootstrap complete!"
echo "═══════════════════════════════════════"
echo ""
echo " Next steps:"
echo "  1. Edit .env with your Atlassian + TestRail credentials"
echo "  2. Edit ~/.claude/.mcp.json with your Atlassian credentials"
echo "  3. Reload window (Cmd+Shift+P → Reload Window)"
echo "  4. Run: /qa-get-started (to verify everything)"
echo ""
