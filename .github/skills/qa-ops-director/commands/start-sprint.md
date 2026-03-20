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

Scan the workspace root for leftover artifacts from a previous sprint:

| Check | What to look for | Status |
|---|---|---|
| Spec files | `specs/*.md` — should not exist (should be archived) | ✅ Clean / ⚠️ Found |
| Test plans | `*-test-plan.md` in root | ✅ Clean / ⚠️ Found |
| TestRail CSVs | `*-testrail.csv` in root | ✅ Clean / ⚠️ Found |
| Generator scripts | `generate-*.py` in root | ✅ Clean / ⚠️ Found |

**If leftover files are found:**
- List them and ask: "These files appear to be from a previous sprint. Archive them now with `/qa:end-sprint`?"
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

Test each required MCP tool with a lightweight call:

| Tool | Test Call | Status |
|---|---|---|
| Atlassian MCP (Jira) | `mcp_atlassian_search_jira_issues(jql="project = AE ORDER BY created DESC", limit=1)` | ✅ / ❌ |
| Atlassian MCP (Confluence) | `mcp_atlassian_list_confluence_spaces()` | ✅ / ❌ |
| Figma MCP | `mcp_figma-remote-_get_metadata(node_url="...")` (skip if no URL provided) | ✅ / ⏭️ |

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

### Step 5 — Readiness Report

Present the final readiness check:

```
🚀 Sprint Readiness Check
   Sprint: {Sprint Name} (ID: {sprint-id})
   Quick Filter: Broccoli

   Workspace:
   ✅ No leftover artifacts from previous sprint
   ✅ Previous sprint archived: archive/agentic-18.1/

   Tools:
   ✅ Jira MCP — connected (ekoapp.atlassian.net)
   ✅ Confluence MCP — connected (space: EP)
   ⏭️ Figma MCP — not tested (no URL provided)

   Sprint Overview:
   📋 {N} total tickets · {M} Stories · {K} Tasks
   🔧 Key assignees: {list}

   ✅ Ready to start! Run /qa:test-plan to begin.
```

Or if issues are found:

```
⚠️ Sprint Readiness Check — Issues Found

   ❌ Leftover files from previous sprint (run /qa:end-sprint first)
   ❌ Jira MCP not responding (check mcp-atlassian process)
   ✅ Confluence MCP — connected

   Fix the issues above before starting the sprint QA cycle.
```

## Output Format

Single readiness report as shown in Step 5. No multi-part output needed.

## Recommended Pipeline

```
/qa:start-sprint   → Check readiness, clean workspace
/qa:test-plan      → Generate + Review + Auto-fix test cases
/qa:sync-testrail  → Export CSV / push to TestRail
/qa:write-ac       → Create feature spec + comment AC on Jira tickets
  ... (testing phase) ...
/qa:end-sprint     → Archive all artifacts for this sprint
```
