# Test Plan: EkoAI Scheduled Jobs

> **Feature**: EkoAI | Eko | AI Scheduled Jobs  
> **Sprint**: Sharp_Test_001  
> **Date**: 2025-07-17  
> **QA Lead**: Apiwat Kansa-ard  

## Sources

| Type | Document | Page ID |
|------|----------|---------|
| Tech Proposal | [TP] EkoAI \| Eko \| AI Scheduled Jobs | 3488645131 |
| Tech Spec | [TS] EkoAI \| Eko \| AI Scheduled Jobs | 3518726148 |
| Tech Spec | [TS] EkoAI \| Eko \| AI Scheduled Jobs; Morning Brief Actions | 3523280914 |
| Team Guide | [Doc] Project Team Guide \| Scheduled Job | 3528917005 |
| Team Guide | [Doc] Project Team Guide \| Home Page | 3535208450 |
| Figma | Dashboard (341:7657) | — |
| Figma | Create (345:6690) | — |
| Figma | Job Configuration (345:5871) | — |
| Figma | Recipients (345:6681) | — |
| Figma | History Logs (344:7102) | — |

## Scope

### In Scope
- **Job configuration & scheduling** — ScheduleJob CRUD, cron trigger, audience resolution, nextRun management
- **Process step** — async per-user external endpoint invocation, throttling (slow-start), callback handling
- **Action step** — delivery orchestration (immediate + time-triggered), action queue, per-user tracking
- **Cutoff timeout** — 24h backstop for stuck runs, BullMQ-based orchestrator/worker
- **Home Page delivery** — Morning Brief action type, HomePage record CRUD, push notifications, real-time events
- **Home Page widget rendering** — JSON widget structure, recognized/unrecognized widgets, rendering order
- **Security** — HMAC signatures, API key auth (EkoApiKey strategy), scope enforcement
- **EkoAI Console UI** — Dashboard, Create wizard, Job Configuration, Recipients, History Logs
- **New UI states** — Hover failure tooltip (Dashboard), Save Changes confirmation modal (Job Config / Recipients), Edit Running job states, Retrying state (History Logs), Bulk select 400 audiences

### Out of Scope
- Phase 2 actions: Eko Message (AI Companion), Eko Task
- Multi-platform delivery (MS Teams, EkoAI SDK)
- Home Page history view
- Home Page block structure details (separate spec)

## Assumptions & Flagged Ambiguities
- Audience type is always "Eko" in Phase 1
- Only MORNING_BRIEF action type is supported
- Process endpoint must use HTTPS
- Default timeout is 100s, max is 24h
- Cutoff timeout default is 24 hours (configurable via env var)
- Race condition between cutoff and action completion is accepted by design
- "Edit Running" jobs should show a confirmation modal before allowing changes
- Hover tooltip on Dashboard failure count shows per-job failure details

## Test Strategy

| Surface | Approach |
|---------|----------|
| Web (EkoAI Console) | Manual — UI flows from Figma: dashboard, create wizard, job config, recipients, history logs |
| API/Backend | Manual — CRUD endpoints, trigger, callback, status check, HomePage APIs |
| Infrastructure | Manual — scheduler logic, BullMQ queue, Redis cleanup, concurrency |
| Security | Manual — HMAC, API key, scope, permission boundaries |

## Coverage Summary

| Group | Test Cases | P1 | P2 | Smoke | Sanity | Regression |
|-------|-----------|----|----|-------|--------|------------|
| 1. Dashboard | 9 | 5 | 4 | 4 | 1 | 4 |
| 2. Create Scheduled Job | 12 | 6 | 6 | 5 | 1 | 6 |
| 3. Job Configuration | 12 | 8 | 4 | 5 | 1 | 6 |
| 4. Recipients (Audience) | 13 | 9 | 4 | 7 | 0 | 6 |
| 5. History Logs | 12 | 7 | 5 | 6 | 2 | 4 |
| 6. Trigger Step | 9 | 6 | 3 | 4 | 0 | 5 |
| 7. Process Step & Throttling | 14 | 8 | 6 | 6 | 0 | 8 |
| 8. Callback | 10 | 7 | 3 | 4 | 0 | 6 |
| 9. Action Step | 10 | 7 | 3 | 4 | 0 | 6 |
| 10. Cutoff Timeout | 7 | 3 | 4 | 2 | 0 | 5 |
| 11. Home Page Delivery | 13 | 7 | 6 | 5 | 1 | 7 |
| 12. Widget Rendering | 9 | 2 | 7 | 2 | 2 | 5 |
| 13. Security & Auth | 9 | 5 | 4 | 2 | 1 | 6 |
| 14. Status Check | 7 | 3 | 4 | 1 | 1 | 5 |
| 15. Database & Infra | 10 | 3 | 7 | 3 | 0 | 7 |
| 16. Race Conditions | 6 | 6 | 0 | 2 | 0 | 4 |
| 17. API Endpoints | 15 | 7 | 8 | 8 | 0 | 7 |
| **TOTAL** | **177** | **118** | **59** | **70** | **10** | **97** |

### Test Case Distribution
- **Positive (Smoke + Sanity)**: 80 cases (45%) — core happy paths
- **Negative + Edge (Regression)**: 97 cases (55%) — error handling, boundary, concurrency
- **All 177 titles** use "Check/Verify ... should ... when ..." style
- **All Steps and Expected Results** use numbered multi-line format for TestRail readability

### Delta from Agentic 18.2
- **+9 new test cases** from updated Figma designs:
  - Dashboard: +2 (hover failure tooltip, sort-by column)
  - Job Configuration: +2 (save changes confirmation modal, edit running job warning)
  - Recipients: +2 (confirmation modal on unsaved changes, edit running job recipients)
  - History Logs: +3 (retrying state, select all 400 audiences, select all this page)

## Known Gaps
- Widget-specific rendering tests are limited because block structure spec is in a separate document
- Multi-cloud testing (Azure CosmosDB vs AWS DynamoDB) not explicitly covered per environment
- End-to-end flow across trigger → process → action → HomePage delivery would benefit from integration test cases

## Test Cases
See: `ekoai-scheduled-jobs-testcases.csv` (TestRail-importable format)

## Next Steps
1. `/qa:sync-testrail` — Import CSV to TestRail
2. `/qa:write-ac` — Write acceptance criteria on Jira tickets
