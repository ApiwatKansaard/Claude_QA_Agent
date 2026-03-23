# /qa:edit-testrail [suite_id] [section or case filter] [change description]

**Triggers:** testrail-manager agent
**References:** [agent-testrail-manager.md](../references/agent-testrail-manager.md), [testrail-api.md](../references/testrail-api.md)

## What This Command Does

Edit existing test cases in TestRail via API when a new feature impacts existing test steps
or expected results. Fetches affected cases, generates a diff of proposed changes,
shows it for user review, then applies updates via `POST /update_case`.

## Parameters

| Parameter | Required | Notes |
|---|---|---|
| `[suite_id]` | Yes | TestRail suite to search in |
| `[section or case filter]` | Yes | Section name, case title keywords, or specific case IDs (C10001, C10002) |
| `[change description]` | Yes | What changed in the feature — used to determine what needs updating |

**Team defaults:** project `1`, host `ekoapp20.testrail.io`

If parameters are missing, ask before proceeding.

## Execution Steps

1. **Understand the change** — analyze `[change description]`:
   - What behavior changed?
   - Which test scenarios are affected? (steps, expected results, preconditions)
   - What is the new expected behavior?

2. **Fetch target cases**:
   - If case IDs given: `GET /get_case/{case_id}` for each
   - If section filter given: `GET /get_cases/{project_id}&suite_id={suite_id}` → filter by section name or title substring
   - Read full case details: title, custom_preconds, custom_steps, custom_expected

3. **Generate proposed changes** — for each affected case, determine:
   - Which field(s) need updating: `custom_steps`, `custom_expected`, `custom_preconds`, `title`
   - What the new value should be based on the change description

4. **Show diff for review (REQUIRED before any update)**:

```markdown
## Edit Preview — [N] cases to update

### C10001 — [Case Title]
**Section:** Agentic > AI Scheduled Job > Create Scheduler

| Field | Before | After |
|---|---|---|
| Steps | 1. Click Add\n2. Fill Name field\n3. Click Save | 1. Click Add Scheduler\n2. Fill Name and Timezone fields\n3. Toggle Active switch\n4. Click Save |
| Expected Result | Scheduler appears in list | Scheduler appears in list with correct timezone shown |

---

### C10002 — [Case Title]
...

**Summary:** N cases will be updated, M fields changed total.
Proceed? (yes / cancel / adjust)
```

5. **Apply updates** (after user confirmation):
   - `POST /update_case/{case_id}` for each case — only changed fields
   - Do NOT send unchanged fields

6. **Report results**:
```markdown
## Update Complete

✅ Updated N cases in [Suite Name]

| Case ID | Title | Fields Changed |
|---|---|---|
| C10001 | [title] | steps, expected_result |
| C10002 | [title] | expected_result |

🔗 Review changes: https://ekoapp20.testrail.io/index.php?/suites/view/{suite_id}
```

7. **Update cache** — after successful edits:
   - Re-fetch all cases from suite (or apply changes locally)
   - Update `testrail-cache/S{suite_id}/cases.csv` with modified case data
   - Update `testrail-cache/S{suite_id}/summary.md` with refreshed stats
   - **ALWAYS update cache after write operations** — ensures next import has accurate baseline

## Impact Analysis

Before showing the diff, briefly surface:
- How many cases are impacted
- Whether any cases should be **marked obsolete** (feature removed or scenario no longer valid)
- Whether any **new cases** should be added to cover new behavior

If obsolete cases are identified, flag them:
> "C10003 'Verify legacy import works' appears obsolete — the legacy import was removed in this feature. Mark as obsolete in TestRail? (TestRail doesn't delete cases; they'll be excluded from future runs.)"

## Scope Guard

If more than 20 cases match the filter, warn the user before proceeding:
> "Found [N] cases matching '[filter]'. This is a broad change — do you want to review all N cases, or narrow the filter first?"

Always require explicit confirmation regardless of scope.
