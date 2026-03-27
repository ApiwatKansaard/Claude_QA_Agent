# /auto:conflicts — Cross-Sprint Conflict Detection

## Trigger
`/auto:conflicts [sprint-folder]`

## Parameters
- `[sprint-folder]` — New sprint's folder to check against existing tests. Auto-detected if omitted.

## Purpose

When automation tests from **multiple sprints** coexist, conflicts can arise.
This command detects them before they cause mysterious test failures.

## Pipeline

### Phase 1: Inventory

1. Collect all existing test files: `tests/**/*.spec.ts` (in QA_Automation)
2. Collect all page objects: `src/pages/**/*.page.ts` (in QA_Automation)
3. Collect all selector maps: `selectors/*.json` (in QA_Automation)
4. Collect all test data files: `test-data/*.json` (in QA_Automation)
5. If `sprint-folder` given, identify which files are NEW (from this sprint)

### Phase 2: Conflict Analysis

Check for 6 types of conflicts:

#### 1. Selector Conflicts
Same page, different expected selectors:
```
Sprint 18.1: dashboard.page.ts → createButton = page.locator('#create-btn')
Sprint 18.2: dashboard.page.ts → createButton = page.getByTestId('new-job-btn')
```
**Detection:** Scan page objects for same selectors pointing to different elements,
or different selectors for the same logical element.

#### 2. Test Data Collisions
Tests creating/using the same entities:
```
Sprint 18.1: creates job named "Test Job Morning Brief"
Sprint 18.2: creates job named "Test Job Morning Brief" (same name, conflict!)
```
**Detection:** Scan test-data/ JSON files and inline test data for duplicates.

#### 3. Global State Mutations
Tests modifying shared database/config:
```
Sprint 18.1: deletes all jobs in afterAll()
Sprint 18.2: expects jobs to exist in beforeEach()
```
**Detection:** Scan for `afterAll`, `afterEach` with destructive operations.

#### 4. Navigation State Conflicts
Tests expecting different page states:
```
Sprint 18.1: expects Dashboard at /scheduled-jobs
Sprint 18.2: Dashboard moved to /jobs/scheduled
```
**Detection:** Compare URLs in page objects across sprints.

#### 5. Fixture Conflicts
Incompatible setup/teardown:
```
Sprint 18.1: auth fixture logs in as admin
Sprint 18.2: new test needs viewer role (different fixture needed)
```
**Detection:** Check fixture definitions for incompatible state.

#### 6. Import/Dependency Conflicts
Package version conflicts, import path changes:
```
Sprint 18.1: uses @playwright/test 1.50
Sprint 18.2: needs @playwright/test 1.52 for new API
```
**Detection:** Check package.json and import statements.

### Phase 3: Output

```markdown
## ⚡ Conflict Report — agentic-18.2 vs Existing

### Summary
| Type | 🔴 Critical | 🟡 Warning | 🟢 Info |
|------|------------|-----------|--------|
| Selector | 1 | 2 | 0 |
| Test Data | 0 | 1 | 0 |
| Global State | 1 | 0 | 0 |
| Navigation | 0 | 0 | 1 |
| Fixtures | 0 | 1 | 0 |
| Dependencies | 0 | 0 | 0 |

### 🔴 Critical

**1. Selector Conflict — Dashboard Create Button**
- Old (18.1): `page.locator('#create-btn')` in dashboard.page.ts:15
- New (18.2): `page.getByTestId('new-job-btn')` in dashboard.page.ts:15
- **Fix:** Update to use data-testid consistently. Re-run `/auto:inspect`.

**2. Global State — afterAll Cleanup**
- File: tests/e2e/agentic/scheduled-jobs/crud.spec.ts:89
- `afterAll` deletes all jobs → breaks other sprint's tests
- **Fix:** Delete only test-created jobs (use unique prefix: `[auto-18.2]`)

### 🟡 Warnings
...

### Recommendations
1. Use sprint-prefixed test data names: `[auto-18.2] Morning Brief Test`
2. Never delete data you didn't create in afterAll/afterEach
3. Run `/auto:update-selectors` after each UI sprint
4. Keep page objects as single source of truth — don't duplicate
```

## Sprint Isolation Best Practices

To prevent conflicts across sprints:

1. **Test Data Naming:** Prefix with sprint identifier
   ```typescript
   const jobName = `[auto-${process.env.SPRINT || '18.2'}] Test Job ${Date.now()}`;
   ```

2. **Cleanup Scope:** Only clean up what you created
   ```typescript
   test.afterAll(async ({ request }) => {
     // Delete only our test data, not all data
     const jobs = await api.get('/jobs?prefix=[auto-18.2]');
     for (const job of jobs) await api.delete(`/jobs/${job.id}`);
   });
   ```

3. **Selector Evolution:** Use selector maps as source of truth
   - One selector file per page per sprint → compare before merging
   - Page objects always reference the latest selectors

4. **Feature Branches:** When targeting external repos
   - Branch per sprint: `auto/agentic-18.2/scheduled-jobs`
   - Merge after validation with `/auto:conflicts`
