# /auto:health — Test Suite Health Check

## Trigger
`/auto:health`

## Parameters
None — runs a full analysis of the entire test suite.

## Pipeline

### Phase 1: Inventory

Scan QA_Automation project root and collect:
- All test files (`.spec.ts`)
- All page objects (`.page.ts`)
- All fixtures and helpers
- All selector maps (`.json`)
- All test data files
- `package.json` dependencies
- `playwright.config.ts` settings

### Phase 2: Checks

#### A. Coverage Analysis
1. Read all CSV test cases from active sprint folder(s)
2. Read existing test-mapping.json (or generate via `/auto:map`)
3. Calculate:
   - Total cases in CSV
   - Automated (matching spec files)
   - Pending (automatable, no test yet)
   - Not automatable (infrastructure, manual-only)
4. Coverage % by section, priority, and type

#### B. Flakiness Patterns
Scan all test files for known flaky patterns:
- `page.waitForTimeout()` — arbitrary sleeps
- Missing `await` on async operations
- Shared mutable state between tests
- Network-dependent assertions without retry
- Time-sensitive assertions (dates, timestamps)
- Browser-specific code without project guards
- `test.only()` left in code

#### C. Dead Code
- Page objects with no importing test files
- Helper functions never called
- Unused fixture declarations
- Commented-out test blocks
- Selector maps with no matching page object

#### D. Outdated Selectors
Cross-check each selector map's `inspectedAt` date:
- Over 2 weeks old → flag for re-inspection
- Page objects using selectors not in any map → flag
- Multiple page objects using the same element differently → flag

#### E. Performance
- Tests with explicit timeouts > 30s
- Large `beforeEach` blocks that could be shared
- Tests that navigate away from their page (unnecessary page loads)
- Missing `fullyParallel` or too many serial tests

#### F. Dependencies
- `package.json` audit — outdated packages
- `playwright.config.ts` — deprecated options
- Missing `@playwright/test` version alignment
- Circular imports between page objects

#### G. Code Quality
- TypeScript `any` usage
- Missing return types on page object methods
- Inconsistent naming patterns
- Long test files (>200 lines → should split)

### Phase 3: Output

```markdown
## 🏥 Test Suite Health Report

**Date:** 2026-03-25
**Test files:** 15
**Page objects:** 8
**Total tests:** 120

### Health Score: 78/100 🟡

| Category | Score | Issues |
|----------|-------|--------|
| Coverage | 85/100 🟢 | 15 pending cases |
| Flakiness | 70/100 🟡 | 3 arbitrary waits, 1 shared state |
| Dead Code | 90/100 🟢 | 1 unused page object |
| Selectors | 65/100 🟡 | 2 maps outdated, 3 missing testid |
| Performance | 80/100 🟢 | 2 slow tests (>30s) |
| Dependencies | 95/100 🟢 | 1 minor update available |
| Code Quality | 75/100 🟡 | 4 `any` types, 2 long files |

### 🔴 Actions Required
1. Remove `waitForTimeout(3000)` in create-job.spec.ts:48
2. Fix shared state in crud.spec.ts — tests share `createdJobId`
3. Re-inspect selectors for dashboard page (last: 14 days ago)

### 🟡 Recommended
4. Add `data-testid` to 3 elements using CSS selectors
5. Split history-logs.spec.ts (245 lines) into two files
6. Remove unused `old-widget.page.ts`

### 🟢 Nice to Have
7. Update @playwright/test to 1.52 (currently 1.50)
8. Add return types to 4 page object methods

### Trend (if previous reports exist)
| Sprint | Score | Tests | Coverage |
|--------|-------|-------|----------|
| 18.1 | 72 | 85 | 68% |
| 18.2 | 78 | 120 | 71% |
| Δ | +6 | +35 | +3% |
```
