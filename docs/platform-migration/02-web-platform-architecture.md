# 02 — Web Platform Architecture

> Migration Plan: CLI → Web UI Platform
> Target: QA Ops Dashboard with test execution, reports, and integrations

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Browser (React)                          │
│                                                                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ ┌────────┐  │
│  │Dashboard │ │Test Run  │ │Reports   │ │TestRail│ │Jira    │  │
│  │          │ │Console   │ │(Team +   │ │Sync    │ │Bugs +  │  │
│  │Pass Rate │ │Run/Stop  │ │Risk Story│ │Import/ │ │AC Post │  │
│  │Trends    │ │Real-time │ │Trends    │ │Push    │ │Sprint  │  │
│  └──────────┘ └──────────┘ └──────────┘ └────────┘ └────────┘  │
│                                                                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                         │
│  │Settings  │ │AI Tools  │ │Test Cases│                         │
│  │Creds     │ │Test Plan │ │CSV View  │                         │
│  │(encrypt) │ │AC Writer │ │Editor    │                         │
│  └──────────┘ └──────────┘ └──────────┘                         │
└───────────────────────┬─────────────────────────────────────────┘
                        │ HTTPS (API Routes)
┌───────────────────────▼─────────────────────────────────────────┐
│                    Next.js Backend                                │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │                   Auth Layer                              │     │
│  │  Auth.js v5 + Amazon Cognito (SSO with EkoAI platform)   │     │
│  │  Roles: Admin | QA Lead | QA Engineer | Viewer           │     │
│  └─────────────────────────────────────────────────────────┘     │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │              Integration Layer (TypeScript)                │     │
│  │                                                           │     │
│  │  JiraClient ──── REST ──── ekoapp.atlassian.net          │     │
│  │  TestRailClient ─ REST ──── ekoapp20.testrail.io         │     │
│  │  FigmaClient ─── REST ──── api.figma.com                 │     │
│  │  ConfluenceClient REST ──── ekoapp.atlassian.net/wiki    │     │
│  │  ClaudeClient ─── REST ──── api.anthropic.com (AI)       │     │
│  │                                                           │     │
│  │  ★ All use server-side credentials (never in browser)    │     │
│  └─────────────────────────────────────────────────────────┘     │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │              Job Queue (BullMQ + Redis)                    │     │
│  │                                                           │     │
│  │  TestRunJob ──── spawns Playwright ──── results.json     │     │
│  │  ReportJob ──── generates reports ──── HTML/PDF          │     │
│  │  SyncJob ────── pushes to TestRail ──── milestones/runs  │     │
│  │  AIJob ──────── calls Claude API ──── test plans/AC      │     │
│  │                                                           │     │
│  │  Real-time: Redis pub/sub → Server-Sent Events → Browser │     │
│  └─────────────────────────────────────────────────────────┘     │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │              Data Layer (Prisma ORM)                       │     │
│  │                                                           │     │
│  │  PostgreSQL:                                              │     │
│  │    users ──── id, email, role, cognito_sub               │     │
│  │    credentials ── user_id, service, encrypted_token      │     │
│  │    test_runs ──── id, status, env, results_json          │     │
│  │    test_results ── run_id, title, module, status, error  │     │
│  │    test_cases ──── testrail_id, title, section, type     │     │
│  │                                                           │     │
│  │  Encryption: AES-256-GCM for all credentials             │     │
│  └─────────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────────┘
         │              │              │
    ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
    │PostgreSQL│   │  Redis  │   │Playwright│
    │  (data)  │   │ (queue) │   │(headless)│
    └─────────┘   └─────────┘   └─────────┘
```

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| **Framework** | Next.js 14+ (App Router) | Full-stack TypeScript, same language as Playwright |
| **UI** | React + Tailwind CSS + shadcn/ui | Fast, dark theme support, Amity green branding |
| **Charts** | Recharts or Chart.js | Replace Python-generated SVG charts |
| **State** | TanStack Query (React Query) | Server-state caching, polling for test runs |
| **Database** | PostgreSQL + Prisma ORM | Test history, credentials, user management |
| **Queue** | BullMQ (Redis-backed) | Long-running test execution jobs |
| **Real-time** | Server-Sent Events (SSE) | Stream test progress to browser |
| **Auth** | Auth.js v5 + Cognito | SSO with existing EkoAI identity |
| **AI** | Anthropic Claude API | Test plan generation, AC writing, bug triage |
| **Credentials** | AES-256-GCM encrypted | Per-user API tokens stored securely |

---

## Monorepo Layout

```
qa-ops-platform/
├── apps/
│   └── web/                          # Next.js application
│       ├── app/
│       │   ├── layout.tsx            # Root layout (dark theme, Amity branding)
│       │   ├── page.tsx              # Dashboard (pass rate, trends, recent runs)
│       │   ├── test-runs/
│       │   │   ├── page.tsx          # Run list + "New Run" button
│       │   │   └── [runId]/page.tsx  # Run detail (real-time progress)
│       │   ├── reports/
│       │   │   ├── page.tsx          # Report list
│       │   │   ├── [runId]/page.tsx  # Team report view
│       │   │   └── [runId]/risk/     # Risk story report view
│       │   ├── test-cases/
│       │   │   └── page.tsx          # CSV viewer + TestRail sync
│       │   ├── jira/
│       │   │   ├── bugs/page.tsx     # Bug filing form
│       │   │   └── sprint/page.tsx   # Sprint board view
│       │   ├── settings/
│       │   │   └── page.tsx          # Credential management
│       │   └── api/                  # API routes (backend)
│       │       ├── test-runs/route.ts
│       │       ├── reports/route.ts
│       │       ├── testrail/route.ts
│       │       ├── jira/route.ts
│       │       └── ai/route.ts
│       └── components/
│           ├── charts/               # Donut, bar, trend charts
│           ├── risk-map/             # Risk story components
│           └── test-table/           # Filterable test result table
│
├── packages/
│   ├── integrations/                 # Shared REST API clients
│   │   ├── jira.ts                   # Jira Cloud REST client
│   │   ├── testrail.ts              # TestRail REST client
│   │   ├── figma.ts                 # Figma REST client
│   │   ├── confluence.ts            # Confluence REST client
│   │   └── claude.ts                # Anthropic Claude API client
│   │
│   ├── test-runner/                  # Playwright job execution
│   │   ├── worker.ts                # BullMQ worker (spawns Playwright)
│   │   ├── progress-parser.ts       # Parse Playwright stdout for progress
│   │   └── result-mapper.ts         # Map results.json → DB schema
│   │
│   └── report-engine/               # Report generation (port from Python)
│       ├── team-report.ts           # Port of generate_report.py
│       ├── risk-report.ts           # Port of generate_risk_report.py
│       └── risk-classifier.ts       # Risk scoring + categorization
│
├── prisma/
│   └── schema.prisma                # Database schema
│
├── docker-compose.yml               # PostgreSQL + Redis for dev
└── package.json                      # Turborepo config
```

---

## Database Schema

```prisma
model User {
  id          String   @id @default(cuid())
  email       String   @unique
  name        String
  role        Role     @default(ENGINEER)
  cognitoSub  String?  @unique
  credentials Credential[]
  testRuns    TestRun[]
  createdAt   DateTime @default(now())
}

enum Role {
  ADMIN
  QA_LEAD
  ENGINEER
  VIEWER
}

model Credential {
  id             String   @id @default(cuid())
  userId         String
  user           User     @relation(fields: [userId], references: [id])
  service        Service
  encryptedEmail String   // AES-256-GCM encrypted
  encryptedToken String   // AES-256-GCM encrypted
  verifiedAt     DateTime?
  createdAt      DateTime @default(now())

  @@unique([userId, service])
}

enum Service {
  JIRA
  TESTRAIL
  FIGMA
}

model TestRun {
  id           String       @id @default(cuid())
  triggeredBy  String
  user         User         @relation(fields: [triggeredBy], references: [id])
  status       RunStatus    @default(QUEUED)
  environment  String       @default("staging")
  project      String       @default("e2e")
  grepFilter   String?      // e.g. "@smoke"
  startedAt    DateTime?
  finishedAt   DateTime?
  total        Int          @default(0)
  passed       Int          @default(0)
  failed       Int          @default(0)
  flaky        Int          @default(0)
  skipped      Int          @default(0)
  passRate     Float        @default(0)
  resultsJson  Json?
  results      TestResult[]
  createdAt    DateTime     @default(now())
}

enum RunStatus {
  QUEUED
  RUNNING
  PASSED
  FAILED
  CANCELLED
}

model TestResult {
  id          String   @id @default(cuid())
  runId       String
  run         TestRun  @relation(fields: [runId], references: [id])
  title       String
  module      String
  status      String   // passed, failed, flaky, skipped
  duration    Int      // ms
  errorMsg    String?
  testrailId  String?
  priority    String?  // P1, P2
  retryCount  Int      @default(0)
}
```
