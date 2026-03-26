# 2-Repo Migration Plan

> **Status:** READY FOR EXECUTION  
> **Owner:** @ApiwatKansaard  
> **Source:** `convolabai/QA_Agent` (monorepo)  
> **Target:** 2 repositories — QA_Agent (agents + sprint data) + QA_Automation (playwright tests)  
> **Critical Constraint:** All agents, skills, prompts MUST work identically after migration.  
> **Cross-repo:** QA_Agent skills read test code from QA_Automation via Multi-Root Workspace.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Why 2 Repos (Not 3)](#2-why-2-repos)
3. [Cross-Reference Map — What Changes](#3-cross-reference-map)
4. [Repo 1: QA_Agent — Structure After Migration](#4-repo-1-qa_agent)
5. [Repo 2: QA_Automation — Structure After Migration](#5-repo-2-qa_automation)
6. [VS Code Multi-Root Workspace Bridge](#6-workspace-bridge)
7. [File-by-File Change List](#7-file-by-file-change-list)
8. [Execution Tasks — Step by Step](#8-execution-tasks)
9. [Dry Run Phase](#9-dry-run-phase)
10. [Validation Checklist](#10-validation-checklist)
11. [Rollback Plan](#11-rollback-plan)

---

## 1. Architecture Overview

### Before (Monorepo)
```
convolabai/QA_Agent/
├── .github/agents/          ─┐
├── .github/skills/          ─┤
├── .github/prompts/         ─┤ AGENT + SPRINT_DATA layer (stays together)
├── .github/workflows/       ─┤
├── .vscode/mcp.json         ─┤
├── scripts/                 ─┤
├── agentic-18.2/            ─┤
├── archive/                 ─┤
├── testrail-cache/          ─┘
└── playwright-tests/        ── AUTOMATION layer (moves out)
```

### After (2 Repos + VS Code Multi-Root Workspace)
```
~/Projects/QA/
├── QA_Agent/                ── Repo 1: Agents + Skills + Sprint Data + Scripts (everything except tests)
├── QA_Automation/           ── Repo 2: Playwright tests (promoted from playwright-tests/ to root)
└── qa-workspace.code-workspace  ── Opens both repos in one VS Code window
```

---

## 2. Why 2 Repos (Not 3)

Sprint data and agent skills are **tightly coupled** — every `/qa:*` command reads or writes sprint data:

| Command | Sprint Data Operation |
|---|---|
| `/qa:start-sprint` | **Creates** sprint folder |
| `/qa:test-plan` | **Writes** test-plan.md + testcases.csv |
| `/qa:write-ac` | **Reads** test-plan + CSV |
| `/qa:import-testrail` | **Reads** CSV, **writes** testrail-cache |
| `/qa:fetch-testrail` | **Writes** testrail-cache |
| `/qa:end-sprint` | **Moves** sprint folder to archive |
| `/qa:morning-standup` | **Reads** sprint data |
| `daily-ac-scan.yml` | **Reads** sprint CSV (via Jira API — no local file) |

Separating sprint data into its own repo would mean every command needs cross-repo file operations
and dual git commits. Keeping them together preserves single-repo atomic commits.

**QA_Automation separates cleanly because:**
- Has its own `package.json`, `node_modules/`, `playwright.config.ts`
- Agent writes TO it, but it never references back to agent code
- CI/CD for test execution is independent
- Git history: test code changes vs skill definition changes don't pollute each other

---

## 3. Cross-Reference Map

### 3.1 References that CHANGE (QA_Agent → QA_Automation)

Every `playwright-tests/` path in skill files must change to point to the QA_Automation workspace root.

| File | Current Reference | After Migration |
|---|---|---|
| **SKILL.md** (playwright-automator) | `playwright-tests/` (project root) | QA_Automation workspace root |
| **SKILL.md** (playwright-automator) | `playwright-tests/selectors/` | `selectors/` in QA_Automation |
| **SKILL.md** (playwright-automator) | `playwright-tests/tests/` | `tests/` in QA_Automation |
| **commands/generate.md** | `playwright-tests/` (target default) | QA_Automation workspace root |
| **commands/generate.md** | `playwright-tests/tests/` (existing check) | `tests/` in QA_Automation |
| **commands/generate.md** | `playwright-tests/selectors/` (selector check) | `selectors/` in QA_Automation |
| **commands/inspect.md** | `playwright-tests/selectors/{page}.json` | `selectors/{page}.json` in QA_Automation |
| **commands/scaffold.md** | `playwright-tests/selectors/`, `src/pages/`, `tests/e2e/` | Same dirs without `playwright-tests/` prefix |
| **commands/run.md** | `cd playwright-tests` + `.env` check | `cd` to QA_Automation root |
| **commands/map.md** | `playwright-tests/tests/`, `test-mapping.json` | `tests/`, `test-mapping.json` in QA_Automation |
| **commands/update-selectors.md** | `playwright-tests/selectors/` | `selectors/` in QA_Automation |
| **commands/review.md** | `playwright-tests/`, `playwright-tests/src/`, `playwright-tests/tests/` | QA_Automation root, `src/`, `tests/` |
| **commands/conflicts.md** | `playwright-tests/tests/`, `src/pages/`, `selectors/`, `test-data/` | Same dirs in QA_Automation root |
| **commands/health.md** | `playwright-tests/` (scan entire project) | QA_Automation root |
| **.gitignore** | `playwright-tests/node_modules/` etc. (5 lines) | Remove (moved to QA_Automation's .gitignore) |

### 3.2 References that STAY THE SAME

| File | Reference | Why No Change |
|---|---|---|
| All qa-ops-director commands | `{sprint-folder}/`, `archive/`, `testrail-cache/` | Sprint data stays in QA_Agent ✅ |
| `.github/agents/*.agent.md` | `.github/skills/*/SKILL.md` | Internal to QA_Agent ✅ |
| All `.github/prompts/*.prompt.md` | `.github/skills/*/SKILL.md`, `commands/*.md` | Internal to QA_Agent ✅ |
| `.github/workflows/daily-ac-scan.yml` | `scripts/daily-ac-agent.py` | Internal to QA_Agent ✅ |
| `.vscode/mcp.json` | Figma + Atlassian MCP servers | Works from QA_Agent root ✅ |
| `.githooks/pre-commit` | `^\.github/`, `^scripts/`, etc. | Patterns still match QA_Agent files ✅ |
| `.github/CODEOWNERS` | `.github/skills/`, `scripts/`, etc. | Still in QA_Agent ✅ |
| All references | Internal cross-references within `.github/skills/` | Self-contained ✅ |

### 3.3 Summary: Exactly 15 files to edit

| # | File | Change Type |
|---|---|---|
| 1 | `.github/skills/playwright-automator/SKILL.md` | Replace 8× `playwright-tests/` paths + add workspace context |
| 2 | `.github/skills/playwright-automator/commands/generate.md` | Replace 4× `playwright-tests/` paths |
| 3 | `.github/skills/playwright-automator/commands/inspect.md` | Replace 1× `playwright-tests/selectors/` |
| 4 | `.github/skills/playwright-automator/commands/scaffold.md` | Replace 4× `playwright-tests/` paths |
| 5 | `.github/skills/playwright-automator/commands/run.md` | Replace 2× `playwright-tests/` paths (cd + .env check) |
| 6 | `.github/skills/playwright-automator/commands/map.md` | Replace 3× `playwright-tests/` paths |
| 7 | `.github/skills/playwright-automator/commands/update-selectors.md` | Replace 1× `playwright-tests/selectors/` |
| 8 | `.github/skills/playwright-automator/commands/review.md` | Replace 4× `playwright-tests/` paths |
| 9 | `.github/skills/playwright-automator/commands/conflicts.md` | Replace 4× `playwright-tests/` paths |
| 10 | `.github/skills/playwright-automator/commands/health.md` | Replace 1× `playwright-tests/` path |
| 11 | `.github/prompts/auto-generate.prompt.md` | Replace 1× `playwright-tests/` default target |
| 12 | `.gitignore` | Remove 5 lines (`playwright-tests/*` rules) |
| 13 | `README.md` | Architecture section + clone instructions |
| 14 | `ARCHITECTURE.md` | New 2-repo directory diagram |
| 15 | `.github/TEAM-SETUP.md` | Add QA_Automation clone step |

**NOT changed (0 edits needed):**
- qa-ops-director SKILL.md — sprint data stays in same repo ✅
- All 15 qa-ops-director command files — no path changes ✅
- All 3 agent.md files — reference SKILL.md internally ✅
- All 14 qa-* prompt files — reference SKILL.md internally ✅
- 5 auto-* prompt files (except auto-generate) — reference SKILL.md internally ✅
- daily-ac-scan.yml — uses Jira API, not local files ✅
- .githooks/pre-commit — patterns still valid ✅
- .vscode/mcp.json — works from QA_Agent ✅
- CODEOWNERS — paths still exist in QA_Agent ✅
- CONTRIBUTING.md — sprint data rules unchanged ✅

---

## 4. Repo 1: QA_Agent — Structure After Migration

**GitHub:** `convolabai/QA_Agent`  
**Purpose:** AI agent orchestration + sprint QA data (CODEOWNERS protects infrastructure, sprint folders open)

```
QA_Agent/
├── .github/
│   ├── agents/
│   │   ├── qa-ops-director.agent.md        (no changes)
│   │   ├── playwright-automator.agent.md   (no changes)
│   │   └── automation-reviewer.agent.md    (no changes)
│   ├── skills/
│   │   ├── qa-ops-director/                (NO CHANGES — sprint data still here)
│   │   │   ├── SKILL.md
│   │   │   ├── commands/ (15 files)
│   │   │   ├── references/ (12 files)
│   │   │   └── evals/
│   │   └── playwright-automator/           ★ 10 files updated (playwright-tests/ → QA_Automation)
│   │       ├── SKILL.md                    ★ UPDATE
│   │       ├── commands/ (9 files)         ★ UPDATE 8 of 9
│   │       └── references/ (4 files)       (no changes)
│   ├── prompts/
│   │   ├── qa-*.prompt.md (14 files)       (no changes)
│   │   └── auto-*.prompt.md (6 files)      ★ UPDATE 1 of 6 (auto-generate)
│   ├── workflows/
│   │   └── daily-ac-scan.yml               (no changes)
│   ├── CODEOWNERS                          (no changes)
│   └── TEAM-SETUP.md                       ★ UPDATE: add QA_Automation clone step
│
├── .vscode/
│   └── mcp.json                            (no changes)
│
├── .githooks/
│   └── pre-commit                          (no changes)
│
├── scripts/
│   ├── daily-ac-agent.py                   (no changes)
│   ├── delete-old-ac-comments.py           (no changes)
│   ├── repost-ac-tables.py                 (no changes)
│   └── setup-mcp-atlassian.sh              (no changes)
│
├── agentic-18.2/                           (stays — sprint data)
│   ├── ekoai-scheduled-jobs-test-plan.md
│   ├── ekoai-scheduled-jobs-testcases.csv
│   ├── generate-csv.py
│   └── release-notes-broccoli-f.md
│
├── archive/                                (stays — sprint archives)
│   └── agentic-18.1/
│
├── testrail-cache/                         (stays — TestRail API cache)
│   └── S5277/
│
├── .gitignore                              ★ UPDATE: remove 5 playwright-tests/* lines
├── README.md                               ★ UPDATE: 2-repo architecture
├── ARCHITECTURE.md                         ★ UPDATE: new directory diagram
├── CONTRIBUTING.md                         (no changes — sprint rules still apply)
└── briefing-qa-ops-director.md             (no changes)
```

---

## 5. Repo 2: QA_Automation — Structure After Migration

**GitHub:** `convolabai/QA_Automation`  
**Purpose:** Playwright test automation code (promoted from `playwright-tests/` subdirectory to repo root)

```
QA_Automation/
├── playwright.config.ts                    (promoted — no internal changes)
├── package.json                            (promoted — no internal changes)
├── package-lock.json                       (promoted)
├── tsconfig.json                           (promoted — no internal changes)
├── .env.example                            (promoted)
│
├── src/
│   ├── config/
│   │   └── env.config.ts
│   ├── fixtures/
│   │   └── test-fixtures.ts
│   ├── helpers/
│   │   ├── auth.helper.ts
│   │   ├── api.helper.ts
│   │   ├── cleanup.helper.ts
│   │   ├── data.helper.ts
│   │   └── env-guard.helper.ts
│   ├── pages/
│   │   ├── base.page.ts
│   │   ├── login.page.ts
│   │   └── scheduler.page.ts
│   └── types/
│       └── index.ts
│
├── tests/
│   ├── auth.setup.ts
│   ├── fixtures.ts
│   ├── e2e/scheduled-jobs/
│   │   └── scheduler-list.spec.ts
│   └── api/scheduled-jobs/
│       ├── scheduled-jobs.api.spec.ts
│       └── scheduled-jobs-crud.api.spec.ts
│
├── environments/
│   ├── .env.dev
│   ├── .env.staging
│   └── .env.prod
│
├── test-data/
│   ├── users.json
│   └── scheduled-jobs.json
│
├── selectors/
│   └── README.md
│
├── scripts/                                (playwright-specific scripts)
│   ├── check-conflicts.ts
│   ├── inspect-dom.ts
│   ├── inspect-dom.js
│   ├── inspect-dashboard.js
│   ├── inspect-scheduler.js
│   └── debug-create.js
│
├── .gitignore                              ★ NEW
├── .github/
│   └── CODEOWNERS                          ★ NEW
├── README.md                               ★ UPDATE (remove "subdirectory" references)
└── CONTRIBUTING.md                         ★ NEW
```

### Why No Internal Path Changes?

All imports use relative paths. When `playwright-tests/` contents are promoted to repo root,
the internal tree structure stays identical:

```
# Before: QA_Agent/playwright-tests/tests/api/scheduled-jobs/scheduled-jobs.api.spec.ts
import { getAuthHeaders } from '../../../src/helpers/auth.helper';
#                          └── still resolves to src/helpers/auth.helper.ts ✅

# After: QA_Automation/tests/api/scheduled-jobs/scheduled-jobs.api.spec.ts
import { getAuthHeaders } from '../../../src/helpers/auth.helper';
#                          └── same relative path, same resolution ✅
```

**Zero TypeScript files need editing inside QA_Automation.**

---

## 6. VS Code Multi-Root Workspace Bridge

### `qa-workspace.code-workspace`
```json
{
  "folders": [
    {
      "name": "🤖 QA_Agent",
      "path": "./QA_Agent"
    },
    {
      "name": "🧪 QA_Automation",
      "path": "./QA_Automation"
    }
  ],
  "settings": {
    "files.exclude": {
      "**/node_modules": true,
      "**/dist": true,
      "**/.git": true
    }
  }
}
```

### Directory Layout
```
~/Projects/QA/
├── QA_Agent/                          ← git clone convolabai/QA_Agent
├── QA_Automation/                     ← git clone convolabai/QA_Automation
└── qa-workspace.code-workspace        ← Open with: code qa-workspace.code-workspace
```

### How Cross-Repo Works

Copilot in Multi-Root Workspace has full read/write access to ALL workspace roots:

```
┌────────────────────────────────────────────────────────────┐
│              VS Code Multi-Root Workspace                   │
│  ┌──────────────────┐        ┌──────────────────────────┐  │
│  │    QA_Agent       │        │    QA_Automation          │  │
│  │  (skills+data)    │        │  (playwright code)       │  │
│  │                   │        │                          │  │
│  │  .github/skills/  │──read──│→ tests/                  │  │
│  │  agentic-18.2/    │──read──│→ selectors/              │  │
│  │  testrail-cache/  │        │  src/pages/              │  │
│  │  scripts/         │        │  playwright.config.ts    │  │
│  └──────────────────┘        └──────────────────────────┘  │
│                                                            │
│  Copilot Agent:                                            │
│  • read_file    → reads from either root                   │
│  • create_file  → writes to either root                    │
│  • run_terminal → cd to either root                        │
│  • list_dir     → scans either root                        │
└────────────────────────────────────────────────────────────┘
```

**Example: `/auto:generate` cross-repo flow:**
```
1. Agent reads SKILL.md from QA_Agent/.github/skills/playwright-automator/
2. Agent reads CSV from QA_Agent/agentic-18.3/testcases.csv
3. Agent reads existing tests from QA_Automation/tests/
4. Agent creates new test files IN QA_Automation/tests/e2e/new-feature/
5. Agent runs `cd QA_Automation && npx tsc --noEmit` to validate
```

### MCP Configuration

`.vscode/mcp.json` stays in QA_Agent. VS Code Multi-Root Workspace reads `.vscode/`
from each workspace root. MCP servers (Figma + Atlassian) load from QA_Agent automatically.

---

## 7. File-by-File Change List

### 7.1 SKILL.md — playwright-automator (8 replacements)

Every `playwright-tests/` must become a workspace-aware path:

| Line(s) | Current Text | New Text |
|---|---|---|
| 21 | `Selectors: Maintained in \`playwright-tests/selectors/\` as JSON maps` | `Selectors: Maintained in \`selectors/\` (in QA_Automation workspace root) as JSON maps` |
| 22 | `Project root: \`playwright-tests/\` (relative to workspace root)` | `Project root: \`QA_Automation\` workspace root (contains \`playwright.config.ts\`)` |
| 57 | `Ask user: target repo or use default (playwright-tests/)` | `Ask user: target repo or use default (QA_Automation workspace root)` |
| 171 | `Save as JSON in \`playwright-tests/selectors/{page-name}.json\`` | `Save as JSON in \`selectors/{page-name}.json\` (in QA_Automation)` |
| 240 | `a) Default: playwright-tests/ in this workspace` | `a) Default: QA_Automation workspace root` |
| 247 | `If no → offer to scaffold (copy base structure from playwright-tests/)` | `If no → offer to scaffold (copy base structure from QA_Automation)` |
| 296-297 | `playwright-tests/selectors/` + `playwright-tests/tests/` | `QA_Automation → selectors/` + `QA_Automation → tests/` |
| 306+ | `playwright-tests/` directory tree | Updated tree without `playwright-tests/` prefix |

**New section to add** (after toolchain context block):

```markdown
## Multi-Root Workspace Context

This skill operates across a 2-repo VS Code Multi-Root Workspace:
- **QA_Agent** (this repo) — agents, skills, prompts, scripts, sprint data, archives, TestRail cache
- **QA_Automation** (separate repo) — Playwright tests, page objects, selectors, test data

File location rules:
- Sprint folders (`agentic-*/`), archive, testrail-cache → in QA_Agent root
- `playwright.config.ts`, `src/`, `tests/`, `selectors/` → in QA_Automation root
- When creating test files, ALWAYS write to QA_Automation
- When reading test cases CSV, ALWAYS read from QA_Agent sprint folder
```

### 7.2 generate.md (4 replacements)

| Location | Current | New |
|---|---|---|
| Parameter default | `Default: \`playwright-tests/\` in workspace` | `Default: QA_Automation workspace root` |
| Phase 1 Step 4 prompt | `1. playwright-tests/ (ใน workspace นี้)` | `1. QA_Automation/ (ใน workspace นี้)` |
| Phase 2 Step 3 | `Read \`playwright-tests/tests/\` for existing test files` | `Read \`tests/\` in QA_Automation for existing test files` |
| Phase 2 Step 4 | `Read \`playwright-tests/selectors/\` for known selector maps` | `Read \`selectors/\` in QA_Automation for known selector maps` |

### 7.3 inspect.md (1 replacement)

| Location | Current | New |
|---|---|---|
| Phase 4 output path | `playwright-tests/selectors/{page-name}.json` | `selectors/{page-name}.json` (in QA_Automation) |

### 7.4 scaffold.md (4 replacements)

| Location | Current | New |
|---|---|---|
| Phase 1 Step 1 | `playwright-tests/selectors/{feature}-{page}.json` | `selectors/{feature}-{page}.json` in QA_Automation |
| Phase 1 Step 2 | `playwright-tests/src/pages/{feature}/{page}.page.ts` | `src/pages/{feature}/{page}.page.ts` in QA_Automation |
| Phase 2 | `playwright-tests/src/pages/{feature}/{page-name}.page.ts` | `src/pages/{feature}/{page-name}.page.ts` in QA_Automation |
| Phase 3 | `playwright-tests/tests/e2e/{feature}/{page-name}.spec.ts` | `tests/e2e/{feature}/{page-name}.spec.ts` in QA_Automation |

### 7.5 run.md (2 replacements)

| Location | Current | New |
|---|---|---|
| Phase 1 Step 1 | `Check .env exists in \`playwright-tests/\`` | `Check .env exists in QA_Automation root` |
| Phase 2 | `cd playwright-tests` | `cd` to QA_Automation workspace root |

### 7.6 map.md (3 replacements)

| Location | Current | New |
|---|---|---|
| Phase 1 Step 2 | `Read all test files from \`playwright-tests/tests/\`` | `Read all test files from \`tests/\` in QA_Automation` |
| Phase 1 Step 3 | `playwright-tests/test-mapping.json` | `test-mapping.json` in QA_Automation root |
| Phase 3 output | `playwright-tests/test-mapping.json` | `test-mapping.json` in QA_Automation root |

### 7.7 update-selectors.md (1 replacement)

| Location | Current | New |
|---|---|---|
| Phase 1 Step 1 | `Find the matching selector JSON in \`playwright-tests/selectors/\`` | `Find the matching selector JSON in \`selectors/\` (QA_Automation)` |

### 7.8 review.md (4 replacements)

| Location | Current | New |
|---|---|---|
| Parameter default | `Default: entire \`playwright-tests/\`` | `Default: entire QA_Automation project` |
| Phase 1 Step 3 | `review all files under \`playwright-tests/src/\` and \`playwright-tests/tests/\`` | `review all files under \`src/\` and \`tests/\` in QA_Automation` |
| Phase 4 scope | `playwright-tests/tests/e2e/scheduled-jobs/` | `tests/e2e/scheduled-jobs/ (QA_Automation)` |

### 7.9 conflicts.md (4 replacements)

| Location | Current | New |
|---|---|---|
| Phase 1 Step 1 | `playwright-tests/tests/**/*.spec.ts` | `tests/**/*.spec.ts` in QA_Automation |
| Phase 1 Step 2 | `playwright-tests/src/pages/**/*.page.ts` | `src/pages/**/*.page.ts` in QA_Automation |
| Phase 1 Step 3 | `playwright-tests/selectors/*.json` | `selectors/*.json` in QA_Automation |
| Phase 1 Step 4 | `playwright-tests/test-data/*.json` | `test-data/*.json` in QA_Automation |

### 7.10 health.md (1 replacement)

| Location | Current | New |
|---|---|---|
| Phase 1 | `Scan \`playwright-tests/\` and collect` | `Scan QA_Automation project root and collect` |

### 7.11 auto-generate.prompt.md (1 replacement)

| Location | Current | New |
|---|---|---|
| Parameters section | `[target-repo]` default `playwright-tests/` | `[target-repo]` default QA_Automation workspace root |

### 7.12 .gitignore (remove 5 lines)

```diff
-playwright-tests/node_modules/
-playwright-tests/test-results/
-playwright-tests/reports/
-playwright-tests/playwright/.auth/
-playwright-tests/dist/
```

### 7.13–7.15 Documentation updates

- **README.md** — Add "2-Repo Architecture" section, update clone instructions
- **ARCHITECTURE.md** — Update directory diagram (remove `playwright-tests/`, add QA_Automation reference)
- **TEAM-SETUP.md** — Add step: clone QA_Automation, npm install, workspace file

---

## 8. Execution Tasks — Step by Step

### Phase A: Preparation

#### Task A1: Create QA_Automation repo on GitHub
```bash
# Via github.com → New Repository:
# Name: convolabai/QA_Automation
# Visibility: Private
# Initialize: Empty (no README, no .gitignore)
```

#### Task A2: Backup current monorepo
```bash
cd ~/Projects/QA   # or wherever your repos live
cp -r QA_Agent QA_Agent_backup_$(date +%Y%m%d)
```

---

### Phase B: Create QA_Automation Repo

#### Task B1: Initialize repo + copy playwright-tests contents
```bash
cd ~/Projects/QA
mkdir QA_Automation && cd QA_Automation
git init
git remote add origin git@github.com:convolabai/QA_Automation.git

# Copy contents (NOT the playwright-tests/ folder itself — promote to root)
cp -r ../QA_Agent/playwright-tests/* .
cp ../QA_Agent/playwright-tests/.env.example . 2>/dev/null || true
```

#### Task B2: Create QA_Automation .gitignore
```bash
cat > .gitignore << 'EOF'
# Dependencies
node_modules/

# Test artifacts
test-results/
reports/
playwright/.auth/
dist/

# Credentials
.env
.env.local
*.env
!.env.example
!environments/.env.*

# OS
.DS_Store
**/.DS_Store

# IDE
.idea/
EOF
```

#### Task B3: Create QA_Automation CODEOWNERS
```bash
mkdir -p .github
cat > .github/CODEOWNERS << 'EOF'
# Config files — team lead approval required
playwright.config.ts        @ApiwatKansaard
tsconfig.json               @ApiwatKansaard
package.json                @ApiwatKansaard
src/config/                 @ApiwatKansaard
src/fixtures/               @ApiwatKansaard

# Test files — any QA engineer can push
# tests/ — not listed = anyone can merge
# test-data/ — not listed = anyone can merge
# selectors/ — not listed = anyone can merge
EOF
```

#### Task B4: Update QA_Automation README.md
Remove any references to being a subdirectory. Update paths to reflect repo root status.

#### Task B5: Verify build
```bash
npm install
npx playwright install chromium
npx tsc --noEmit                         # Should pass — 0 errors
npx playwright test --list               # Should show 14 tests
```

#### Task B6: Commit & push
```bash
git add -A
git commit -m "feat: initialize QA_Automation from monorepo playwright-tests/"
git branch -M main
git push -u origin main
```

---

### Phase C: Update QA_Agent Repo

#### Task C1: Remove playwright-tests/ directory
```bash
cd ~/Projects/QA/QA_Agent
rm -rf playwright-tests/
```

#### Task C2: Update 10 playwright-automator skill files

Apply ALL changes from Section 7.1–7.10. The key pattern for every file:

**Replace pattern:** `playwright-tests/X` → `X` (in QA_Automation)

Plus add **Multi-Root Workspace Context** section to SKILL.md (Section 7.1).

#### Task C3: Update auto-generate.prompt.md
Replace `playwright-tests/` default target → QA_Automation (Section 7.11).

#### Task C4: Update .gitignore
Remove 5 lines with `playwright-tests/` prefix (Section 7.12).

#### Task C5: Update documentation
- README.md — 2-repo architecture
- ARCHITECTURE.md — Updated diagram
- TEAM-SETUP.md — Clone step for QA_Automation

#### Task C6: Commit & push
```bash
git add -A
git commit -m "refactor: remove playwright-tests/, update skill paths for 2-repo split

- Removed playwright-tests/ (now in convolabai/QA_Automation)
- Updated 10 playwright-automator skill/command files
- Updated auto-generate prompt
- Updated .gitignore, README, ARCHITECTURE, TEAM-SETUP
- Sprint data stays in this repo (no qa-ops-director changes needed)"
git push
```

---

### Phase D: Create Workspace Bridge

#### Task D1: Create workspace file
```bash
cd ~/Projects/QA
cat > qa-workspace.code-workspace << 'EOF'
{
  "folders": [
    {
      "name": "🤖 QA_Agent",
      "path": "./QA_Agent"
    },
    {
      "name": "🧪 QA_Automation",
      "path": "./QA_Automation"
    }
  ],
  "settings": {
    "files.exclude": {
      "**/node_modules": true,
      "**/dist": true,
      "**/.git": true
    }
  }
}
EOF
```

#### Task D2: Open workspace
```bash
code qa-workspace.code-workspace
```

---

## 9. Dry Run Phase

**Before any git push**, validate everything works locally.

### Dry Run 1: QA_Automation — Tests Still Pass

```bash
cd ~/Projects/QA/QA_Automation

# 1. Dependencies install
npm install

# 2. TypeScript compiles
npx tsc --noEmit
echo "Expected: 0 errors"

# 3. Tests are discoverable
npx playwright test --list 2>&1 | tail -5
echo "Expected: 14 tests listed"

# 4. Tests pass on staging
TEST_ENV=staging npx playwright test --project=e2e --project=api 2>&1 | tail -10
echo "Expected: 14 passed"
```

### Dry Run 2: QA_Agent — No Broken References

```bash
cd ~/Projects/QA/QA_Agent

# 1. No remaining playwright-tests/ references in skill files
grep -r "playwright-tests/" .github/skills/ .github/prompts/ 2>/dev/null
echo "Expected: 0 matches (all replaced)"

# 2. playwright-tests/ directory gone
ls -d playwright-tests/ 2>/dev/null
echo "Expected: 'No such file or directory'"

# 3. .gitignore has no playwright-tests/ lines
grep "playwright-tests/" .gitignore
echo "Expected: 0 matches"

# 4. Sprint data still intact
ls agentic-18.2/
echo "Expected: test-plan.md, testcases.csv, generate-csv.py, release-notes"

ls archive/agentic-18.1/
echo "Expected: archived sprint files"

ls testrail-cache/S5277/
echo "Expected: cases.csv, summary.md"
```

### Dry Run 3: Workspace — Cross-Repo Agent Functionality

Open `qa-workspace.code-workspace` in VS Code, then test each agent:

#### Test A: QA Ops Director (sprint data — should work unchanged)
```
Switch to qa-ops-director agent mode
Say: "ดู sprint ปัจจุบัน"
Expected: Agent finds agentic-18.2/ in QA_Agent root ✅
          Agent reads test-plan.md and testcases.csv ✅
          No errors about missing files ✅
```

#### Test B: Playwright Automator (cross-repo read)
```
Switch to playwright-automator agent mode
Say: "ดู health ของ test suite"
Expected: Agent finds playwright.config.ts in QA_Automation root ✅
          Agent reads tests/ and src/ from QA_Automation ✅
          Agent reports test count, coverage, etc. ✅
```

#### Test C: Playwright Automator (cross-repo generate — dry run)
```
Switch to playwright-automator agent mode
Say: "/auto:generate agentic-18.2"
Expected: Agent reads CSV from QA_Agent/agentic-18.2/ ✅
          Agent asks where to put tests (default: QA_Automation) ✅
          Agent can see existing tests in QA_Automation ✅
          (say "cancel" after confirming the flow works)
```

#### Test D: Automation Reviewer (cross-repo review)
```
Switch to automation-reviewer agent mode
Say: "/auto:review"
Expected: Agent finds test files in QA_Automation ✅
          Agent produces review report ✅
```

#### Test E: MCP Servers
```
In any agent mode, test:
- Figma MCP: ask about a Figma file → should connect ✅
- Atlassian MCP: ask about Jira tickets → should connect ✅
```

### Dry Run 4: CI/CD — GitHub Actions

```bash
cd ~/Projects/QA/QA_Agent

# Verify workflow file is valid
cat .github/workflows/daily-ac-scan.yml | head -20
echo "Expected: workflow still references scripts/daily-ac-agent.py ✅"

# Verify script exists
ls scripts/daily-ac-agent.py
echo "Expected: file exists ✅"
```

### Dry Run Pass/Fail Criteria

| # | Check | Pass Criteria |
|---|---|---|
| DR-1 | `npx tsc --noEmit` in QA_Automation | 0 errors |
| DR-2 | `npx playwright test --list` | 14 tests listed |
| DR-3 | `npx playwright test` (staging) | 14/14 passed |
| DR-4 | No `playwright-tests/` in QA_Agent skill files | 0 grep matches |
| DR-5 | Sprint data intact in QA_Agent | All files present |
| DR-6 | qa-ops-director finds sprint folder | Agent locates agentic-18.2/ |
| DR-7 | playwright-automator finds test project | Agent locates playwright.config.ts |
| DR-8 | `/auto:generate` reads CSV cross-repo | Agent reads from QA_Agent, targets QA_Automation |
| DR-9 | `/auto:review` finds test files | Agent scans QA_Automation |
| DR-10 | MCP servers connect | Figma + Atlassian respond |

**All 10 must pass before any git push.**

---

## 10. Validation Checklist (Post-Push)

After pushing both repos:

| # | Check | Expected | Repo |
|---|---|---|---|
| 1 | `npx tsc --noEmit` | 0 errors | QA_Automation |
| 2 | `npx playwright test --list` | 14 tests | QA_Automation |
| 3 | `TEST_ENV=staging npx playwright test` | 14/14 pass | QA_Automation |
| 4 | `/auto:generate` finds CSV + targets correct repo | ✅ | Workspace |
| 5 | `/qa:test-plan` finds sprint folder | ✅ | QA_Agent |
| 6 | `/qa:start-sprint` creates folder | ✅ | QA_Agent |
| 7 | `/qa:end-sprint` archives | ✅ | QA_Agent |
| 8 | `/qa:fetch-testrail` writes cache | ✅ | QA_Agent |
| 9 | `/auto:review` scans tests | ✅ | Workspace |
| 10 | `/auto:health` reports suite status | ✅ | Workspace |
| 11 | MCP servers (Figma + Atlassian) connect | ✅ | QA_Agent |
| 12 | Pre-commit hook blocks protected files | ✅ | QA_Agent |
| 13 | `daily-ac-scan.yml` manual trigger | ✅ | QA_Agent |
| 14 | Workspace file opens both repos | ✅ | qa-workspace.code-workspace |

---

## 11. Rollback Plan

If anything breaks after push:

### Quick Rollback (< 5 min)
```bash
cd ~/Projects/QA

# Restore monorepo from backup
rm -rf QA_Agent
cp -r QA_Agent_backup_YYYYMMDD QA_Agent
cd QA_Agent
git push --force origin main

# Delete QA_Automation repo on github.com if needed
```

### Partial Rollback (keep QA_Automation, revert QA_Agent)
```bash
cd ~/Projects/QA/QA_Agent
git revert HEAD     # Reverts the "remove playwright-tests" commit
git push

# playwright-tests/ is back in QA_Agent
# QA_Automation also exists separately (harmless)
```

### No-Risk Guarantees
1. **QA_Agent backup** preserved before any changes
2. **QA_Automation** is additive — creating it doesn't affect QA_Agent
3. **Phase C (QA_Agent update) is the only destructive step** — and it's reversible via git revert
4. **Dry Run phase catches issues before any push**

---

## Appendix: Summary Numbers

| Metric | Count |
|---|---|
| **Files to edit in QA_Agent** | 15 |
| **Files to create in QA_Automation** | 3 (.gitignore, CODEOWNERS, CONTRIBUTING.md) |
| **Files to edit in QA_Automation** | 1 (README.md) |
| **qa-ops-director files changed** | 0 |
| **Dry run checks** | 10 |
| **Validation checks** | 14 |
| **Import paths that change in TypeScript** | 0 |

## Appendix: Execution Order

```
Phase A: Preparation (5 min)
  A1: Create QA_Automation repo on GitHub
  A2: Backup monorepo

Phase B: QA_Automation (15 min)
  B1: Init + copy playwright-tests/ contents
  B2: Create .gitignore
  B3: Create CODEOWNERS
  B4: Update README.md
  B5: Verify build (tsc + test list)
  B6: DO NOT PUSH YET — wait for dry run

Phase C: QA_Agent (20 min)
  C1: Remove playwright-tests/
  C2: Update 10 skill/command files
  C3: Update auto-generate prompt
  C4: Update .gitignore
  C5: Update README, ARCHITECTURE, TEAM-SETUP
  C6: DO NOT PUSH YET — wait for dry run

Phase D: Workspace Bridge (2 min)
  D1: Create .code-workspace file
  D2: Open workspace in VS Code

=== DRY RUN GATE ===
  DR-1 to DR-10 must ALL pass
  If any fail → fix before continuing
  If unfixable → rollback from backup
=== END GATE ===

Phase E: Push (5 min)
  E1: git push QA_Automation
  E2: git push QA_Agent

Phase F: Post-Push Validation (10 min)
  Checks 1-14 from validation checklist
```
