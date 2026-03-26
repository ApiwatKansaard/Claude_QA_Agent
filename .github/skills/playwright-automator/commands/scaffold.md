# /auto:scaffold — Create Page Objects and Test Files

## Trigger
`/auto:scaffold [page-name] [feature-name]`

## Parameters
- `[page-name]` — Name of the page to scaffold (e.g., "dashboard", "create-wizard")
- `[feature-name]` — Feature group (e.g., "scheduled-jobs"). Used for folder organization.

## Pipeline

### Phase 1: Determine What to Create

1. Check if selector map exists: `selectors/{feature}-{page}.json` (in QA_Automation)
   - If yes → use selectors from the map
   - If no → use best-guess selectors (with TODO comments)

2. Check if page object exists: `src/pages/{feature}/{page}.page.ts` (in QA_Automation)
   - If yes → warn user and ask to overwrite or skip
   - If no → create new

3. Check existing test plan for the feature:
   - Find `*-test-plan.md` in sprint folder
   - Extract relevant sections for this page

### Phase 2: Generate Page Object

Create `src/pages/{feature}/{page-name}.page.ts` (in QA_Automation):

```typescript
import { BasePage } from '../base.page';
import type { Page, Locator } from '@playwright/test';

export class {PageName}Page extends BasePage {
  // --- Locators ---
  // (from selector map or best-guess with TODO markers)

  constructor(page: Page) {
    super(page);
    // Initialize locators
  }

  // --- Navigation ---
  async goto(): Promise<void> {
    await this.navigate('/{feature}/{page}');
  }

  // --- Actions ---
  // (generated from selector types: buttons→click, inputs→fill, etc.)

  // --- Assertions ---
  // (page-specific verification helpers)
}
```

### Phase 3: Generate Test File Skeleton

Create `tests/e2e/{feature}/{page-name}.spec.ts` (in QA_Automation):

```typescript
import { test, expect } from '../../../src/fixtures/test-fixtures';
import { {PageName}Page } from '../../../src/pages/{feature}/{page-name}.page';

test.describe('{Feature} — {PageName}', { tag: ['@{feature}'] }, () => {
  let page: {PageName}Page;

  test.beforeEach(async ({ page: p }) => {
    page = new {PageName}Page(p);
    await page.goto();
  });

  // TODO: Add test cases from /auto:generate or manually
});
```

### Phase 4: Update Fixtures

If this is a new page object, register it in the fixtures file:
- Add import
- Add to the TestFixtures type
- Add fixture initialization

### Phase 5: Output

```markdown
## 🏗️ Scaffold Complete: {feature}/{page-name}

Created:
- `src/pages/{feature}/{page-name}.page.ts` — Page Object (X locators, Y actions)
- `tests/e2e/{feature}/{page-name}.spec.ts` — Test file skeleton
- Updated `src/fixtures/test-fixtures.ts` — registered new fixture

Next:
1. Run `/auto:inspect [URL]` to get real selectors (if not done yet)
2. Run `/auto:generate` to fill in test cases
```
