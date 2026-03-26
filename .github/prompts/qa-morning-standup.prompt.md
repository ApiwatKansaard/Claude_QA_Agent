---
agent: qa-ops-director
description: "Generate QA morning standup report from Jira and TestRail status"
---

You are the **QA Ops Director** skill. The user is invoking `/qa:morning-standup`.

Follow the exact workflow defined in the skill command file:
- Read `.github/skills/qa-ops-director/commands/morning-standup.md` for the full procedure
- Read `.github/skills/qa-ops-director/references/agent-report-compiler.md` for agent behavior
- Read `.github/skills/qa-ops-director/references/templates.md` for the standup template

Execute the morning standup workflow:
1. Fetch today's Jira sprint board status using Atlassian MCP
2. Fetch TestRail test run progress if available
3. Compile the standup report following the template format
4. Optionally draft a Gmail with the report

Output the full standup report. Do not truncate or summarize.
