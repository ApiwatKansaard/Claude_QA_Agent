# Sprint Archive: sharp-test-001
*Archived: 2026-03-27 · Sprint ID: sharp-test-001*
*Quick Filter: Broccoli*

## Artifacts

| File | Type | Description |
|---|---|---|
| ekoai-scheduled-jobs-test-plan.md | Test Plan | 177 test cases across 17 sections |
| ekoai-scheduled-jobs-testcases.csv | Test Cases CSV | 177 rows, all TestRail IDs populated (C1548489–C1549227) |
| generate-csv.py | Script | CSV generator/validator |

## Sprint Stats

- **Test cases generated:** 177
  - Smoke: 70 · Sanity: 10 · Regression: 97
  - Web: 67 · API: 110
- **TestRail import:** 177 cases imported to suite S5277
- **TestRail milestone:** M904 — AI Scheduled Jobs — Sprint Release
- **Smoke run:** R6323 (70 cases) — Passed: 37 · Failed: 5 · Blocked: 13 · Untested: 15
- **Regression run:** R6324 (107 cases) — Passed: 50 · Failed: 4 · Blocked: 21 · Untested: 32
- **Automation fixes shipped:**
  - BUG-1: Ant Design React input — nativeInputValueSetter pattern
  - BUG-2: Audience tab strict mode — span.filter({ hasText: /^Audience$/ })
  - BUG-4: Update Audience button — isEnabled() guard before click
  - TestRail include_all fix — create-regression.md Phase 6/7
  - beforeAll fixture pattern for 37 Blocked tests (job-factory.ts)
- **Skill updates:**
  - create-regression.md: include_all: false now enforced
  - best-practices.md §9: Prerequisite Data — beforeAll Fixture Pattern
  - triage-rules.md: auto-fix rule for Blocked/Skipped prerequisite pattern

## Coverage by Section

| Section | Cases | Channel |
|---|---|---|
| Action Step | 10 | API |
| API Endpoints | 15 | API |
| Callback | 10 | API |
| Create Job | 12 | Web |
| Cutoff Timeout | 7 | API |
| Dashboard | 9 | Web |
| Database and Infra | 10 | API |
| History Logs | 12 | Web |
| Home Page Delivery | 13 | API |
| Job Configuration | 12 | Web |
| Process Step | 14 | API |
| Race Conditions | 6 | API |
| Recipients | 13 | Web |
| Security | 9 | API |
| Status Check | 7 | API |
| Trigger Step | 9 | API |
| Widget Rendering | 9 | API |

## Known Gaps (Untested — no automation)

| Section | Count | Reason |
|---|---|---|
| API Endpoints | 15 | Playwright API project not covering these endpoints yet |
| Database & Infra | 10 | Requires DB-level test framework |
| Race Conditions | 6 | Requires concurrent test setup |
| Dashboard | 6 | Cases C1548492–C1548495, C1549219–C1549220 — not yet scripted |

## Data Sources

- **Confluence:** AI Scheduled Jobs feature spec
- **Jira:** project AE, Quick Filter: Broccoli
- **TestRail:** project 1, suite S5277 (ekoapp20.testrail.io)
- **Automation repo:** Claude_QA_Automation/tests/e2e/scheduled-jobs/ + tests/api/scheduled-jobs/

## How to Access

These files are preserved exactly as they were at end of sprint.
TestRail cases remain in suite S5277 and are reusable in future sprints.
