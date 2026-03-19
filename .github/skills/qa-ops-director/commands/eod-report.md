# /qa:eod-report

**Triggers:** report-compiler agent
**Reference:** [agent-report-compiler.md](../references/agent-report-compiler.md)

## What This Command Does

Compile today's QA activity into an EOD report formatted for async team communication.
Pulls live data from Jira and incorporates any TestRail progress the user provides.
Output is email-ready with a subject line included.

## Parameters

This command takes no required parameters. However, if the user provides TestRail run progress
(e.g., pasted inline or mentioned in conversation), incorporate it into the report.
If not provided, mark TestRail section as `[pending — provide run progress to include]`.

## Live Data Sources

| Tool | Purpose | Call |
|---|---|---|
| Jira (Atlassian MCP) | Today's bug activity, sprint status | `searchJiraIssuesUsingJql` |
| Google Calendar MCP | Sprint timeline context | `mcp_google-calend_list-events` |
| Gmail MCP | Create EOD report draft | `mcp_gmail_draft_email` |

## Execution Steps

1. **Pull Jira data** using `searchJiraIssuesUsingJql(jql, cloudId="ekoapp.atlassian.net")`:

   ```
   -- Bugs filed today
   project = AE AND issuetype = Bug AND created >= startOfDay() ORDER BY priority ASC

   -- Bugs closed/resolved today
   project = AE AND issuetype = Bug AND status changed to (Done, Resolved, Closed) during (startOfDay(), now())

   -- Currently open bugs in sprint
   project = AE AND issuetype = Bug AND sprint in openSprints() AND status not in (Done, Closed, Passed, "Won't fix", "Can't reproduce") ORDER BY priority ASC

   -- Actively worked tasks today (excludes Sub-task / Create Test Case)
   project = AE AND sprint in openSprints() AND issuetype != Sub-task AND status in ("In Progress", "In Code Review", "Ready For Test", "In Test", "Blocked") AND updated >= startOfDay()
   ```

2. **Check Google Calendar** for sprint timeline context:
   ```
   mcp_google-calend_list-events(calendarId, timeMin=today, timeMax=+7d)
   ```
   Use any sprint end date or release milestone to frame tomorrow's focus section.

3. **Incorporate TestRail data** if provided: run name, cases executed, pass/fail/blocked counts.

4. **Synthesize the day** — the most useful EOD report tells a story:
   what was attempted, what succeeded, what failed, what's blocking tomorrow.
   Don't just list activities — surface the narrative.

5. **Format as async post** — see output format below.

## Output Format

```
Subject: QA EOD Report — [Day DD MMM YYYY]

---

## QA EOD Report — [Day, DD MMM YYYY]

### ✅ Completed Today
- [Feature/area]: [What was done + outcome — e.g., "Completed TC-001–TC-018 for AI Chat feature. 16 passed, 2 failed — bugs filed as AE-5021 and AE-5022"]
- [Feature/area]: [...]
- *(If nothing completed: "No test execution completed — [reason]")*

### 🔄 In Progress / Carrying Over to Tomorrow
- [Feature/area]: [What's partially done, ETA, any risks]

### 🐛 Bugs Filed Today (N total)
| Bug ID | Title | Severity | Assigned To |
|---|---|---|---|
| AE-XXXX | [title] | S2 — High | [Dev team / specific engineer] |
*(None if no bugs filed)*

### ✅ Bugs Closed Today (N total)
| Bug ID | Title | Resolution |
|---|---|---|
| AE-XXXX | [title] | Fixed and verified |
*(None if no bugs closed)*

### 🔴 Active Blockers
- [Description] — Owner: [name] — Expected resolution: [time/date]
- *(None if no blockers)*

### 📊 Sprint Metrics (Cumulative)
Bugs open: **N** | Bugs closed this sprint: **N** | Critical/High open: **N**
*(↑N or ↓N vs yesterday if previous data available)*

### 🧪 TestRail Progress
[If data provided:]
- [Run name]: [N]/[Total] cases — Pass: [N] | Fail: [N] | Blocked: [N] — Pass rate: [X%]
[If not provided:]
- [pending — provide run progress to include]

### 📋 Tomorrow's Focus
- [Engineer / Area]: [What they'll work on]
- [Risk or dependency to watch]
```

The subject line format is required — it makes the email easy to find and filter.
Keep bullets concise: 1–2 lines each. The report should be readable in under 3 minutes.

## Gmail Draft

After generating the report, create a draft via Gmail MCP:
```
mcp_gmail_draft_email(
  to="[QA team distribution — ask user if not known]",
  subject="QA EOD Report — [Day DD MMM YYYY]",
  body="[full report text, starting from the --- separator line]"
)
```
Confirm to the user: "Draft created in Gmail — subject: 'QA EOD Report — [date]'. Ready to review and send."
