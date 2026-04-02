# Test Plan: EkoAI Console Morning Brief

> **Feature**: EkoAI | Eko | Console Morning Brief
> **Sprint**: Console Morning Brief 18.0
> **Date**: 2026-03-30
> **QA Lead**: Apiwat Kansa-ard
> **Previous Sprint**: Agentic 18.2 (168 test cases / 17 groups)

## Sources

| Type | Document | Page ID |
|------|----------|---------|
| Tech Spec | [TS] EkoAI \| Eko \| AI Scheduled Jobs | 3518726148 |
| Tech Spec | [TS] EkoAI \| Eko \| AI Scheduled Jobs; Morning Brief Actions | 3523280914 |
| Team Guide | [Doc] Project Team Guide \| Scheduled Job | 3528917005 |
| Team Guide | [Doc] Project Team Guide \| Home Page | 3535208450 |
| Figma | Dashboard (341:7657) | -- |
| Figma | Create (345:6690) | -- |
| Figma | Job Configuration (345:5871) | -- |
| Figma | Recipients (345:6681) | -- |
| Figma | History Logs (344:7102) | -- |

## Sprint Delta from Agentic 18.2

This sprint continues the EkoAI Scheduled Jobs feature with updated specs (TS page modified 2026-03-29). Key spec changes driving new/revised test cases:

1. **iCalendar (RFC 5545) recurrence rules** -- DTSTART + RRULE for flexible scheduling replaces simple cron
2. **Termination conditions** -- runUntilTimes (max 10) / endDate / natural RRULE end
3. **Process throttling** -- slow-start adaptive algorithm (no user-configurable delay/maxConsecutiveCalls/retry)
4. **Callback auth** -- `scbk_<uuid>` key per ScheduledJob generated via POST endpoint
5. **Action modes** -- IMMEDIATE vs SCHEDULED delivery timing
6. **Cutoff deduplication** -- via scheduledJobRunId in BullMQ
7. **HomePage append model** -- new record per run (no 1-per-day limit)
8. **Widget rendering** -- flexible JSON structure / max 3 levels / max 10 widgets per wrapper
9. **Dual DB** -- CosmosDB + DynamoDB via repository abstraction

### Previous Sprint Known Gaps Addressed

| Gap | Resolution |
|-----|-----------|
| Widget-specific rendering tests were limited | Added widget type variants: text / image / list / carousel / nested wrappers |
| Multi-cloud testing not covered | Added CosmosDB vs DynamoDB parity and failover cases |
| E2E integration flow missing | Added trigger-to-process-to-action-to-HomePage integration cases |

## Scope

### In Scope

- **Console UI (5 screens)** -- Dashboard / Create wizard / Job Configuration / Recipients / History Logs
- **Backend pipeline** -- Trigger / Process / Callback / Action / Cutoff / HomePage delivery
- **Widget rendering** -- JSON structure / recognized vs unrecognized widgets / nesting / limits
- **Security** -- HMAC signatures / API key auth (EkoApiKey) / callback auth (scbk_uuid) / scope enforcement
- **Infrastructure** -- BullMQ queues / Redis / dual DB (CosmosDB + DynamoDB) / scheduler
- **API endpoints** -- CRUD / trigger / callback / status-check / HomePage / webhook

### Out of Scope

- Phase 2 actions: Eko Message (AI Companion) / Eko Task
- Multi-platform delivery (MS Teams / EkoAI SDK)
- Home Page history view
- Cosmetics properties (bgColor / color / borderWidth / borderColor) -- postponed per spec

## Assumptions and Flagged Ambiguities

1. Audience type is always "Eko" in Phase 1
2. Only MORNING_BRIEF action type is supported
3. Process endpoint must use HTTPS
4. Default process timeout is 100s (only `step.process.limit.timeout` configurable)
5. Cutoff timeout default is 24 hours
6. Race condition between cutoff and action completion is accepted by design (etag-based)
7. Webhook ack timeout is 10s (NOT configurable)
8. Retry: 3 attempts for 5xx/timeout / NO retry for 4xx
9. HomePage `expiresAt` default 24h (configurable via `com.ekoapp.homepage.expiresInMinutes`)
10. Push notification types: HOME_PAGE_DELIVERED (create) / HOME_PAGE_UPDATED (update)

## Test Strategy

| Surface | Approach |
|---------|----------|
| Web (EkoAI Console) | Manual -- UI flows from Figma: Dashboard / Create wizard / Job Configuration / Recipients / History Logs |
| API/Backend | Manual -- CRUD endpoints / trigger / callback / status-check / HomePage APIs |
| Infrastructure | Manual -- scheduler logic / BullMQ queue / Redis cleanup / dual DB / concurrency |
| Security | Manual -- HMAC / API key / callback key / scope / permission boundaries |
| Integration (E2E) | Manual -- full pipeline trigger through HomePage delivery verification |

## Coverage Summary

| # | Group | Cases | P1 | P2 | Smoke | Sanity | Regression | Delta from 18.2 |
|---|-------|-------|----|----|-------|--------|------------|-----------------|
| 1 | Dashboard | 9 | 4 | 5 | 2 | 2 | 5 | +2 |
| 2 | Create Scheduled Job | 13 | 7 | 6 | 5 | 2 | 6 | +1 |
| 3 | Job Configuration | 11 | 6 | 5 | 4 | 1 | 6 | +1 |
| 4 | Recipients (Audience) | 11 | 6 | 5 | 4 | 2 | 5 | 0 |
| 5 | History Logs | 10 | 5 | 5 | 3 | 2 | 5 | +1 |
| 6 | Trigger Step | 10 | 6 | 4 | 3 | 2 | 5 | +1 |
| 7 | Process Step and Throttling | 12 | 7 | 5 | 4 | 2 | 6 | -2 |
| 8 | Callback | 10 | 6 | 4 | 3 | 1 | 6 | 0 |
| 9 | Action Step | 11 | 7 | 4 | 4 | 1 | 6 | +1 |
| 10 | Cutoff Timeout | 8 | 4 | 4 | 2 | 1 | 5 | +1 |
| 11 | Home Page Delivery | 13 | 7 | 6 | 4 | 2 | 7 | 0 |
| 12 | Widget Rendering | 12 | 4 | 8 | 2 | 2 | 8 | +3 |
| 13 | Security and Auth | 10 | 6 | 4 | 2 | 2 | 6 | +1 |
| 14 | Status Check | 8 | 4 | 4 | 2 | 1 | 5 | +1 |
| 15 | Database and Infra | 11 | 4 | 7 | 2 | 2 | 7 | +1 |
| 16 | Race Conditions | 7 | 5 | 2 | 2 | 0 | 5 | +1 |
| 17 | API Endpoints | 12 | 6 | 6 | 5 | 1 | 6 | -3 |
| **TOTAL** | | **178** | **104** | **74** | **53** | **26** | **99** | **+10** |

## Risk Areas

| Risk | Mitigation |
|------|-----------|
| iCalendar RRULE complexity -- many recurrence patterns to validate | Focus on common patterns (daily / weekly / monthly) + BYSETPOS / BYDAY edge cases |
| Dual database parity -- CosmosDB and DynamoDB may behave differently | Explicit cross-DB cases for CRUD / query ordering / TTL behavior |
| Race condition (cutoff vs action) -- accepted by design | Verify etag mechanism prevents data corruption; test concurrent completion |
| BullMQ queue isolation -- dynamic queue per run | Test queue cleanup / orphan detection / Redis memory pressure |
| HomePage append model -- no 1-per-day limit | Test multiple runs per day / verify refId uniqueness / expiration cleanup |

## Test Case File

All test cases are in the companion CSV file:
`console-morning-brief-testcases.csv` (178 cases / 15 columns / TestRail import format)

## Next Steps

1. Import to TestRail: `/qa-import-testrail` with target suite link
2. Create regression milestone: `/qa-create-regression Console Morning Brief 18.0`
3. Write AC for sprint tickets: `/qa-write-ac`
