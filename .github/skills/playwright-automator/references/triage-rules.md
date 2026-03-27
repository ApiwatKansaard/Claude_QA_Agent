# Triage Classification Rules

Reference file for the test-result-analyzer agent and `/auto:triage` command.

## Error Pattern → Classification Map

### AUTOMATION_BUG Patterns

| Error Pattern | Root Cause | Common Fix |
|---|---|---|
| `strict mode violation` — locator resolved to N elements | Broad text locator matching multiple elements | Use `getByRole()`, `nth()`, or more specific locator |
| `Expected: "X" Received: "Y"` where Y is correct behavior | Test assertion hardcoded wrong value | Update expected value to match actual spec |
| Element not found — but screenshot shows element present | Selector mismatch (text changed, attribute changed) | Inspect DOM for current selector; update POM or test |
| `page.goto()` navigated to wrong URL | Base URL or route path incorrect in test | Check route; update URL constant |
| Timeout on `waitForSelector` — element loads but differently | Selector uses old class/id that was refactored | Re-inspect DOM; use role/testid locator |
| `locator.click()` — element is covered by overlay | z-index issue or modal blocking; test doesn't dismiss it | Add wait for overlay to disappear or dismiss modal first |
| `toHaveCount(N)` — count differs because test assumes specific data | Test data dependency; hard-coded expected count | Make assertion flexible or ensure test data setup |

### PRODUCT_BUG Patterns

| Error Pattern | Root Cause | Verification |
|---|---|---|
| "Oops! something went wrong" visible in screenshot | App error page; unhandled exception | Confirm by visiting URL; check network tab/API |
| API returns 500 with error body | Server-side exception | Replay curl; check if reproducible |
| UI shows data that contradicts the spec | Feature regression or incorrect implementation | Compare Figma/Confluence spec vs actual behavior |
| Missing UI element that spec says should exist | Feature not implemented or removed | Check Figma spec + recent PRs |
| API returns different schema than documented | Breaking API change | Compare swagger/docs vs actual response |
| Pagination shows wrong total count | Backend calculation bug | Verify via direct API call with different params |

### ENVIRONMENT_ISSUE Patterns

| Error Pattern | Root Cause | Verification |
|---|---|---|
| Timeout (navigation, networkidle) — site is slow | Staging environment under load or deploying | Retry 1× or curl health check |
| `401 Unauthorized` — auth was valid before | Token expired during test run | Check token expiry in auth state JSON |
| `net::ERR_CONNECTION_REFUSED` | Staging service down | curl the base URL |
| `502 Bad Gateway` | Load balancer/proxy issue | Check if transient; retry in 30s |
| Flaky — passes on retry without code change | Race condition in test or transient infra issue | Mark as `test.fixme()` if consistent flake |

## Known EkoAI Staging Patterns

These are verified patterns from the EkoAI staging app (discovered in this project):

### Dashboard Page (`/ai-task-scheduler`)
- Search input exists but does NOT perform client-side filtering → don't assert result count after search
- Status filter dropdown: "All Status", "Active", "Inactive"
- Sort dropdown: "Created date", "Alphabetical", "Latest modified"
- Job cards have toggle switches (`role=switch`)
- No `data-testid` attributes → use role-based locators

### Job Detail Page (`/ai-task-scheduler/{id}`)
- Tabs: "Job Configuration", "Audience", "History Log"
- ⚠️ "Job Configuration" text appears TWICE on page (heading + tab) → use `getByRole('button', { name: 'Job Configuration' })`
- Page sometimes shows "Oops! something went wrong" for invalid/deleted job IDs → test must handle with `.or()` pattern
- Skeleton loaders appear before content; wait for them to disappear

### API (`ekoai.staging.ekoapp.com`)
- Auth: Bearer token from Cognito `idToken` cookie
- `GET /v1/scheduled-jobs` returns `{ data: [], metadata: { pagination: { ... } } }`
- Pagination: `limit` (default 10), `offset`
- CRUD on `/v1/scheduled-jobs` — POST requires name, template, recipients at minimum
- After create, verify with GET by ID (eventual consistency: may need small delay)

## Confidence Scoring for Auto-Fix

| Scenario | Confidence | Action |
|---|---|---|
| Selector text differs but element visible in screenshot | HIGH | Auto-fix: update selector |
| Strict mode → obvious fix with getByRole | HIGH | Auto-fix: replace locator |
| Wrong expected value, correct value obvious | HIGH | Auto-fix: update assertion |
| Multiple possible fixes; unclear which is right | MEDIUM | Present options to user |
| Error in page object shared by multiple tests | MEDIUM | Present fix; warn about impact |
| Root cause unclear from evidence | LOW | Report as "needs manual investigation" |

## Blocked / Skipped → Prerequisite Data Pattern

When TestRail shows **Blocked** status or Playwright shows `skipped` for tests, check whether the root cause is a missing prerequisite.

### Recognition

A test is blocked-by-prerequisite when:
- Playwright result status = `skipped`
- Test body contains `test.skip(true, 'No ... available to test')`
- Test body pattern: `getJobCount() === 0 → skip` or `navigated === false → skip`

These are **not true blocks** — they are automation gaps solvable with a `beforeAll` fixture.

### Auto-fix rule (HIGH confidence)

When triage detects this pattern, apply the following fix automatically:

1. **Import** `createJob` / `deleteJob` from `src/helpers/job-factory`
2. **Add** `let resourceId: string` at module scope
3. **Add** `test.beforeAll(async () => { resourceId = await createJob('...'); })`
4. **Add** `test.afterAll(async () => { if (resourceId) await deleteJob(resourceId); })`
5. **Replace** each test's skip guard + `clickJob(0)` navigation with direct navigation via `gotoJob(resourceId)` / `gotoAudienceTab(resourceId)` / `gotoHistoryTab(resourceId)`
6. **Remove** `schedulerPage` from fixture params if it was only used for `getJobCount()` / `clickJob()`

Full reference: [best-practices.md § 9 — Prerequisite Data](./best-practices.md)

---

## Anti-Patterns to Flag

When triaging, also flag these test quality issues even in passing tests:
1. **Hard-coded waits** (`page.waitForTimeout(5000)`) — suggest replacing with waitFor conditions
2. **Broad text locators** (`page.locator('text=Submit')`) — flag as future strict-mode risk
3. **Missing error resilience** — test doesn't handle known error states with `.or()`
4. **No cleanup** — CRUD test creates data but doesn't delete it in afterAll
