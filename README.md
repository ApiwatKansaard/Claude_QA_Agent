# QA Ops Director

> **AI-Powered QA Assistant for Test Planning, Bug Triage, and TestRail Management**
>
> Last updated: 2026-03-25 · Maintainer: QA Engineering Team

---

## What Is This?

QA Ops Director is a **VS Code Copilot Agent** that automates the full QA lifecycle for your team.
Instead of manually writing test plans, syncing TestRail, or compiling standup reports — just type
a slash command and the agent handles the rest.

**What it can do:**
- Generate test plans from Figma designs + Confluence specs
- Auto-review test cases for coverage gaps and fix them
- Import/edit test cases in TestRail via API
- Create Jira bug tickets with proper custom fields
- Post Acceptance Criteria to sprint tickets
- Generate morning standup and EOD reports
- Run daily automated AC scans via GitHub Actions

---

## Quick Start (New Team Member)

> **Time:** ~5 minutes for minimum setup (Jira + Confluence only)

### Prerequisites

| Tool | Version | Check |
|---|---|---|
| VS Code | Latest | `code --version` |
| GitHub Copilot extension | Latest | Installed from Extensions marketplace |
| Node.js | 18+ | `node --version` |
| Python | 3.8+ | `python3 --version` |
| Git | Any | `git --version` |

### Step 1: Clone & Install

> **💡 AI-Guided Setup Available!** ไม่ต้องทำ Step 1-5 เอง — หลัง clone แล้ว
> เปิด Copilot Chat ในโหมด **qa-ops-director** แล้วกด `/` → เลือก **`qa-setup`**
> Agent จะ check prerequisites, รัน script, ติดตั้ง hook, แนะนำ credentials และ verify ให้ทั้งหมด

```bash
# Clone the repository
git clone <repo-url>
cd <repo-name>

# Install and patch mcp-atlassian (one-time)
bash scripts/setup-mcp-atlassian.sh

# Enable pre-commit hook (protects infrastructure files)
git config core.hooksPath .githooks
```

### Step 2: Get Your API Credentials

You need your **own** credentials for each service. Nothing is shared.

| Service | Where to Get | Required? |
|---|---|---|
| **Atlassian API Token** | https://id.atlassian.com/manage-profile/security/api-tokens | ✅ Required |
| **Figma Personal Access Token** | https://www.figma.com → Settings → Security → Personal access tokens | 🟡 Optional (for design-based test plans) |
| **TestRail API Key** | https://ekoapp20.testrail.io → Your name → My Settings → API Keys | 🟡 Optional (for TestRail sync) |
| **Google OAuth JSON** | Ask team lead for shared OAuth file, or create at https://console.cloud.google.com | 🟡 Optional (for Gmail/Calendar) |

### Step 3: Reload VS Code

```
Cmd+Shift+P (macOS) / Ctrl+Shift+P (Windows/Linux) → "Developer: Reload Window"
```

### Step 4: Switch to QA Ops Director Mode

1. Open **Copilot Chat** panel (sidebar)
2. Click the **agent mode dropdown** at the top
3. Select **"qa-ops-director"**
4. Type anything — VS Code will prompt for your Atlassian credentials on first use

### Step 5: Verify

```
Type: what MCP tools do you have?
Expected: Should list Atlassian tools (search_jira_issues, read_confluence_page, etc.)
```

**That's it!** You're ready to use all Jira/Confluence commands.

---

## Optional Setup (Per Service)

### Figma MCP (for design-based test plans)

Add to your **user-level** MCP config:

**File:** `~/Library/Application Support/Code/User/mcp.json`

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

Figma will ask to authenticate via browser on first use.

> **Note:** The workspace `.vscode/mcp.json` also has a `figma-developer-mcp` server for 
> structural data. It prompts for your Figma PAT at startup.

### Gmail + Google Calendar MCP (for standup/EOD reports)

These require Google Cloud OAuth credentials.

**Gmail:**
```bash
mkdir -p ~/.gmail-mcp
cp <oauth-json-from-team-lead> ~/.gmail-mcp/gcp-oauth.keys.json
npx -y @gongrzhe/server-gmail-autoauth-mcp auth
# → Opens browser for Google OAuth consent
```

**Google Calendar:**
```bash
mkdir -p ~/.config/mcp
cp <oauth-json-from-team-lead> ~/.config/mcp/gcp-oauth.keys.json
GOOGLE_OAUTH_CREDENTIALS=~/.config/mcp/gcp-oauth.keys.json npx -y @cocal/google-calendar-mcp auth
```

Then add to your **user-level** `mcp.json`:

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

### TestRail (for import/edit/regression)

No config file needed. The agent will ask for your TestRail API key when you run
TestRail-related commands (`/qa:import-testrail`, `/qa:fetch-testrail`, etc.).

1. Log in to https://ekoapp20.testrail.io
2. Click your name → **My Settings** → **API Keys** tab
3. Click **Add Key** → copy the key
4. Provide it when prompted

---

## Credential Summary

| Credential | Storage Method | Shared? |
|---|---|---|
| Atlassian email + token | VS Code `${input:}` prompt (runtime) | ❌ Each person |
| Figma PAT | VS Code `${input:}` prompt (runtime) | ❌ Each person |
| TestRail API key | Agent asks at runtime | ❌ Each person |
| Gmail OAuth | `~/.gmail-mcp/` (local filesystem) | ❌ Each person |
| Google Calendar OAuth | `~/.config/mcp/` (local filesystem) | ❌ Each person |
| Jira for scripts | `JIRA_EMAIL` + `JIRA_TOKEN` env vars, or macOS Keychain | ❌ Each person |
| Jira for GitHub Actions | GitHub Secrets (`JIRA_EMAIL`, `JIRA_TOKEN`) | ✅ Shared (repo admin sets) |

> **⚠️ NEVER commit credentials to the repository.** All credentials are entered at runtime
> or stored in personal config files outside the repo.

---

## Available Commands

### Core QA Commands

| Command | What It Does | Required MCPs |
|---|---|---|
| `/qa:test-plan` `[Figma URL]` `[Confluence URL]` | Generate test plan + test cases (4-phase auto pipeline) | Atlassian, Figma |
| `/qa:review-testcases` `[test cases]` | Review test cases for coverage gaps | Atlassian, Figma |
| `/qa:write-ac` `[Sprint Board URL]` | Generate & post Acceptance Criteria to Jira (10-phase) | Atlassian |
| `/qa:bug-report` `[description/screenshot]` | Create Jira bug ticket with all custom fields | Atlassian |
| `/qa:bug-triage` `[Jira filter URL]` | Triage and prioritize bug reports | Atlassian |

### TestRail Commands

| Command | What It Does | Required |
|---|---|---|
| `/qa:import-testrail` `[suite link]` | Import test cases into TestRail via API | TestRail API key |
| `/qa:fetch-testrail` `[suite_id]` | Fetch existing cases for analysis | TestRail API key |
| `/qa:edit-testrail` `[suite_id]` `[filter]` `[change]` | Update existing TestRail cases | TestRail API key |
| `/qa:sync-testrail` `[test cases]` `[suite]` `[milestone]` | Export CSV + create milestone/run | TestRail, Calendar |
| `/qa:create-regression` `[feature]` `[suite_id]` | Create regression milestone + test run | TestRail, Calendar |

### Reporting Commands

| Command | What It Does | Required MCPs |
|---|---|---|
| `/qa:morning-standup` | Generate morning QA standup report | Atlassian, Gmail |
| `/qa:eod-report` | Generate end-of-day QA summary | Atlassian, Gmail, Calendar |
| `/qa:regression-check` `[release scope]` | Generate regression checklist | Atlassian, Calendar |

### Sprint Management

| Command | What It Does | Required |
|---|---|---|
| `/qa:start-sprint` `[Board URL]` | Check readiness, create sprint folder | Atlassian |
| `/qa:end-sprint` `[Sprint ID]` | Archive sprint folder + generate summary | None |

---

## Recommended Sprint Workflow

Run these commands **in order** at the start of each sprint:

```
1. /qa:start-sprint                  → Set up sprint workspace
2. /qa:test-plan [Figma] [Confluence]→ Generate + review + auto-fix test cases
3. /qa:import-testrail [suite URL]   → Push test cases to TestRail
4. /qa:write-ac [Board URL]          → Generate & post AC to Jira tickets

   ... (testing phase — execute tests, log bugs) ...

5. /qa:bug-report [description]      → Create bug tickets as needed
6. /qa:morning-standup               → Daily standup reports
7. /qa:eod-report                    → Daily EOD reports
8. /qa:end-sprint                    → Archive everything
```

---

## Project Structure

> **2-Repo Architecture:** This is repo 1 of 2. Test automation code lives in [convolabai/QA_Automation](https://github.com/convolabai/QA_Automation).
> Open both repos via `qa-workspace.code-workspace` for full cross-repo agent functionality.

```
.
├── README.md                    ← You are here
├── ARCHITECTURE.md              ← System design, data flow, tech stack
├── CONTRIBUTING.md              ← What team members can/cannot push
├── MIGRATION-PLAN.md            ← 2-repo migration plan
│
├── .github/
│   ├── TEAM-SETUP.md            ← Detailed setup instructions
│   ├── CODEOWNERS               ← File ownership (protects infrastructure)
│   ├── agents/                  ← Agent mode definitions (3 agents)
│   ├── prompts/                 ← Slash command prompt files (20)
│   ├── skills/qa-ops-director/  ← QA Ops Director skill
│   │   ├── SKILL.md             ← ★ Orchestrator (routing, pipelines)
│   │   ├── commands/            ← Workflow files (15 commands)
│   │   └── references/          ← Agent behaviors + shared knowledge
│   ├── skills/playwright-automator/ ← Test Automation skill (targets QA_Automation repo)
│   │   ├── SKILL.md             ← ★ Orchestrator (cross-repo workflows)
│   │   ├── commands/            ← Workflow files (9 commands)
│   │   └── references/          ← Best practices + code generation rules
│   └── workflows/               ← GitHub Actions (daily-ac-scan)
│
├── .githooks/
│   └── pre-commit               ← Blocks infra file changes (local guard)
│
├── .vscode/
│   └── mcp.json                 ← MCP server config (creds via ${input:})
│
├── scripts/                     ← Python scripts (stdlib only, no pip)
│   ├── setup-mcp-atlassian.sh   ← One-time Atlassian MCP setup + patch
│   ├── daily-ac-agent.py        ← Automated AC posting for CI
│   ├── repost-ac-tables.py      ← Reformat AC as ADF tables
│   └── delete-old-ac-comments.py← Clean stale AC comments
│
├── testrail-cache/              ← Cached TestRail data (gitignored, local only)
├── {sprint-folder}/             ← Active sprint artifacts (auto-created)
└── archive/                     ← Completed sprint archives

── Sibling Repo (QA_Automation) ──────────────────────
QA_Automation/                   ← convolabai/QA_Automation
├── playwright.config.ts
├── src/pages/                   ← Page Object Model classes
├── tests/e2e/                   ← UI end-to-end tests
├── tests/api/                   ← API integration tests
├── selectors/                   ← JSON selector maps
└── environments/                ← Per-environment .env files
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed component descriptions and data flow diagrams.

---

## Troubleshooting

### "mcp-atlassian not found" after setup

```bash
# Check global npm prefix
npm root -g
# If using nvm, make sure you're on the right Node version
nvm use 18
# Re-run setup
bash scripts/setup-mcp-atlassian.sh
```

### Atlassian MCP shows no tools / breaks

```bash
# Re-run setup script (re-installs + re-patches)
bash scripts/setup-mcp-atlassian.sh
# Then reload VS Code: Cmd+Shift+P → "Developer: Reload Window"
```

### "LOG_LEVEL=error" — why?

The `mcp-atlassian` package logs to stdout, which breaks the MCP JSON-RPC protocol.
Setting `LOG_LEVEL=error` suppresses info/debug logs. This is already set in `.vscode/mcp.json`.

### Jira Search API errors (deprecated endpoint)

The `setup-mcp-atlassian.sh` script patches `GET /rest/api/3/search` → `POST /rest/api/3/search/jql`.
If you see 404 errors on Jira search, re-run the setup script:

```bash
bash scripts/setup-mcp-atlassian.sh
```

> **Important:** You must re-run the patch after every `npm update -g mcp-atlassian`.

### Figma MCP hangs indefinitely

**Never use** `mcp_figma-remote-_get_design_context` — it hangs on complex pages.
Use `mcp_figma_get_figma_data` (local, fast) or `mcp_figma-remote-_get_screenshot` instead.
See [ARCHITECTURE.md](ARCHITECTURE.md) for details.

### TestRail import fails with "not a valid array"

Multi-select fields (`custom_supportversion`, `custom_qa_responsibility`) must be arrays:
```
✅ Correct: [160]
❌ Wrong:   160
```

### Scripts ask for JIRA_EMAIL / JIRA_TOKEN

For local script usage, either:
```bash
# Option A: Environment variables
export JIRA_EMAIL="yourname@amitysolutions.com"
export JIRA_TOKEN="your-api-token"

# Option B: macOS Keychain (daily-ac-agent.py supports this)
security add-generic-password -s 'jira-api-token' -a 'yourname@amitysolutions.com' -w 'your-token'
```

---

## For Repo Admins

### GitHub Actions Setup

The `daily-ac-scan.yml` workflow needs two secrets:

1. Go to **Settings → Secrets and variables → Actions**
2. Add:
   - `JIRA_EMAIL` — Service account email for Jira
   - `JIRA_TOKEN` — API token for that account

### Adding New Commands

1. Create `commands/{name}.md` in the skill folder
2. Add the command to the table in `SKILL.md`
3. Create a matching `prompts/qa-{name}.prompt.md` in `.github/prompts/`
4. **Update** `ARCHITECTURE.md` and this `README.md`

### Adding New MCP Servers

1. Add server config to `.vscode/mcp.json` (use `${input:}` for credentials)
2. Add corresponding `inputs` entry for VS Code prompts
3. Update the Tool Integrations table in `SKILL.md`
4. Add setup instructions to `.github/TEAM-SETUP.md`
5. **Update** `ARCHITECTURE.md` (MCP Servers section) and this `README.md`

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for full details on:

- **What you can push:** Sprint artifacts (`agentic-*/`, `archive/`) — no PR needed
- **What you cannot modify:** Infrastructure files (skills, prompts, scripts, docs) — protected by CODEOWNERS
- **Pre-commit hook:** Run `git config core.hooksPath .githooks` to install (blocks infra changes locally)
- **Pre-push review:** Use `/qa:review-before-push` to validate test cases before pushing
- **Commit messages:** Use `test:` prefix for sprint artifacts, `infra:` for infrastructure changes

---

## Documentation Maintenance Policy

> **Rule:** Any change to the project structure, commands, scripts, or integrations
> MUST include updates to these docs:

| What Changed | Update These Files |
|---|---|
| New command added | `SKILL.md`, `README.md`, `ARCHITECTURE.md`, `TEAM-SETUP.md` |
| New MCP server | `.vscode/mcp.json`, `SKILL.md`, `README.md`, `ARCHITECTURE.md`, `TEAM-SETUP.md` |
| New script | `README.md` (project structure), `ARCHITECTURE.md` |
| Directory structure change | `README.md`, `ARCHITECTURE.md` |
| Credential flow change | `README.md` (credential summary), `ARCHITECTURE.md` (credential flow) |
| Setup process change | `TEAM-SETUP.md`, `README.md` (quick start) |
| New protected path | `CODEOWNERS`, `CONTRIBUTING.md`, `.githooks/pre-commit` |

**Last verified:** 2026-03-25

---

## License

Internal team tool — not for external distribution.
