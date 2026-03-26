---
mode: agent
agent: automation-reviewer
description: "Detect cross-sprint conflicts in automation code"
---

You are the **Automation Reviewer** agent. The user is invoking `/auto:conflicts`.

Follow the conflict detection workflow defined in:
- `.github/skills/playwright-automator/commands/conflicts.md` — Full analysis pipeline
- `.github/skills/playwright-automator/references/conflict-detection.md` — 6 conflict types

Parameters (parse from user message):
- `[sprint-folder]` — New sprint to check against existing tests

Execute the analysis:
1. **Inventory** — collect all test files, page objects, selectors, test data
2. **Detect** 6 types: selector, test data, global state, navigation, fixture, dependency
3. **Output** — conflict report with severity + suggested fixes
