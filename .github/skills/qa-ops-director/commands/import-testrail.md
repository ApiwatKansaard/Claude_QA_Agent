# /qa:import-testrail [test cases] [suite_id] [project_id]

**Triggers:** testrail-manager agent
**References:** [agent-testrail-manager.md](../references/agent-testrail-manager.md), [testrail-api.md](../references/testrail-api.md), [testrail-csv.md](../references/testrail-csv.md)

## What This Command Does

Import test cases directly into TestRail via API — no manual CSV upload required.
Infers target sections from the `Section` column, creates missing sections automatically,
shows a full import preview for user review, then creates cases via `POST /add_case`.

## Parameters

| Parameter | Required | Notes |
|---|---|---|
| `[test cases]` | Yes | Pasted inline, from `/qa:test-plan` output, or uploaded CSV |
| `[suite_id]` | No | TestRail suite ID — ask if ambiguous |
| `[project_id]` | No | TestRail project ID — defaults to `1` (main Eko project) |

**Team defaults:**
- Host: `ekoapp20.testrail.io`
- Default project: `1` (Eko/EGT testing)
- Default Agentic suite: `3924` ([Main] Agentic in project 1)

If `[suite_id]` is not provided, list the available suites from the API and ask the user to confirm which one to import into.

## Pre-Import Review (REQUIRED)

**Always show this review table before importing anything:**

```markdown
## Import Preview — [Suite Name] (S[suite_id])

| # | Section Path | Title | Priority | Type |
|---|---|---|---|---|
| 1 | Agentic > AI Scheduled Job > Create Scheduler | Verify user can create a new scheduler | P0 | Smoke Test |
| 2 | Agentic > AI Scheduled Job > Create Scheduler | Verify required fields show validation errors | P1 | Regression Test |
...

**Total:** N cases across X sections
**New sections to create:** [list any sections that don't exist yet]
**Target suite:** [suite name] (S[suite_id]) — Project [project_name]

Confirm import? (yes / cancel / adjust)
```

**Do NOT proceed to import until the user explicitly confirms.**

## Execution Steps

1. **Parse test cases** — accept CSV rows or inline test case list. Map to the 15-column schema.

2. **Authenticate** — use stored API key or ask:
   > "Please provide your TestRail API key (My Settings → API Keys)."

3. **List suites** (if suite_id not given):
   ```
   GET /get_suites/{project_id}
   ```
   Present suite names and IDs, ask user to confirm target.

4. **Fetch existing sections**:
   ```
   GET /get_sections/{project_id}&suite_id={suite_id}&limit=250
   ```
   Build a section path → ID map.

5. **Build import plan** — for each case:
   - Parse `Section` column into path segments
   - Match against existing sections
   - Flag sections that need to be created

6. **Show preview** — present the review table above and wait for confirmation.

7. **Execute import** (after user confirmation):
   - For each unique section path: resolve or create via `POST /add_section`
   - For each case: `POST /add_case/{section_id}` with mapped fields
   - Add small delay between calls for large batches (>50 cases)

8. **Report results**:
   ```markdown
   ## Import Complete

   ✅ Created N test cases in [Suite Name]
   📂 Sections created: X new, Y existing

   | Case ID | Title | Section |
   |---|---|---|
   | C10001 | [title] | [section path] |
   ...

   🔗 View suite: https://ekoapp20.testrail.io/index.php?/suites/view/{suite_id}
   ```

## Field Mapping (CSV → TestRail API)

| CSV Column | TestRail API Field | Notes |
|---|---|---|
| Title | `title` | Direct |
| Preconditions | `custom_preconds` | Direct |
| Steps | `custom_steps` | Newlines preserved |
| Expected Result | `custom_expected` | Direct |
| References | `refs` | Direct |
| P | `priority_id` | P0→4 (Critical), P1→3 (High), P2→2 (Medium) |
| Type | `type_id` | Smoke Test→19, Regression Test→9, Sanity Test→11 |
| Section | Resolved to `section_id` | Via section resolution pattern |

## Error Handling

| Error | Action |
|---|---|
| Section not found + can't create | Ask user for correct section path |
| 400 Bad Request on add_case | Show the failing row, skip and continue, report at end |
| 401/403 | Stop and report — credentials issue |
| Partial failure (some cases created, some failed) | Report what succeeded and what failed |
