# /auto:run — Run Playwright Tests

## Trigger
`/auto:run [tag or file] [project]`

## Parameters
- `[tag or file]` — Tag filter (`@smoke`, `@regression`, `@P1`) or specific file path
- `[project]` — Playwright project name (`e2e`, `api`, `mobile`, `firefox`). Default: all.

## Pipeline

### Phase 1: Prepare

1. Check `.env` exists in QA_Automation root:
   - If missing → error with "Copy .env.example to .env and fill credentials"
2. Check `node_modules/` exists:
   - If missing → run `npm install` first
3. Check Playwright browsers installed:
   - If missing → run `npx playwright install --with-deps chromium`

### Phase 2: Build Command

Construct the Playwright command:

```bash
cd QA_Automation   # (workspace root of QA_Automation repo)

# By tag
npx playwright test --grep @smoke

# By file
npx playwright test tests/e2e/scheduled-jobs/dashboard.spec.ts

# By project
npx playwright test --project=api

# Combined
npx playwright test --grep @smoke --project=e2e

# With reporter
npx playwright test --grep @smoke --reporter=html
```

### Phase 3: Execute

Run in terminal and capture output.

### Phase 4: Report

Parse the test output and present:

```markdown
## 🎯 Test Run Results

**Command:** `npx playwright test --grep @smoke --project=e2e`
**Duration:** 45s
**Browser:** Chromium 131.0

| Status | Count |
|--------|-------|
| ✅ Passed | 28 |
| ❌ Failed | 3 |
| ⏭️ Skipped | 2 |

### ❌ Failures
1. **dashboard.spec.ts:15** — "should display job list"
   - Error: `Timeout waiting for selector '[data-testid="job-list"]'`
   - Suggestion: Run `/auto:inspect` to update selectors

2. **create-job.spec.ts:42** — "should validate cron expression"
   - Error: `Expected "weekdays at 08:00" but got "Every weekday at 8:00 AM"`
   - Suggestion: Update expected text assertion

### Next Steps
- Fix failures and re-run: `npm run test:smoke`
- View HTML report: `npm run report`
- Debug a specific test: `npx playwright test --debug tests/e2e/.../dashboard.spec.ts:15`
```
