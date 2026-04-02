# /qa:get-started

**Triggers:** onboarding-guide
**References:** [products.md](../references/products.md)

## What This Command Does

Interactive onboarding wizard for new QA team members. Walks through setup step-by-step,
verifies each tool is working, and confirms the user is ready to run their first test.

The agent acts as a patient guide — checks each step, waits for confirmation,
troubleshoots issues, and never skips ahead until the current step passes.

**Supports both Claude Code and GitHub Copilot** — detects which platform the user is on
and adjusts the setup path accordingly.

## Pre-flight: What the agent needs to do BEFORE MCP is available

Steps 0–3 use only Bash + Read + Write tools (no MCP needed).
Steps 4+ require MCP tools (Jira, Confluence) which are available after reload.
The agent must handle the full setup using only basic tools first.

**Bootstrap script:** `scripts/bootstrap.sh` handles system-level installs.
The agent runs it automatically and fills in the gaps interactively.

## Execution Steps

### Step 0 — Detect Platform & Welcome

**First, ask the user which platform they're using:**

```
👋 Welcome to QA Ops Director!

Before we begin, which AI coding tool are you using?

  A) Claude Code (CLI or VSCode Extension)  ← Full features
  B) GitHub Copilot (VS Code)               ← Lite mode (~80% features)
```

Set `$PLATFORM` = `claude-code` or `copilot` based on the answer.

**Auto-detection hint:** If the agent can detect Claude Code-specific context
(CLAUDE.md loaded, `.claude/` folder exists, MCP tools available), suggest:
```
It looks like you're running Claude Code. Is that correct? (yes/no)
```

**Then display the platform comparison:**

```
📊 Platform Comparison:

| Feature                    | Claude Code | Copilot |
|----------------------------|-------------|---------|
| Slash commands (/qa-*)     | ✅ Full     | ✅ Full  |
| MCP tools (Jira/Figma)     | ✅ Full     | ✅ Full  |
| Run tests (Playwright)     | ✅ Full     | ✅ Full  |
| Bug reports + TestRail     | ✅ Full     | ✅ Full  |
| Mock webhook server        | ✅ Full     | ✅ Full  |
| Sprint memory/context      | ✅ Auto     | ⚠️ Manual (.sprint.json only) |
| Scheduled agents (cron)    | ✅ Built-in | ❌ Use GitHub Actions |
| Worktree isolation          | ✅ Built-in | ❌ Manual git worktree |
| Feedback memory             | ✅ Auto     | ❌ Not available |
```

If `$PLATFORM` = `copilot`, add:
```
⚠️ Copilot Lite Mode:
   - All QA commands work normally
   - Sprint context reads from .sprint.json (not memory)
   - No auto-memory of your preferences (use CLAUDE.md comments instead)
   - For scheduled reports, use GitHub Actions instead of /loop
   
   Let's proceed with setup!
```

### Step 1 — Run Bootstrap (Installs everything automatically)

Run the bootstrap script which handles: prerequisites check, sibling repo verification,
npm install, Playwright browsers, mcp-atlassian, ngrok, and config file templates.

```bash
bash scripts/bootstrap.sh
```

**The agent should run this and parse the output.** If any step fails, the script
exits with an error message — the agent should show it and help the user fix it.

If bootstrap succeeds, move to Step 2 (credentials).

**If bootstrap script is not available** (old clone), do manual checks:

```bash
# Prerequisites
node --version      # >= 18
python3 --version   # >= 3.8
git --version       # any

# Sibling repo
ls ../Claude_QA_Automation/playwright.config.ts

# Install deps
cd ../Claude_QA_Automation && npm install
npx playwright install --with-deps chromium

# Install MCP
npm install -g mcp-atlassian
```

### Step 2 — Configure Credentials (Interactive — agent writes files)

The agent collects credentials interactively and writes all config files.
**NEVER log passwords or tokens in output — only confirm they were saved.**

**2a. Ask for all credentials at once:**

```
📝 I need 4 pieces of information to set up everything.
   I'll create all config files for you automatically.

   1. Your Amity email:        (e.g., yourname@amitysolutions.com)
   2. Atlassian API Token:     https://id.atlassian.com/manage-profile/security/api-tokens
   3. TestRail API Key:        https://ekoapp20.testrail.io → My Settings → API Keys
   4. Staging login password:  (your EkoAI Console staging password)

   Please provide them one by one (I won't display them back).
```

**2b. Agent creates all files automatically using the credentials:**

**File 1: `.env` (QA_Agent root)**
```bash
# Agent writes this file — NEVER echo credentials to terminal
cat > .env << EOF
JIRA_EMAIL={email}
JIRA_TOKEN={atlassian_token}
ATLASSIAN_EMAIL={email}
ATLASSIAN_API_TOKEN={atlassian_token}
ATLASSIAN_BASE_URL=https://ekoapp.atlassian.net
TESTRAIL_EMAIL={email}
TESTRAIL_API_KEY={testrail_key}
EOF
```

**File 2: `~/.claude/.mcp.json` (Claude Code MCP — only if `$PLATFORM` = `claude-code`)**
```bash
mkdir -p ~/.claude
cat > ~/.claude/.mcp.json << EOF
{
  "mcpServers": {
    "atlassian": {
      "command": "mcp-atlassian",
      "env": {
        "ATLASSIAN_BASE_URL": "https://ekoapp.atlassian.net",
        "ATLASSIAN_EMAIL": "{email}",
        "ATLASSIAN_API_TOKEN": "{atlassian_token}",
        "LOG_LEVEL": "error",
        "NODE_ENV": "production"
      }
    }
  }
}
EOF
```

**File 3: `.vscode/mcp.json` (Copilot — only if `$PLATFORM` = `copilot`)**
Use `${input:}` prompts instead of hardcoded credentials — Copilot asks at runtime.

**File 4: `environments/.env.staging` in QA_Automation**
```bash
# Update ADMIN_EMAIL and ADMIN_PASSWORD in existing file
sed -i '' "s/ADMIN_EMAIL=.*/ADMIN_EMAIL={email}/" ../Claude_QA_Automation/environments/.env.staging
sed -i '' "s/ADMIN_PASSWORD=.*/ADMIN_PASSWORD={staging_password}/" ../Claude_QA_Automation/environments/.env.staging
```

**File 5: macOS Keychain (for Jira bug reports)**
```bash
security add-generic-password -U -s 'jira-api-token' -a '{email}' -w '{atlassian_token}'
```
For Windows/Linux: add to `~/.bashrc` as `export JIRA_EMAIL=... JIRA_TOKEN=...`

**2c. Verify all files were created:**
```
✅ .env created (Atlassian + TestRail)
✅ ~/.claude/.mcp.json created (MCP servers)
✅ environments/.env.staging updated (login credentials)
✅ Keychain token stored (Jira bug reports)

⚠️ IMPORTANT: Reload the window now!
   Cmd+Shift+P → "Reload Window"
   
   After reload, come back and type: /qa-get-started continue
   (I'll pick up from Step 3 — tool verification)
```

### Step 3 — Reload & Resume

After the user reloads, MCP servers will be available.
The agent should detect it's a continuation and skip to Step 4 (verify tools).

Check: Can I access MCP tools now?
- If MCP tools available → proceed to Step 4
- If not → guide the user to check `~/.claude/.mcp.json` or `.vscode/mcp.json`

### Step 4 — Verify Tool Connectivity

Run quick checks for each tool:

| Tool | Test | Command/Method |
|---|---|---|
| **Playwright** | Run auth setup | `cd ../Claude_QA_Automation && npm run setup:staging` |
| **TestRail** | API ping | `curl` with credentials from `.env` |
| **Jira REST** | Check keychain/env | `security find-generic-password -s jira-api-token -w` or check `$JIRA_TOKEN` |
| **Jira MCP** | Search 1 issue | MCP call: search Jira issues (jql="project=AE", limit=1) |
| **Confluence MCP** | List spaces | MCP call: get Confluence spaces (keys=["EP"]) |

Present results as a table:

```
🔧 Tool Connectivity

| Tool | Status |
|---|---|
| Playwright auth | ✅ Auth state saved |
| TestRail API | ✅ Connected (14 projects) |
| Jira Keychain | ✅ Token found |
| Jira MCP | ✅ Connected |
| Confluence MCP | ✅ Connected |
| Figma MCP | ⏭️ Optional (authenticate later if needed) |
| Gmail MCP | ⏭️ Optional |
```

**If a tool fails:** Show specific troubleshooting steps and offer to retry.

### Step 5 — Run Smoke Test

Run a quick smoke test to verify everything end-to-end:

```bash
cd ../Claude_QA_Automation
TEST_ENV=staging npx playwright test --grep @smoke --project=e2e --workers=1
```

Show results:
```
🧪 Smoke Test Results

   Passed: 45
   Failed: 0
   Skipped: 2
   Duration: 1.2m

   ✅ All smoke tests passing!
```

If tests fail, offer to diagnose:
```
❌ 3 tests failed. Want me to analyze the failures? (yes/no)
```

### Step 6 — Generate First Report

```bash
cd ../Claude_QA_Automation
python3 scripts/generate_report.py
open reports/staging/team-report.html
```

```
📊 Your first QA report is ready!
   Opened in browser: reports/staging/team-report.html
```

### Step 7 — Quick Tour of Commands

Present available commands based on platform:

```
🎉 Setup complete! Here's what you can do now:

📋 QA Commands:
   /qa-test-plan          — Generate test plan from Figma/Confluence
   /qa-write-ac           — Post Acceptance Criteria to Jira
   /qa-bug-report         — File a bug in Jira
   /qa-import-testrail    — Push test cases to TestRail
   /qa-start-sprint       — Start a new sprint
   /qa-morning-standup    — Generate standup report
   /qa-eod-report         — Generate EOD report

🤖 Automation Commands:
   /auto-run              — Run Playwright tests
   /auto-generate         — Generate tests from CSV
   /auto-triage           — Analyze test failures
   /auto-inspect          — Inspect a URL for selectors

📖 Documentation:
   CLAUDE.md              — How this agent works
   ARCHITECTURE.md        — System design
   CONTRIBUTING.md        — What you can/cannot push
```

**If `$PLATFORM` = `copilot`, add:**
```
⚠️ Copilot Notes:
   - Sprint context is stored in .sprint.json (read by commands automatically)
   - For scheduled reports, set up GitHub Actions instead of /loop
   - MCP tools work the same — Jira, Confluence, Figma, TestRail
   - If you switch to Claude Code later, all commands + data carry over seamlessly
```

**If `$PLATFORM` = `claude-code`, add:**
```
💡 Claude Code Extras:
   - /loop 10m /qa-morning-standup  — Auto-generate standup every 10 min
   - Memory system remembers your preferences across conversations
   - Worktree isolation for safe experimentation
```

```
💡 Try it now! Type: /qa-morning-standup
```

### Step 8 — Readiness Checklist

Present final status with platform indicator:

```
✅ QA Onboarding Complete! (Platform: Claude Code / Copilot)

| Step | Status |
|---|---|
| Platform | ✅ Claude Code / Copilot |
| Prerequisites | ✅ Node 18+, Python 3.8+, Git |
| Repos | ✅ QA_Agent + QA_Automation |
| Dependencies | ✅ npm + Playwright browsers |
| Credentials | ✅ Staging login, Atlassian, TestRail, Keychain |
| MCP Servers | ✅ Jira + Confluence |
| Auth State | ✅ Staging authenticated |
| Smoke Test | ✅ 45/45 passed |
| First Report | ✅ Generated |

You're ready to QA! 🚀
```

## Platform Feature Matrix (for reference)

| Feature | Claude Code Path | Copilot Path |
|---|---|---|
| MCP config location | `~/.claude/.mcp.json` (hardcoded creds) | `.vscode/mcp.json` (`${input:}` prompts) |
| Credential storage | `.env` + macOS Keychain + MCP env | `.env` + `${input:}` prompts |
| Sprint context | `.sprint.json` + memory system | `.sprint.json` only |
| Slash commands | Auto-discovered from SKILL.md | Same — Copilot reads SKILL.md via agent mode |
| Scheduled tasks | `CronCreate()` / `/loop` | GitHub Actions (manual setup) |
| Agent memory | `~/.claude/projects/.../memory/` | Not available — use CLAUDE.md comments |
| Worktree | Built-in isolation | Manual `git worktree` |
| Tool calls (Bash/Read/Edit) | Identical | Identical |
| MCP tools (Jira/Figma/TestRail) | Identical | Identical |

## Error Recovery

| Scenario | Action |
|---|---|
| User says "skip" on any step | Skip and note it as ⏭️ in final checklist |
| npm install fails | Check Node version, suggest `rm -rf node_modules && npm install` |
| Auth setup fails | Check credentials in .env, suggest re-entering |
| MCP not found (Claude Code) | Guide creating `~/.claude/.mcp.json` |
| MCP not found (Copilot) | Guide creating `.vscode/mcp.json` with `${input:}` |
| mcp-atlassian not installed | Run `npm install -g mcp-atlassian` or `brew install mcp-atlassian` |
| Test failures on smoke | Offer `/auto-triage` to analyze |
| User on Windows/Linux | Adjust Keychain command to use env vars instead |
| User switches platform later | All data is in git repos — just switch tools, no migration needed |

## Output

Single interactive wizard session. No files created (credentials go into existing config files).
Final output is the readiness checklist showing all green checks + platform indicator.
