# /qa:create-regression [feature or sprint name] [suite_id]

**Triggers:** testrail-manager agent
**References:** [agent-testrail-manager.md](../references/agent-testrail-manager.md), [testrail-api.md](../references/testrail-api.md), [ai-llm-testing.md](../references/ai-llm-testing.md)

## What This Command Does

Create a TestRail **milestone** + **2 test runs** (Smoke + Regression) for a sprint or feature release.

Sources case IDs from the active sprint CSV (col 16 `TestRailID`) — no manual impact analysis needed.
Groups cases by `Type` column:
- `Smoke Test` → Smoke run
- `Regression Test` + `Sanity Test` → Regression run

Shows a plan for review, then creates everything via API in one shot.

## Parameters

| Parameter | Required | Notes |
|---|---|---|
| `[feature or sprint name]` | Yes | e.g., "AI Scheduled Jobs", "sharp-test-001" |
| `[suite_id]` | No | TestRail suite ID — defaults to `5277` (Scheduled Jobs sprint suite) |

**Team defaults:** project `1`, host `ekoapp20.testrail.io`

---

## Execution Steps

### Phase 1 — Detect Sprint CSV

Use standard sprint folder detection:
1. Scan QA_Agent workspace root for `agentic-*/` or `sprint-*/` (not in `archive/`)
2. One found → use it. Multiple → highest version. None → ask user.

Read `{sprint-folder}/*-testcases.csv` — parse with Python csv.DictReader.

**Required columns:**
- `TestRailID` (col 16) — C-IDs written back by `/qa:import-testrail`
- `Type` — `Smoke Test` / `Sanity Test` / `Regression Test`
- `P` — `P0` / `P1` / `P2`
- `Section` — for grouping summary
- `Channel` — `Web` / `API` (for breakdown)

If any row has empty `TestRailID`:
> ⚠️ Warning: {n} rows have no TestRailID — run `/qa:import-testrail` first to populate C-IDs.
> Proceed with {available} cases? (yes / cancel)

---

### Phase 2 — Build Case Sets from CSV

Parse and group C-IDs:

```python
import csv, re

smoke_ids = []
regression_ids = []
missing_ids = []

with open(csv_path) as f:
    reader = csv.DictReader(f)
    for row in reader:
        tid = row.get('TestRailID', '').strip()
        type_ = row.get('Type', '').strip()
        if not tid:
            missing_ids.append(row['Title'])
            continue
        case_id = int(re.sub(r'[^0-9]', '', tid))
        if type_ == 'Smoke Test':
            smoke_ids.append(case_id)
        else:  # Regression Test, Sanity Test
            regression_ids.append(case_id)
```

**Rules:**
- `Smoke Test` → smoke run only
- `Regression Test` → regression run only
- `Sanity Test` → regression run (grouped with regression)
- A case goes into exactly one run based on its Type

---

### Phase 3 — Check Google Calendar for Release Date

```
mcp_gcal_list_events(timeMin=today, timeMax=+30days)
```

Look for events containing "release", "RC", sprint name, or "cut". Suggest as milestone due date.
If nothing found → suggest +14 days from today and ask user to confirm.

---

### Phase 4 — Show Plan for Review (REQUIRED — do not skip)

```markdown
## Sprint Regression Plan — [Feature/Sprint Name]

**Source:** {sprint-folder}/{csv-filename} ({total} cases total)
**Suite:** S{suite_id}

---

### Milestone
**Name:** [Feature Name] — Sprint Release
**Due date:** [suggested date from calendar or +14d]

---

### Test Run 1 — Smoke
**Name:** [Feature Name] — Smoke Run
**Cases:** {n} (from Smoke Test type)

| Channel | Count |
|---|---|
| Web | {n} |
| API | {n} |

### Test Run 2 — Regression
**Name:** [Feature Name] — Regression Run
**Cases:** {n} (Regression Test + Sanity Test)

| Channel | Count | P1 | P2 |
|---|---|---|---|
| Web | {n} | {n} | {n} |
| API | {n} | {n} | {n} |

---

⚠️ Missing TestRailID: {n} cases skipped

Confirm? (yes / adjust / cancel)
```

Wait for user confirmation before proceeding to Phase 5.

---

### Phase 5 — Create Milestone

```
POST /add_milestone/{project_id}
{
  "name": "[Feature Name] — Sprint Release",
  "description": "Sprint: [sprint-folder]. Source: [csv filename]. Smoke: {n} cases. Regression: {n} cases.",
  "due_on": [unix_timestamp]
}
```

Save `milestone_id` from response.

---

### Phase 6 — Create Smoke Run

```
POST /add_run/{project_id}
{
  "suite_id": {suite_id},
  "name": "[Feature Name] — Smoke Run",
  "description": "Smoke test run — {n} cases. Source: {csv}. Sprint: {sprint-folder}.",
  "milestone_id": {milestone_id},
  "case_ids": [smoke_ids]
}
```

Save `smoke_run_id`.

---

### Phase 7 — Create Regression Run

```
POST /add_run/{project_id}
{
  "suite_id": {suite_id},
  "name": "[Feature Name] — Regression Run",
  "description": "Regression + Sanity test run — {n} cases. Source: {csv}. Sprint: {sprint-folder}.",
  "milestone_id": {milestone_id},
  "case_ids": [regression_ids]
}
```

Save `regression_run_id`.

---

### Phase 8 — Report

```markdown
## ✅ TestRail Milestone + Runs Created

**Milestone:** [Feature Name] — Sprint Release
🔗 https://ekoapp20.testrail.io/index.php?/milestones/view/{milestone_id}
📅 Due: {due_date}

---

### 🔵 Smoke Run — R{smoke_run_id}
🔗 https://ekoapp20.testrail.io/index.php?/runs/view/{smoke_run_id}
**Cases:** {n} (Web: {n} | API: {n})

### 🟡 Regression Run — R{regression_run_id}
🔗 https://ekoapp20.testrail.io/index.php?/runs/view/{regression_run_id}
**Cases:** {n} (Regression: {n} | Sanity: {n})

---

### Next Steps
1. Run smoke: `/auto:run @smoke --project=e2e`  then `/auto:run @smoke --project=api`
2. Send smoke results: `/auto:send-results {smoke_run_id}`
3. Run regression: `/auto:run @regression`
4. Send regression results: `/auto:send-results {regression_run_id}`

Or run everything at once: `/auto:pipeline`
```

---

## Error Handling

| Error | Action |
|---|---|
| No sprint CSV found | Ask user to specify path |
| All TestRailIDs empty | Abort — run `/qa:import-testrail` first |
| Some TestRailIDs empty | Warn + proceed with available cases |
| 400 case not in suite | Log skipped case IDs, continue |
| Milestone name conflict | Append timestamp suffix to name |
| 401 Unauthorized | "Check TESTRAIL_EMAIL / TESTRAIL_TOKEN in .env" |

---

## AI Feature Regression Rules

When the feature involves AI/LLM behavior, always include these mandatory scenarios
from [ai-llm-testing.md](../references/ai-llm-testing.md):

| Scenario | Section to add to |
|---|---|
| M1 — Prompt injection resistance | Agentic > Security |
| M2 — Hallucination rate (3-run consistency) | Agentic > Functional |
| M3 — Output format compliance | Agentic > Functional |
| M4 — Latency under load | Agentic > Functional |
| M5 — Graceful degradation | Agentic > Functional |

If these cases don't exist in TestRail yet, offer to create them via `/qa:import-testrail`.
