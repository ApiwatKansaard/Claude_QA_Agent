# Conflict Detection Reference

> Used by: automation-reviewer agent during `/auto:conflicts` command.

---

## Conflict Types

### Type 1: Selector Conflicts

**What:** Same logical element targeted by different selectors across sprint test files.

**How to detect:**
1. Parse all page objects → extract locator definitions
2. Group by page (file path or class name)
3. For each page, check if any locator property:
   - Exists in multiple versions with different selector strings
   - Was changed between sprints (git diff or file comparison)

**Severity:**
- 🔴 Same page object, same property, different selector → will break tests
- 🟡 Different page objects for same page → confusion, should consolidate

**Resolution:** One page object per page. Latest sprint updates the selectors. Run `/auto:update-selectors` to verify.

---

### Type 2: Test Data Collisions

**What:** Tests from different sprints create entities with the same name/ID.

**How to detect:**
1. Scan `test-data/*.json` for duplicate values
2. Scan inline test data in spec files (`const payload = {...}`)
3. Check for hardcoded entity names without unique identifiers

**Severity:**
- 🔴 Same name + both tests modify the entity → race condition
- 🟡 Same name + only one modifies → may cause confusion

**Resolution:** Always use sprint-prefixed + timestamped names:
```typescript
const name = `[auto-${sprint}] Job ${Date.now()}`;
```

---

### Type 3: Global State Mutations

**What:** Tests modify shared state (database, config) that other tests depend on.

**How to detect:**
1. Scan `afterAll`, `afterEach` for:
   - Bulk delete operations
   - Config/settings changes
   - User role/permission changes
2. Scan `beforeAll` for:
   - State assumptions (data must exist, must not exist)

**Severity:**
- 🔴 `afterAll` deletes ALL entities of a type → breaks other sprint's tests
- 🟡 `beforeAll` assumes specific state without creating it

**Resolution:**
- Cleanup only what you created (filter by sprint prefix)
- Setup always creates its own state (never assume)

---

### Type 4: Navigation Conflicts

**What:** Page URL or routing changed between sprints.

**How to detect:**
1. Compare `goto()` methods across page object versions
2. Check `playwright.config.ts` baseURL changes
3. Compare URL assertions in tests

**Severity:**
- 🔴 URL changed, old page object not updated → 404 errors
- 🟢 URL same but layout changed → may need selector update

**Resolution:** Update page objects for URL changes. Re-run `/auto:inspect`.

---

### Type 5: Fixture Conflicts

**What:** Auth fixtures or setup code creates incompatible state.

**How to detect:**
1. Check `auth.setup.ts` for changes between sprints
2. Check custom fixtures for state that's incompatible
3. Look for role/permission mismatches

**Severity:**
- 🔴 Auth flow changed (new login page, new fields) → all E2E tests fail
- 🟡 New role needed → add fixture, don't modify existing

**Resolution:** Auth setup should be backwards-compatible. Add new auth states, don't replace old ones.

---

### Type 6: Dependency Conflicts

**What:** Package versions or config changes break existing code.

**How to detect:**
1. Check `package.json` for version changes
2. Check `playwright.config.ts` for deprecated options
3. Check `tsconfig.json` for compiler option changes

**Severity:**
- 🔴 Major version bump breaks API → compilation errors
- 🟡 Minor version bump → test behavior change

**Resolution:** Keep dependency updates in separate PRs. Test before + after.

---

## Cross-Sprint Merge Strategy

When merging automation from multiple sprints:

```
1. Run /auto:conflicts to identify all issues
2. Fix all 🔴 Critical before merge
3. Document all 🟡 Warnings with fix timeline
4. Update selector maps to latest
5. Run full test suite: npm test
6. If passing → merge. If failing → fix before merge.
```

### Git Branch Strategy

```
main
├── auto/agentic-18.1/scheduled-jobs    (merged, archived)
├── auto/agentic-18.2/scheduled-jobs    (in progress)
│   ├── tests/e2e/scheduled-jobs/
│   └── src/pages/scheduled-jobs/
└── auto/agentic-18.2/chat-export       (in progress)
    ├── tests/e2e/chat-export/
    └── src/pages/chat-export/
```

Feature branches keep sprint work isolated until validated.
