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

### Step 1 — Prerequisites Check

**Auto-check (no user input needed):**

| Check | Command | Expected |
|---|---|---|
| Node.js | `node --version` | >= 18.0.0 |
| Python | `python3 --version` | >= 3.8 |
| Git | `git --version` | Any |
| ngrok | `ngrok version` | Any (optional — warn if missing) |

**Platform-specific checks:**

| Check | Claude Code | Copilot |
|---|---|---|
| AI tool | Check CLAUDE.md loaded | Check Copilot Chat available |
| MCP config location | `~/.claude/.mcp.json` | `.vscode/mcp.json` |

**If a check fails:** Show the install command and wait for the user to fix it.
```
❌ Node.js not found. Install:
   brew install node
   
   Let me know when you've installed it and I'll check again.
```

### Step 2 — Verify Repository Structure

Check that both repos are cloned and accessible:

```bash
# Check QA_Agent (current repo)
ls CLAUDE.md .github/skills/qa-ops-director/SKILL.md

# Check QA_Automation (sibling repo)
ls ../Claude_QA_Automation/playwright.config.ts
ls ../Claude_QA_Automation/package.json
```

**If QA_Automation not found:**
```
⚠️ Claude_QA_Automation repo not found at ../Claude_QA_Automation/

Please clone it:
   cd ~/Documents
   git clone <repo-url> Claude_QA_Automation

Let me know when done.
```

### Step 3 — Install Dependencies

```bash
cd ../Claude_QA_Automation
npm install
npx playwright install --with-deps chromium
```

Show progress and verify:
```
✅ npm install — 245 packages
✅ Playwright chromium installed
```

### Step 4 — Configure Credentials

Guide the user through each credential. Ask only for what's needed:

**4a. Staging login credentials (REQUIRED)**

```
📝 I need your staging login credentials.
   Edit: Claude_QA_Automation/environments/.env.staging

   Required fields:
   - ADMIN_EMAIL=yourname@amitysolutions.com
   - ADMIN_PASSWORD=your-staging-password
   
   Have you filled these in? (yes/no)
```

Verify by reading the .env file (check non-empty, don't log the password):
```bash
# Verify (don't print values!)
grep -c "ADMIN_EMAIL=.\+" ../Claude_QA_Automation/environments/.env.staging
grep -c "ADMIN_PASSWORD=.\+" ../Claude_QA_Automation/environments/.env.staging
```

**4b. Atlassian API Token (REQUIRED for Jira/Confluence)**

```
📝 Get your Atlassian API Token:
   1. Go to: https://id.atlassian.com/manage-profile/security/api-tokens
   2. Click "Create API token"
   3. Copy the token

   Now add it to the .env file:
   Claude_QA_Agent/.env
   
   ATLASSIAN_EMAIL=yourname@amitysolutions.com
   ATLASSIAN_API_TOKEN=your-token-here
```

**4c. TestRail API Key (REQUIRED for test management)**

```
📝 Get your TestRail API Key:
   1. Go to: https://ekoapp20.testrail.io
   2. Click your name → My Settings → API Keys
   3. Add Key → copy it

   Add to .env:
   TESTRAIL_EMAIL=yourname@amitysolutions.com
   TESTRAIL_API_KEY=your-key-here
```

**4d. Jira Keychain (REQUIRED for bug reports — macOS only)**

```
📝 Store Jira token in macOS Keychain (for bug report scripts):
   
   security add-generic-password -s 'jira-api-token' \
     -a 'yourname@amitysolutions.com' \
     -w 'your-atlassian-api-token'
```

For Windows/Linux users, set environment variables instead:
```bash
export JIRA_EMAIL="yourname@amitysolutions.com"
export JIRA_TOKEN="your-atlassian-api-token"
```

**4e. MCP Server Config**

**If `$PLATFORM` = `claude-code`:**

Check if `~/.claude/.mcp.json` exists:
- If yes → verify it has `atlassian` server entry
- If no → create it with the user's credentials from `.env`:

```json
{
  "mcpServers": {
    "atlassian": {
      "command": "mcp-atlassian",
      "env": {
        "ATLASSIAN_BASE_URL": "https://ekoapp.atlassian.net",
        "ATLASSIAN_EMAIL": "yourname@amitysolutions.com",
        "ATLASSIAN_API_TOKEN": "your-token-here",
        "LOG_LEVEL": "error",
        "NODE_ENV": "production"
      }
    }
  }
}
```

Then instruct:
```
After saving, reload the window:
   Cmd+Shift+P → "Reload Window"
```

**If `$PLATFORM` = `copilot`:**

Check if `.vscode/mcp.json` exists in the workspace:
- If yes → verify it has `atlassian` server entry with credentials filled in
- If no → create it:

```json
{
  "servers": {
    "atlassian": {
      "command": "mcp-atlassian",
      "env": {
        "ATLASSIAN_BASE_URL": "https://ekoapp.atlassian.net",
        "ATLASSIAN_EMAIL": "${input:atlassianEmail}",
        "ATLASSIAN_API_TOKEN": "${input:atlassianToken}",
        "LOG_LEVEL": "error",
        "NODE_ENV": "production"
      }
    }
  },
  "inputs": [
    { "id": "atlassianEmail", "description": "Atlassian email", "type": "promptString" },
    { "id": "atlassianToken", "description": "Atlassian API token", "type": "promptString", "password": true }
  ]
}
```

Then instruct:
```
After saving, reload VS Code:
   Cmd+Shift+P → "Developer: Reload Window"
   Copilot will prompt for your credentials on first use.
```

### Step 5 — Verify Tool Connectivity

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

### Step 6 — Run Smoke Test

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

### Step 7 — Generate First Report

```bash
cd ../Claude_QA_Automation
python3 scripts/generate_report.py
open reports/staging/team-report.html
```

```
📊 Your first QA report is ready!
   Opened in browser: reports/staging/team-report.html
```

### Step 8 — Quick Tour of Commands

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

### Step 9 — Readiness Checklist

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
