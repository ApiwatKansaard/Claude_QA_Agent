# Webhook E2E Testing Guide — AI Task Scheduler

## Overview

This guide describes how to test the AI Task Scheduler's webhook integration end-to-end.
The approach uses a **local mock process server** + **ngrok tunnel** to simulate the
External Process Server that EkoAI calls during scheduled job execution.

This validates the full **Trigger → Process → Action** pipeline without relying on
a real external service.

## Architecture

```
┌───────────────────────┐     ┌──────────────────────────────┐     ┌──────────────┐
│   EkoAI Platform      │     │  Mock Process Server (local)  │     │  EkoAI       │
│   (Scheduled Jobs)    │     │  Port 3333                    │     │  Callback    │
│                       │     │                                │     │  Endpoint    │
│  1. POST /status-check├────►│  ✓ Validate X-API-Key         │     │              │
│     (health check)    │◄────│  ✓ Return 200 OK              │     │              │
│                       │     │                                │     │              │
│  2. POST /webhook     ├────►│  ✓ Log timestamp + payload    │     │              │
│     (per-user data)   │◄────│  ✓ Ack 200 immediately        │     │              │
│                       │     │                                │     │              │
│                       │     │  3. POST callback (async)      ├────►│  ✓ Receive   │
│                       │     │     X-API-Key: {cbk_key}       │◄────│    result    │
│                       │     │     Body: {id, status, result} │     │              │
└───────────────────────┘     └──────────────────────────────┘     └──────────────┘
                                       │
                                       │ ngrok tunnel
                                       ▼
                              https://xxxx.ngrok-free.app
                              (public URL for EkoAI to reach)
```

## Prerequisites

| Requirement | How to check |
|---|---|
| Node.js >= 18 | `node --version` |
| ngrok installed + authenticated | `ngrok version` |
| Playwright auth state | `npm run setup:staging` (or target env) |
| EkoAI Console access | Login to staging/dev environment |

## Files

All files live in the **Claude_QA_Automation** repository:

| File | Purpose |
|---|---|
| `src/mock-server/process-server.ts` | Mock server implementation (status-check, webhook, logs, callback) |
| `src/mock-server/server-manager.ts` | Lifecycle manager: start/stop server + ngrok tunnel |
| `src/mock-server/index.ts` | Barrel exports |
| `tests/e2e/ekoai-console/ai-task-scheduler/webhook-e2e.spec.ts` | 7 E2E test cases |

## Spec Compliance

The mock server implements the contract defined in:

- **[Doc] Project Team Guide | Scheduled Job** — endpoint spec, payload format, auth
- **[TS] EkoAI | Eko | AI Scheduled Jobs** — pipeline architecture, throttling, callback pattern

### Endpoints implemented

| Endpoint | Method | Spec Reference |
|---|---|---|
| `/status-check` | POST | Section 6 — Health check before each run |
| `/webhook` | POST | Section 4 — Receive per-user processing request |
| `/logs` | GET | Test-only — retrieve all received webhook calls |
| `/logs` | DELETE | Test-only — clear logs between test runs |
| `/health` | GET | Test-only — internal health check |

### Webhook payload format (from EkoAI)

```json
{
  "id": "<scheduleJobRunUserId>",
  "data": {
    "userId": "string",
    "username": "string",
    "email": "string (optional)",
    "firstname": "string (optional)",
    "lastname": "string (optional)",
    "position": "string (optional)",
    "extras": { "key": "value" }
  }
}
```

### Callback payload format (to EkoAI)

**Endpoint:** `POST https://ekoai.{env}.ekoapp.com/v1/scheduled-jobs/runs/callback`
**Header:** `x-api-key: scbk_<callbackApiKey>` (generate via `POST /v1/scheduled-jobs/{jobId}/callback-api-key`)

```json
{
  "id": "<scheduleJobRunUserId>",
  "homePage": {
    "html": "<div>Hello {{displayName}}</div><p>{{homePageUpdatedAtFormatted}}</p>",
    "lang": "en"
  }
}
```

**Schema notes** (verified against staging 2026-04-21):
- `id` is **required** (422 "id is required" if missing)
- `homePage` is optional — id-only callback marks the run user as finished (fail-style)
- `homePage.html` is a string (HTML content) — replaces the deprecated `widgets` array per Tech Spec AE-14600
- **Do NOT include** `status`, `result`, `quotaConsumed`, or `failReason` at the root — server returns 422 `"status" is not allowed`
- Payload body limit is ~1 MB — exceeding returns 413 `PayloadTooLargeException` (see [AE-14621](https://ekoapp.atlassian.net/browse/AE-14621))

> ⚠️ The callback schema in [Doc] Project Team Guide | Scheduled Job (Confluence 3528917005, §5.2) still documents the legacy `{id, status, quotaConsumed, result, failReason}` shape, which the server no longer accepts. Follow the schema above instead.

## How to Run

### 1. Standalone mock server (manual testing)

```bash
cd ~/Documents/Claude_QA_Automation

# Start server (default port 3333)
npm run mock-server

# With custom config
MOCK_API_KEY=my-secret CALLBACK_URL=https://ekoai.example.com/callback \
  CALLBACK_API_KEY=scbk_xxx npm run mock-server
```

Then use the ngrok URL in EkoAI Console:

```bash
ngrok http 3333
# Copy the https://xxxx.ngrok-free.app URL
```

### 2. Automated smoke tests (mock server only)

```bash
# Validates: server starts, ngrok works, endpoints respond correctly
npm run test:webhook:smoke
```

### 3. Full E2E test (creates real scheduled job)

```bash
# Creates a job in EkoAI, waits for trigger, validates webhook received
npm run test:webhook
```

**Note:** The full E2E test (Test 7) has a 10-minute timeout because it waits for
EkoAI to trigger the webhook at the scheduled time.

## Test Cases

| # | Test | Tag | What it validates |
|---|---|---|---|
| 1 | Mock server is running | @smoke | Server starts on port 3333 |
| 2 | ngrok tunnel accessible | @smoke | Public URL is reachable |
| 3 | /status-check returns 200 | @smoke | Health check with valid API key |
| 4 | /status-check rejects invalid key | — | Auth validation |
| 5 | /webhook accepts and logs payload | @P1 | Payload logging, ack response |
| 6 | /webhook rejects invalid key | — | Auth validation |
| 7 | EkoAI triggers webhook on time | @P1 @slow | Full pipeline: create job → wait → verify trigger |

## Configuration

### Environment variables (for standalone mode)

| Variable | Default | Description |
|---|---|---|
| `MOCK_SERVER_PORT` | `3333` | Port for mock server |
| `MOCK_API_KEY` | *(none)* | Expected API key (skip validation if not set) |
| `CALLBACK_URL` | *(none)* | EkoAI callback endpoint URL |
| `CALLBACK_API_KEY` | *(none)* | Callback API key (from EkoAI Console) |
| `CALLBACK_DELAY_MS` | `1000` | Delay before sending callback (simulates processing) |

### EkoAI Console configuration

When creating a scheduled job in EkoAI Console:

| Field | Value |
|---|---|
| **Process endpoint** | ngrok public URL (e.g., `https://xxxx.ngrok-free.app`) |
| **API Key** | Same value as `MOCK_API_KEY` |
| **Timeout** | `00:01:00` (60 seconds) |

## Troubleshooting

| Problem | Solution |
|---|---|
| ngrok tunnel not starting | Check `ngrok authtoken` is configured |
| Webhook not received after job trigger | Check ngrok URL is still active (free tier tunnels expire) |
| 401 on /webhook | Verify API key matches between EkoAI Console and mock server |
| Callback fails | Verify callback URL and API key from EkoAI Console Edit Job page |
| Test 7 times out | Increase `test.setTimeout()` or check if job trigger time is correct |

## Extending

### Adding new action types

When EkoAI adds new action types (e.g., `EKO_MESSAGE`, `EKO_TASK`), extend the
callback payload in `process-server.ts` with new root-level fields alongside
`homePage` (the production validator rejects a `result` wrapper):

```typescript
// Current (verified 2026-04-21)
{ id, homePage: { html, lang } }

// Future (hypothetical — confirm with backend before adding)
{ id, homePage: { html, lang }, tasks: { ... }, message: { ... } }
```

### Adding failure scenario tests

The mock server can be extended to simulate failures:

- Return 5xx on `/webhook` to test EkoAI retry logic
- Delay callback beyond timeout to test cutoff behavior
- Return invalid payload to test EkoAI error handling
