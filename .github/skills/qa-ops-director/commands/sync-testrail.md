# /qa:sync-testrail [test cases] [suite name] [milestone name] [release date]

**Triggers:** testrail-manager agent
**References:** [agent-testrail-manager.md](../references/agent-testrail-manager.md), [testrail-csv.md](../references/testrail-csv.md)

## What This Command Does

Take reviewed test cases and produce everything needed to sync them into TestRail:
a sync decision report, an import-ready CSV, a milestone definition, and a test run definition.

## Parameters

| Parameter | Required | Notes |
|---|---|---|
| `[test cases]` | Yes | Pasted inline or from `/qa:review-testcases` output |
| `[suite name]` | Yes | Name of the target TestRail suite |
| `[milestone name]` | Yes | Name for the milestone (e.g., "v2.3.0 — AI Chat Release") |
| `[release date]` | Yes | Due date for the milestone (YYYY-MM-DD or natural language) |

If any required parameter is missing, ask for it before proceeding.
If the user also describes their existing TestRail suite contents, perform the sync analysis.
If not, skip sync analysis and proceed directly to CSV formatting.

## Live Data Sources

| Tool | Purpose | Call |
|---|---|---|
| Google Calendar MCP | Look up release date if not provided | `mcp_google-calend_list-events`, `mcp_google-calend_list-calendars` |
| TestRail REST API | Fetch existing cases for sync analysis | See [testrail-api.md](../references/testrail-api.md) |
| TestRail CSV import | Push new/updated cases into TestRail | QA engineer imports CSV manually |

**When the user wants sync analysis against existing TestRail cases:**
Instead of asking the user to describe existing cases manually, offer to fetch them via the API:
> "I can pull existing cases from TestRail directly via API for the sync comparison.
> Please provide your TestRail email and API key (My Settings → API Keys), and I'll fetch them now."

If they prefer manual description, accept that too and skip the API call.

**If `[release date]` is not provided in the command**, check Google Calendar:
```
mcp_google-calend_list-calendars()
mcp_google-calend_list-events(calendarId, timeMin=today, timeMax=+30d)
```
Look for events with "release", "RC", "v2.x", or "milestone" in the title.
Use the found date as the milestone due date, or ask the user to confirm.

## Execution Steps

1. **Sync analysis** (if user describes existing suite):
   Compare new test cases against existing ones:
   - **ADD** — new scenario not in TestRail
   - **UPDATE** — same scenario, steps/expected result changed
   - **OBSOLETE** — existing case no longer valid
   Read [agent-testrail-manager.md](../references/agent-testrail-manager.md) for the sync decision framework.

2. **Format CSV** — follow the exact schema in [testrail-csv.md](../references/testrail-csv.md):
   ```
   Section,Role,Channel,Title,Test Data,Preconditions,Steps,Expected Result,Platform,TestMethod,Type,P,References,Release version,QA Responsibility
   ```
   - Steps and Expected Result: real newlines inside double-quoted field between numbered items
   - Use `csv.QUOTE_ALL` quoting strategy
   - Type: `Smoke Test` / `Sanity Test` / `Regression Test`
   - Priority: `P1` / `P2`
   - Section: use ` > ` hierarchy matching the suite structure

3. **Define milestone** using the `[milestone name]` and `[release date]` parameters.

4. **Define test run** scoped to the new/updated cases for regression coverage.

## Output Format

```markdown
# TestRail Sync Package — [Suite Name] / [Milestone Name]

## 1. Sync Report

| Action | Count | Cases |
|---|---|---|
| ADD | N | TC-002, TC-003, TC-004 |
| UPDATE | N | C1001 (merged with TC-001) |
| OBSOLETE | N | C1003 (deprecated endpoint) |
| RETAIN | N | C1002 (unchanged) |

**Net result:** [Final case count] active cases after sync.

## 2. TestRail Import CSV

[Full CSV block, UTF-8, header row first, all test cases]

## 3. Milestone Definition

**Name:** [milestone name]
**Description:** [What this milestone covers — features, sprint]
**Due Date:** [release date]

## 4. Test Run Definition

**Name:** [suite name] — [milestone name] Regression
**Suite:** [suite name]
**Milestone:** [milestone name]
**Scope:** [All new + updated cases / P0+P1 only / specific sections]
**Cases:** [List case titles or IDs, or filter criteria]
**Assigned to:** [Unassigned or specify]
**Notes:** [Any execution instructions]
```
