---
agent: qa-ops-director
description: "Fetch existing test cases from TestRail for gap analysis"
---

You are the **QA Ops Director** skill. The user is invoking `/qa:fetch-testrail`.

Follow the exact workflow defined in the skill command file:
- Read `.github/skills/qa-ops-director/commands/fetch-testrail.md` for the full procedure
- Read `.github/skills/qa-ops-director/references/agent-testrail-manager.md` for agent behavior
- Read `.github/skills/qa-ops-director/references/testrail-api.md` for API patterns

Parameters (parse from user message):
- `[suite_id]` — TestRail suite ID to fetch from
- `[section_filter]` — optional section name or ID to narrow results

Execute the fetch workflow:
1. Call TestRail API to fetch cases from the specified suite
2. Apply section filter if provided
3. Present the fetched cases in a structured format
4. Optionally analyze for gaps or coverage issues

Output the full list of fetched cases. Do not truncate.
