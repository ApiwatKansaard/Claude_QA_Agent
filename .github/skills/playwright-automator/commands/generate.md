# /auto:generate — Generate Playwright Tests from Test Cases

## Trigger
`/auto:generate [sprint-folder] [section-filter] [target-repo]`

## Parameters
- `[sprint-folder]` — Sprint folder path (e.g., `agentic-18.2`). Auto-detected if omitted.
- `[section-filter]` — Optional section name to filter (e.g., "Dashboard", "API Endpoints")
- `[target-repo]` — Optional target repo path. Default: QA_Automation workspace root.

## Pipeline

### Phase 1: Discovery

1. **Detect sprint folder** — use standard algorithm:
   - Scan workspace root for `agentic-*/` or `sprint-*/` (not in `archive/`)
   - One found → use it. Multiple → highest version. None → ask user.

2. **Read test plan** — `{sprint-folder}/*-test-plan.md`
   - Extract: feature name, scope, assumptions, surfaces, test strategy
   - This provides the **context** for understanding what each test case does

3. **Read test cases** — `{sprint-folder}/*-testcases.csv`
   - Parse CSV with these columns:
     ```
     Section, Role, Channel, Title, Test Data, Preconditions, Steps, Expected Result,
     Platform, TestMethod, Type, P, References, Release version, QA Responsibility, TestRailID
     ```
   - Col 16 (`TestRailID`) is optional — present only after `/qa:import-testrail` has run
   - If `TestRailID` is empty for a row, generate the test but leave annotation blank with a TODO comment
   - If `section-filter` provided, only include matching sections

4. **Ask user about target repo:**
   ```
   📁 จะเอา test ไว้ที่ไหน?
   1. QA_Automation/ (ใน workspace นี้) — default
   2. ระบุ path ของ repo อื่น
   3. สร้าง repo ใหม่
   
   Branch:
   - ใช้ branch ปัจจุบัน
   - สร้าง branch ใหม่: auto/{sprint}/{feature}
   ```

### Phase 2: Analysis

1. **Group test cases** by `Section` column:
   - Each unique section → one `test.describe()` block
   - Nested sections (e.g., `Agentic > Scheduled Jobs > Dashboard`) → folder structure

2. **Classify automatable cases:**
   - `TestMethod=Manual` + `Platform=Web` → E2E test (automatable)
   - `TestMethod=Manual` + `Channel=API` → API test (automatable)
   - `TestMethod=Manual` + `Platform=Infrastructure` → Skip (mark as not-automatable)
   - Cases requiring physical devices, third-party services → Skip with note

3. **Check existing automation:**
   - Read `tests/` in QA_Automation for existing test files
   - Match existing tests by section + title
   - Skip already-automated cases (show in summary)

4. **Check existing selectors:**
   - Read `selectors/` in QA_Automation for known selector maps
   - Reuse existing selectors in generated code
   - Flag pages with no selector map → suggest `/auto:inspect`

### Phase 3: Code Generation

For each section group, generate:

**A. Page Object (if not exists):**
```typescript
import { BasePage } from '../base.page';
import type { Page, Locator } from '@playwright/test';

export class DashboardPage extends BasePage {
  // Locators from selectors/ or best-guess from CSV steps
  readonly jobList: Locator;
  readonly createButton: Locator;
  readonly statusFilter: Locator;

  constructor(page: Page) {
    super(page);
    this.jobList = page.getByTestId('job-list');       // Update after /auto:inspect
    this.createButton = page.getByRole('button', { name: 'Create' });
    this.statusFilter = page.getByRole('combobox', { name: 'Status' });
  }

  async goto(): Promise<void> {
    await this.navigate('/scheduled-jobs');
  }

  async clickJob(index: number): Promise<void> {
    await this.jobList.locator('tr').nth(index).click();
  }

  async filterByStatus(status: string): Promise<void> {
    await this.statusFilter.selectOption(status);
  }
}
```

**B. Test file:**

Map `TestRailID` (col 16) → Playwright `annotation` on every test. Use `annotation` (not tag) so C-IDs are queryable at runtime without polluting the test name or grep filters.

```typescript
import { test, expect } from '../../src/fixtures/test-fixtures';
import { DashboardPage } from '../../src/pages/scheduled-jobs/dashboard.page';

test.describe('Scheduled Jobs — Dashboard', { tag: ['@smoke', '@scheduled-jobs'] }, () => {
  let dashboard: DashboardPage;

  test.beforeEach(async ({ page }) => {
    dashboard = new DashboardPage(page);
    await dashboard.goto();
  });

  // TestRailID present → add annotation
  test('should display job list on Dashboard page',
    {
      annotation: { type: 'TestRail', description: 'C1548642' },
      tag: ['@smoke', '@P1'],
    },
    async ({ page }) => {
      // From CSV: Steps 1-3, Expected Results 1-3
      await expect(dashboard.jobList).toBeVisible();
      const headers = page.locator('th');
      await expect(headers).toContainText(['name', 'status', 'schedule']);
    }
  );

  // TestRailID missing → placeholder annotation with TODO
  test('should show empty state when no jobs exist',
    {
      annotation: { type: 'TestRail', description: '' }, // TODO: run /qa:import-testrail to get C-ID
      tag: ['@regression', '@P2'],
    },
    async ({ page }) => {
      // ...
    }
  );
});
```

**Rules for annotation:**
- If `TestRailID` column exists and has value → `annotation: { type: 'TestRail', description: 'C{id}' }`
- If `TestRailID` is empty → `annotation: { type: 'TestRail', description: '' }` + comment `// TODO: run /qa:import-testrail to populate`
- **Never** use tag `@C1548642` — tags pollute grep filters and test names
- The annotation is read by `/auto:send-results` to map test outcome → TestRail case ID

**C. Update fixtures** if new page objects were created.

**D. Generate test data** JSON if the CSV has `Test Data` entries.

### Phase 4: Validation

1. Run `npx tsc --noEmit` — check TypeScript compilation
2. Verify all imports resolve
3. Check for selector conflicts with existing tests
4. Check naming conventions compliance

### Phase 5: Output Summary

```markdown
## ✅ Generation Complete

**Sprint:** agentic-18.2
**Feature:** Scheduled Jobs
**Source:** 168 test cases from CSV

### Generated Files
| File | Type | Tests | Tags |
|------|------|-------|------|
| tests/e2e/scheduled-jobs/dashboard.spec.ts | E2E | 7 | @smoke(2) @regression(4) @sanity(1) |
| tests/e2e/scheduled-jobs/create-job.spec.ts | E2E | 12 | @smoke(5) @regression(6) @sanity(1) |
| tests/api/scheduled-jobs/crud.api.spec.ts | API | 15 | @smoke(8) @regression(7) |
| src/pages/scheduled-jobs/dashboard.page.ts | POM | — | — |
| ... | | | |

### Coverage
- Automated: 120/168 (71.4%)
- Not automatable: 33 (infrastructure, race conditions)
- Already existed: 15
- Needs /auto:inspect: 3 pages missing selector maps

### Next Steps
1. Run `/auto:inspect [URL]` for pages missing selectors
2. Run `/auto:run @smoke` to verify smoke suite
3. Run `/auto:review` to validate code quality
```
