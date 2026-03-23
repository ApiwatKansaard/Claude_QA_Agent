# /qa:import-testrail [suite link]

**Triggers:** testrail-manager agent
**References:** [agent-testrail-manager.md](../references/agent-testrail-manager.md), [testrail-api.md](../references/testrail-api.md), [testrail-csv.md](../references/testrail-csv.md)

## What This Command Does

Import new or updated test cases into a TestRail suite.
Reads the existing suite (with local caching), compares against new sprint test cases,
produces an impact analysis, then executes the import after user confirmation.

## Parameters

| Parameter | Required | Notes |
|---|---|---|
| `[suite link]` | Yes | TestRail suite URL or suite_id number |

**Sprint test cases** are auto-detected from the current sprint folder (`{sprint-folder}/*-testcases.csv`).
If not found, ask the user to provide them.

**Team defaults:**
- Host: `ekoapp20.testrail.io`
- Projects: `1` (Eko/EGT — Suite 3924=[Main] Agentic), `6` (Amity Solutions — Suite 3923=Agentic)

## URL Parsing

Extract `suite_id` from TestRail URLs:
```
https://ekoapp20.testrail.io/index.php?/suites/view/3924             → suite_id = 3924
https://ekoapp20.testrail.io/index.php?/suites/view/3924&group_by=...→ suite_id = 3924
```
If user provides just a number (e.g., "3924"), treat as suite_id directly.
Resolve `project_id` via `GET /get_suite/{suite_id}` → `project_id` field in response.

---

## Execution Flow

### Phase 1 — Read Existing Suite (with Cache)

Check local cache at `testrail-cache/S{suite_id}/`:

**A) Cache EXISTS:**

```
testrail-cache/S{suite_id}/
  summary.md     — Suite overview: name, section tree, case stats
  cases.csv      — Full case dump in 15-column CSV format
```

Report to user:
> "Found cached data for suite S{suite_id} ({suite_name}) — last synced {date}, {n} cases.
> Using cached data. Say 're-fetch' if you want fresh data from TestRail."

**B) Cache DOES NOT EXIST (first time reading this suite):**

1. **Authenticate** — use credentials from session or ask:
   > "Please provide your TestRail API key (My Settings → API Keys)."

2. **Fetch suite info:**
   ```
   GET /get_suite/{suite_id}
   ```
   Get suite name and project_id.

3. **Fetch section hierarchy:**
   ```
   GET /get_sections/{project_id}?suite_id={suite_id}&limit=250
   ```
   Build section tree: id → name → parent_id → full path.

4. **Fetch ALL cases** (paginated):
   ```
   GET /get_cases/{project_id}?suite_id={suite_id}&limit=250&offset=0
   ```
   Continue until page returns < 250 cases.

5. **Create cache folder** at `testrail-cache/S{suite_id}/`:
   - `summary.md` — Suite analysis (see Cache Format section below)
   - `cases.csv` — All cases exported in 15-column CSV format (same schema as sprint testcases)

**C) Suite is EMPTY (0 cases — new suite):**
> "Suite S{suite_id} ({suite_name}) has 0 test cases. All sprint cases will be added as new."

Skip comparison (Phase 2) — go directly to Phase 3 with all cases marked as **ADD**.

---

### Phase 2 — Compare Sprint Cases vs Suite

Read sprint test cases from `{sprint-folder}/*-testcases.csv` (auto-detect from current sprint).

**Comparison logic** — match by **Section path + Title** (case-insensitive, trimmed):

| Match Result | Action | Description |
|---|---|---|
| Same section + same title → Steps/Expected differ | **UPDATE** | Existing case needs changes |
| Same section + same title → identical content | **SKIP** | Already in suite — no action |
| Title NOT found anywhere in suite | **ADD** | New test case |
| Suite case not in sprint scope | **RETAIN** | Existing case — untouched |

**For ADD cases** — suggest target section:
1. Use the `Section` column from sprint CSV (primary source)
2. Match against existing section hierarchy in the suite
3. If section path doesn't exist → flag it for creation

**For UPDATE cases** — generate a field-level diff:
- Compare: Steps, Expected Result, Preconditions, Title, Type, Priority
- Show before/after for each changed field

---

### Phase 3 — Show Import Preview (REQUIRED)

```markdown
## Import Preview — {Suite Name} (S{suite_id})

### Cases to ADD ({count} new)

| # | Section Path | Title | Priority | Type |
|---|---|---|---|---|
| 1 | Agentic > AI Scheduled Job > Dashboard | Check empty state should be shown when no jobs exist | P1 | Smoke Test |
| ... | | | | |

**New sections to create:** {list sections not yet in suite}

### Cases to UPDATE ({count} changed)

| # | Case ID | Title | Fields Changed |
|---|---|---|---|
| 1 | C10001 | Check job config should be saved when user clicks save | steps / expected_result |

<details>
<summary>Show field diffs</summary>

**C10001 — Check job config should be saved when user clicks save**

| Field | Before | After |
|---|---|---|
| Steps | 1. Open config<br>2. Click Save | 1. Open config<br>2. Set timezone<br>3. Click Save |

</details>

### Cases UNCHANGED ({count} skipped)
Already exist in suite with identical content — no action needed.

### Summary

| Action | Count |
|---|---|
| ADD | {n} new cases |
| UPDATE | {n} existing cases |
| SKIP | {n} unchanged |
| RETAIN | {n} existing (out of sprint scope) |

Confirm import? (yes / cancel / adjust)
```

**Do NOT import until user explicitly confirms.**

---

### Phase 4 — Execute Import

After user confirmation:

**For ADD cases** — create via API:
1. Create missing sections first: `POST /add_section/{project_id}`
2. Create cases: `POST /add_case/{section_id}` with full field mapping
3. Add 0.1–0.2s delay between calls for batches > 50 cases

**For UPDATE cases** — update via API:
1. `POST /update_case/{case_id}` with only changed fields
2. Do NOT resend unchanged fields

**Report results:**

```markdown
## Import Complete

✅ Created {n} new test cases
📝 Updated {n} existing cases
📂 Sections created: {n} new / {n} existing used

| Case ID | Action | Title | Section |
|---|---|---|---|
| C10050 | ADD | Check empty state should be shown... | AI Scheduled Job > Dashboard |
| C10001 | UPDATE | Check job config should be saved... | AI Scheduled Job > Configuration |
| ... | | | |

🔗 View suite: https://ekoapp20.testrail.io/index.php?/suites/view/{suite_id}
```

---

### Phase 5 — Update Cache (MANDATORY)

**ALWAYS update cache after any write operation.**

1. Re-fetch ALL cases from TestRail (ensures cache matches reality)
2. Overwrite `testrail-cache/S{suite_id}/cases.csv` with fresh data
3. Overwrite `testrail-cache/S{suite_id}/summary.md` with updated stats

This ensures the next import session has accurate baseline data.

---

## Field Mapping

### CSV Import (Manual Upload with Config)

Based on the actual TestRail import config file ([testrail-import-config.cfg](../references/testrail-import-config.cfg)):

| Col # | CSV Column | TestRail Field | Config Key | Notes |
|---|---|---|---|---|
| 0 | Section | Section hierarchy | `cases:section_hierarchy` | ` > ` path separator |
| 1 | Role | *(skipped)* | — | Not imported — documentation only |
| 2 | Channel | Platform | `cases:custom_platform` | Dropdown: Web→3 |
| 3 | Title | Title | `cases:title` | Direct |
| 4 | Test Data | Test Data | `cases:custom_test_data` | Direct |
| 5 | Preconditions | Preconditions | `cases:custom_preconds` | Direct |
| 6 | Steps | Steps | `cases:custom_steps` | Multi-line numbered |
| 7 | Expected Result | Expected | `cases:custom_expected` | Multi-line numbered |
| 8 | Platform | *(skipped)* | — | Already mapped via Channel (col 2) |
| 9 | TestMethod | *(skipped)* | — | No TestRail field |
| 10 | Type | Type | `cases:type_id` | Smoke Test→19 / Regression Test→9 / Sanity Test→11 |
| 11 | P | Priority | `cases:priority_id` | P1→4(Critical) / P2→3(High) |
| 12 | References | *(skipped)* | — | Not imported |
| 13 | Release version | Support Version | `cases:custom_supportversion` | Dropdown — map value on import screen |
| 14 | QA Responsibility | QA Responsibility | `cases:custom_qa_responsibility` | Dropdown — map name→ID |

**Skipped columns** (1, 8, 9, 12) stay in the CSV for human readability.
The import config expects all 15 columns in this exact order.

### API Import (POST /add_case)

| CSV Column | API Field | Transform |
|---|---|---|
| Section | `section_id` | Resolve path → ID via section hierarchy |
| Title | `title` | Direct |
| Test Data | `custom_test_data` | Direct |
| Preconditions | `custom_preconds` | Direct |
| Steps | `custom_steps` | Direct (real newlines preserved) |
| Expected Result | `custom_expected` | Direct (real newlines preserved) |
| Channel | `custom_platform` | Map to dropdown ID (Web→3) |
| Type | `type_id` | Smoke Test→19 / Regression Test→9 / Sanity Test→11 |
| P | `priority_id` | P1→4(Critical) / P2→3(High) |
| Release version | `custom_supportversion` | Map string → dropdown ID (call `GET /get_case_fields`) |
| QA Responsibility | `custom_qa_responsibility` | Map name → ID array (see testrail-api.md) |

⚠️ **Before first API import**, call `GET /get_case_fields` to:
1. Verify which custom fields are **required** (prevents 400 errors)
2. Get dropdown values for `custom_supportversion` and `custom_platform`
3. Confirm field names match the instance

---

## Cache Format

### `testrail-cache/S{suite_id}/summary.md`

```markdown
# TestRail Suite — {Suite Name} (S{suite_id})

**Project:** {project_name} (ID: {project_id})
**Last synced:** {YYYY-MM-DD HH:MM UTC}
**Total cases:** {n}
**Total sections:** {n}

## Section Tree

Agentic
├── AI Scheduled Job
│   ├── Dashboard (12 cases)
│   ├── Create Scheduler (8 cases)
│   ├── Job Configuration (10 cases)
│   └── History Logs (6 cases)
└── Base Skill
    └── Internal Library (5 cases)

## Stats by Section

| Section Path | Cases | P1 | P2 | Smoke | Sanity | Regression |
|---|---|---|---|---|---|---|
| AI Scheduled Job > Dashboard | 12 | 8 | 4 | 5 | 1 | 6 |
| AI Scheduled Job > Create Scheduler | 8 | 6 | 2 | 4 | 0 | 4 |

## Coverage Summary

- **Priorities:** P1: {n} / P2: {n}
- **Types:** Smoke: {n} / Sanity: {n} / Regression: {n}
```

### `testrail-cache/S{suite_id}/cases.csv`

Full export in the same 15-column schema as sprint test cases (see [testrail-csv.md](../references/testrail-csv.md)).
This enables direct CSV-to-CSV comparison between suite and sprint.

When exporting from API response, map fields back to CSV columns:
- `section_id` → resolve to section path string using section hierarchy
- `priority_id` → 4="P1" / 3="P2"
- `type_id` → 19="Smoke Test" / 9="Regression Test" / 11="Sanity Test"
- `custom_qa_responsibility` → resolve IDs to names using the lookup table in [testrail-api.md](../references/testrail-api.md)
- Columns without API equivalent (Role, TestMethod, References) → leave empty

---

## Error Handling

| Error | Action |
|---|---|
| URL parse fails | "Could not parse suite_id from URL. Expected format: .../suites/view/{id}" |
| 401 Unauthorized | "API key is invalid. Check My Settings → API Keys in TestRail." |
| 403 Forbidden | "API access not enabled. Contact your TestRail admin." |
| 404 Suite not found | "Suite S{id} not found. Verify the URL and project access." |
| 400 on add_case | Show the failing row, skip it, continue with rest, report at end |
| Partial failure | Report what succeeded and what failed. Update cache with successes only. |
| Rate limit (429) | Wait 2s and retry. Add longer delays between subsequent calls. |
