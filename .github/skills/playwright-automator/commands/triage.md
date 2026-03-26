# /auto:triage — Analyze Failed Tests and Classify Root Cause

## Trigger
- Slash command: `/auto:triage`
- Natural language: "analyze test results", "why did this test fail", "triage the failures"

## Prerequisites
- A Playwright test run has been executed (results exist)
- QA_Automation repo is accessible

## Pipeline

### Phase 1: Collect Evidence

1. **Find the latest test results** — read in priority order:
   ```
   QA_Automation/reports/{env}/results.json    ← structured JSON (preferred)
   QA_Automation/reports/{env}/junit.xml       ← JUnit XML
   QA_Automation/test-results/                 ← failure artifacts (screenshots, traces)
   ```

2. **Parse each failure** — extract:
   - Test name and file path (with line number)
   - Error message and type (assertion, timeout, element not found, strict mode)
   - Stack trace (identify failing line in test code)
   - Screenshot path (if exists in test-results/)
   - Test tags (@smoke, @P1, etc.)

3. **Read the failing test code** — open the spec file at the failing line:
   - Understand what the test expects
   - Identify the selector/locator being used
   - Identify the assertion (toBe, toBeVisible, toContainText, etc.)

4. **View failure screenshots** — use `view_image` on each screenshot:
   - What does the page actually look like?
   - Is the element visible in the screenshot?
   - Is there an error state visible?

### Phase 2: Inspect Live Application

For each failed test, **reproduce the conditions live**:

#### UI Tests (e2e project)
1. **Fetch the actual page** — use `fetch_webpage` on the target URL:
   ```
   URL from: base URL + navigation path in the test
   e.g., https://ekoai-console.staging.ekoapp.com/ai-task-scheduler
   ```
2. **Check element existence** — search for the selector in the fetched HTML:
   - Does the element exist?
   - Has the text changed?
   - Has the class/role/testid changed?
3. **If the page is a SPA** — the fetch may return only the shell. In that case:
   - Rely primarily on the **failure screenshot** (actual rendered state)
   - Use the **inspect-dom.ts script** if deeper DOM analysis is needed:
     ```
     cd QA_Automation && npx ts-node scripts/inspect-dom.ts <URL> <page-name>
     ```
4. **Compare screenshot vs test expectation**:
   - Screenshot shows element → selector/locator is wrong (AUTOMATION_BUG)
   - Screenshot shows error page → app is broken (PRODUCT_BUG or ENVIRONMENT_ISSUE)
   - Screenshot shows different content → spec changed (PRODUCT_BUG)

#### API Tests (api project)
1. **Replay the API call** — use terminal to curl the endpoint:
   ```bash
   # Get auth token from stored auth state
   TOKEN=$(python3 -c "import json; d=json.load(open('playwright/.auth/staging-user.json')); print([c['value'] for c in d['cookies'] if 'idToken' in c['name']][0])")
   
   # Replay the API call
   curl -s -w "\nHTTP %{http_code}" \
     -H "Authorization: Bearer $TOKEN" \
     "https://ekoai.staging.ekoapp.com/v1/scheduled-jobs"
   ```
2. **Compare response vs test assertion**:
   - Status code matches but body is different → check assertion (AUTOMATION_BUG)
   - Status code is unexpected (500, 502) → PRODUCT_BUG or ENVIRONMENT_ISSUE
   - Auth rejected (401, 403) → ENVIRONMENT_ISSUE (token expired)

### Phase 3: Root Cause Classification

For each failure, classify into exactly ONE category:

| Category | Criteria | Confidence Threshold |
|---|---|---|
| `PRODUCT_BUG` | App behavior differs from spec; live inspection confirms it's not a test issue | Verified by live inspection |
| `AUTOMATION_BUG` | Test code has wrong selector, wrong assertion, wrong assumption about behavior | Verified by screenshot+DOM comparison |
| `ENVIRONMENT_ISSUE` | Transient failure; site down/slow; auth expired; works on retry | Confirmed by retry or health check |

**Classification decision tree:**
```
Failure?
├─ Element not found?
│  ├─ Screenshot shows the element → AUTOMATION_BUG (selector wrong)
│  ├─ Screenshot shows error page → PRODUCT_BUG or ENVIRONMENT_ISSUE
│  └─ Screenshot shows different page → AUTOMATION_BUG (navigation wrong)
│
├─ Assertion failed (wrong value)?
│  ├─ Live value matches test expectation → ENVIRONMENT_ISSUE (data changed between test and assertion)  
│  ├─ Live value differs from both → PRODUCT_BUG (app returns wrong data)
│  └─ LiveURL shows correct value but test expects wrong value → AUTOMATION_BUG (test logic wrong)
│
├─ Strict mode violation (multiple elements)?
│  └─ Always AUTOMATION_BUG — locator is too broad
│
├─ Timeout (networkidle, navigation)?
│  ├─ Site responds to curl/health check → likely ENVIRONMENT_ISSUE (transient slow)
│  └─ Site consistently unreachable → ENVIRONMENT_ISSUE (outage)
│
└─ Other error?
   └─ Read stack trace, classify manually
```

### Phase 4: Output

Generate a **Triage Report** with this structure per failed test:

```markdown
## [TEST_ID]: [Test Name]
**File:** `tests/e2e/scheduled-jobs/scheduler-list.spec.ts:68`
**Tags:** @scheduled-jobs @sanity @P2
**Error:** [one-line error summary]
**Classification:** 🐛 PRODUCT_BUG | 🔧 AUTOMATION_BUG | ⚡ ENVIRONMENT_ISSUE

### Evidence
- **Screenshot:** [view_image result or link]
- **Error message:** [exact error]
- **Live inspection:** [what the URL/API shows now]

### Analysis
[Detailed explanation: what happened, why, and how you know]

### Action
[Depends on classification — see below]
```

#### For PRODUCT_BUG:
```markdown
### Bug Report Data
- **Summary:** [concise bug title]
- **Steps to Reproduce:**
  1. Navigate to [URL]
  2. [action from test steps]
  3. Observe: [actual behavior]
- **Expected:** [from test assertion / spec]
- **Actual:** [from live inspection]
- **Severity:** [Critical/Major/Minor — based on test priority tag]
- **Screenshot:** [attached]
- **Environment:** staging / [browser]
- **Suggested Jira fields:**
  - Project: EP
  - Issue Type: Bug
  - Priority: [P1→Highest, P2→High]
  - Labels: automation-detected
```
→ Output is ready for `/qa:bug-report` command to create the Jira ticket.

#### For AUTOMATION_BUG:
```markdown
### Fix Instructions
- **Root cause:** [e.g., "Selector 'text=Trigger' doesn't exist; actual tab name is 'Job Configuration'"]
- **Failing code:** [exact lines from spec file]
- **Fix:**
  ```typescript
  // Before (broken)
  await expect(page.locator('text=Trigger')).toBeVisible();
  
  // After (fixed)
  await expect(page.getByRole('button', { name: 'Job Configuration' })).toBeVisible();
  ```
- **Confidence:** HIGH / MEDIUM
- **Auto-fix:** [YES if confidence=HIGH — apply the fix automatically]
```
→ If confidence is HIGH, apply the fix directly to the test file.
→ If confidence is MEDIUM, present the fix for user approval.

#### For ENVIRONMENT_ISSUE:
```markdown
### Environment Issue
- **Type:** [transient slow / site down / auth expired / data inconsistency]
- **Recommendation:** [retry / re-authenticate / skip with annotation]
- **No action needed on test code or product**
```

### Phase 5: Auto-Fix (AUTOMATION_BUG only)

If classification is AUTOMATION_BUG with HIGH confidence:
1. Apply the fix to the test file
2. Run ONLY the fixed test to verify:
   ```bash
   TEST_ENV=staging npx playwright test [file]:[line] --reporter=list
   ```
3. If it passes → commit with message: `fix(test): [TC-ID] fix [description]`
4. If it still fails → re-analyze with new evidence, possibly reclassify

### Phase 6: Summary

After analyzing all failures, output a summary table:

```markdown
## Triage Summary

| # | Test Case | Classification | Action | Status |
|---|---|---|---|---|
| 1 | TC-DASH-005 | 🔧 AUTOMATION_BUG | Auto-fixed | ✅ Fixed & verified |
| 2 | TC-DASH-009 | 🐛 PRODUCT_BUG | Bug report prepared | 📝 Ready for /qa:bug-report |
| 3 | TC-API-001 | ⚡ ENVIRONMENT | Retry recommended | ⏭️ Skip |

**Overall:** X failures analyzed → Y bugs found, Z automation fixes applied, W environment issues
```

## Important Rules

1. **NEVER guess** — always inspect the live URL/API before classifying
2. **Screenshots are primary evidence** for UI tests — if you can see the element in the screenshot, the selector is wrong
3. **Replay API calls** for API tests — don't just read the error message
4. **One classification per failure** — never hedge with "could be either"
5. **Auto-fix only when confident** — if in doubt, present fix for approval
6. **Read the ACTUAL test code** — understand what the test expects before analyzing
7. **Check the POM** — if the selector is in a page object, the fix goes in the page object, not the test file
