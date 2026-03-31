# 04 — Implementation Phases

> Step-by-step plan สำหรับ developer ที่จะมาสร้าง Web Platform

---

## Phase 1: Foundation (2-3 weeks)

### Goals
- Next.js app ที่ login ได้
- เก็บ credentials ของ user อย่าง secure
- Jira + TestRail REST clients ทำงานได้

### Tasks

```
1.1  Scaffold Next.js 14+ App Router project
     - Turborepo monorepo with apps/web + packages/*
     - Tailwind CSS + shadcn/ui (dark theme)
     - Docker Compose: PostgreSQL + Redis

1.2  Auth.js v5 + Cognito Setup
     - Configure Amazon Cognito as OAuth provider
     - Create User model in Prisma
     - Role-based access: Admin, QA Lead, Engineer, Viewer
     - Protected routes middleware

1.3  Credential Vault
     - Settings page: form to enter Jira/TestRail/Figma tokens
     - AES-256-GCM encryption before storing in DB
     - Validate token on save (make test API call)
     - Never return decrypted token to frontend

1.4  Jira REST Client
     - Port from: scripts/daily-ac-agent.py (QA_Agent repo)
     - TypeScript class in packages/integrations/jira.ts
     - Methods: getIssue, createIssue, searchJql, postComment
     - Test: verify bug creation works from web backend

1.5  TestRail REST Client
     - Port from: scripts/push_testrail.py, import-new-testrail-cases.py
     - TypeScript class in packages/integrations/testrail.ts
     - Methods: getCases (with pagination!), addCase, addRun, pushResults
     - Test: verify case import works from web backend
```

### Deliverable
- User can login, store credentials, view Jira issues, browse TestRail cases

---

## Phase 2: Test Runner + Reports (3-5 weeks)

### Goals
- Run Playwright tests จาก UI
- ดู progress real-time
- ดู reports (team + risk story) ใน browser

### Tasks

```
2.1  BullMQ Job Queue Setup
     - Redis connection in docker-compose
     - BullMQ queue: "test-runs"
     - API route: POST /api/test-runs → enqueue job
     - Options: environment, grep filter, project (e2e/api)

2.2  Playwright Worker
     - Separate Node process (not inside Next.js)
     - Spawns: npx playwright test --reporter=json --timeout=60000
     - Sets TEST_ENV from job params
     - Parses stdout for progress events
     - Stores results in PostgreSQL on completion

2.3  Real-time Progress (SSE)
     - Worker publishes progress via Redis pub/sub
     - API route: GET /api/test-runs/[runId]/stream (SSE endpoint)
     - Frontend: EventSource consumer with progress bar

2.4  Run History Page
     - /test-runs → list all runs with status badges
     - /test-runs/[runId] → detail view with real-time progress
     - Store run metadata + all test results in DB

2.5  Team Report (React Port)
     - Port: scripts/generate_report.py → packages/report-engine/team-report.ts
     - React components: score cards, donut chart, module grid, test table
     - /reports/[runId] → full team report view
     - PDF export option

2.6  Risk Story Report (React Port)
     - Port: scripts/generate_risk_report.py → packages/report-engine/risk-report.ts
     - React components: verdict, risk cards, exit criteria, meeting script
     - /reports/[runId]/risk → risk story view
     - Dark glassmorphism design (Amity branded)

2.7  TestRail Sync
     - After test run completes: auto-push results to TestRail
     - Create milestone + run with section filtering (IMPORTANT: only Morning Brief sections)
     - Show sync status in UI
```

### Deliverable
- User can trigger test runs, watch real-time progress, view reports, auto-sync to TestRail

---

## Phase 3: AI Features (4-8 weeks)

### Goals
- AI-powered test plan generation
- Acceptance Criteria writing
- Bug triage + classification

### Tasks

```
3.1  Claude API Integration
     - Anthropic SDK: @anthropic-ai/sdk
     - packages/integrations/claude.ts
     - System prompts ported from SKILL.md files
     - Streaming responses for long operations

3.2  Test Plan Generation
     - Input: Figma URL + Confluence URL
     - Backend fetches design data (Figma REST) + spec content (Confluence REST)
     - Sends to Claude API with qa-test-plan SKILL.md as system prompt
     - Output: test cases CSV + test plan document
     - UI: wizard with preview + edit before saving

3.3  Acceptance Criteria Writer
     - Input: Sprint board URL
     - Backend fetches sprint tickets (Jira REST)
     - Sends each ticket to Claude API with qa-write-ac prompt
     - Output: AC items in emoji-coded format
     - Posts as ADF comment to Jira (with user approval in UI)

3.4  Bug Triage
     - Input: Jira filter URL or test results with failures
     - Backend analyzes errors with Claude API
     - Classifies: INFRA / BUG / CLEANUP / UNKNOWN
     - Suggests priority + assignee
     - UI: triage dashboard with one-click actions

3.5  Trend Analytics (New!)
     - Historical pass rate chart (line chart over time)
     - Flaky test tracker (which tests flip-flop most)
     - Module-level heatmap (which areas are most unstable)
     - Failure pattern detection (recurring errors)
```

### Deliverable
- Full AI-powered QA platform matching current Claude Code capabilities + new analytics

---

## Phase Summary

| Phase | Duration | Features | Dependencies |
|---|---|---|---|
| **Phase 1** | 2-3 weeks | Auth, credentials, Jira/TestRail clients | PostgreSQL, Redis |
| **Phase 2** | 3-5 weeks | Test runner, reports, real-time progress | Phase 1 + BullMQ |
| **Phase 3** | 4-8 weeks | AI test plans, AC writing, analytics | Phase 2 + Claude API key |

**Total estimated: 9-16 weeks** for full feature parity + new capabilities

---

## What's NOT Needed from Current System

| Current Component | Web Platform Equivalent | Action |
|---|---|---|
| `.vscode/mcp.json` | Not needed — REST clients replace MCP | Skip |
| `mcp-atlassian` binary | `JiraClient.ts` + `ConfluenceClient.ts` | Replace |
| `figma-developer-mcp` | `FigmaClient.ts` | Replace |
| `${input:}` prompts | Settings page credential vault | Replace |
| SKILL.md orchestration | Claude API system prompts | Port |
| Python scripts (`.py`) | TypeScript packages | Port |
| `.env` files | Database encrypted credentials | Replace |
| Playwright HTML reporter | React report components | Replace |
| Claude Code CLI | Web UI | Replace |
