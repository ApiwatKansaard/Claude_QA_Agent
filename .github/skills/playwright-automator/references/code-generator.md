# Test Code Generator Reference

> Used by: playwright-automator agent during `/auto:generate` command.
> Contains detailed mapping rules from TestRail CSV → Playwright code.

---

## CSV Column → Code Mapping

### Section → test.describe()

```
CSV: "Agentic > Scheduled Jobs > Dashboard"
     ↓
test.describe('Scheduled Jobs — Dashboard', ...)
     ↓
File: tests/e2e/agentic/scheduled-jobs/dashboard.spec.ts
Page: src/pages/agentic/scheduled-jobs/dashboard.page.ts
```

Nested sections map to folder structure:
- `Agentic > Scheduled Jobs > Dashboard` → `scheduled-jobs/dashboard.spec.ts`
- `Agentic > Scheduled Jobs > Create Job` → `scheduled-jobs/create-job.spec.ts`
- `Agentic > Scheduled Jobs > API Endpoints` → API: `scheduled-jobs/crud.api.spec.ts`

### Title → test()

Transform CSV title to Playwright test name:
1. Remove "Check " prefix (TestRail convention)
2. Convert to "should {expected behavior}" format
3. Append tags

```
CSV: "Check scheduled jobs list should be displayed on Dashboard page"
     ↓
test('should display scheduled jobs list on Dashboard page @smoke @P1', ...)
```

### Steps → Test Body (Actions)

Parse numbered steps and map to Playwright actions:

| Step Pattern | Playwright Action |
|---|---|
| "Navigate to {page}" | `await page.goto('/path')` or `await pageObject.goto()` |
| "Click {element}" | `await pageObject.element.click()` |
| "Enter {value} in {field}" | `await pageObject.field.fill('value')` |
| "Select {option} from {dropdown}" | `await pageObject.dropdown.selectOption('option')` |
| "Observe {area}" | (no action — just assertion in Expected) |
| "Scroll to {position}" | `await page.mouse.wheel(0, 500)` |
| "Wait for {thing}" | `await page.waitForSelector('...')` |

### Expected Result → Assertions

Parse expected results and map to Playwright assertions:

| Expected Pattern | Playwright Assertion |
|---|---|
| "{element} is displayed/visible" | `await expect(locator).toBeVisible()` |
| "{element} shows {text}" | `await expect(locator).toContainText('text')` |
| "Page navigates to {url}" | `await expect(page).toHaveURL(/pattern/)` |
| "Toast/notification with {message}" | `await expect(toast).toContainText('message')` |
| "{field} shows error {message}" | `await expect(errorMsg).toContainText('message')` |
| "{list} contains {N} items" | `await expect(items).toHaveCount(N)` |
| "User is redirected to {page}" | `await expect(page).toHaveURL(/page/)` |
| "Data is saved/persisted" | API assertion or page reload + check |
| "Button is disabled" | `await expect(button).toBeDisabled()` |

### Preconditions → beforeEach / Test Setup

| Precondition Pattern | Implementation |
|---|---|
| "User is logged in" | Auth setup (handled by auth.setup.ts) |
| "User is logged in as admin" | Auth setup with admin credentials |
| "{N} jobs exist" | Create via API in `beforeEach` or `beforeAll` |
| "No jobs exist" | Delete test data before test |
| "Backend is unavailable" | Network intercept: `page.route()` |
| "{Feature} is enabled" | API call or config setup |

### Test Data → Parameterized Data

| Test Data Pattern | Implementation |
|---|---|
| Specific values listed | JSON in `test-data/{feature}.json` |
| "Valid/invalid {entity}" | Named objects in JSON: `validJob`, `invalidJob` |
| "Cron expression: {expr}" | Inline const or parameterized |
| "{N}+ items" | Loop to create N items via API |

---

## Template: E2E Test File

```typescript
import { test, expect } from '../../src/fixtures/test-fixtures';
import { {PageName}Page } from '../../src/pages/{feature}/{page}.page';

/**
 * {Feature} — {Page} Tests
 * Generated from: {sprint-folder}/{feature}-testcases.csv
 * Section: {section}
 * Total cases: {count}
 */
test.describe('{Feature} — {Page}', {
  tag: ['@{feature-tag}'],
}, () => {
  let {pageName}: {PageName}Page;

  test.beforeEach(async ({ page }) => {
    {pageName} = new {PageName}Page(page);
    await {pageName}.goto();
  });

  // --- Smoke Tests ---

  test('should {behavior} @smoke @P1', async ({ page }) => {
    // Arrange
    // Act
    // Assert
  });

  // --- Regression Tests ---

  test('should {behavior} @regression @P2', async ({ page }) => {
    // Arrange
    // Act
    // Assert
  });
});
```

## Template: API Test File

```typescript
import { test, expect } from '@playwright/test';
import { ApiHelper } from '../../src/helpers/api.helper';

/**
 * {Feature} — API Tests
 * Generated from: {sprint-folder}/{feature}-testcases.csv
 * Section: {section}
 * Total cases: {count}
 */
test.describe('{Feature} — API', {
  tag: ['@api', '@{feature-tag}'],
}, () => {
  const baseURL = process.env.API_BASE_URL || '';

  test('should {behavior} @smoke @P1', async ({ request }) => {
    const api = new ApiHelper(request, baseURL);
    // Arrange + Act
    const response = await api.getRaw('/api/v1/{resource}');
    // Assert
    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body.data).toBeDefined();
  });
});
```

## Template: Page Object

```typescript
import { BasePage } from '../base.page';
import type { Page, Locator } from '@playwright/test';

export class {PageName}Page extends BasePage {
  // --- Locators ---
  readonly {element1}: Locator;
  readonly {element2}: Locator;

  constructor(page: Page) {
    super(page);
    this.{element1} = page.getByTestId('{testid}');     // Priority 1
    this.{element2} = page.getByRole('{role}', { name: '{name}' }); // Priority 2
  }

  // --- Navigation ---
  async goto(): Promise<void> {
    await this.navigate('/{feature}/{page}');
  }

  // --- Actions ---
  async click{Element}(): Promise<void> {
    await this.{element1}.click();
  }

  async fill{Field}(value: string): Promise<void> {
    await this.{element2}.fill(value);
  }
}
```
