# Playwright Best Practices Reference

> Used by: playwright-automator agent, automation-reviewer agent.
> This document defines the coding standards for all generated and reviewed automation code.

---

## 1. Page Object Model (POM) — Mandatory

Every UI test MUST use POM. The pattern:

```
src/pages/
  base.page.ts          ← Abstract base with common helpers
  login.page.ts         ← Shared across all features
  {feature}/
    {page}.page.ts      ← One per distinct page/view
```

### Rules

- **Locators as class properties** — defined in constructor, never inline in tests
- **Actions as methods** — `clickCreateButton()`, not `page.click('[data-testid="create"]')`
- **No assertions in page objects** — page objects describe capabilities, not tests
- **One page object per logical page** — wizards with multiple steps = one PO with step methods
- **Inherit from BasePage** — gets common helpers (navigate, waitForElement, screenshot)

### Anti-patterns

```typescript
// ❌ Selector in test
test('create job', async ({ page }) => {
  await page.locator('[data-testid="create-btn"]').click();
});

// ❌ Assertion in page object
class DashboardPage {
  async verifyJobExists() {
    await expect(this.jobList).toContainText('Job 1'); // Don't do this
  }
}

// ❌ Hardcoded values in page object
class LoginPage {
  async login() {
    await this.emailInput.fill('admin@test.com'); // Don't do this
  }
}
```

---

## 2. Selector Strategy

Priority order — always use the highest-priority option available:

| Priority | Strategy | Playwright API | When to Use |
|----------|----------|---------------|-------------|
| 1 | `data-testid` | `page.getByTestId('...')` | Always preferred. Ask dev to add if missing. |
| 2 | ARIA role | `page.getByRole('button', { name: '...' })` | Semantic HTML elements |
| 3 | Label | `page.getByLabel('...')` | Form inputs with labels |
| 4 | Placeholder | `page.getByPlaceholder('...')` | Inputs with placeholder text |
| 5 | Text | `page.getByText('...')` | Static text content |
| 6 | CSS | `page.locator('.class')` | Last resort — fragile |

### Never Use
- XPath — hard to read, breaks on DOM restructure
- Generated class names — `.css-1a2b3c` changes every build
- Nth-child without context — `div:nth-child(3)` is meaningless
- Chained CSS without data attributes — `.wrapper > .inner > .btn`

---

## 3. Test Structure

Follow AAA pattern (Arrange, Act, Assert):

```typescript
test('should create a scheduled job with valid data @smoke @P1', async ({ page }) => {
  // Arrange — setup specific state for this test
  const createWizard = new CreateWizardPage(page);
  const testData = readTestData<JobData>('scheduled-jobs.json').validJob;

  // Act — perform the user action
  await createWizard.goto();
  await createWizard.fillJobName(testData.name);
  await createWizard.setCronExpression(testData.schedule);
  await createWizard.submit();

  // Assert — verify the expected outcome
  await expect(page).toHaveURL(/scheduled-jobs\/[\w-]+/);
  const toast = await createWizard.waitForToast();
  expect(toast).toContain('Success');
});
```

---

## 4. Waiting Strategy

**NEVER** use arbitrary timeouts:

```typescript
// ❌ NEVER
await page.waitForTimeout(3000);

// ✅ Wait for specific element
await page.waitForSelector('[data-testid="job-list"]');

// ✅ Wait for network idle
await page.waitForLoadState('networkidle');

// ✅ Wait for response
await page.waitForResponse(resp =>
  resp.url().includes('/api/v1/jobs') && resp.status() === 200
);

// ✅ Expect with auto-retry (Playwright's built-in)
await expect(page.getByTestId('job-list')).toBeVisible();
await expect(page.getByTestId('toast')).toContainText('Created');
```

---

## 5. Test Independence

Each test MUST be able to run alone, in any order.

```typescript
// ❌ Tests depend on shared state
let jobId: string;

test('create job', async () => {
  jobId = await createJob(); // Sets shared variable
});

test('delete job', async () => {
  await deleteJob(jobId); // Depends on previous test
});

// ✅ Each test creates its own state
test('create job', async ({ request }) => {
  const job = await api.createJob(testData);
  expect(job.id).toBeTruthy();
});

test('delete job', async ({ request }) => {
  const job = await api.createJob(testData); // Create fresh
  await api.deleteJob(job.id);               // Then delete
});
```

---

## 6. Test Data Management

- **Static data** → `test-data/*.json` files
- **Dynamic data** → generate in fixtures or helpers with unique identifiers
- **Credentials** → `.env` file only, never in code
- **Sprint isolation** → prefix test data with sprint identifier

```typescript
// Generate unique test data
const jobName = `[auto-${sprint}] Job ${randomString(6)} ${timestamp()}`;
```

---

## 7. Tags and Test Organization

Every test MUST have:
1. **Type tag** — `@smoke`, `@sanity`, `@regression` (from TestRail CSV)
2. **Priority tag** — `@P1`, `@P2`
3. **Feature tag** — `@scheduled-jobs`, `@chat-export`, etc.

```typescript
test.describe('Feature — Page', { tag: ['@smoke', '@scheduled-jobs'] }, () => {
  test('should do X @smoke @P1', ...);      // Inherits describe tags + own
  test('should handle Y @regression @P2', ...);
});
```

**File organization:**
```
tests/
  e2e/
    {feature}/           ← One folder per feature
      {page}.spec.ts     ← One file per page/view
  api/
    {feature}/
      {resource}.api.spec.ts
```

---

## 8. Authentication — Cognito Pattern

EkoAI uses **AWS Cognito** for auth. There is NO REST login endpoint — authentication happens via browser cookies set during the login flow.

### Key Rules

1. **UI tests** use `storageState` from `playwright/.auth/user.json` (saved by `auth.setup.ts`)
2. **API tests** extract the `idToken` from saved auth state cookies — **NOT `accessToken`**
3. **Always use** `src/helpers/auth.helper.ts` — never inline token extraction in test files

```typescript
// ✅ CORRECT — use centralized helper
import { getAuthHeaders } from '../../../src/helpers/auth.helper';

test('API call', async ({ request }) => {
  const response = await request.get(url, { headers: getAuthHeaders() });
});

// ❌ WRONG — hardcoded token type
const token = cookies.find(c => c.name.includes('accessToken')); // WRONG token!

// ❌ WRONG — inline fs.readFileSync in test file
const state = JSON.parse(fs.readFileSync('playwright/.auth/user.json', 'utf-8'));
```

### Cognito Cookie Map

| Cookie | Used For |
|--------|----------|
| `idToken` | **API Authorization header** — contains user claims (email, groups) |
| `accessToken` | Cognito UserPool operations only — NOT for API calls |
| `refreshToken` | Token renewal — never used directly in tests |

### Important

- API project in `playwright.config.ts` **must depend on setup** (`dependencies: ['setup']`)
- Auth state must be fresh — Cognito tokens expire after ~1 hour
- If API tests get 401, re-run setup first: `npx playwright test --project=setup`

---

## 9. API Testing

Use `APIRequestContext` with the `ApiHelper` wrapper:

```typescript
test.describe('API — Scheduled Jobs', { tag: ['@api', '@scheduled-jobs'] }, () => {
  test('should return 401 without auth @security @P1', async ({ request }) => {
    const response = await request.get(`${baseURL}/api/v1/jobs`, {
      headers: { Authorization: '' },
    });
    expect(response.status()).toBe(401);
  });

  test('should create job via API @smoke @P1', async ({ request }) => {
    const api = new ApiHelper(request, baseURL);
    const job = await api.post('/api/v1/jobs', validJobPayload);
    expect(job).toHaveProperty('id');
  });
});
```

---

## 9. Prerequisite Data — beforeAll Fixture Pattern

Use this pattern whenever a test **requires existing data** (e.g., a job must exist before the test can navigate to it).

### When to use

- Test body contains `test.skip(true, 'No scheduled jobs available to test')` or similar
- Test navigates to an existing resource (`schedulerPage.clickJob(0)`, etc.)
- Playwright status = **Blocked** in TestRail because prerequisite was missing

### Pattern

```typescript
import { createJob, deleteJob } from '../../../src/helpers/job-factory';

let jobId: string;

test.beforeAll(async () => {
  jobId = await createJob('SuiteName');   // creates via API, returns ID
});

test.afterAll(async () => {
  if (jobId) await deleteJob(jobId);     // cleanup after suite
});

test.describe('Feature — Page', { tag: ['@scheduled-jobs'] }, () => {
  test('should display config', async ({ jobConfigPage, page }) => {
    await jobConfigPage.gotoJob(jobId);  // navigate directly — no clickJob(0)
    await page.waitForLoadState('networkidle');
    // ... assertions
  });
});
```

### Rules

1. **Never use `test.skip(true, 'No ... available')` for prerequisite data** — create the data instead
2. **Navigate by ID, not by list position** — `gotoJob(jobId)` not `clickJob(0)` (fragile if list changes)
3. **One `createJob` per describe block** — not per test (expensive); tests share the fixture job
4. **Cancel, don't confirm** in tests that open delete/edit modals — preserve the fixture job for subsequent tests
5. **`afterAll` always cleans up** — even if `beforeAll` threw; use `if (jobId)` guard

### Available factories (`src/helpers/job-factory.ts`)

| Function | What it creates | Cleanup |
|---|---|---|
| `createJob(suffix)` | Scheduled job via `POST /v1/scheduled-jobs` | `deleteJob(jobId)` |

Add new factories to `job-factory.ts` when other resource types are needed (e.g., `createUser`, `createTeam`).

### Available navigation methods (already in page objects)

| Page object | Direct navigation method |
|---|---|
| `jobConfigPage` | `gotoJob(jobId)` |
| `recipientsPage` | `gotoAudienceTab(jobId)` |
| `historyLogsPage` | `gotoHistoryTab(jobId)` |

---

## 10. Error Handling in Tests

```typescript
// Known bug — skip until fixed
test.skip('flaky test', { annotation: { type: 'bug', description: 'AE-1234' } }, ...);

// Test expected to fail (known issue)
test('known failure', async ({ page }) => {
  test.fail(true, 'Blocked by AE-1234 — backend returns 500');
  // ... test code ...
});

// Environment-dependent
test('requires staging', async ({ page }) => {
  test.skip(process.env.BASE_URL?.includes('prod'), 'Not safe on production');
  // ... test code ...
});
```

---

## 10. Reporting

- Always generate HTML + JSON + JUnit reports
- On failure: screenshot + trace + video (configured in playwright.config.ts)
- Test names should be human-readable (describe the behavior, not the implementation)
