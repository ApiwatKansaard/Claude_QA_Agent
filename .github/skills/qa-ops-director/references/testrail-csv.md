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
| 4 | Title | Yes | Concise, action-oriented sentence describing what is being verified |
| 5 | Test Data | No | Specific input data or content needed to execute the test |
| 6 | Preconditions | No | State required before executing — use ` / ` separator, NEVER commas |
| 7 | Steps | Yes | Numbered steps on a SINGLE LINE separated by `. ` — e.g. `1. Do this. 2. Do that. 3. Check result.` |
| 8 | Expected Result | Yes | Observable, precise expected outcome |
| 9 | Platform | Yes | `Web`, `iOS`, `Android`, `API` — matches Channel unless cross-platform |
| 10 | TestMethod | Yes | `Manual`, `Automated` |
| 11 | Type | Yes | `Smoke Test`, `Sanity Test`, `Regression Test` |
| 12 | P | Yes | `P0`, `P1`, `P2` |
| 13 | References | No | Short component/feature tag, e.g. `Mode Enforcement`, `File Preview`, `Permission Filtering` |
| 14 | Release version | No | e.g. `Eko 18.0`, `EGT 18.1` — sprint or release this test targets |
| 15 | QA Responsibility | No | Assignee name, e.g. `Peam`, `Sharp` |

---

## Priority Mapping

| Our notation | CSV value |
|---|---|
| P0-Blocker | `P0` |
| P1-Critical | `P1` |
| P2-High / P2-Medium | `P2` |

---

## Scenario Category — MANDATORY: All 3 Must Exist Per Feature Group

Every component or feature group in the test plan **must** have test cases from all three categories.
Do not ship a test plan that is missing any category for any feature group.

| Category | When to use | Title pattern |
|---|---|---|
| **Positive** | Valid input / happy path / user successfully achieves goal | `Verify [X] succeeds when [valid condition]` |
| **Negative** | Invalid input / missing field / unauthorized / system correctly rejects | `Verify [X] rejects or returns error when [invalid condition]` |
| **Edge Case** | Boundary values / empty state / max length / zero / null / concurrent / extreme input | `Verify [X] handles [boundary / empty / extreme] correctly` |

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

### CRITICAL RULE 1 — No embedded newlines (causes rows to split)

**Every cell must be on a single line. No embedded newlines anywhere in the CSV.**

| WRONG — rows split in Excel/Numbers | CORRECT |
|---|---|
| `"1. Login\n2. Click button\n3. Observe"` | `1. Login. 2. Click button. 3. Observe.` |

- NEVER use real newlines (`\n`, `Enter`) inside any cell value, even inside quoted strings
- Write all steps on ONE line with `. ` (period + space) as step separator
- Apply this rule to ALL fields: Steps, Expected Result, Preconditions, Test Data

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

### CRITICAL RULE 3 — Always generate CSV via Python csv.writer, never raw string

**After writing all test case content, ALWAYS run a Python validation script:**

```python
import csv

# Step 1: Write via csv.writer — handles quoting automatically
with open('output.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
    writer.writerows(all_rows)

# Step 2: Validate — re-read and check every row
with open('output.csv', 'r', encoding='utf-8') as f:
    rows = list(csv.reader(f))

bad_cols = [(i+1, len(r)) for i, r in enumerate(rows) if len(r) != 15]
embedded_commas = [(i+1, r[0][:40]) for i, r in enumerate(rows[1:]) for cell in r if ',' in cell]
embedded_newlines = [(i+1,) for i, r in enumerate(rows[1:]) for cell in r if '\n' in cell or '\r' in cell]

assert not bad_cols, f"Column count errors: {bad_cols}"
assert not embedded_commas, f"Embedded commas found: {embedded_commas}"
assert not embedded_newlines, f"Embedded newlines found: {embedded_newlines}"
print(f"PASS: {len(rows)-1} rows, all 15 cols, no commas, no newlines")
```

Do NOT ship the CSV without running this check. If any assertion fails, fix the offending cells before outputting.

**Section hierarchy:**
Use ` > ` (space-arrow-space) as path separator.
Example: `Agentic > AI Scheduled Job > Empty State`

---

## Sample CSV (correct single-line format)

```csv
Section,Role,Channel,Title,Test Data,Preconditions,Steps,Expected Result,Platform,TestMethod,Type,P,References,Release version,QA Responsibility
Agentic > Base Skill > Internal Library,User,Web,Verify user can enable internal library mode,User with library permission,User logged in and has permission to use internal library,1. Login to the system. 2. Open Agentic chat. 3. Click on tool selector below message input. 4. Turn on Use internal library option.,Internal library mode is activated and shown as enabled,Web,Manual,Regression Test,P1,Library Mode UI,Eko 17.29,Peam
Agentic > Base Skill > Internal Library,User,Web,Verify system uses internal data when user asks company-related information,Company internal content,Internal library mode enabled,1. Turn on Use internal library. 2. Ask about company policy or internal document. 3. Send message.,System answers using relevant internal company information,Web,Manual,Smoke Test,P0,Auto Matching Logic,Eko 17.29,Peam
```

**Notice:** No quotes wrapping fields unless the field contains a comma. No embedded newlines anywhere.
Steps use `. ` separator and fit on one line.

---

## Import Instructions

1. Save as UTF-8 CSV
2. In TestRail: target Test Suite → **Import Cases**
3. Select **CSV** format
4. Map columns to the schema above on the mapping screen
5. Review section hierarchy and step formatting in preview
6. Confirm import

---

## Notes on Updating Existing Cases

TestRail CSV import creates new cases by default — it does not update existing ones.
To update: use TestRail API `POST /api/v2/update_case/:case_id` or TestRail bulk update.
To avoid duplicates on re-import, check for existing titles in the target section first.
