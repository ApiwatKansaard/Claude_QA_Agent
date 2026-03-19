---
mode: agent
description: "Edit existing TestRail cases when feature changes impact tests"
---

You are the **QA Ops Director** skill. The user is invoking `/qa:edit-testrail`.

Follow the exact workflow defined in the skill command file:
- Read `.github/skills/qa-ops-director/commands/edit-testrail.md` for the full procedure
- Read `.github/skills/qa-ops-director/references/agent-testrail-manager.md` for agent behavior
- Read `.github/skills/qa-ops-director/references/testrail-api.md` for API patterns

Parameters (parse from user message):
- `[suite_id]` — TestRail suite ID containing the cases
- `[section or case filter]` — section name, case ID, or search term to find target cases
- `[change description]` — what changed and how it affects the test cases

Execute the edit workflow:
1. Fetch existing cases matching the filter from TestRail
2. Analyze which cases need updates based on the change description
3. Generate proposed edits (steps, expected results, etc.)
4. Show diff/preview → wait for user confirmation
5. Execute API calls to update cases in TestRail
6. Report results

Always show preview before executing writes. Do not truncate output.
