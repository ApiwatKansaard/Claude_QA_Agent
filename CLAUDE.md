# QA Ops Director — Claude Code Project

This is an AI-powered QA assistant for test planning, bug triage, TestRail management, and QA reporting.
It runs on **Claude Code** (replacing GitHub Copilot Agent Mode).

## How to use

Use slash commands (e.g., `/qa-test-plan`) or describe your task in natural language.
Claude will route to the correct workflow automatically.

## Agent roster

- **qa-ops-director** — QA Lead: test plans, AC writing, bug reports, TestRail, standups
- **playwright-automator** — Automation Engineer: generate/run/review Playwright tests
- **automation-reviewer** — Code Reviewer: review test quality and detect conflicts

## Full routing and workflow details

Read `.github/skills/qa-ops-director/SKILL.md` for:
- Complete slash command routing table
- Auto-chain pipeline details (/qa-test-plan, /qa-write-ac)
- Tool integrations (Jira, Confluence, Figma, TestRail, Gmail, Calendar)
- Known issues and troubleshooting

Read `.github/skills/playwright-automator/SKILL.md` for:
- Automation command routing (/auto-*)
- Code generation rules and best practices

## MCP credentials setup

Set these environment variables before using (add to `~/.zshrc` or `.env`):

```bash
export ATLASSIAN_EMAIL="yourname@amitysolutions.com"
export ATLASSIAN_TOKEN="your-atlassian-api-token"
export FIGMA_API_KEY="your-figma-personal-access-token"
export TESTRAIL_EMAIL="yourname@amitysolutions.com"
export TESTRAIL_API_KEY="your-testrail-api-key"
```

## Companion repo

Test automation code lives in **Claude_QA_Automation** (sibling folder).
Open both in the same workspace for full cross-repo agent functionality.
