# /qa:write-ac [Sprint Board URL]

**Triggers:** test-planner + bug-analyzer (hybrid)
**References:** [agent-test-planner.md](../references/agent-test-planner.md), [jira-workflows.md](../references/jira-workflows.md)

## What This Command Does

After test cases have been generated and reviewed (via `/qa:test-plan`), this command:
1. Creates a **feature spec file** summarizing the feature knowledge gathered during test planning
2. Fetches all sprint tickets from the given board, filtered to **Broccoli** quick filter scope only
3. Maps each ticket to spec requirements and test cases
4. Generates concise **Acceptance Criteria** for each ticket
5. Comments the AC on each Jira ticket (with user confirmation)

⚠️ **Prerequisite:** Run `/qa:test-plan` first. This command relies on the spec data
and test cases already generated in the current session or saved to the workspace.

## Sprint Scope & Usage

- **Frequency:** This command is used **once per sprint** — after test planning is done and before QA begins.
- **Quick Filter:** Focus exclusively on tickets visible under the **"Broccoli"** quick filter on the board.
  The board may show multiple sprint sections (e.g., "EGT 18.1", "Agentic 18.1") — the version numbers
  (18.0, 18.1, etc.) change every sprint and should NOT be hardcoded. Use the sprint ID from the URL.
- **Sprint lifecycle:** After AC is posted, continue with testing. At sprint end, run `/qa:end-sprint`
  to archive all artifacts. Run `/qa:start-sprint` at the start of the next sprint.

## Parameters

| Parameter | Required | Notes |
|---|---|---|
| `[Sprint Board URL]` | Yes | Jira board URL with sprint filter, e.g. `https://ekoapp.atlassian.net/jira/software/c/projects/AE/boards/257?sprints=4077` |

**Parsing the Sprint Board URL:**
- Extract `projects/{key}` → project key (e.g., `AE`)
- Extract `boards/{id}` → board ID (e.g., `257`)
- Extract `sprints={id}` → sprint ID (e.g., `4077`)

If the URL doesn't contain a sprint param, ask user to specify which sprint.

## Live Data Sources

| Tool | Purpose | Call |
|---|---|---|
| Jira (Atlassian MCP) | Fetch sprint tickets, read ticket details | `mcp_atlassian_search_jira_issues`, `mcp_atlassian_read_jira_issue` |
| Jira (Atlassian MCP) | Comment AC on tickets | `mcp_atlassian_add_jira_comment` |
| Confluence (Atlassian MCP) | Read related specs if needed | `mcp_atlassian_read_confluence_page` |

⚠️ No `cloudId` parameter — the MCP server is already configured with the Atlassian instance.

## Execution Steps

### Step 1 — Create Feature Spec File

Before touching Jira, consolidate the knowledge from the test planning phase:

1. **Gather sources** from the current session:
   - Confluence spec data (fetched during `/qa:test-plan`)
   - Figma design analysis (UI elements, states, flows)
   - Generated test cases (final version after review + auto-fix)
   - Flagged ambiguities and assumptions

2. **Write the feature spec file** to the workspace:
   - Create folder: `specs/` in workspace root (if not exists)
   - Filename: `specs/{feature-name-kebab-case}.md`
   - Format: see [Feature Spec Output Format](#feature-spec-output-format) below

### Step 2 — Fetch Sprint Tickets (Broccoli Scope)

1. **Fetch all tickets in the sprint** using JQL:
   ```
   mcp_atlassian_search_jira_issues(
     jql="project = {projectKey} AND sprint = {sprintId} ORDER BY rank ASC"
   )
   ```
   ⚠️ The MCP caps results at 50 per call. If `totalResults > 50`, paginate with `startAt`.

2. **Filter to Broccoli scope** — The "Broccoli" quick filter on the Jira board is NOT accessible
   via JQL/MCP. Use **content-based filtering** to identify Broccoli tickets:

   **Strategy (in priority order):**
   a. **Check `fixVersion`/`sprint` name** — If sprint sections are named
      (e.g., "Agentic 18.1"), match tickets to the section relevant to the feature spec.
      Ignore the version number suffix — it changes every sprint.
   b. **Match by feature scope** — Compare each ticket's summary/description against
      the feature spec sections generated in `/qa:test-plan`. Tickets that match any
      spec section are in scope. Tickets that don't match any spec section → out of scope.
   c. **Match by assignee** — If the user provides known team members for Broccoli,
      filter by assignee.

   **If uncertain:** Present all potentially-matching tickets and ask the user to confirm scope.

3. **Collect ticket details** for each filtered ticket:
   - Issue key, summary, description, status, assignee
   - Issue type (Story / Task / Sub-task / Bug)
   - Any existing AC in the description (to avoid overwriting)
   - Linked Confluence pages or Figma URLs

### Step 3 — Map Tickets to Spec & Test Cases

For each ticket, perform analysis:

1. **Read the ticket** — understand what it implements:
   - Parse the summary and description
   - Check if it references a specific part of the spec (e.g., "Dashboard page", "Create scheduler")

2. **Match to feature spec sections** — determine which section(s) of the spec this ticket covers:
   - Exact match: ticket summary mentions a spec section name
   - Semantic match: ticket description describes behavior covered in the spec
   - No match: ticket is unrelated to the current spec → skip AC, note in output

3. **Match to test cases** — find which test cases exercise this ticket's scope:
   - By feature group (e.g., "Dashboard & Statistics" → TC-001 to TC-008)
   - By specific functionality described in the ticket

4. **Classify the ticket:**
   - ✅ **COVERED** — has matching spec section AND test cases → generate AC
   - ⚠️ **PARTIAL** — matches spec but test cases don't fully cover it → generate AC + flag gap
   - ❌ **UNRELATED** — no spec/test case match → skip, note in output
   - 🔍 **AMBIGUOUS** — ticket is vague, could match multiple areas → generate AC with assumptions noted

### Step 4 — Generate Acceptance Criteria

For each COVERED or PARTIAL ticket, generate AC using this format:

#### AC Format — Compact Checklist

```
### Acceptance Criteria

**Scope:** [1-line description of what this ticket delivers]

- [ ] [Positive criterion — what MUST work]
- [ ] [Positive criterion — another required behavior]
- [ ] [Negative criterion — what MUST be rejected/handled]
- [ ] [Edge case — boundary or unusual input]

**Ref:** [Spec section] · [Test case IDs, e.g. TC-015, TC-016, TC-018]
```

**AC Writing Rules:**
- **Max 6 items** per ticket — be concise, not exhaustive (test cases handle the depth)
- **Start each item with a verb** — "Shows", "Rejects", "Navigates", "Displays", "Returns"
- **No implementation details** — describe WHAT, not HOW
- **Include at least 1 negative criterion** — what the system should NOT do or should reject
- **Reference test case IDs** — link back to the generated test cases for traceability
- **Skip obvious criteria** — "page loads" is not an AC unless loading has special behavior

**AC Quality Checklist:**
- Is each criterion **testable** in under 2 minutes?
- Can a developer read this and know **exactly** what to verify before marking done?
- Does it avoid restating the ticket summary?
- Are there **no more than 6 items**? If more are needed, the ticket should be split.

### Step 5 — Comment on Jira Tickets

⚠️ **IMPORTANT: Always show a preview of ALL comments before posting any.**

1. **Present the full AC batch** to the user in a table:

| Ticket | Summary | Lane | Status | AC Preview (first 2 items) | Match |
|---|---|---|---|---|---|
| AE-14288 | Dashboard page (ui) | Agentic | In Code Review | ✅ Shows stats cards... / ✅ Rejects unauthorized... | COVERED |
| ... | ... | ... | ... | ... | ... |

2. **Wait for user confirmation:**
   - "Confirm" → post all comments
   - "Edit AE-XXXX" → let user modify specific AC before posting
   - "Skip AE-XXXX" → exclude specific tickets
   - "Cancel" → abort all comments

3. **Post comments** using:
   ```
   mcp_atlassian_add_jira_comment(issue_key="AE-14288", body="...")
   ```
   Format the body with Jira wiki markup or ADF (Atlassian Document Format).

4. **Report results:**

| Ticket | Status | Comment |
|---|---|---|
| AE-14288 | ✅ Posted | 4 AC items |
| AE-14290 | ✅ Posted | 5 AC items |
| AE-14296 | ⏭️ Skipped | Unrelated to spec |

## Feature Spec Output Format

```markdown
# Feature Spec: [Feature Name]
*Sprint: [Sprint Name] (ID: [Sprint ID]) · Quick Filter: Broccoli*
*Generated: [date] · Once-per-sprint artifact*
*Sources: [Confluence page IDs] · [Figma file/node IDs]*

## Overview
[2–3 sentence summary of the feature's purpose and scope]

## Functional Requirements
### [Area 1 — e.g., Dashboard & Statistics]
- [FR-001] [Requirement description]
- [FR-002] [Requirement description]

### [Area 2 — e.g., Create Scheduler Wizard]
- [FR-010] [Requirement description]
...

## UI States (from Figma)
| Screen | States Covered |
|---|---|
| Dashboard | Default / Empty / Error / Large data |
| Create Wizard | Step 1 / Step 2 / Validation errors |
...

## API Contracts (from Confluence)
| Endpoint | Method | Key Behaviors |
|---|---|---|
| /api/v1/scheduled-jobs | POST | Creates job / validates cron / returns 201 |
...

## Business Rules
- [BR-001] [Rule description]
- [BR-002] [Rule description]

## Out of Scope
- [Items explicitly excluded from this sprint/feature]

## Assumptions & Open Questions
- [Items flagged during test planning that remain unresolved]

## Test Coverage Summary
| Feature Group | Test Cases | Coverage |
|---|---|---|
| Dashboard & Statistics | TC-001 to TC-008 | 8 cases (2P/2N/4E) |
...
Total: [N] test cases across [M] groups
```

## Output Format

### Part 1 — Feature Spec

The generated spec file path and a brief confirmation:
```
📄 Created: specs/ekoai-scheduled-jobs.md
   [N] functional requirements · [M] UI states · [K] API contracts
```

### Part 2 — Sprint Ticket Analysis

| # | Ticket | Summary | Assignee | Status | Match | Spec Sections |
|---|---|---|---|---|---|---|
| 1 | AE-14288 | Dashboard page (ui) | Pakkawat | In Code Review | ✅ COVERED | Dashboard & Stats |
| 2 | AE-14296 | Job configuration (ui) | Pakkawat | In Progress | ✅ COVERED | Edit > Job Config |
...

**Sprint:** {sprint name} (ID: {sprintId}) · Quick Filter: Broccoli
**In scope:** {N} tickets matched to feature spec · **Out of scope:** {M} tickets skipped

### Part 3 — AC Preview & Confirmation

Full AC for each ticket, ready for user review before posting.

### Part 4 — Post Results

Comment posting results table (after user confirms).
