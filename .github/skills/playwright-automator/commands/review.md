# /auto:review — Automation Code Review

## Trigger
`/auto:review [file or folder]`

## Parameters
- `[file or folder]` — Specific file/folder to review. Default: entire QA_Automation project.

## Pipeline

### Phase 1: Scope

1. If file specified → review that file only
2. If folder → review all `.ts` files in it
3. If omitted → review all files under `src/` and `tests/` in QA_Automation

### Phase 2: Read Code

Read all files in scope. For each file, apply the **8-point review checklist**.

### Phase 3: Review Checklist

| # | Check | Severity | Description |
|---|-------|----------|-------------|
| 1 | **POM Compliance** | 🔴 Critical | No selectors (locator/getBy*) in test files. All via page objects. |
| 2 | **Test Independence** | 🔴 Critical | No test depends on another test's state. Each can run in isolation. |
| 3 | **Proper Tagging** | 🟡 Warning | Tags match CSV Type + Priority. Feature tag present. |
| 4 | **Assertion Quality** | 🟡 Warning | Meaningful expects — not just `.toBeVisible()`. Check text, count, state. |
| 5 | **Wait Strategy** | 🔴 Critical | No `page.waitForTimeout()` / arbitrary sleeps. Use explicit waits. |
| 6 | **Error Handling** | 🟢 Info | Proper `test.fail()` for known issues, `test.skip()` for env-dependent. |
| 7 | **Data Isolation** | 🟡 Warning | No shared mutable state. Tests create own data or use fixtures. |
| 8 | **Selector Stability** | 🟡 Warning | No fragile CSS (`.class-xyz123`). Prefer testid > role > label > text. |

### Additional Checks

- **Import consistency** — fixtures vs @playwright/test (use fixtures!)
- **Naming conventions** — files, test names, page objects
- **Type safety** — proper TypeScript types, no `any`
- **Code duplication** — repeated selectors or logic that should be page object methods
- **Test data exposure** — no credentials, tokens, or PII in test files
- **Unused imports** — dead code cleanup

### Phase 4: Output

```markdown
## 📝 Code Review Report

**Scope:** tests/e2e/scheduled-jobs/ (QA_Automation)
**Files reviewed:** 5
**Time:** 2026-03-25

### Summary
| Severity | Count |
|----------|-------|
| 🔴 Critical | 2 |
| 🟡 Warning | 5 |
| 🟢 Info | 3 |

### 🔴 Critical Issues

**1. Selector in test file** — dashboard.spec.ts:25
```typescript
// ❌ Current
await page.locator('.job-row').first().click();

// ✅ Fix: Move to DashboardPage
await dashboard.clickFirstJob();
```

**2. Arbitrary wait** — create-job.spec.ts:48
```typescript
// ❌ Current
await page.waitForTimeout(3000);

// ✅ Fix: Wait for specific element
await page.waitForSelector('[data-testid="success-toast"]');
```

### 🟡 Warnings
...

### 🟢 Info
...

### ✅ Passing Checks
- [x] Test independence
- [x] Data isolation
- [x] No credential exposure
```
