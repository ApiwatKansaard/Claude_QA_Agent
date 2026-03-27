# /auto:send-results — Send Test Results to TestRail

## Trigger
`/auto:send-results [run_id] [results-file]`

## Parameters

| Parameter | Required | Notes |
|---|---|---|
| `[run_id]` | Yes | TestRail Test Run ID (integer). Create one with `/qa:create-regression` first. |
| `[results-file]` | No | Path to Playwright JSON results. Default: `reports/{env}/results.json` |

---

## Overview

Reads Playwright test results, extracts TestRail case IDs from test annotations,
and calls `POST /add_results_for_cases/{run_id}` to update pass/fail status in TestRail.

This command is also called automatically as **Phase 6** of `/auto:pipeline` when `TESTRAIL_RUN_ID` is set.

---

## Execution Flow

### Phase 1 — Load Results

Read Playwright JSON results file:
```
reports/{env}/results.json
```

Expected format (Playwright JSON reporter output):
```json
{
  "suites": [{
    "specs": [{
      "title": "should display job list on Dashboard page",
      "annotations": [{ "type": "TestRail", "description": "C1548642" }],
      "tests": [{ "status": "passed" }]
    }]
  }]
}
```

If file not found:
> "No results file at `reports/{env}/results.json`. Run `/auto:run` first."

---

### Phase 2 — Extract Case ID → Result Mapping

For each spec in the results:
1. Find annotation where `type === 'TestRail'`
2. Extract case ID: `"C1548642"` → `1548642` (integer)
3. Skip specs where annotation is missing or `description` is empty
4. Map Playwright status → TestRail status:

| Playwright status | TestRail status_id | Label |
|---|---|---|
| `passed` | `1` | Passed |
| `failed` | `5` | Failed |
| `timedOut` | `5` | Failed |
| `skipped` | `2` | Blocked |
| `interrupted` | `4` | Retest |

Build payload:
```python
results = []
for spec in specs:
    case_id = extract_testrail_id(spec)  # returns int or None
    if not case_id:
        continue
    status_id = STATUS_MAP[spec['status']]
    entry = {"case_id": case_id, "status_id": status_id}
    if spec['status'] == 'failed':
        entry["comment"] = extract_error_message(spec)  # first error line
    results.append(entry)
```

---

### Phase 3 — Validate Run

Call `GET /get_run/{run_id}` to confirm:
- Run exists and is open (not closed)
- Project matches expected suite

If run is closed:
> "Test Run R{run_id} is already closed. Create a new run with `/qa:create-regression`."

---

### Phase 4 — Send Results

```python
POST /add_results_for_cases/{run_id}
Content-Type: application/json

{
  "results": [
    { "case_id": 1548642, "status_id": 1 },
    { "case_id": 1548643, "status_id": 5, "comment": "AssertionError: expected 200 got 400" },
    ...
  ]
}
```

**Rules:**
- Send ALL results in a single request (batch) — not one-by-one
- If case_id is not in the run, TestRail returns 400 — catch and report, don't abort
- Max batch: 250 results per request. If > 250, split into chunks

---

### Phase 5 — Report

```markdown
## TestRail Results Sync — R{run_id}

✅ Passed: {n}
❌ Failed: {n}
⏭️ Blocked/Skipped: {n}
⚠️ No TestRail ID (not sent): {n}

### Failed Cases
| Case ID | Test Name | Error |
|---|---|---|
| C1548643 | should reject invalid payload | AssertionError: expected 400 got 200 |
| ... | | |

### Skipped (no TestRailID annotation)
{n} tests had no TestRail annotation — run `/qa:import-testrail` to populate case IDs,
then regenerate tests with `/auto:generate`.

🔗 View run: https://ekoapp20.testrail.io/index.php?/runs/view/{run_id}
```

---

## Integration with `/auto:pipeline`

When `TESTRAIL_RUN_ID` env var is set, `/auto:pipeline` calls this command automatically after Phase 4 (run):

```
Phase 1: RUN         → /auto:run
Phase 2: TRIAGE      → /auto:triage
Phase 3: DISPATCH    → fix code / create bugs
Phase 4: VERIFY      → re-run after fixes
Phase 5: REPORT      → summary
Phase 6: SYNC        → /auto:send-results $TESTRAIL_RUN_ID   ← NEW
```

To enable auto-sync, set in `.env`:
```
TESTRAIL_RUN_ID=123
```

---

## Error Handling

| Error | Action |
|---|---|
| 401 Unauthorized | "Check TESTRAIL_EMAIL / TESTRAIL_TOKEN in .env" |
| 400 case not in run | Log the case ID, skip it, continue batch |
| Run already closed | Abort with message to create a new run |
| results.json missing | Abort — run tests first |
| No cases with TestRail annotation | Warn — run `/qa:import-testrail` to get C-IDs, then `/auto:generate` |
