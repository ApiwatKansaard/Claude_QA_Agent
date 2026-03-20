# /qa:morning-standup

**Triggers:** report-compiler agent
**Reference:** [agent-report-compiler.md](../references/agent-report-compiler.md)

## What This Command Does

Pull the team's current bug and task status from Jira and produce a standup digest
the QA Lead can read aloud in under 2 minutes. No manual input needed — data comes live from Jira.

## Live Data Sources

| Tool | Purpose | Call |
|---|---|---|
| Jira (Atlassian MCP) | Open bugs, in-progress tasks, assignees | `mcp_atlassian_search_jira_issues` |
| Gmail MCP | Create standup draft for QA distribution | `mcp_gmail_draft_email` |

## Execution Steps

1. **Pull Jira data** using `mcp_atlassian_search_jira_issues(jql="...")` — no cloudId needed:

   ```
   -- Open bugs in current sprint (exclude sub-tasks like "Create Test Case")
   project = AE AND issuetype = Bug AND sprint in openSprints() AND status not in (Done, Closed, Passed, "Won't fix", "Can't reproduce") ORDER BY priority ASC

   -- Actively worked items across the team (exclude unassigned sub-tasks)
   project = AE AND sprint in openSprints() AND issuetype != Sub-task AND status in ("In Progress", "In Code Review", "Ready For Test", "In Test", "Blocked") ORDER BY assignee ASC

   -- P0/P1 bugs open (any non-done status)
   project = AE AND issuetype = Bug AND priority in (Highest, High) AND status not in (Done, Closed, Passed, "Won't fix", "Can't reproduce")
   ```

2. **Group by assignee** to map work to each engineer. If an issue is unassigned, flag it as "Needs owner".

3. **Identify blockers** — look for issues with:
   - `status = Blocked` or label `blocker`
   - Comments mentioning "waiting on", "blocked by", "need help"
   - Issues marked as Critical/Highest that are still Open with no assignee

4. **Flag P0 alerts** — any Critical or Highest priority bug not yet In Progress or Done needs explicit mention.

5. **Format and output** — see output format below.

## Output Format

```
## QA Morning Standup — [Weekday, DD MMM YYYY]

### 👤 Team Status

| Engineer | Focus Today | Status |
|---|---|---|
| [Name] | [Feature/task being tested or triaged] | ✅ On track |
| [Name] | [Bug investigation / regression run] | 🔴 Blocked — [one-line reason] |
| [Name] | [TestRail run / exploratory] | ✅ On track |
| (Unassigned) | [N issues with no owner] | ⚠️ Needs owner |

### 🚧 Blockers
- **[Engineer]**: [Blocker description] → impacts [what it's blocking]
- *(None if no blockers)*

### 🔴 P0 Alerts — Same-Day Resolution Required
- [AE-XXXX] [Bug title] — Owner: [name or Unassigned] — Status: [Open/In Progress]
- *(None if no P0/P1 open bugs)*

### 📊 Sprint Bug Snapshot
Open: **N** | In Progress: **N** | Resolved today: **N** | Critical/High open: **N**
```

Keep the entire output scannable in under 2 minutes. If there are more than 5 unresolved
Critical/High bugs, explicitly call that out as a risk flag at the top.

## Gmail Draft

After formatting the report, create a draft via Gmail MCP:
```
mcp_gmail_draft_email(
  to="[QA team distribution — ask user if not known]",
  subject="QA Standup — [Weekday DD MMM YYYY]",
  body="[full standup text, plain formatting for email]"
)
```
Confirm to the user: "Draft created in Gmail — ready to review and send."
