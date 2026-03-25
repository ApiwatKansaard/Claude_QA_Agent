# QA Ops Director — Architecture

> **Last updated:** 2026-03-25
> **Maintainer:** QA Engineering Team

---

## Overview

**QA Ops Director** is a VS Code-based AI QA assistant built on GitHub Copilot Agent Mode.
It automates the full QA lifecycle — from test planning to bug reporting — by orchestrating
multiple MCP (Model Context Protocol) servers and external APIs.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          VS Code + Copilot Chat                         │
│                        (Agent Mode: qa-ops-director)                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   User ──→ /qa:* slash commands ──→ SKILL.md (Orchestrator)            │
│                                         │                               │
│                  ┌──────────────────────┼──────────────────────┐       │
│                  ▼                      ▼                      ▼       │
│          commands/*.md          references/*.md          prompts/*.md   │
│        (workflow logic)       (agent behaviors)        (quick prompts)  │
│                  │                      │                      │       │
│                  └──────────────────────┼──────────────────────┘       │
│                                         │                               │
│                  ┌──────────────────────┼──────────────────────┐       │
│                  ▼                      ▼                      ▼       │
│            Atlassian MCP          Figma MCP             TestRail API    │
│          (Jira+Confluence)     (Design files)          (REST, Basic)    │
│                  │                                          │           │
│                  ▼                                          ▼           │
│            Gmail MCP           Google Calendar MCP    TestRail Cache    │
│         (Draft emails)        (Sprint milestones)    (testrail-cache/)  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
.
├── README.md                          # Main documentation — START HERE
├── ARCHITECTURE.md                    # This file — system design & data flow
├── .gitignore                         # Git ignore rules (credentials excluded)
│
├── .github/
│   ├── TEAM-SETUP.md                  # Step-by-step setup for each team member
│   ├── agents/
│   │   └── qa-ops-director.agent.md   # Agent mode definition (VS Code)
│   ├── prompts/                       # Quick-access prompt files (/qa:* shortcuts)
│   │   ├── qa-setup.prompt.md         #   AI-guided onboarding for new team members
│   │   ├── qa-test-plan.prompt.md
│   │   ├── qa-bug-report.prompt.md
│   │   ├── qa-bug-triage.prompt.md
│   │   ├── qa-morning-standup.prompt.md
│   │   ├── qa-eod-report.prompt.md
│   │   └── ... (13 prompt files total)
│   ├── skills/
│   │   └── qa-ops-director/
│   │       ├── SKILL.md               # ★ ORCHESTRATOR — routing, pipeline, rules
│   │       ├── commands/              # Workflow definitions (15 commands)
│   │       │   ├── test-plan.md       #   /qa:test-plan (4-phase pipeline)
│   │       │   ├── write-ac.md        #   /qa:write-ac (10-phase pipeline)
│   │       │   ├── import-testrail.md #   /qa:import-testrail
│   │       │   ├── bug-report.md      #   /qa:bug-report
│   │       │   └── ... (15 files)
│   │       ├── references/            # Agent behavior definitions & shared knowledge
│   │       │   ├── agent-test-planner.md
│   │       │   ├── agent-test-case-reviewer.md
│   │       │   ├── agent-bug-reporter.md
│   │       │   ├── agent-testrail-manager.md
│   │       │   ├── testrail-api.md
│   │       │   ├── testrail-csv.md
│   │       │   ├── testrail-import-config.cfg
│   │       │   ├── ai-llm-testing.md
│   │       │   └── ... (14 files)
│   │       └── evals/
│   │           └── evals.json         # Evaluation tests for skill quality
│   └── workflows/
│       └── daily-ac-scan.yml          # GitHub Actions — daily AC posting
│
├── .vscode/
│   └── mcp.json                       # MCP server config (shared, uses ${input:} for creds)
│
├── scripts/
│   ├── setup-mcp-atlassian.sh         # One-time setup: install + patch mcp-atlassian
│   ├── daily-ac-agent.py              # Standalone AC posting (GHA + local)
│   ├── repost-ac-tables.py            # Reformat AC comments as ADF tables
│   └── delete-old-ac-comments.py      # Clean up stale AC comments
│
├── testrail-cache/                    # Cached TestRail suite data (persistent)
│   └── S{suite_id}/
│       ├── summary.md                 # Suite metadata
│       └── cases.csv                  # Cached test cases
│
├── {sprint-folder}/                   # Active sprint artifacts (auto-detected)
│   ├── {feature}-test-plan.md         # Test plan (strategy, scope)
│   ├── {feature}-testcases.csv        # Test cases in TestRail CSV format
│   ├── release-notes-{sprint}.md      # Release notes (from /qa:write-ac)
│   └── generate-csv.py               # CSV generation helper (optional)
│
└── archive/                           # Completed sprint archives
    └── {sprint-name}/
        ├── ARCHIVE-SUMMARY.md         # Sprint summary + artifact index
        └── ... (preserved artifacts)
```

---

## Core Components

### 1. Orchestrator (`SKILL.md`)

The central brain. Routes user input to the correct workflow:

- **Slash commands** (`/qa:test-plan`, `/qa:bug-triage`, etc.) → loads `commands/*.md`
- **Natural language** ("what should we test?", "triage these bugs") → loads `references/*.md`

Manages sprint folder detection, auto-chain pipelines, and cross-sprint context.

### 2. Commands (15 files)

Each command file is a complete workflow specification:

| Command | Phases | Output |
|---|---|---|
| `/qa:test-plan` | 4 (Fetch→Generate→Review→Fix) | test-plan.md + testcases.csv |
| `/qa:write-ac` | 10 (Select→Check→Understand→Fetch→Generate→Review→Fix→Approve→Post→Notes) | AC on Jira tickets + release-notes.md |
| `/qa:import-testrail` | 5 (Cache→Compare→Plan→Import→Verify) | Cases in TestRail |
| `/qa:start-sprint` | 3 (Check→Create→Report) | Sprint folder |
| `/qa:end-sprint` | 3 (Archive→Summary→Report) | archive/{sprint}/ |
| `/qa:bug-report` | 4 (Analyze→Draft→Create→Verify) | Jira bug ticket |
| *others* | 1-3 phases each | Various reports |

### 3. Agent References (7 agents)

Specialized behavior definitions loaded by the orchestrator:

| Agent | Role | MCP Tools Used |
|---|---|---|
| `agent-test-planner` | Generate test cases from specs | Figma, Confluence |
| `agent-test-case-reviewer` | Review test cases for gaps | Figma, Confluence |
| `agent-bug-reporter` | Create Jira bug tickets | Jira REST API |
| `agent-bug-analyzer` | Triage & prioritize bugs | Jira |
| `agent-testrail-manager` | TestRail CRUD operations | TestRail REST API |
| `agent-report-compiler` | Standup/EOD reports | Jira, Gmail, Calendar |
| `agent-ac-reviewer` | Review Acceptance Criteria quality | Internal (no external tools) |

### 4. MCP Servers (External Integrations)

```
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  Atlassian MCP   │    │    Figma MCP      │    │   TestRail API   │
│  (workspace)     │    │  (user-level)     │    │   (REST/Basic)   │
├──────────────────┤    ├──────────────────┤    ├──────────────────┤
│ Jira: read/write │    │ get_figma_data   │    │ GET/POST cases   │
│ Confluence: read │    │ get_screenshot   │    │ Sections, Suites │
│ ADF format       │    │ depth=2-3        │    │ Milestones, Runs │
└──────────────────┘    └──────────────────┘    └──────────────────┘

┌──────────────────┐    ┌──────────────────┐
│    Gmail MCP     │    │ Google Cal MCP   │
│  (user-level)    │    │  (user-level)    │
├──────────────────┤    ├──────────────────┤
│ Draft emails     │    │ Read milestones  │
│ (never auto-send)│    │ Sprint dates     │
└──────────────────┘    └──────────────────┘
```

**Config locations:**
- **Workspace-level** (`.vscode/mcp.json`): Atlassian — shared config, personal creds via `${input:}`
- **User-level** (`~/Library/Application Support/Code/User/mcp.json`): Figma, Gmail, Calendar — each member configures in their own VS Code

### 5. GitHub Actions (`daily-ac-scan.yml`)

Automated daily job that runs independently of VS Code:

```
Schedule: Mon-Fri 09:00 BKK (02:00 UTC)
    │
    ▼
daily-ac-agent.py
    │
    ├── Discover active sprints (Jira Agile API)
    ├── Fetch all tickets in "Broccoli" quick filter
    ├── Check which tickets lack AC comments
    ├── Match tickets to test plan groups (keyword-based)
    └── Post ADF table AC comments (if mode=post)
```

**Credentials:** GitHub Secrets (`JIRA_EMAIL`, `JIRA_TOKEN`)

---

## Data Flow

### Sprint Lifecycle

```
/qa:start-sprint
    └── Creates: {sprint-folder}/

/qa:test-plan [Figma URL] [Confluence URL]
    ├── Phase 0: Scan archive/ for previous sprint context
    ├── Phase 1: Fetch specs → Generate test cases
    ├── Phase 2: Review against specs → Gap analysis
    ├── Phase 3: Auto-fix gaps → Final output
    └── Creates: {sprint-folder}/{feature}-test-plan.md
                 {sprint-folder}/{feature}-testcases.csv

/qa:import-testrail [suite URL]
    ├── Read testrail-cache/S{id}/ (or fetch fresh)
    ├── Compare CSV vs existing cases
    ├── Import new/changed cases via API
    └── Updates: testrail-cache/S{id}/

/qa:write-ac [Sprint Board URL]
    ├── Read test plan + CSV from sprint folder
    ├── Fetch sprint tickets from Jira
    ├── Generate AC per ticket (mapped to test cases)
    ├── Internal AI review + auto-fix
    ├── User approval
    ├── Post to Jira as ADF table comments
    └── Creates: {sprint-folder}/release-notes-{sprint}.md

/qa:end-sprint
    ├── Move {sprint-folder}/ → archive/{sprint-name}/
    └── Creates: archive/{sprint-name}/ARCHIVE-SUMMARY.md
```

### Credential Flow

```
Each QA team member provides their OWN credentials:

┌─────────────────────────────────────────────────────────────┐
│                    Credential Sources                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  VS Code Input Prompts (on first use)                       │
│  ├── Atlassian email     → ${input:atlassian_email}         │
│  ├── Atlassian API token → ${input:atlassian_token}         │
│  └── Figma PAT           → ${input:figma_token}             │
│                                                              │
│  macOS Keychain (for scripts)                               │
│  └── security find-generic-password -s 'jira-api-token' -w  │
│                                                              │
│  Environment Variables (for CI/local scripts)               │
│  ├── JIRA_EMAIL                                              │
│  └── JIRA_TOKEN                                              │
│                                                              │
│  GitHub Secrets (for GitHub Actions)                        │
│  ├── secrets.JIRA_EMAIL                                      │
│  └── secrets.JIRA_TOKEN                                      │
│                                                              │
│  TestRail API Key (entered when agent asks)                 │
│  └── Each member gets their own from TestRail settings      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Important:** No credentials are stored in the repository. The `.vscode/mcp.json` uses `${input:}` 
variables that prompt each user for their own credentials at runtime.

---

## Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| AI Engine | GitHub Copilot (Claude) | LLM for test generation, analysis, reporting |
| Agent Framework | VS Code Agent Mode | Skill/command/reference routing |
| MCP Protocol | Model Context Protocol | Tool integration (Jira, Figma, Gmail, Calendar) |
| Test Management | TestRail REST API | Test case CRUD, milestones, test runs |
| Bug Tracking | Jira (Atlassian Cloud) | Bug creation, sprint management, AC posting |
| Specs | Confluence + Figma | PRD, tech specs, UI designs |
| CI/CD | GitHub Actions | Daily automated AC scanning |
| Scripts | Python 3.8+ (stdlib only; CI uses 3.12) | `urllib.request` — no external dependencies |
| Config | JSON (`.vscode/mcp.json`) | MCP server definitions with `${input:}` variables |

---

## Key Design Decisions

1. **No external Python packages** — All scripts use `urllib.request` from stdlib. This avoids
   dependency management and works on any machine with Python 3.8+.

2. **`${input:}` for credentials** — VS Code prompts each user at runtime. No `.env` files needed
   for the VS Code agent; credentials never touch the filesystem.

3. **TestRail cache** — Suite data is cached locally at `testrail-cache/S{id}/` to avoid repeated
   API calls. Cache persists across sprints (not archived).

4. **Archive pattern** — Completed sprints move to `archive/` with an `ARCHIVE-SUMMARY.md`. 
   New test plans can reference archived data for cross-sprint context (Phase 0).

5. **Dual AC posting** — VS Code skill uses LLM (high quality), GitHub Actions uses keyword matching
   (daily catch-up). Both produce identical ADF table format.

6. **mcp-atlassian patch** — Atlassian deprecated `GET /search`, requiring a local patch script.
   Must re-run after every `npm update -g mcp-atlassian`.

---

## Updating This Document

**When to update:**
- New command or agent reference added → update "Commands" and "Agent References" tables
- New MCP server integrated → update "MCP Servers" section and credential flow
- Directory structure changes → update "Directory Structure" tree
- New script added → update the tree and "Technology Stack" if new dependencies
- Sprint workflow changes → update "Data Flow" section

**Rule:** Any PR that modifies `.github/skills/`, `scripts/`, or `.vscode/mcp.json` MUST also 
update this file and `README.md` to keep documentation current.
