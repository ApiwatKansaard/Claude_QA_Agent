# Contributing — QA Ops Director

> **Who this is for:** Every QA team member who pushes work to this repo.
>
> **TL;DR** Push sprint artifacts freely. Don't touch infrastructure files — they're protected.
>
> **Last updated:** 2026-03-25

---

## What You CAN Push

Everything under **sprint folders** and **archives** is open for all team members:

| Path | What Goes Here |
|---|---|
| `agentic-{version}/` | Active sprint test plans, test case CSVs, release notes |
| `archive/` | Completed sprint archives |

### Sprint Folder Naming

Sprint folders follow the pattern `agentic-{version}` — e.g., `agentic-18.2`, `agentic-19.0`.

- The agent creates the folder via `/qa:start-sprint`
- If the folder already exists, just add your files inside it

### File Naming Convention

Use the **feature slug** to keep files unique when multiple QA work on the same sprint:

```
{sprint-folder}/
├── ekoai-{feature-slug}-test-plan.md       # Your test plan
├── ekoai-{feature-slug}-testcases.csv      # Test cases (TestRail CSV format)
├── release-notes-{sprint-name}.md          # Shared — one per sprint
└── generate-csv.py                         # Helper script (optional)
```

**Examples:**
- `ekoai-scheduled-jobs-test-plan.md` — Scheduled Jobs feature
- `ekoai-chat-export-test-plan.md` — Chat Export feature
- `ekoai-user-roles-testcases.csv` — User Roles feature

> **Avoid name collisions:** Always include the feature slug. Don't use generic names like `test-plan.md`.

---

## What You CANNOT Modify

The following paths are **infrastructure files** maintained by the team lead. They are protected
by [CODEOWNERS](.github/CODEOWNERS) and a [pre-commit hook](.githooks/pre-commit).

| Protected Path | Why |
|---|---|
| `.github/skills/` | Agent skill logic (commands, references, orchestrator) |
| `.github/agents/` | Agent mode definition |
| `.github/prompts/` | Prompt files for slash commands |
| `.github/workflows/` | GitHub Actions CI/CD |
| `.vscode/` | MCP server config (shared) |
| `scripts/` | Python automation scripts |
| `README.md` | Main documentation |
| `ARCHITECTURE.md` | System design documentation |
| `CONTRIBUTING.md` | This file |
| `.gitignore` | Git ignore rules |
| `.github/TEAM-SETUP.md` | Team setup guide |
| `.github/CODEOWNERS` | Ownership rules |
| `.githooks/` | Git hooks |

**If you need a change to any of these:** Open a PR and request review from the team lead,
or ask the team lead directly.

---

## Pre-Commit Hook Setup

The repo includes a pre-commit hook that blocks accidental changes to infrastructure files.

**Install it once** after cloning:

```bash
git config core.hooksPath .githooks
```

**What it does:**
- **Blocks** commits that modify protected infrastructure files
- **Warns** (non-blocking) about CSV format issues in test case files

**Bypass (team lead only):**

```bash
git commit --no-verify -m "infra: your message"
```

---

## Before You Push: Review Checklist

Use the **pre-push review agent** to validate your work before pushing:

1. Open Copilot Chat in **qa-ops-director** mode
2. Type: `/qa:review-before-push`
3. The agent will check:
   - CSV format (15 columns, required fields)
   - Test case quality (clear steps, expected results)
   - Release notes completeness
   - TestRail mapping consistency
4. Fix any ❌ issues before pushing

---

## Commit Message Convention

Use these prefixes for sprint artifact commits:

```
test: add scheduled-jobs test plan (agentic-18.2)
test: update chat-export test cases after review
docs: add release notes for broccoli-f sprint
fix: correct test case priorities after triage
```

For infrastructure changes (team lead only):

```
infra: add new /qa:review-before-push command
infra: update CODEOWNERS for new protected paths
ci: fix daily-ac-scan cron schedule
```

---

## Git Workflow

```
main (shared)
  │
  ├── You push sprint artifacts directly to main
  │     git add agentic-18.2/
  │     git commit -m "test: add scheduled-jobs test plan (agentic-18.2)"
  │     git push origin main
  │
  └── Infrastructure changes go through PRs
        git checkout -b infra/add-new-command
        # Make changes
        git push origin infra/add-new-command
        # Open PR → team lead reviews → merge
```

> **Why direct push for sprint artifacts?** Test plans and CSVs are created per-feature
> and don't conflict. PRs add unnecessary overhead for daily QA work.

---

## Quick Reference

| I want to… | Do this |
|---|---|
| Start working on a sprint | `/qa:start-sprint` creates the folder |
| Generate test cases | `/qa:test-plan [Figma URL] [Confluence URL]` |
| Push my test plan | `git add agentic-*/` → `git commit` → `git push` |
| Review before pushing | `/qa:review-before-push` |
| Report a bug | `/qa:bug-report [description]` |
| Suggest an infra change | Open a PR or ask the team lead |
| Check my pre-commit hook | `git config core.hooksPath` → should show `.githooks` |
