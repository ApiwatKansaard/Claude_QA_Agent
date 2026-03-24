# /qa:start-sprint [Sprint Board URL]

**Triggers:** report-compiler
**References:** [templates.md](../references/templates.md)

## What This Command Does

Performs a readiness check before starting a new sprint's QA cycle. Ensures the workspace
is clean, previous sprint is archived, and required tools are accessible.

## Parameters

| Parameter | Required | Notes |
|---|---|---|
| `[Sprint Board URL]` | Optional | Jira board URL for the new sprint. If provided, fetches sprint info for context. |

## Sprint Scope

- Run this **once at the start of each sprint** before running `/qa:test-plan`.
- Quick Filter context: **Broccoli** — only Broccoli-related work is in scope.
- Sprint version numbers (18.0, 18.1, etc.) change each sprint — do not hardcode them.

## Execution Steps

### Step 1 — Check Workspace Cleanliness

Scan the workspace for unarchived sprint artifacts in two locations:

**1a. Unarchived sprint folders** (primary check):
Look for sprint folders at the workspace root that haven't been moved to `archive/` yet.
Sprint folders follow the pattern `agentic-*/` or `sprint-*/` and contain test plans/cases.

| Check | What to look for | Status |
|---|---|---|
| Sprint folders | `agentic-*/` or `sprint-*/` at root — should be archived | ✅ Clean / ⚠️ Found |

**1b. Root-level stray files** (secondary check):
Legacy artifacts or files accidentally created at root instead of inside a sprint folder.

| Check | What to look for | Status |
|---|---|---|
| Test plans | `*-test-plan.md` at root | ✅ Clean / ⚠️ Found |
| TestRail CSVs | `*-testcases.csv` or `*-testrail.csv` at root | ✅ Clean / ⚠️ Found |
| Generator scripts | `generate-*.py` at root | ✅ Clean / ⚠️ Found |
| Release notes | `release-notes-*.md` at root | ✅ Clean / ⚠️ Found |

**If unarchived items are found:**
- List them and ask: "These artifacts appear to be from a previous sprint. Archive them now with `/qa:end-sprint`?"
- Do NOT proceed until the workspace is clean or the user explicitly says to continue.

### Step 2 — Check Archive History

List existing archives to show sprint history:

```
📁 Sprint Archives:
   ├── archive/agentic-18.1/  (5 files, archived 2026-03-15)
   └── (no other archives)

   Previous sprint: Agentic 18.1
```

If the `archive/` folder doesn't exist, note: "No previous sprint archives found — this appears to be the first sprint."

### Step 3 — Verify Tool Accessibility

Test each required tool with a lightweight call:

| Tool | Test Call | Status |
|---|---|---|
| Atlassian MCP (Jira) | `mcp_atlassian_search_jira_issues(jql="project = AE ORDER BY created DESC", limit=1)` | ✅ / ❌ |
| Atlassian MCP (Confluence) | `mcp_atlassian_list_confluence_spaces()` | ✅ / ❌ |
| Jira REST API | Verify macOS Keychain: `security find-generic-password -s jira-api-token -w` | ✅ / ❌ |
| TestRail API | `curl -s -u 'email:key' https://ekoapp20.testrail.io/index.php?/api/v2/get_projects` | ✅ / ❌ |
| Gmail MCP | `mcp_gmail_search_emails(query="subject:test", maxResults=1)` | ✅ / ❌ |
| Google Calendar MCP | `mcp_google-calend_list-calendars()` | ✅ / ❌ |
| Figma MCP | `mcp_figma_get_figma_data(fileKey="test", nodeId="0:0", depth=1)` (skip if no URL) | ✅ / ⏭️ |

**Jira REST API** is needed for `/qa:bug-report` (issue creation with custom fields).
**TestRail API** is needed for `/qa:import-testrail` and `/qa:fetch-testrail`.

**If a tool fails:** Report the error and suggest troubleshooting steps.
Do NOT block the sprint start — the user may fix it later.

### Step 4 — Fetch New Sprint Context (if URL provided)

If a Sprint Board URL is provided:

1. **Parse the URL** for project key, board ID, and sprint ID.
2. **Fetch sprint tickets** for a quick overview:
   ```
   mcp_atlassian_search_jira_issues(
     jql="project = {projectKey} AND sprint = {sprintId} ORDER BY rank ASC"
   )
   ```
3. **Summarize the sprint:**
   - Total tickets
   - Breakdown by status (To Do / In Progress / In Code Review / etc.)
   - Breakdown by issue type (Story / Task / Bug / Sub-task)
   - Key assignees

### Step 4a — Create Sprint Folder

If the sprint name is known (from URL or user input), create the sprint folder:

```bash
mkdir -p {sprint-folder}   # e.g., agentic-18.3/
```

This folder will be used by `/qa:test-plan` to output the test plan and test cases.
If the sprint name is not yet known, skip and note that the folder will be created by `/qa:test-plan`.

### Step 4b — TestRail Cache Status

Check `testrail-cache/` for existing suite caches:

```
📦 TestRail Cache:
   ├── testrail-cache/S5277/ — summary.md + cases.csv (last updated: {date})
   └── (no other cached suites)
```

Cache persists across sprints and is NOT archived. `/qa:import-testrail` uses it
for comparison when importing new cases.

### Step 5 — Readiness Report

Present the final readiness check:

```
🚀 Sprint Readiness Check
   Sprint: {Sprint Name} (ID: {sprint-id})
   Quick Filter: Broccoli

   Workspace:
   ✅ No unarchived sprint folders
   ✅ No root-level stray files
   ✅ Previous sprint archived: archive/agentic-18.1/
   📁 Sprint folder created: {sprint-folder}/

   Tools:
   ✅ Jira MCP — connected (ekoapp.atlassian.net)
   ✅ Confluence MCP — connected (space: EP)
   ✅ Jira REST API — Keychain token found
   ✅ TestRail API — connected (ekoapp20.testrail.io)
   ✅ Gmail MCP — connected
   ✅ Google Calendar MCP — connected
   ⏭️ Figma MCP — not tested (no URL provided)

   TestRail Cache:
   📦 S5277 — cached (summary.md + cases.csv)

   Sprint Overview:
   📋 {N} total tickets · {M} Stories · {K} Tasks · {B} Bugs
   🔧 Key assignees: {list}

   ✅ Ready to start! Run /qa:test-plan to begin.
```

Or if issues are found:

```
⚠️ Sprint Readiness Check — Issues Found

   ❌ Unarchived sprint folder: agentic-18.2/ (run /qa:end-sprint first)
   ❌ Jira MCP not responding (check mcp-atlassian process)
   ⚠️ Jira REST API — Keychain token not found (needed for /qa:bug-report)
   ✅ Confluence MCP — connected

   Fix critical issues (❌) before starting. Warnings (⚠️) can be fixed later.
```

## Output Format

Single readiness report as shown in Step 5. No multi-part output needed.

## Recommended Pipeline

```
/qa:start-sprint    → Check readiness, clean workspace, create sprint folder
/qa:test-plan       → Generate + Review + Auto-fix → test-plan.md + testcases.csv
/qa:import-testrail → Import test cases to TestRail via API (with caching + comparison)
/qa:write-ac        → 10-phase pipeline: generate AC → review → post to Jira → release notes
  ... (testing phase — execute test cases, log bugs) ...
/qa:bug-report      → Create bug ticket in Jira + auto-post Bug Fix Criteria AC
/qa:end-sprint      → Archive sprint folder to archive/{sprint-name}/
```
