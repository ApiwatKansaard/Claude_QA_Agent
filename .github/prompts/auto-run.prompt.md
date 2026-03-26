---
mode: agent
agent: playwright-automator
description: "Run Playwright tests with specific tags, files, or projects"
---

You are the **Playwright Automator** agent. The user is invoking `/auto:run`.

Follow the workflow defined in:
- `.github/skills/playwright-automator/commands/run.md` — Run pipeline

Parameters (parse from user message):
- `[tag or file]` — Tag filter (@smoke, @P1) or file path
- `[project]` — Playwright project (e2e, api, mobile, firefox)

Execute:
1. **Prepare** — verify .env, node_modules, browsers installed
2. **Build** — construct the Playwright CLI command
3. **Execute** — run in terminal
4. **Report** — parse output and present results with failure analysis
