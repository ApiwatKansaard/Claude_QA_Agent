# /auto:pipeline — Full Automation Pipeline (Run → Triage → Dispatch)

## Trigger
- Slash command: `/auto:pipeline`
- Natural language: "run and analyze", "full test pipeline", "run tests and fix failures"

## Parameters
| Parameter | Required | Default | Notes |
|---|---|---|---|
| `[tag or file]` | No | all tests | Tag filter (`@smoke`, `@P1`) or specific file path |
| `[project]` | No | all projects | `e2e`, `api`, or both |
| `[env]` | No | `staging` | Test environment |

## Overview

This is the **master orchestration command** that chains all automation agents into a single flow:

```
┌─────────────────────────────────────────────────────────┐
│                  /auto:pipeline                          │
│                                                         │
│  Stage 1: RUN         ─→  Execute Playwright tests      │
│  Stage 2: TRIAGE      ─→  Analyze each failure          │
│  Stage 3: DISPATCH    ─→  Route to correct agent:       │
│     ├─ PRODUCT_BUG    ─→  qa-ops-director /qa:bug-report│
│     ├─ AUTOMATION_BUG ─→  playwright-automator (fix)    │
│     └─ ENVIRONMENT    ─→  Log + skip                    │
│  Stage 4: VERIFY      ─→  Re-run fixed tests            │
│  Stage 5: REPORT      ─→  Final summary                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Stage 1: RUN — Execute Tests

### 1.1 Build the command

```bash
cd /path/to/QA_Automation
TEST_ENV={env} npx playwright test {tag-or-file} {--project=project}
```

- Use the config reporters (list + html + json + junit) — do NOT override `--reporter`
- This ensures `reports/{env}/results.json` is generated for Stage 2

### 1.2 Execute and capture

Run in terminal, wait for completion. Capture exit code.

### 1.3 Quick status check

```bash
# Parse results.json for pass/fail counts
python3 -c '
import json
d = json.load(open("reports/{env}/results.json"))
s = d["stats"]
print(f"PASSED={s[\"expected\"]} FAILED={s[\"unexpected\"]} SKIPPED={s[\"skipped\"]}")
'
```

**Decision point:**
- `FAILED=0` → **All passed.** Skip to Stage 5 (summary only). Show: `✅ All {n} tests passed in {duration}s`
- `FAILED>0` → Continue to Stage 2 (triage)

---

## Stage 2: TRIAGE — Analyze Each Failure

Follow the full triage workflow from `commands/triage.md`, with these modifications for pipeline mode:

### 2.1 Collect evidence (for all failures at once)

Read `reports/{env}/results.json` and extract ALL failures into a structured list:

```
failures = [
  {
    "id": 1,
    "testName": "TC-DASH-005: search accepts input...",
    "file": "tests/e2e/agentic/scheduled-jobs/scheduler-list.spec.ts",
    "line": 68,
    "error": "Expected substring: ...",
    "errorType": "assertion" | "timeout" | "element-not-found" | "strict-mode" | "other",
    "screenshotPath": "test-results/.../test-failed-1.png",
    "tags": ["@scheduled-jobs", "@sanity", "@P2"]
  },
  ...
]
```

### 2.2 Inspect live application (per failure)

For each failure, follow Phase 2 of `commands/triage.md`:
- UI tests → view screenshot + fetch actual page
- API tests → replay curl with auth token

### 2.3 Classify each failure

Assign exactly ONE classification per failure using `references/triage-rules.md`:
- `PRODUCT_BUG` — app is broken
- `AUTOMATION_BUG` — test code is wrong
- `ENVIRONMENT_ISSUE` — transient/infra problem

### 2.4 Build dispatch queue

Group failures by classification:

```
dispatchQueue = {
  "PRODUCT_BUG": [...failures classified as product bug],
  "AUTOMATION_BUG": [...failures classified as automation bug],
  "ENVIRONMENT_ISSUE": [...failures classified as environment issue]
}
```

**Show the triage summary to user before dispatching:**

```markdown
## Triage Complete — {n} failures analyzed

| # | Test | Classification | Confidence |
|---|---|---|---|
| 1 | TC-DASH-005 | 🐛 PRODUCT_BUG | HIGH |
| 2 | TC-DASH-009 | 🔧 AUTOMATION_BUG | HIGH |
| 3 | TC-API-001 | ⚡ ENVIRONMENT | MEDIUM |

Proceeding to dispatch...
```

---

## Stage 3: DISPATCH — Route to Correct Agent

Process each group in order: AUTOMATION_BUG first (quick fixes), then PRODUCT_BUG (reports), then ENVIRONMENT (log only).

### 3A: AUTOMATION_BUG → Fix the Code

For each automation bug, **invoke the playwright-automator agent** (or act as it) to fix:

#### 3A.1 Prepare fix context

For each AUTOMATION_BUG failure, prepare this handoff data:

```markdown
## Fix Request: {testName}

**File:** {file}:{line}
**Error:** {error}
**Error Type:** {errorType}
**Screenshot:** {screenshotPath}

### Current Code (broken)
```typescript
// Lines around the failure from the spec file
{read the actual failing code — 10 lines before and after the error line}
```

### Root Cause Analysis
{from triage Phase 3 — why it fails}

### Proposed Fix
```typescript
// The corrected code
{generate the fix based on:
  - screenshot analysis (what the page actually shows)
  - DOM inspection (actual selectors available)
  - triage-rules.md patterns
}
```

### Confidence: {HIGH | MEDIUM}
```

#### 3A.2 Apply the fix

- **HIGH confidence** → Apply directly using file edit tools
  - Read the spec file
  - Replace the broken code with the fix
  - Also update the Page Object if the selector is in a POM file

- **MEDIUM confidence** → Show the proposed fix to the user
  - Wait for approval before applying
  - If user edits the fix, apply their version

#### 3A.3 Verify each fix

After applying a fix, run ONLY that specific test:

```bash
TEST_ENV={env} npx playwright test {file}:{line} --reporter=list
```

- Pass → Mark as `✅ Fixed & verified`
- Fail again → Re-analyze with new error. If still can't fix after 2 attempts, escalate to user:
  `⚠️ Could not auto-fix {testName}. Manual investigation needed.`

**Max retry: 2 attempts per failure.** Don't loop indefinitely.

---

### 3B: PRODUCT_BUG → Prepare Bug Report

For each product bug, **prepare handoff data for qa-ops-director's `/qa:bug-report`**:

#### 3B.1 Compose bug report input

Build a structured bug description that the `/qa:bug-report` command can consume directly:

```markdown
## Bug Report Data: {testName}

### Summary
[Scheduler Dashboard] {concise description of what's broken}

### Steps to Reproduce
1. Navigate to {URL}
2. {action from test steps, translated to human-readable steps}
3. {action}
4. Observe: {actual behavior seen in screenshot/inspection}

### Expected Result
{from test assertion — what the test expected}

### Actual Result
{from live inspection — what the app actually does}

### Environment
- URL: {full URL}
- Browser: Chromium (Playwright)
- Environment: {env}
- Test: {file}:{line}

### Evidence
- Screenshot: {screenshotPath}
- Error: {error message}
- Related Test Cases: {tags → TestRail IDs if known}

### Severity Assessment
- Impact: {based on test priority tag: @P1→S2, @P2→S3}
- Scope: {single page / multiple pages / API-level}
- Workaround: {exists / none known}

### Suggested Jira Fields
- Project: AE
- Issue Type: Bug
- Priority: {mapped from severity}
- Labels: [automation-detected, {feature-tag}]
- EKO Squad: Broccoli (14379)
- Severity: {S1-S4 with ID}
- Platform: All Web Apps (10996)
```

#### 3B.2 Invoke bug report creation

**Invoke the qa-ops-director agent** (via `runSubagent` with agent name `qa-ops-director`) with this prompt:

```
/qa:bug-report

{paste the composed bug report data from 3B.1}

This bug was detected by automated tests. Please create the Jira ticket following the full /qa:bug-report pipeline. Use the data provided above — it has already been verified by inspecting the live application.
```

**Important rules:**
- Always show the bug ticket preview to user before creating in Jira
- Wait for user approval (the `/qa:bug-report` pipeline handles this)
- If multiple PRODUCT_BUGs exist, process them ONE AT A TIME — show each preview, get approval, then move to next

---

### 3C: ENVIRONMENT_ISSUE → Log and Skip

For environment issues, no action needed — just log them:

```markdown
### ⚡ Environment Issues ({count})

| # | Test | Issue | Recommendation |
|---|---|---|---|
| 1 | TC-API-001 | 502 Bad Gateway | Retry later — staging may be deploying |
| 2 | TC-DASH-003 | Timeout (30s) | Staging slow — not a code issue |

**No tickets or code changes needed.** These tests should pass on retry.
```

---

## Stage 4: VERIFY — Re-run All Tests

After all AUTOMATION_BUG fixes are applied, run the full suite again:

```bash
TEST_ENV={env} npx playwright test {original tag-or-file} {--project=project}
```

Parse results:
- All pass → 
- New failures → Run mini-triage (Stage 2 again, but only for NEW failures)
- Same failures → Escalate to user

**Max full-suite re-runs: 2.** After 2 attempts, report remaining failures to user.

---

## Stage 5: REPORT — Final Pipeline Summary

Output a comprehensive summary:

```markdown
## 🔄 Pipeline Report

**Run:** {timestamp}
**Environment:** {env}
**Command:** `npx playwright test {args}`
**Duration:** Stage 1: {run_time} → Stage 2: {triage_time} → Stage 3: {fix_time} → Stage 4: {verify_time}

### Test Results
| Metric | Initial Run | After Fixes |
|---|---|---|
| Total | {n} | {n} |
| ✅ Passed | {passed_1} | {passed_2} |
| ❌ Failed | {failed_1} | {failed_2} |
| 🔧 Auto-fixed | — | {fixed_count} |

### Failure Breakdown
| # | Test | Classification | Action | Result |
|---|---|---|---|---|
| 1 | TC-DASH-005 | 🔧 AUTOMATION_BUG | Auto-fixed selector | ✅ Fixed & verified |
| 2 | TC-DASH-009 | 🐛 PRODUCT_BUG | AE-12345 created | 📝 Ticket filed |
| 3 | TC-API-001 | ⚡ ENVIRONMENT | Skipped (staging slow) | ⏭️ No action |

### Actions Taken
- 🔧 **{n} automation fixes** applied and verified
- 🐛 **{n} bug tickets** created: {AE-XXXXX, AE-YYYYY}
- ⚡ **{n} environment issues** logged (no action needed)

### Remaining Issues
{any failures that couldn't be resolved — with details}
```

---

## Pipeline Configuration

### Retry & Safety Limits

| Setting | Value | Rationale |
|---|---|---|
| Max auto-fix attempts per failure | 2 | Prevent infinite fix loops |
| Max full-suite re-runs | 2 | Prevent infinite retry loops |
| Auto-fix confidence threshold | HIGH | Only auto-apply when sure |
| Bug report approval | Required | Always show preview before creating Jira ticket |
| Environment skip threshold | Any | Always skip environment issues |

### Agent Handoff Protocol

When dispatching to another agent via `runSubagent`:

| Classification | Target Agent | Prompt Template |
|---|---|---|
| PRODUCT_BUG | `qa-ops-director` | `/qa:bug-report` + structured bug data |
| AUTOMATION_BUG | `playwright-automator` | Fix request with code context + screenshot |
| ENVIRONMENT_ISSUE | (none) | Log only |

### File Paths Reference

| Artifact | Path |
|---|---|
| Test results JSON | `QA_Automation/reports/{env}/results.json` |
| JUnit XML | `QA_Automation/reports/{env}/junit.xml` |
| HTML report | `QA_Automation/reports/{env}/html/` |
| Failure screenshots | `QA_Automation/test-results/*/test-failed-*.png` |
| Test spec files | `QA_Automation/tests/{e2e,api}/**/*.spec.ts` |
| Page objects | `QA_Automation/src/pages/*.page.ts` |
| Triage rules | `QA_Agent/.github/skills/playwright-automator/references/triage-rules.md` |
| Bug report command | `QA_Agent/.github/skills/qa-ops-director/commands/bug-report.md` |
