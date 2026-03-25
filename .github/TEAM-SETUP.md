# QA Ops Director — Team Setup Guide

> **See also:** [README.md](../README.md) for overview & command reference,
> [ARCHITECTURE.md](../ARCHITECTURE.md) for system design & data flow.

## Prerequisites

- VS Code with **GitHub Copilot** extension (+ Copilot Chat)
- Node.js 18+ (`node --version`)

## Quick Start (3 minutes)

```bash
# 1. Clone
git clone <repo-url> && cd <repo-name>

# 2. Install & patch mcp-atlassian (one-time)
bash scripts/setup-mcp-atlassian.sh

# 3. Reload VS Code
# Cmd+Shift+P → "Developer: Reload Window"

# 4. Done! Switch to "qa-ops-director" agent mode in Copilot Chat
```

VS Code will prompt you for your Atlassian email + API token on first use.

> **💡 AI-Guided Setup:** After cloning, open Copilot Chat in **qa-ops-director** mode
> and use the `/` menu → select **`qa-setup`**. The AI will check prerequisites, run the
> setup script, and guide you through credential setup interactively.

---

## Detailed Setup

### Step 1: Atlassian (Jira + Confluence) — Required

The workspace already has `.vscode/mcp.json` configured. You just need:

1. **Run the setup script** (installs `mcp-atlassian` globally + patches Jira API):
   ```bash
   bash scripts/setup-mcp-atlassian.sh
   ```

2. **Create an Atlassian API token** at https://id.atlassian.com/manage-profile/security/api-tokens

3. **Reload VS Code** — `Cmd+Shift+P` → "Developer: Reload Window"

4. When Copilot first uses Atlassian, VS Code will prompt for:
   - Email: your `@amitysolutions.com` email
   - API Token: the token from step 2

> **Why the setup script?** The `mcp-atlassian` package has two issues:
> - It writes log messages to stdout, breaking the MCP protocol (`LOG_LEVEL=error` fixes this)
> - It uses a deprecated Jira API endpoint that Atlassian removed (the script patches this)
>
> Re-run the script after `npm update -g mcp-atlassian` to re-apply the patch.

### Step 2: Figma (optional — for design-based test plans)

Add to your **user-level** MCP config at `~/Library/Application Support/Code/User/mcp.json`:

```json
{
  "servers": {
    "figma-remote-mcp": {
      "url": "https://mcp.figma.com/mcp",
      "type": "http"
    }
  }
}
```

Figma will ask you to authenticate via browser on first use.

### Step 3: Gmail + Google Calendar (optional — for standup/EOD reports)

These require a Google Cloud OAuth setup. Ask the team lead for the shared OAuth JSON file, or create your own:

1. Create a project at https://console.cloud.google.com/
2. Enable Gmail API + Google Calendar API
3. Create OAuth 2.0 credentials (Desktop app type)
4. Download the JSON file

**Gmail setup:**
```bash
mkdir -p ~/.gmail-mcp
cp <downloaded-json> ~/.gmail-mcp/gcp-oauth.keys.json
npx -y @gongrzhe/server-gmail-autoauth-mcp auth
```

**Google Calendar setup:**
```bash
mkdir -p ~/.config/mcp
cp <downloaded-json> ~/.config/mcp/gcp-oauth.keys.json
GOOGLE_OAUTH_CREDENTIALS=~/.config/mcp/gcp-oauth.keys.json npx -y @cocal/google-calendar-mcp auth
```

Add both to your user-level `mcp.json`:
```json
{
  "servers": {
    "gmail": {
      "command": "npx",
      "args": ["-y", "@gongrzhe/server-gmail-autoauth-mcp"],
      "env": {
        "GMAIL_OAUTH_PATH": "${userHome}/.gmail-mcp/gcp-oauth.keys.json",
        "GMAIL_CREDENTIALS_PATH": "${userHome}/.gmail-mcp/credentials.json"
      }
    },
    "google-calendar": {
      "command": "npx",
      "args": ["-y", "@cocal/google-calendar-mcp"],
      "env": {
        "GOOGLE_OAUTH_CREDENTIALS": "${userHome}/.config/mcp/gcp-oauth.keys.json"
      }
    }
  }
}
```

### Step 4: TestRail (optional — for import/edit/regression)

Each team member needs their own TestRail API key:

1. Log in to https://ekoapp20.testrail.io
2. Click your name → **My Settings** → **API Keys** tab
3. Click **Add Key** → copy the key
4. Provide it when the agent asks during TestRail commands

---

## Verify Setup

1. Open Copilot Chat (sidebar)
2. Switch to **qa-ops-director** agent mode (dropdown at top)
3. Test: type `what MCP tools do you have?` — should list Atlassian tools
4. Test: use the `/` menu → select `qa-morning-standup` → should pull Jira data

## Available Commands

| Command | What it does | Requires |
|---|---|---|
| `/qa:test-plan` | Generate test cases from Figma/Confluence (4-phase auto pipeline) | Atlassian, Figma |
| `/qa:review-testcases` | Review test cases for coverage gaps | Atlassian, Figma |
| `/qa:write-ac` | Generate & post Acceptance Criteria to Jira (10-phase) | Atlassian |
| `/qa:bug-report` | Create Jira bug ticket with all custom fields | Atlassian |
| `/qa:bug-triage` | Triage Jira bug reports | Atlassian |
| `/qa:sync-testrail` | Export test cases to TestRail CSV | TestRail, GCal |
| `/qa:import-testrail` | Import test cases into TestRail via API | TestRail |
| `/qa:fetch-testrail` | Fetch existing cases from TestRail | TestRail |
| `/qa:edit-testrail` | Edit existing TestRail cases | TestRail |
| `/qa:create-regression` | Create milestone + test run for regression | TestRail, GCal |
| `/qa:morning-standup` | Generate morning QA standup | Atlassian, Gmail |
| `/qa:eod-report` | Generate end-of-day QA summary | Atlassian, Gmail, GCal |
| `/qa:regression-check` | Generate regression checklist | Atlassian, GCal |
| `/qa:start-sprint` | Check readiness, create sprint folder | Atlassian |
| `/qa:end-sprint` | Archive sprint folder + generate summary | None |

## Minimum Setup

If you only need Jira + Confluence (test plans, bug triage, standups):
1. Clone the repo
2. Run `bash scripts/setup-mcp-atlassian.sh`
3. Reload VS Code
4. Enter Atlassian credentials when prompted

That's all — no other config needed.

---

## Running Scripts Locally (Optional)

Some Python scripts (`daily-ac-agent.py`, `repost-ac-tables.py`) need Jira credentials:

```bash
# Option A: Environment variables
export JIRA_EMAIL="yourname@amitysolutions.com"
export JIRA_TOKEN="your-api-token"

# Option B: macOS Keychain (daily-ac-agent.py supports auto-discovery)
security add-generic-password -s 'jira-api-token' -a 'yourname@amitysolutions.com' -w 'your-token'
```

No `pip install` needed — all scripts use Python stdlib only.

---

## Documentation Maintenance

> **⚠️ IMPORTANT:** When modifying this project (new commands, scripts, integrations),
> you MUST also update the documentation. See the "Documentation Maintenance Policy" 
> section in [README.md](../README.md) for the full checklist.

**Last updated:** 2026-03-25
