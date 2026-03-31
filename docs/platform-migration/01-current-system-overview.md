# 01 — Current System Overview

> QA Ops Director: AI-Powered QA Automation System
> Author: QA Engineering Team (Amity)
> Date: 2026-03-31

---

## What Is This System?

QA Ops Director is an **AI-powered QA automation system** that runs on **Claude Code** (CLI). It automates the full QA lifecycle: test planning, test case management, Playwright test execution, TestRail sync, Jira bug filing, and report generation.

The system is split across **2 GitHub repositories** that work together:

---

## Repository 1: Claude_QA_Agent

**URL:** `https://github.com/ApiwatKansaard/Claude_QA_Agent`

**Purpose:** QA intelligence layer — skills, orchestration, test plans, and test case data.

### What It Contains

| Folder | Purpose |
|---|---|
| `.github/skills/qa-ops-director/` | Main QA orchestration skill (15 slash commands) |
| `.github/skills/playwright-automator/` | Automation skill (9 commands + 13 pitfall rules A1-A13) |
| `.github/skills/qa-html-report/` | HTML report generation skill |
| `console-morning-brief-18.0/` | Sprint data: 208 test cases (CSV) + test plan + TestRail importer |
| `scripts/` | Python scripts for Jira AC posting, comment management |
| `archive/` | Completed sprint archives |
| `.env` | Credentials for Jira, TestRail, Atlassian (not committed) |

### Key Files

| File | What It Does |
|---|---|
| `SKILL.md` (qa-ops-director) | Routes slash commands, orchestrates 4-phase pipelines |
| `SKILL.md` (playwright-automator) | Generates Playwright tests, documents 13 Ant Design pitfalls |
| `console-morning-brief-testcases.csv` | 208 test cases with 16 columns, TestRail IDs |
| `import-new-testrail-cases.py` | Creates test cases in TestRail via REST API |
| `daily-ac-agent.py` | Posts Acceptance Criteria to Jira sprint tickets |

### External Integrations (from this repo)

| Service | Protocol | Auth | Purpose |
|---|---|---|---|
| **Jira Cloud** | REST API | Basic Auth (email:token) | Bug filing, AC posting, sprint management |
| **Confluence** | REST API | Basic Auth (same token) | Read spec pages for test planning |
| **TestRail** | REST API | Basic Auth (email:key) | Import/sync test cases, create milestones/runs, push results |
| **Figma** | MCP (stdio) → REST API | Personal Access Token | Read design specs for test planning |
| **Atlassian MCP** | MCP (stdio) → REST API | Basic Auth | Wrapper for Jira/Confluence (VS Code only) |

---

## Repository 2: Claude_QA_Automation

**URL:** `https://github.com/ApiwatKansaard/Claude_QA_Automation`

**Purpose:** Test execution layer — Playwright tests, page objects, and report generators.

### What It Contains

| Folder | Purpose |
|---|---|
| `tests/e2e/agentic/morning-brief/` | 7 E2E spec files (90 tests) |
| `tests/api/agentic/morning-brief/` | 5 API spec files (53 tests) |
| `src/pages/` | Page Object Model classes |
| `src/helpers/` | Auth, API, cleanup, job-factory utilities |
| `src/config/` | Multi-environment config loader |
| `scripts/` | Report generators (team + risk story) |
| `environments/` | Per-env .env files (dev/staging/prod) |

### Test Coverage (Morning Brief 18.0)

| Spec File | Tests | Type |
|---|---|---|
| `dashboard.spec.ts` | 9 | E2E |
| `create-job.spec.ts` | 13 | E2E |
| `custom-recurrence.spec.ts` | 24 | E2E |
| `job-config.spec.ts` | 11 | E2E |
| `recipients.spec.ts` | 11 | E2E |
| `history-logs.spec.ts` | 10 | E2E |
| `widget-rendering.spec.ts` | 12 | E2E |
| `trigger-step.api.spec.ts` | 10 | API |
| `process-step.api.spec.ts` | 12 | API |
| `action-step.api.spec.ts` | 11 | API |
| `callback.api.spec.ts` | 10 | API |
| `security.api.spec.ts` | 10 | API |
| **Total** | **143** | |

### Key Scripts

| Script | What It Does |
|---|---|
| `generate_report.py` | Reads `results.json` → generates team HTML report (numbers, charts, GO/NO-GO) |
| `generate_risk_report.py` | Reads `results.json` → generates risk story report (for PM meetings) |

### External Integrations (from this repo)

| Service | Protocol | Auth | Purpose |
|---|---|---|---|
| **EkoAI Console** | Browser (Playwright) | Cognito OAuth 2.0 | Application under test (E2E) |
| **EkoAI API** | REST | Bearer JWT (Cognito) | API tests + job factory |

---

## How The 2 Repos Work Together

```
Claude_QA_Agent                          Claude_QA_Automation
┌────────────────────┐                  ┌──────────────────────┐
│ SKILL.md           │  "generate tests"│ Playwright tests     │
│ (orchestration)    │ ──────────────── │ (143 test cases)     │
│                    │                  │                      │
│ Test Cases CSV     │  "read cases"    │ spec files map to    │
│ (208 rows)         │ ──────────────── │ CSV TestRail IDs     │
│                    │                  │                      │
│ TestRail importer  │  "push results"  │ results.json         │
│ (Python scripts)   │ ◄──────────────  │ (Playwright output)  │
│                    │                  │                      │
│ Jira scripts       │                  │ Report generators    │
│ (AC posting, bugs) │                  │ (team + risk story)  │
└────────────────────┘                  └──────────────────────┘
```

**Data Flow:**
1. QA Agent generates test plan → CSV test cases
2. Test cases imported to TestRail via Python script
3. Playwright Automator reads CSV → generates `.spec.ts` files
4. Playwright runs tests → outputs `results.json`
5. Report scripts read `results.json` → generate HTML reports
6. Results pushed to TestRail milestone/run via Python script
7. Bugs filed to Jira with cURL reproduce steps

---

## Authentication Summary

| Credential | Storage | Format |
|---|---|---|
| Jira email + API token | `.env` file | `JIRA_EMAIL`, `JIRA_TOKEN` |
| Atlassian email + token | `.env` file | `ATLASSIAN_EMAIL`, `ATLASSIAN_API_TOKEN` |
| TestRail email + API key | `.env` file | `TESTRAIL_EMAIL`, `TESTRAIL_API_KEY` |
| Figma PAT | VS Code runtime prompt | `${input:figma_token}` |
| EkoAI admin credentials | `environments/.env.staging` | `ADMIN_EMAIL`, `ADMIN_PASSWORD` |
| GitHub Actions | GitHub Secrets | `secrets.JIRA_EMAIL`, `secrets.JIRA_TOKEN` |

All credentials are **per-user** and **never committed** to the repository.
