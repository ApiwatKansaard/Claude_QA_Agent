#!/usr/bin/env bash
# ============================================================
# QA Ops Director — mcp-atlassian Setup & Patch Script
# ============================================================
# Installs mcp-atlassian globally and patches the Jira Search API
# to use the new POST /search/jql endpoint (the old GET /search
# was removed by Atlassian in 2025).
#
# Run once:  bash scripts/setup-mcp-atlassian.sh
# Re-run after:  npm update -g mcp-atlassian
# ============================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { printf "${GREEN}✓${NC} %s\n" "$1"; }
warn()  { printf "${YELLOW}⚠${NC} %s\n" "$1"; }
fail()  { printf "${RED}✗${NC} %s\n" "$1"; exit 1; }

# -----------------------------------------------------------
# 1. Install mcp-atlassian + jsdom globally
# -----------------------------------------------------------
echo "=== Step 1: Installing mcp-atlassian globally ==="

if command -v mcp-atlassian &>/dev/null; then
    info "mcp-atlassian already installed at $(which mcp-atlassian)"
else
    npm install -g mcp-atlassian jsdom || fail "npm install failed"
    info "mcp-atlassian installed"
fi

MCP_BIN=$(which mcp-atlassian)
info "Binary: $MCP_BIN"

# -----------------------------------------------------------
# 2. Locate handlers.js
# -----------------------------------------------------------
echo ""
echo "=== Step 2: Locating handlers.js ==="

# Resolve the actual npm global prefix (works for nvm, homebrew, volta, etc.)
NPM_PREFIX=$(npm root -g)
HANDLERS="$NPM_PREFIX/mcp-atlassian/dist/jira/handlers.js"

if [ ! -f "$HANDLERS" ]; then
    fail "Cannot find $HANDLERS — is mcp-atlassian installed globally?"
fi
info "Found: $HANDLERS"

# -----------------------------------------------------------
# 3. Check if already patched
# -----------------------------------------------------------
echo ""
echo "=== Step 3: Checking patch status ==="

if grep -q "POST.*search/jql" "$HANDLERS" 2>/dev/null; then
    info "Already patched — Jira search uses POST /search/jql"
    echo ""
    echo "Done! No changes needed."
    exit 0
fi

warn "Not patched yet — applying fix..."

# -----------------------------------------------------------
# 4. Backup
# -----------------------------------------------------------
echo ""
echo "=== Step 4: Creating backup ==="

cp "$HANDLERS" "$HANDLERS.bak"
info "Backup: $HANDLERS.bak"

# -----------------------------------------------------------
# 5. Patch: GET /search → POST /search/jql
# -----------------------------------------------------------
echo ""
echo "=== Step 5: Patching Jira Search endpoint ==="

# 5a. Change .get('/rest/api/3/search' to .post('/rest/api/3/search/jql'
#     But NOT /rest/api/3/user/search (different endpoint)
python3 << 'PYEOF'
import re, sys

path = sys.argv[1] if len(sys.argv) > 1 else ""
if not path:
    sys.exit(1)

with open(path, "r") as f:
    content = f.read()

original = content

# 5a. GET /search → POST /search/jql (skip /user/search)
content = re.sub(
    r"this\.client\.get\('/rest/api/3/search'",
    "this.client.post('/rest/api/3/search/jql'",
    content
)

# 5b. Convert fields from comma-separated string to array
#     e.g. fields: 'summary,status,...' → fields: ['summary','status',...]
def convert_fields(m):
    fields_str = m.group(1)
    fields_list = [f"'{f.strip()}'" for f in fields_str.split(',')]
    return f"fields: [{', '.join(fields_list)}]"

content = re.sub(
    r"fields:\s*'([^']+)'",
    convert_fields,
    content
)

# 5c. Remove startAt from POST body (new API uses nextPageToken)
#     Match: startAt: 0, or startAt, or startAt: startAt,
content = re.sub(
    r",?\s*startAt:\s*(?:0|startAt)\s*,?",
    lambda m: "," if m.group(0).count(",") == 2 else "",
    content
)
# Clean up double commas and trailing commas before }
content = re.sub(r",\s*,", ",", content)
content = re.sub(r",(\s*})", r"\1", content)

changes = 0
if content != original:
    with open(path, "w") as f:
        f.write(content)
    # Count changes
    changes += content.count("search/jql") - original.count("search/jql")
    print(f"Patched: {changes} search endpoints updated")
else:
    print("No changes needed")

PYEOF

python3 -c "
import sys
path = '$HANDLERS'
with open(path) as f:
    content = f.read()
post_count = content.count(\"post('/rest/api/3/search/jql'\")
get_count = content.count(\"get('/rest/api/3/search'\")
print(f'  POST /search/jql: {post_count} occurrences')
print(f'  GET /search: {get_count} occurrences (should be 0)')
if get_count > 0:
    print('  WARNING: Some endpoints were not patched!')
    sys.exit(1)
"

info "Jira Search endpoint patched"

# -----------------------------------------------------------
# 6. Verify
# -----------------------------------------------------------
echo ""
echo "=== Step 6: Verifying ==="

# Quick MCP protocol test
python3 << 'PYEOF'
import subprocess, os, json, time, sys

if not os.environ.get("ATLASSIAN_BASE_URL"):
    print("  Skipping live test (no ATLASSIAN_BASE_URL set)")
    print("  To test manually: ATLASSIAN_BASE_URL=... ATLASSIAN_EMAIL=... ATLASSIAN_API_TOKEN=... bash scripts/setup-mcp-atlassian.sh")
    sys.exit(0)

env = os.environ.copy()
env['LOG_LEVEL'] = 'error'

proc = subprocess.Popen(
    [os.environ.get('MCP_BIN', 'mcp-atlassian')],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    env=env
)

msg = json.dumps({
    'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
    'params': {
        'protocolVersion': '2024-11-05',
        'capabilities': {},
        'clientInfo': {'name': 'setup-verify', 'version': '1.0'}
    }
})
proc.stdin.write((msg + '\n').encode())
proc.stdin.flush()
time.sleep(3)
proc.stdin.close()

stdout = proc.stdout.read().decode()
proc.wait(timeout=5)

try:
    response = json.loads(stdout.strip().split('\n')[0])
    server_name = response.get('result', {}).get('serverInfo', {}).get('name', '?')
    server_ver = response.get('result', {}).get('serverInfo', {}).get('version', '?')
    print(f"  MCP server responds: {server_name} v{server_ver}")
except Exception as e:
    print(f"  WARNING: Could not verify MCP response: {e}")
    sys.exit(1)
PYEOF

info "Setup complete!"

echo ""
echo "============================================================"
echo "  mcp-atlassian is installed and patched."
echo "  Reload VS Code (Cmd+Shift+P → Reload Window) to activate."
echo "============================================================"
