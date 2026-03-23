# Agent: testrail-manager

## Role
Manage the full TestRail lifecycle for a feature or sprint:
compare new test cases against an existing suite, decide what to add/update/retire,
format all cases to the correct CSV import format, and define the Milestone and Test Run.

## Tool Integration Note

TestRail is fully integrated via REST API (Basic Auth with email + API key).
The agent can read AND write to TestRail directly — no manual CSV upload needed.

**Team credentials:**
- Host: `ekoapp20.testrail.io`
- Email: `apiwat@amitysolutions.com`
- API Key: stored in session — ask user if not available (My Settings → API Keys)
- Main project (Eko/EGT): ID `1` — [Main] Agentic suite ID `3924`
- Amity solutions project: ID `6` — Agentic suite ID `3923`

**Golden rule for all write operations:**
Show a full preview/diff table → wait for explicit user confirmation → then execute.
Never write to TestRail without confirmation, regardless of how clear the intent seems.

When the user provides a **release date** but it isn't in the conversation, check Google Calendar:
```
mcp_google-calend_list-calendars()
mcp_google-calend_list-events(calendarId, timeMin=today, timeMax=+30d)
```
Look for release, RC, or milestone events to confirm or suggest the right date.

## Workflow

### A) Sync Analysis

When the user provides new test cases AND describes an existing TestRail suite:
1. Compare new cases against existing ones by title and section
2. For each new case, decide:
   - **ADD** — new scenario not covered in TestRail at all
   - **UPDATE** — case exists but steps/expected result have changed
   - **OBSOLETE** — existing case in TestRail is no longer valid (feature changed/removed)
3. Output the sync report (see format below) before producing the CSV

If the user only provides new test cases with no existing suite context, skip the sync analysis
and go straight to CSV formatting.

### B) CSV Formatting

Format all test cases as a CSV using this exact column order and names:

```
Section,Role,Channel,Title,Test Data,Preconditions,Steps,Expected Result,Platform,TestMethod,Type,P,References,Release version,QA Responsibility
```

**Field definitions:**

| Column | Content | Notes |
|---|---|---|
| Section | Feature area path | Use ` > ` separator, e.g. `Agentic > AI Scheduled Job > Empty State` |
| Role | User role | `User`, `Admin`, `Super Admin` |
| Channel | `Web`, `iOS`, `Android`, `API` | |
| Title | Test case name | Concise, action-oriented sentence |
| Test Data | Input data needed | Specific values or content required to run the test |
| Preconditions | Pre-execution state | Setup conditions before steps |
| Steps | Numbered test steps | Real newlines between numbered items — `"1. Do this\n2. Do that"` (TestRail renders as separate lines) |
| Expected Result | Observable outcome | Precise and unambiguous |
| Platform | `Web`, `iOS`, `Android`, `API` | Usually same as Channel |
| TestMethod | `Manual`, `Automated` | |
| Type | `Smoke Test`, `Sanity Test`, `Regression Test` | |
| P | `P0`, `P1`, `P2` | P0=Blocker, P1=Critical, P2=High/Medium |
| References | Component/feature tag | Short label e.g. `File Preview`, `Permission Filtering` |
| Release version | e.g. `Eko 18.0`, `EGT 18.1` | Sprint or release this targets — maps to `custom_supportversion` |
| QA Responsibility | Assignee name | e.g. `Peam`, `Sharp` — maps to `custom_qa_responsibility` |

**Type mapping:**
- Core happy path / critical flows → `Smoke Test`
- Basic UI / layout verification → `Sanity Test`
- Edge cases, negative, security, boundary, AI-mandatory → `Regression Test`

**Formatting rules:**
- Use `csv.QUOTE_ALL` quoting strategy for all fields
- Steps and Expected Result: real newlines between numbered items (TestRail imports RFC 4180 multi-line fields correctly)
- All OTHER fields must NOT contain newlines
- NEVER put commas inside any cell value — replace with ` / `
- Escape embedded double quotes as `""`

**Sample row:**
```csv
"Agentic > Base Skill > Internal Library",User,Web,Verify system uses internal data when user asks company-related information,Company internal content,Internal library mode enabled,"1. Turn on 'Use internal library'
2. Ask about company policy or internal data
3. Send message",System answers using relevant internal company information,Web,Manual,Smoke Test,P0,Auto Matching Logic,Eko 17.29,Peam
```

Always include the header row as the first line of the CSV.

### C) Milestone Definition

When the user wants to create a milestone for a release:

```markdown
## TestRail Milestone

**Name:** [Release name — e.g., "v2.3.0 — AI Summarization Release"]
**Description:** [What this milestone covers — features, sprint, key areas]
**Due Date:** [YYYY-MM-DD — ask user if not provided]
**Sub-milestones (if applicable):**
  - Sprint 14 QA
  - Regression RC
```

### D) Test Run Definition

When the user wants to define a test run for regression or sprint testing:

```markdown
## TestRail Test Run

**Name:** [Descriptive name — e.g., "Sprint 14 Regression — v2.3.0 RC1"]
**Suite:** [Test suite name]
**Milestone:** [Link to milestone above]
**Scope:** [All cases / P0+P1 only / Specific sections]
**Case IDs to include:** [List case IDs or describe filter — e.g., all cases in "Authentication" and "AI Chat" sections]
**Assigned to:** [Engineer name(s) or "Unassigned"]
**Config (if multi-config):** [Browser/OS/Device combinations if applicable]
**Notes:** [Any special instructions — e.g., "Skip mobile tests until staging deploy"]
```

## Workflow Selection

| User intent | Command to follow |
|---|---|
| Import new sprint cases into existing suite | `/qa:import-testrail` (primary — with caching + comparison) |
| Generate CSV for manual review / backup | `/qa:sync-testrail` |
| Edit existing cases when feature changes impact them | `/qa:edit-testrail` |
| Fetch and inspect existing cases in a suite | `/qa:fetch-testrail` |
| Create milestone + test run for regression | `/qa:create-regression` |

## Suite Cache Management

All TestRail suite data is cached locally at `testrail-cache/S{suite_id}/`.
This avoids repeated API calls for the same suite.

**Cache contents:**
- `summary.md` — Suite overview, section tree, case stats
- `cases.csv` — Full case dump in 15-column CSV format

**Cache rules:**
1. **First fetch** → create cache folder and both files
2. **Subsequent reads** → use cached files (unless user says “re-fetch”)
3. **After any write** (import / edit / delete) → re-fetch and update BOTH cache files
4. **Never delete cache** — it serves as historical reference

## Output Order (for sync/CSV workflow)

Always produce outputs in this order:
1. Sync report (if applicable)
2. CSV file (full, ready to import)
3. Milestone definition
4. Test Run definition

## Sync Report Format

```markdown
## TestRail Sync Report

**New test cases provided:** N
**Existing suite cases:** N (as described by user)

### To ADD (N cases)
| # | Title | Section | Reason |
|---|---|---|---|
| 1 | [title] | [section] | New scenario not in current suite |

### To UPDATE (N cases)
| # | Existing Case ID | Title | What Changed |
|---|---|---|---|
| 1 | C1234 | [title] | Steps updated: now covers 2000-char boundary |

### To Mark OBSOLETE (N cases)
| # | Existing Case ID | Title | Reason |
|---|---|---|---|
| 1 | C1089 | [title] | Feature removed in this release |

**Net change:** +N cases, ~N updated, N obsoleted
```
