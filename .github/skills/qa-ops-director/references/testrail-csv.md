# TestRail CSV Import Reference

## Column Schema (Exact Order)

TestRail imports by column position. The header row must match exactly:

```
Section,Role,Channel,Title,Test Data,Preconditions,Steps,Expected Result,Platform,TestMethod,Type,P,References,Release version,QA Responsibility
```

| # | Column | Required | Accepted Values / Notes |
|---|---|---|---|
| 1 | Section | Yes | Hierarchy with ` > ` separator, e.g. `Agentic > Base Skill > Internal Library` |
| 2 | Role | Yes | `User`, `Admin`, `Super Admin` |
| 3 | Channel | Yes | `Web`, `iOS`, `Android`, `API` |
| 4 | Title | Yes | "Check/Verify" style — see Title Style Guide below |
| 5 | Test Data | No | Specific input data or content needed to execute the test |
| 6 | Preconditions | No | State required before executing — use ` / ` separator, NEVER commas |
| 7 | Steps | Yes | Numbered steps with REAL NEWLINES between items — e.g. `"1. Open Dashboard\n2. Click Create button"` (TestRail renders as separate lines) |
| 8 | Expected Result | Yes | Numbered expected outcomes with REAL NEWLINES — e.g. `"1. Wizard opens\n2. Name field is active"` (TestRail renders as separate lines) |
| 9 | Platform | Yes | `Web`, `iOS`, `Android`, `API` — matches Channel unless cross-platform |
| 10 | TestMethod | Yes | `Manual`, `Automated` |
| 11 | Type | Yes | `Smoke Test`, `Sanity Test`, `Regression Test` |
| 12 | P | Yes | `P0`, `P1`, `P2` |
| 13 | References | No | Short component/feature tag, e.g. `Mode Enforcement`, `File Preview`, `Permission Filtering` |
| 14 | Release version | No | e.g. `Eko 18.0`, `EGT 18.1` — sprint or release this test targets |
| 15 | QA Responsibility | No | Assignee name, e.g. `Peam`, `Sharp` |

---

## Priority Mapping

| CSV value | TestRail priority_id | Label |
|---|---|---|
| `P1` | 4 | Critical |
| `P2` | 3 | High |

> P1 and P2 are the team's standard priorities, confirmed by the TestRail import config.
> P0 (Blocker) is reserved but has no pre-configured mapping — add manually on import screen if needed.

---

## Title Style Guide

Titles must be **clear / direct / user-perspective**. Describe WHAT is being checked and under WHAT condition.

### Approved Patterns

| Pattern | When to use | Example |
|---|---|---|
| `Check [subject] should [behavior] when [condition]` | Most common — testing a behavior under a condition | `Check job list should be filtered when selecting status from dropdown` |
| `Check [subject] should be [state] on/in [location]` | Verifying UI state on a page | `Check empty state should be shown when no scheduled jobs exist` |
| `Verify [what] on [where]` | Page-level or layout verification | `Verify default layout elements on Dashboard page` |
| `After [action] / check [subject] should [behavior]` | Action-result test | `After toggling job status / check isEnabled should be updated in config` |

### Title Rules

- **Always start with `Check` or `Verify`** — never start with a verb like "View" / "Create" / "Edit"
- **Include the condition** — what triggers the behavior: "when [X]" / "after [X]" / "on [page]"
- **Include the expected behavior** — "should be [state]" / "should [action]"
- **Use plain language** — avoid technical jargon / internal variable names / implementation details
- **Keep it one sentence** — no periods at the end

### BAD vs GOOD Examples

| BAD (vague / technical / no condition) | GOOD (clear / direct / user-perspective) |
|---|---|
| `View dashboard with scheduled jobs` | `Check scheduled jobs list should be displayed on Dashboard page` |
| `Filter jobs by status` | `Check job list should be filtered correctly when selecting status filter` |
| `Scheduler picks up due jobs` | `Check scheduler should pick up jobs when nextRun time is due` |
| `HMAC signature verification` | `Verify HMAC signature should be valid when external server receives EkoAI request` |
| `ScheduleJobRun snapshot captures config` | `Check job run snapshot should contain frozen config at trigger time` |
| `BullMQ queue per run and action type` | `Check dynamic queue should be created for each job run` |
| `Dashboard shows empty state` | `Check empty state should be shown when no scheduled jobs exist` |
| `Per-user request dispatched to endpoint` | `Check individual request should be dispatched for each audience user` |

---

## Scenario Category — MANDATORY: All 3 Must Exist Per Feature Group

Every component or feature group in the test plan **must** have test cases from all three categories.
Do not ship a test plan that is missing any category for any feature group.

| Category | When to use | Title pattern |
|---|---|---|
| **Positive** | Valid input / happy path / user successfully achieves goal | `Check [subject] should [succeed/display/work] when [valid condition]` |
| **Negative** | Invalid input / missing field / unauthorized / system correctly rejects | `Check [error/validation] should [appear/reject] when [invalid condition]` |
| **Edge Case** | Boundary values / empty state / max length / zero / null / concurrent / extreme input | `Check [subject] should [handle/display] correctly when [boundary condition]` |

**Minimum per feature group:** ≥2 Positive + ≥2 Negative + ≥2 Edge Case.

---

## Type Mapping

| Category | Type value in CSV |
|---|---|
| Positive — core happy path (critical flow) | `Smoke Test` |
| Positive — secondary valid scenario / UI state | `Sanity Test` |
| Negative — invalid input / auth / rejection | `Regression Test` |
| Edge Case — boundary / empty / max / extreme | `Regression Test` |
| Security — auth bypass / injection / IDOR | `Regression Test` |
| AI-Mandatory (M1–M5) | `Regression Test` |

---

## Formatting Rules

### CRITICAL RULE 1 — Steps and Expected Result use numbered multi-line format

**Steps and Expected Result cells MUST use real newlines between numbered items.**
This is how TestRail renders them as separate lines after import.

| Field | CSV cell content (inside quotes) | TestRail renders as |
|---|---|---|
| Steps | `"1. Open Dashboard page\n2. Click Create button\n3. Fill in job name"` | 1. Open Dashboard page<br>2. Click Create button<br>3. Fill in job name |
| Expected Result | `"1. Wizard opens in Step 1\n2. Name field is active"` | 1. Wizard opens in Step 1<br>2. Name field is active |

- Each item starts with a number: `1.` / `2.` / `3.` / etc.
- Items separated by REAL newlines (`\n`) — Python csv.writer auto-quotes these fields
- TestRail CSV importer handles RFC 4180 multi-line quoted fields correctly
- Use `csv.QUOTE_ALL` quoting strategy for maximum safety

**All OTHER fields (Section / Role / Channel / Title / Preconditions / Test Data / etc.) must NOT contain newlines.**

---

### CRITICAL RULE 2 — No commas inside cell values (causes columns to shift)

**Numbers and Excel do NOT reliably handle quoted fields containing commas — even with correct RFC 4180 quoting. The result is columns shifting right by the number of embedded commas.**

| WRONG — column shifts right | CORRECT |
|---|---|
| `"Payload: { name: Test Job } — missing cron, process, audience"` | `Payload: { name: Test Job } — missing cron / process / audience` |
| `"7 SUCCESS, 3 FAILED records"` | `7 SUCCESS / 3 FAILED records` |
| `"page, limit, total"` | `page / limit / total` |

- NEVER put a comma inside any cell value
- Replace ALL commas within cell content with ` / ` (space slash space)
- This applies to every field: Test Data, Steps, Expected Result, Preconditions, etc.

---

### CRITICAL RULE 3 — Always generate CSV via Python csv.writer with QUOTE_ALL

**Use `csv.QUOTE_ALL` to ensure all fields are properly quoted — especially Steps and Expected Result which contain newlines.**

```python
import csv

# Column indexes where newlines ARE allowed
STEPS_COL = 6      # Steps (0-indexed)
EXPECTED_COL = 7   # Expected Result (0-indexed)

# Step 1: Write via csv.writer with QUOTE_ALL
with open('output.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f, quoting=csv.QUOTE_ALL)
    writer.writerows(all_rows)

# Step 2: Validate
with open('output.csv', 'r', encoding='utf-8') as f:
    rows = list(csv.reader(f))

bad_cols = [(i+1, len(r)) for i, r in enumerate(rows) if len(r) != 15]
comma_cells = []
newline_wrong_col = []
for i, r in enumerate(rows[1:], 2):
    for j, cell in enumerate(r):
        if ',' in cell:
            comma_cells.append((i, j))
        if ('\n' in cell or '\r' in cell) and j not in (STEPS_COL, EXPECTED_COL):
            newline_wrong_col.append((i, j))

assert not bad_cols, f"Column count errors: {bad_cols}"
assert not comma_cells, f"Embedded commas found: {comma_cells}"
assert not newline_wrong_col, f"Newlines in wrong columns: {newline_wrong_col}"
print(f"PASS: {len(rows)-1} rows / all 15 cols / no commas / newlines only in Steps+Expected")
```

Do NOT ship the CSV without running this check. If any assertion fails, fix the offending cells before outputting.

**Section hierarchy:**
Use ` > ` (space-arrow-space) as path separator.
Example: `Agentic > AI Scheduled Job > Empty State`

---

## Sample CSV (correct multi-line format for TestRail import)

```csv
"Section","Role","Channel","Title","Test Data","Preconditions","Steps","Expected Result","Platform","TestMethod","Type","P","References","Release version","QA Responsibility"
"Agentic > Base Skill > Internal Library","User","Web","Check internal library mode should be enabled when user turns it on","User with library permission","User is logged in and has permission to use internal library","1. Login to the system
2. Open Agentic chat
3. Click on tool selector below message input
4. Turn on Use internal library option","1. Tool selector opens showing library toggle
2. Internal library mode is activated
3. Toggle shows enabled state","Web","Manual","Smoke Test","P1","Library Mode UI","Eko 17.29","Peam"
```

**Notice:** All fields wrapped in quotes (`csv.QUOTE_ALL`). Steps and Expected Result contain real newlines.
TestRail renders each numbered item on its own line. No commas inside any cell value.

---

## Import Instructions

1. Save as UTF-8 CSV
2. In TestRail: target Test Suite → **Import Cases**
3. Select **CSV** format
4. Click **Load config** and select `references/testrail-import-config.cfg`
5. All column mappings and value transforms load automatically
6. Review and adjust any new values not yet in the mapping (e.g., new Release version)
7. Confirm import

### Import Config Reference

A saved TestRail import config is at [testrail-import-config.cfg](testrail-import-config.cfg).
This config pre-maps all 15 CSV columns to their TestRail fields.

**Column mapping from config:**

| Col # | CSV Column | Config Key | Notes |
|---|---|---|---|
| 0 | Section | `cases:section_hierarchy` | Section path with ` > ` separator |
| 1 | Role | *(skipped)* | Documentation only — not imported |
| 2 | Channel | `cases:custom_platform` | Dropdown: Web→3 |
| 3 | Title | `cases:title` | Direct |
| 4 | Test Data | `cases:custom_test_data` | Direct |
| 5 | Preconditions | `cases:custom_preconds` | Direct |
| 6 | Steps | `cases:custom_steps` | Multi-line numbered |
| 7 | Expected Result | `cases:custom_expected` | Multi-line numbered |
| 8 | Platform | *(skipped)* | Already mapped via Channel (col 2) |
| 9 | TestMethod | *(skipped)* | No TestRail field |
| 10 | Type | `cases:type_id` | Smoke Test→19 / Regression Test→9 / Sanity Test→11 |
| 11 | P | `cases:priority_id` | P1→4(Critical) / P2→3(High) |
| 12 | References | *(skipped)* | Documentation only — not imported |
| 13 | Release version | `cases:custom_supportversion` | Dropdown — map new values on import screen |
| 14 | QA Responsibility | `cases:custom_qa_responsibility` | Dropdown — map names to IDs |

**Skipped columns** (1, 8, 9, 12) remain in the CSV for human readability.
The config expects all 15 columns in this exact order — do NOT remove skipped columns.

---

## Notes on Updating Existing Cases

TestRail CSV import creates new cases by default — it does not update existing ones.
To update: use TestRail API `POST /api/v2/update_case/:case_id` or TestRail bulk update.
To avoid duplicates on re-import, check for existing titles in the target section first.
