---
description: "Generate test cases from Figma/Confluence specs (4-phase auto-pipeline: fetch → generate → review → fix)"
---

Read `.github/skills/qa-ops-director/SKILL.md` for routing context, then execute the workflow in `.github/skills/qa-ops-director/commands/test-plan.md`.

Parse from $ARGUMENTS:
- `[Figma URL]` — Figma design link (use Figma MCP)
- `[Confluence URL]` — Confluence spec page (use Atlassian MCP)

If a required parameter is missing, ask for it before proceeding.
