# QA Ops Director — Claude Code Project

AI-powered QA assistant for test planning, bug triage, TestRail management, and QA reporting.
Runs on **Claude Code** (CLI + VSCode Extension) and **GitHub Copilot** (lite mode).

## First time? Run: `/qa-get-started`

The onboarding wizard will install everything, configure credentials, verify tools, and run your first test — all interactively. Works on both Claude Code and Copilot.

## How to use

Use slash commands (e.g., `/qa-test-plan`) or describe your task in natural language.
Claude will route to the correct workflow automatically.

## Agent roster

- **qa-ops-director** — QA Lead: test plans, AC writing, bug reports, TestRail, standups
- **playwright-automator** — Automation Engineer: generate/run/review Playwright tests
- **automation-reviewer** — Code Reviewer: review test quality and detect conflicts

## Full routing and workflow details

Read `.github/skills/qa-ops-director/SKILL.md` for:
- Complete slash command routing table (16 commands)
- Auto-chain pipeline details (/qa-test-plan, /qa-write-ac)
- Tool integrations (Jira, Confluence, Figma, TestRail, Gmail, Calendar)

Read `.github/skills/playwright-automator/SKILL.md` for:
- Automation command routing (/auto-*)
- Code generation rules and best practices

## Credentials setup

Copy `.env.example` → `.env` and fill in your credentials. See `scripts/bootstrap.sh` for automated setup.

## Companion repo

Test automation code lives in **Claude_QA_Automation** (sibling folder).
Open both in the same workspace for full cross-repo agent functionality.

## Team QA Rules (Apply to ALL conversations)

These rules are learned from team experience. Follow them strictly:

- **TestRail credentials:** Always read from `.env` file before any TestRail script/call — NOT from shell env
- **TestRail runs:** Always create 3 runs per milestone: Smoke + Regression + Manual
- **TestRail sections:** When creating runs, ALWAYS filter cases by section_id — NEVER use all cases in a suite
- **CSV counting:** Never use `wc -l` to count test cases — always use Python `csv.DictReader`
- **Test case titles:** SHORT format: "Verify [subject] [action]" max 8-10 words. No "Check...should"
- **Dynamic tests:** NEVER hardcode day/date in tests — use `todayLabel()`/`todayName()` and `startsWith()`
- **DOM inspection:** NEVER write selectors from assumptions — ALWAYS inspect actual platform DOM first
- **Bug filing:** API bugs MUST include cURL for reproduce. UI bugs MUST include screenshot/video
- **Bug Jira fields:** Squad field required (EGT=11641, Broccoli=14379). Sprint=customfield_10006
- **HTML report:** ALWAYS generate team HTML report after every test run
- **README:** ALWAYS update README.md when making significant changes (applies to BOTH repos)
- **Prod test users:** Only use Sharp (Apiwat) and Boss (Tanawoot) as audience for prod scheduled jobs
