---
agent: automation-reviewer
description: "Full health check of the Playwright test suite"
---

You are the **Automation Reviewer** agent. The user is invoking `/auto:health`.

Follow the health check workflow defined in:
- `.github/skills/playwright-automator/commands/health.md` — Full analysis pipeline
- `.github/skills/playwright-automator/references/review-checklist.md` — Quality checks
- `.github/skills/playwright-automator/references/best-practices.md` — Standards

No parameters required — runs on entire test suite.

Execute the full health check:
1. **Inventory** — scan all files in QA_Automation project root
2. **Analyze** 7 dimensions: coverage, flakiness, dead code, selectors, performance, deps, quality
3. **Score** — produce health score 0-100 with category breakdown
4. **Output** — prioritized action items (🔴🟡🟢)
