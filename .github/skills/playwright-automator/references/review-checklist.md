# Review Checklist Reference

> Used by: automation-reviewer agent during `/auto:review` command.

---

## 8-Point Review Checklist

### 1. POM Compliance (🔴 Critical if violated)

**Rule:** Zero selectors in test files. All element interactions via page objects.

**Check:**
- Scan `tests/**/*.spec.ts` for:
  - `page.locator(` — should not appear (except for dynamic one-off cases)
  - `page.getByTestId(` — should not appear in tests
  - `page.getByRole(` — should not appear in tests
  - `page.getByText(` — should not appear in tests
  - `page.getByLabel(` — should not appear in tests
- All should be `dashboard.clickX()` or `dashboard.element.click()`

**Allowed exceptions:**
- Dynamic locators that depend on test data (e.g., `page.getByText(jobName)`)
- One-time assertions on page-level state (e.g., URL check)

---

### 2. Test Independence (🔴 Critical if violated)

**Rule:** Each test runs in isolation. No shared mutable state.

**Check:**
- No `let` variables at describe scope used across tests
- No test references results from a previous test
- `beforeEach` only does navigation/setup, not data creation for specific tests
- `afterAll` cleanup is scoped (deletes only test-created data)
- No `test.describe.serial()` unless absolutely necessary

---

### 3. Proper Tagging (🟡 Warning if missing)

**Rule:** Tags match TestRail CSV metadata.

**Check:**
- Every `test.describe()` has `tag` array with feature tag
- Every `test()` has at least: type tag + priority tag
- Valid type tags: `@smoke`, `@sanity`, `@regression`
- Valid priority tags: `@P1`, `@P2`
- Feature tags match CSV section: `@scheduled-jobs`, `@dashboard`, etc.
- No orphan tests without tags

---

### 4. Assertion Quality (🟡 Warning if weak)

**Rule:** Assertions verify meaningful state, not just visibility.

**Check:**
- Avoid: `await expect(element).toBeVisible()` as the only assertion
- Prefer: text content, count, URL, attribute values
- At least 2 assertions per test (existence + correctness)
- API tests: check status code + response body structure
- No assertions on implementation details (class names, internal IDs)

**Good vs Bad:**
```typescript
// ❌ Weak
await expect(page.locator('.toast')).toBeVisible();

// ✅ Strong
const toast = page.locator('[role="alert"]');
await expect(toast).toBeVisible();
await expect(toast).toContainText('Job created successfully');
```

---

### 5. Wait Strategy (🔴 Critical if violated)

**Rule:** No arbitrary sleeps. Use explicit waits.

**Check:**
- `page.waitForTimeout(` — NEVER allowed
- `setTimeout(` — in test files — NEVER allowed
- Every navigation → followed by `waitForLoadState` or element wait
- Every form submit → followed by response wait or element appearance
- Every animation → use `expect().toBeVisible()` (has auto-retry)

---

### 6. Error Handling (🟢 Info)

**Rule:** Known issues properly annotated.

**Check:**
- `test.skip()` — has reason string and bug reference
- `test.fail()` — has condition and description
- `test.fixme()` — only for incomplete tests
- No empty catch blocks
- No silent error swallowing

---

### 7. Data Isolation (🟡 Warning if violated)

**Rule:** Tests don't corrupt each other's data.

**Check:**
- Test data uses unique identifiers (timestamps, random strings)
- Sprint prefix on created entities: `[auto-18.2] Test Job`
- `afterEach/afterAll` cleanup is scoped (not `DELETE * FROM jobs`)
- No hardcoded entity IDs that might conflict
- JSON test data files have unique values per test

---

### 8. Selector Stability (🟡 Warning if fragile)

**Rule:** Selectors survive DOM restructuring.

**Check:**
- No generated class names (`.css-abc123`, `.sc-dlfnuX`)
- No deep CSS chains (`.wrapper > div > .inner > button`)
- No index-only selectors (`nth-child(3)` without attribute context)
- `data-testid` or ARIA role used when available
- Selectors match entries in `selectors/*.json`

---

## Review Output Format

For each issue found:

```markdown
**{severity} {check_name}** — {file}:{line}
```typescript
// ❌ Current
{problematic code}

// ✅ Suggested fix
{corrected code}
```
Reason: {why this is a problem}
```

## Severity Escalation

- 1 or more 🔴 → **BLOCK** — must fix before merging
- 3 or more 🟡 → **WARN** — should fix, may merge with plan
- Only 🟢 → **PASS** — good to merge
