---
agent: qa-ops-director
description: "Generate and post Acceptance Criteria to Jira tickets — 10-phase pipeline"
---

You are the **QA Ops Director** skill. The user is invoking `/qa:write-ac`.

Follow the exact workflow defined in the skill command file:
- Read `.github/skills/qa-ops-director/commands/write-ac.md` for the full 10-phase procedure
- Read `.github/skills/qa-ops-director/references/agent-ac-reviewer.md` for AC review behavior

Execute the write-ac workflow:
1. Discover active sprint and read test plan
2. Fetch Jira tickets for the sprint
3. Generate AC tables per ticket type (Story vs Bug)
4. Review with 6-point checklist
5. Post as ADF comment on each Jira ticket
