# /qa:write-ac [Sprint Board URL]

**Triggers:** test-planner + ac-reviewer (hybrid pipeline)
**References:** [agent-test-planner.md](../references/agent-test-planner.md), [agent-ac-reviewer.md](../references/agent-ac-reviewer.md), [jira-workflows.md](../references/jira-workflows.md)

## What This Command Does

After test cases have been generated and reviewed (via `/qa:test-plan`), this command runs a
**10-phase pipeline** to generate, review, fix, and post Acceptance Criteria on Jira sprint tickets:

```
Phase 1  → Smart Sprint Selection (parse URL or discover active sprints)
Phase 2  → Prerequisite Check (test plan + test cases must exist)
Phase 3  → Understand Test Plan (read and internalize spec + test cases)
Phase 4  → Fetch Sprint Tickets (all tickets, present lanes for selection)
Phase 5  → Generate AC (map tickets → spec → test cases → write AC)
Phase 6  → Internal AI Review (agent-ac-reviewer 6-point checklist)
Phase 7  → Auto-Fix (apply review findings silently)
Phase 8  → User Review (present final AC batch for approval)
Phase 9  → Post to Jira & Verify (comment + re-read to confirm)
Phase 10 → Release Notes (generate sprint release notes file)
```

⚠️ **Prerequisite:** Run `/qa:test-plan` first. This command relies on the test plan and
test cases already generated in the sprint folder.

## Sprint Scope & Usage

- **Frequency:** Once per sprint — after test planning is done and before QA begins.
- **Sprint Selection:** The board may show multiple sprint sections (e.g., "EGT 18.1", "Broccoli-F").
  Phase 1 detects all active sprints and lets the user choose which to target.
  Version numbers (18.0, 18.1, etc.) change every sprint — use sprint IDs, not names.
- **Sprint lifecycle:** After AC is posted, continue with testing. Run `/qa:end-sprint` at sprint end.

## Parameters

| Parameter | Required | Notes |
|---|---|---|
| `[Sprint Board URL]` | Yes | Jira board URL, optionally with sprint filter. e.g., `https://ekoapp.atlassian.net/jira/software/c/projects/AE/boards/257` or `...?sprints=4077` |

**Parsing the Sprint Board URL:**
- Extract `projects/{key}` → project key (e.g., `AE`)
- Extract `boards/{id}` → board ID (e.g., `257`)
- Extract `sprints={id}` → sprint ID (e.g., `4077`) — **optional**, if missing Phase 1 will discover

If the URL has `?sprints=XXXX`, use that sprint directly.
If not, Phase 1 will discover all active sprints and let the user choose.

## Live Data Sources

| Tool | Purpose | Call |
|---|---|---|
| Jira (Atlassian MCP) | Fetch sprint tickets, read ticket details | `mcp_atlassian_search_jira_issues`, `mcp_atlassian_read_jira_issue` |
| Jira (Atlassian MCP) | Comment AC on tickets | `mcp_atlassian_add_jira_comment` |
| Confluence (Atlassian MCP) | Read related specs if needed | `mcp_atlassian_read_confluence_page` |

⚠️ No `cloudId` parameter — the MCP server is already configured with the Atlassian instance.

---

## Execution Steps

### Phase 1 — Smart Sprint Selection

**Goal:** Determine which sprint to write AC for without hardcoding sprint names.

1. **Parse the board URL** — extract projectKey, boardId, and sprintId (if present).

2. **If sprintId is in the URL** → use it directly, skip to step 4.

3. **If no sprintId in URL** → discover active sprints:
   ```
   mcp_atlassian_search_jira_issues(
     jql="project = {projectKey} AND sprint in openSprints() ORDER BY rank ASC",
     maxResults=1
   )
   ```
   From the results, extract unique sprint names and IDs. Present the choices:

   ```
   🏃 Active sprints on board {boardId}:
   
   | # | Sprint Name  | Sprint ID | Tickets |
   |---|-------------|-----------|---------|
   | 1 | EGT 18.1    | 4011      | ~25     |
   | 2 | Broccoli-F  | 4077      | ~18     |
   
   Which sprint should I write AC for? (enter number or sprint ID)
   ```

4. **Confirm the target sprint** — once selected, store:
   - `sprintId` — for JQL queries
   - `sprintName` — for display and release notes
   - `projectKey` — for JQL queries

5. **Identify the sprint folder** — check the workspace for the current sprint folder
   (e.g., `agentic-18.2/`). This is where the test plan and test cases should be.

---

### Phase 2 — Prerequisite Check

**Goal:** Verify that `/qa:test-plan` has been run and artifacts exist.

1. **Scan the sprint folder** for test plan and test case files:
   - Look for `{sprint-folder}/*-test-plan.md`
   - Look for `{sprint-folder}/*-testcases.csv`

2. **If BOTH exist** → report found and proceed:
   ```
   ✅ Prerequisites found:
      📄 Test Plan: agentic-18.2/ekoai-scheduled-jobs-test-plan.md
      📊 Test Cases: agentic-18.2/ekoai-scheduled-jobs-testcases.csv (168 cases)
   ```

3. **If MISSING** → abort with actionable guidance:
   ```
   ❌ Prerequisites missing — cannot generate AC without a test plan.
   
   Missing:
   - [ ] Test plan (.md) — not found in {sprint-folder}/
   - [ ] Test cases (.csv) — not found in {sprint-folder}/
   
   👉 Run `/qa:test-plan [Figma URL] [Confluence URL]` first to generate these artifacts.
      Then re-run `/qa:write-ac` to continue.
   ```
   **STOP HERE** — do not proceed without prerequisites.

---

### Phase 3 — Understand Test Plan & Cases

**Goal:** Read and internalize the test plan so AC generation is grounded in the spec.

1. **Read the test plan file** — extract:
   - Feature name and scope (In Scope / Out of Scope)
   - Functional areas and groups
   - Sources used (Confluence pages, Figma nodes)
   - Assumptions and flagged ambiguities
   - Coverage summary (groups, case counts, P0/P1/P2 mix)

2. **Read the test cases CSV** — parse and build an index:
   - Count total cases and cases per Section (feature group)
   - Map each Section to its test case ID range (e.g., "Dashboard & Statistics" → TC-001 to TC-008)
   - Identify test case types: Positive (Smoke/Sanity) vs Negative vs Edge Case per group

3. **Build a Feature Knowledge Map** — internal reference for AC generation:
   ```
   Feature: [name]
   Groups: [N] functional areas
   Total Cases: [N] (P: X, N: Y, E: Z)
   
   Group Index:
   - [Group 1]: TC-001 to TC-008 (2P, 2N, 4E) — covers: [brief scope]
   - [Group 2]: TC-009 to TC-020 (4P, 4N, 4E) — covers: [brief scope]
   ...
   ```

4. **Present understanding summary** to the user:
   ```
   📖 Feature Knowledge Loaded:
      Feature: EkoAI Scheduled Jobs
      Scope: 17 groups, 168 test cases
      Key areas: Dashboard, Create Wizard, Job Config, Execution, Permissions, API...
      
      Ready to fetch sprint tickets. Proceeding to Phase 4...
   ```

---

### Phase 4 — Fetch Sprint Tickets

**Goal:** Get all tickets in the target sprint and let the user select the focus scope.

1. **Fetch all tickets** in the sprint using JQL:
   ```
   mcp_atlassian_search_jira_issues(
     jql="project = {projectKey} AND sprint = {sprintId} ORDER BY rank ASC"
   )
   ```
   ⚠️ The MCP caps results at 50 per call. If `totalResults > 50`, **paginate** with `startAt`.

2. **Group tickets by sprint lane** — The Jira board often shows tickets under different
   sprint section headers. Group them by their `sprint` field name:

   ```
   📋 Sprint Tickets Found: {total} tickets
   
   Lane: EGT 18.1 (sprint 4011)
   | # | Ticket   | Summary                    | Type    | Status        | Assignee |
   |---|----------|----------------------------|---------|---------------|----------|
   | 1 | AE-14270 | [EGT] Search enhancement   | Story   | In Progress   | Somchai  |
   | 2 | AE-14271 | [EGT] Filter optimization  | Task    | To Do         | Somchai  |
   
   Lane: Broccoli-F (sprint 4077)
   | # | Ticket   | Summary                    | Type    | Status        | Assignee |
   |---|----------|----------------------------|---------|---------------|----------|
   | 3 | AE-14288 | Dashboard page (ui)        | Story   | In Code Review| Pakkawat |
   | 4 | AE-14290 | Create scheduler (ui)      | Story   | In Progress   | Pakkawat |
   ...
   ```

3. **Ask user which lanes to target** (if multiple lanes exist):
   ```
   Which lane(s) should I write AC for?
   - [1] EGT 18.1 only
   - [2] Broccoli-F only
   - [3] All lanes
   ```

4. **Read each selected ticket's full details** — for each ticket in scope:
   ```
   mcp_atlassian_read_jira_issue(issueKey="AE-14288")
   ```
   Extract:
   - Issue key, summary, full description, status, assignee
   - Issue type (Story / Task / Sub-task / Bug)
   - **Existing AC** — check if the description already contains "Acceptance Criteria" or "AC:" section
   - Linked Confluence pages or Figma URLs in the description

5. **Duplicate AC Detection** — for each ticket, check:
   - Does the ticket description already contain an AC section?
   - Are there existing Jira comments with AC content?
   
   If existing AC found → flag it:
   ```
   ⚠️ AE-14288 already has AC in description. Options:
   - [A] Skip — keep existing AC
   - [B] Replace — overwrite with new AC (will note "Updated by QA Agent")
   - [C] Append — add new AC as a separate comment
   ```

---

### Phase 5 — Generate Acceptance Criteria

**Goal:** Create AC for each in-scope ticket, grounded in the test plan and test cases.

#### 5.1 — Map Tickets to Spec & Test Cases

For each ticket, perform mapping:

1. **Match to feature spec sections** — which group(s) does this ticket map to?
   - Exact match: ticket summary mentions a group name ("Dashboard", "Scheduler")
   - Semantic match: ticket description describes behavior in a spec group
   - No match: ticket is unrelated to current spec → classify as UNRELATED

2. **Match to test cases** — which TC-IDs exercise this ticket's scope?
   - By feature group (e.g., "Dashboard & Statistics" → TC-001 to TC-008)
   - By specific functionality described in the ticket

3. **Classify the ticket:**
   - ✅ **COVERED** — has matching spec section AND test cases → generate AC
   - ⚠️ **PARTIAL** — matches spec but test cases don't fully cover it → generate AC + flag gap
   - ❌ **UNRELATED** — no spec/test case match → skip, note in output
   - 🔍 **AMBIGUOUS** — ticket is vague, could match multiple areas → generate AC with assumptions

#### 5.2 — Generate AC per Ticket

For each COVERED or PARTIAL ticket, generate AC using the appropriate template:

**Template: Story / Task**
```
### Acceptance Criteria (QA Generated)

**Scope:** [1-line description of what this ticket delivers]

1. ✅ [Positive — primary happy path behavior] — TC-XXX
2. ✅ [Positive — secondary expected behavior] — TC-XXX
3. ❌ [Negative — what MUST be rejected/handled correctly] — TC-XXX
4. ⚠️ [Edge case — boundary, empty state, or extreme input] — TC-XXX
5. ✅ [Additional criterion if needed — max 6 total] — TC-XXX

---
**Icon Legend:** ✅ = Positive (expected behavior) · ❌ = Negative (error/rejection) · ⚠️ = Edge case (boundary/race condition)

**Ref:** [Spec group name] · Test Cases: [TC-IDs e.g. TC-015, TC-016, TC-018]
**Generated:** [date] by QA Agent from test plan
```

**Template: Bug**
```
### Acceptance Criteria (Bug Fix)

**Scope:** Fix for [bug description]

1. ✅ [Original bug is fixed — specific verification of the fix] — TC-XXX
2. ❌ [Regression — related area still works correctly] — TC-XXX
3. ⚠️ [Edge case around the fix — boundary condition] — TC-XXX

---
**Icon Legend:** ✅ = Positive (expected behavior) · ❌ = Negative (error/rejection) · ⚠️ = Edge case (boundary/race condition)

**Ref:** [Related spec group if applicable] · Test Cases: [TC-IDs]
**Generated:** [date] by QA Agent from test plan
```

**Template: Sub-task**
```
### Acceptance Criteria (QA Generated)

**Scope:** [Sub-task deliverable within parent story scope]

1. ✅ [Sub-task specific criterion — narrow scope] — TC-XXX
2. ✅ [Integration — works correctly with parent story] — TC-XXX

---
**Icon Legend:** ✅ = Positive (expected behavior) · ❌ = Negative (error/rejection) · ⚠️ = Edge case (boundary/race condition)

**Ref:** Parent: [Parent issue key] · Test Cases: [TC-IDs]
**Generated:** [date] by QA Agent from test plan
```

**AC Writing Rules:**
- **Max 6 items** per ticket — be concise (test cases handle the depth)
- **Start each item with a verb** — "Shows", "Rejects", "Navigates", "Displays", "Returns"
- **No implementation details** — describe WHAT, not HOW
- **Include at least 1 negative criterion** for Story/Task types
- **Reference test case IDs** — traceability back to the test plan
- **Skip obvious criteria** — "page loads" is not an AC unless loading has special behavior
- **Adapt by issue type** — see templates above (Story ≠ Bug ≠ Sub-task)

---

### Phase 6 — Internal AI Review

**Goal:** Review all generated AC using the 6-point checklist before showing to the user.

⚠️ **This phase runs silently — do NOT show the review to the user.**
The user only sees the final result after auto-fix. This is an internal quality gate.

1. **Apply the AC Reviewer agent** — follow the full review process in
   [agent-ac-reviewer.md](../references/agent-ac-reviewer.md):

   For each ticket's AC, evaluate:
   | Dimension | Check |
   |-----------|-------|
   | **Testability** | Every item has clear pass/fail in <2 min? |
   | **Completeness** | Positive + Negative + Edge case items present? |
   | **Traceability** | Ref line has valid TC-IDs that exist in the CSV? |
   | **Consistency** | No contradictions across the ticket batch? |
   | **Scope Match** | AC matches ticket scope — no over/under reach? |
   | **Developer Clarity** | Specific enough for dev to verify without guessing? |

2. **Flag anti-patterns:**
   - Copy-paste AC (same text on multiple tickets)
   - Spec echo (AC just restates the ticket summary)
   - Implementation AC ("use X framework" — that's HOW, not WHAT)
   - Kitchen sink AC (>6 items → ticket should be split)
   - Orphan AC (item with no matching test case)

3. **Produce internal review table** (for auto-fix, not shown to user):

   | Ticket | Verdict | Issues | Auto-Fixable |
   |--------|---------|--------|-------------|
   | AE-XXX | PASS    | 0      | —           |
   | AE-YYY | WARN    | 2      | Yes         |
   | AE-ZZZ | FAIL    | 3      | 2 yes, 1 no |

---

### Phase 7 — Auto-Fix

**Goal:** Apply all review findings from Phase 6 silently. No user prompt needed.

1. **Process each finding:**
   - **PASS** → no changes needed
   - **WARN** → apply the suggested fix from the review
   - **FAIL** → apply auto-fixable items; for non-auto-fixable items, add an
     `⚠️ Note:` annotation to the AC so the user can see it in Phase 8

2. **Typical auto-fixes:**
   - Vague language → replace with specific, measurable criteria
   - Missing negative criterion → add one based on the test plan's negative test cases
   - Wrong TC-ID references → correct to valid IDs from the CSV
   - Scope creep → remove out-of-scope items
   - Missing Ref line → add from the ticket-to-group mapping

3. **Track changes** — for each auto-fixed ticket, record what changed:
   ```
   AE-YYY: Fixed 2 items
     - Item 3: "works correctly" → "Returns 200 with valid job payload"
     - Added: negative criterion "Rejects request with missing required field 'schedule'"
   ```

4. **Proceed immediately to Phase 8** after all fixes are applied.

---

### Phase 8 — User Review

**Goal:** Present the final, reviewed-and-fixed AC batch for user approval.

1. **Present the Sprint Health Score** — overall quality summary:
   ```
   📊 Sprint AC Health Score: 92% (Excellent)
   
   | Metric | Value |
   |--------|-------|
   | Tickets in scope | 12 |
   | AC generated | 10 |
   | Skipped (unrelated) | 2 |
   | Review: PASS | 8 |
   | Review: Auto-fixed | 2 |
   | Avg AC items/ticket | 4.3 |
   | Test case coverage | 85% (142/168 cases linked) |
   ```

2. **Present the full AC batch** in a summary table:

   | # | Ticket | Summary | Type | Status | Items | Match | Review |
   |---|--------|---------|------|--------|-------|-------|--------|
   | 1 | AE-14288 | Dashboard page (ui) | Story | In Code Review | 5 | ✅ COVERED | PASS |
   | 2 | AE-14290 | Create scheduler (ui) | Story | In Progress | 4 | ✅ COVERED | Auto-fixed |
   | 3 | AE-14296 | Performance tuning | Task | To Do | — | ❌ UNRELATED | Skipped |

3. **Show full AC for each ticket** — expand every ticket's AC below the table so the user
   can read each one in full. If any item was auto-fixed, mark it with `🔧` prefix.

4. **Wait for user commands:**
   - **"Confirm"** or **"ทำเลย"** → proceed to Phase 9
   - **"Edit AE-XXXX"** → let user modify specific AC, then re-present
   - **"Skip AE-XXXX"** → exclude from posting
   - **"Cancel"** → abort all (no Jira writes)

---

### Phase 9 — Post to Jira & Verify

**Goal:** Comment AC on each approved ticket, then verify the comments were posted.

#### 9.1 — Post Comments via Jira REST API (ADF Table Format)

Posting uses **Jira REST API v3 directly** with ADF (Atlassian Document Format) JSON.
Do NOT use `mcp_atlassian_add_jira_comment` — it cannot render tables.

**Method:** `POST /rest/api/3/issue/{issueKey}/comment` with `{"body": <ADF JSON>}`

**Authentication:** Basic auth using Jira API token from macOS Keychain:
```bash
export JIRA_EMAIL="apiwat@amitysolutions.com"
export JIRA_TOKEN=$(security find-generic-password -a "apiwat@amitysolutions.com" -s "jira-api-token" -w)
```

**Script location:** `/tmp/repost_adf_tables.py` (or `scripts/repost-ac-tables.py`)

⛔ **NEVER use these formats** — they DO NOT render via the API:
- Wiki markup: `||table||`, `{panel}`, `(/)` `(x)` `(!)`
- Markdown tables: `| col | col |`
- Plain text pipes: show as raw characters
- ADF JSON as string body in MCP tool: shows as literal JSON text

✅ **ALWAYS use ADF JSON** posted directly to Jira REST API v3.
✅ **ALWAYS use Unicode emoji** — `✅` `❌` `⚠️` — they render everywhere.
✅ **ALWAYS include the icon legend** at the bottom of every comment.
✅ **ALWAYS delete old AC comments** before posting new ones.

**ADF Table Structure:**
```json
{
  "version": 1,
  "type": "doc",
  "content": [
    {"type": "heading", "attrs": {"level": 3}, "content": [{"type": "text", "text": "Acceptance Criteria — QA Generated"}]},
    {
      "type": "table",
      "attrs": {"isNumberColumnEnabled": false, "layout": "default"},
      "content": [
        {"type": "tableRow", "content": [
          {"type": "tableHeader", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "#", "marks": [{"type": "strong"}]}]}]},
          {"type": "tableHeader", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Type", "marks": [{"type": "strong"}]}]}]},
          {"type": "tableHeader", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Criteria", "marks": [{"type": "strong"}]}]}]},
          {"type": "tableHeader", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "TC Ref", "marks": [{"type": "strong"}]}]}]}
        ]},
        {"type": "tableRow", "content": [
          {"type": "tableCell", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "1"}]}]},
          {"type": "tableCell", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "✅ Positive"}]}]},
          {"type": "tableCell", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Criterion description here"}]}]},
          {"type": "tableCell", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "TC-001"}]}]}
        ]}
      ]
    },
    {"type": "rule"},
    {"type": "paragraph", "content": [
      {"type": "text", "text": "Icon Legend: ", "marks": [{"type": "strong"}]},
      {"type": "text", "text": "✅ Positive (expected behavior) · ❌ Negative (error/rejection) · ⚠️ Edge case (boundary/race condition)"}
    ]},
    {"type": "paragraph", "content": [
      {"type": "text", "text": "Ref: ", "marks": [{"type": "strong"}]},
      {"type": "text", "text": "[Spec group] · Test Cases: [TC-IDs]"}
    ]},
    {"type": "paragraph", "content": [
      {"type": "text", "text": "Generated: ", "marks": [{"type": "strong"}]},
      {"type": "text", "text": "[date] by QA Agent from test plan"}
    ]}
  ]
}
```

The icon legend is **mandatory on every AC comment** — never omit it.

⚠️ **Post one ticket at a time** — if any fails, report the error and continue with the rest.
⚠️ **Delete before posting** — use `DELETE /rest/api/3/issue/{key}/comment/{id}` on old AC comments first.

#### 9.2 — Verify Comments

After all comments are posted, **re-read each ticket** to verify:
```
mcp_atlassian_read_jira_issue(issueKey="AE-14288")
```

Check that the comment appears in the ticket's comment list. Report:

| # | Ticket | Post | Verify | Items |
|---|--------|------|--------|-------|
| 1 | AE-14288 | ✅ Posted | ✅ Verified | 5 AC items |
| 2 | AE-14290 | ✅ Posted | ✅ Verified | 4 AC items |
| 3 | AE-14292 | ❌ Failed | — | Error: 403 Forbidden |

If any ticket fails verification:
- Log the error
- Suggest manual check: "Please verify AE-14292 manually — the API returned 403."

---

### Phase 10 — Release Notes

**Goal:** Generate a sprint release notes file summarizing everything done.

1. **Create the release notes file** in the sprint folder:
   - **Path:** `{sprint-folder}/release-notes-{sprint-name-kebab}.md`
   - Example: `agentic-18.2/release-notes-broccoli-f.md`

2. **Release Notes Format:**

```markdown
# Release Notes: [Sprint Name]
*Generated: [date] · Sprint ID: [sprintId]*
*Board: [board URL]*

## Sprint Summary

| Metric | Value |
|--------|-------|
| Total tickets in sprint | N |
| Tickets with AC | N |
| Tickets skipped (unrelated) | N |
| Test cases linked | N / Total |
| AC Health Score | X% |

## Tickets with Acceptance Criteria

### [Group Name — e.g., Dashboard & Statistics]

#### AE-14288 — Dashboard page (ui)
- **Type:** Story · **Status:** In Code Review · **Assignee:** Pakkawat
- **AC Items:** 5
- **Test Cases:** TC-001, TC-002, TC-003, TC-005, TC-007
- **Scope:** Dashboard displays scheduled job statistics with filtering and sorting

#### AE-14290 — Create scheduler (ui)
...

### [Group Name — e.g., Scheduler Wizard]
...

## Skipped Tickets

| Ticket | Summary | Reason |
|--------|---------|--------|
| AE-14296 | Performance tuning | Unrelated to current feature spec |

## Coverage Gaps

| Gap | Severity | Notes |
|-----|----------|-------|
| No test cases for [area] | Medium | Consider adding in next sprint |
| Ticket AE-XXXX is PARTIAL coverage | Low | 2 test cases missing for edge cases |

## Test Plan Reference

- **Test Plan:** [{sprint-folder}/{feature-slug}-test-plan.md]
- **Test Cases:** [{sprint-folder}/{feature-slug}-testcases.csv] ({N} cases)
- **TestRail Suite:** S{suite_id} ({N} cases imported)
```

3. **Present the release notes summary** to the user:
   ```
   📝 Release Notes Created:
      File: agentic-18.2/release-notes-broccoli-f.md
      Tickets: 10 with AC · 2 skipped
      Coverage: 85% test cases linked
      
   ✅ /qa:write-ac complete! All AC posted and verified.
   ```

---

## Feature Spec Output Format

The feature spec is generated as part of Phase 5 mapping. If a standalone spec file is useful,
create it in the sprint folder:

```markdown
# Feature Spec: [Feature Name]
*Sprint: [Sprint Name] (ID: [Sprint ID])*
*Generated: [date] · Sources: [Confluence page IDs] · [Figma file/node IDs]*

## Overview
[2–3 sentence summary of the feature's purpose and scope]

## Functional Requirements
### [Area 1 — e.g., Dashboard & Statistics]
- [FR-001] [Requirement description]
- [FR-002] [Requirement description]

### [Area 2 — e.g., Create Scheduler Wizard]
- [FR-010] [Requirement description]

## UI States (from Figma)
| Screen | States Covered |
|---|---|
| Dashboard | Default / Empty / Error / Large data |
| Create Wizard | Step 1 / Step 2 / Validation errors |

## API Contracts (from Confluence)
| Endpoint | Method | Key Behaviors |
|---|---|---|
| /api/v1/scheduled-jobs | POST | Creates job / validates cron / returns 201 |

## Business Rules
- [BR-001] [Rule description]

## Out of Scope
- [Items explicitly excluded from this sprint/feature]

## Assumptions & Open Questions
- [Items flagged during test planning that remain unresolved]

## Test Coverage Summary
| Feature Group | Test Cases | Coverage |
|---|---|---|
| Dashboard & Statistics | TC-001 to TC-008 | 8 cases (2P/2N/4E) |
Total: [N] test cases across [M] groups
```

---

## Output Summary

The full pipeline produces these outputs (shown to user at each phase boundary):

| Phase | Output | Visible to User |
|-------|--------|----------------|
| 1 | Sprint selection confirmation | ✅ Yes |
| 2 | Prerequisite check result | ✅ Yes |
| 3 | Feature knowledge summary | ✅ Yes (brief) |
| 4 | Sprint ticket table by lane | ✅ Yes |
| 5 | AC generated (internal) | ❌ No (goes to review) |
| 6 | Review findings (internal) | ❌ No (goes to auto-fix) |
| 7 | Auto-fix applied (internal) | ❌ No (merged into final) |
| 8 | Final AC batch + health score | ✅ Yes (user approves) |
| 9 | Post results + verification | ✅ Yes |
| 10 | Release notes file | ✅ Yes |

---

## Error Handling

| Error | Phase | Recovery |
|-------|-------|----------|
| No sprint in URL, no active sprints found | 1 | Ask user for sprint ID manually |
| Test plan / CSV not found | 2 | STOP — tell user to run `/qa:test-plan` first |
| JQL returns 0 tickets | 4 | Verify sprint ID is correct; ask user to check board |
| All tickets are UNRELATED | 5 | Warn user — spec may not match this sprint's scope |
| MCP add_jira_comment fails (403/404) | 9 | Log error, continue with other tickets, report at end |
| Comment verification fails | 9 | Note for manual check, do not retry automatically |

---

## GitHub Actions Integration

This skill coexists with the **Daily AC Scan** GitHub Actions workflow:

| Execution Context | File | Trigger | Use Case |
|---|---|---|---|
| VS Code (this skill) | `commands/write-ac.md` | `/qa:write-ac [URL]` | Full 10-phase pipeline with LLM review + user approval |
| GitHub Actions | `.github/workflows/daily-ac-scan.yml` | Manual dispatch or daily cron (09:00 BKK) | Automated scan — find tickets without AC |

**Key differences:**
- **This skill** uses LLM for semantic matching, AC generation, and 6-point review → higher quality
- **GitHub Actions** uses keyword-based matching (`scripts/daily-ac-agent.py`) → catches missed tickets daily
- Both use the same ADF table format and Jira REST API v3 for posting
- The daily job runs in `report-only` mode by default (safe) — manual trigger can `post`

**Root cause fix (2025-03-24):**
Previous `repost-ac-tables.py` used a hardcoded `TICKETS = [...]` list which missed tickets added
to the sprint after the initial run. The `daily-ac-agent.py` script dynamically fetches ALL sprint
tickets via `/rest/agile/1.0/sprint/{id}/issue` with pagination, eliminating this failure mode.

**GitHub Actions modes:**
```bash
# Report-only (scheduled default) — just lists tickets needing AC
python3 scripts/daily-ac-agent.py --project AE --report-only

# Dry-run — shows what would be posted
python3 scripts/daily-ac-agent.py --sprint-id 4077 --dry-run

# Post — actually posts AC comments
python3 scripts/daily-ac-agent.py --sprint-id 4077

# Force re-post — overwrites existing AC
python3 scripts/daily-ac-agent.py --sprint-id 4077 --force
```

**Required GitHub Secrets:**
- `JIRA_EMAIL` — Jira user email
- `JIRA_TOKEN` — Jira API token
