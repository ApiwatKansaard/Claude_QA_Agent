# /qa:test-plan [Figma URL] [Confluence URL]

**Triggers:** test-planner agent → auto-chains to test-case-reviewer agent → auto-fix agent
**Reference:** [agent-test-planner.md](../references/agent-test-planner.md), [agent-test-case-reviewer.md](../references/agent-test-case-reviewer.md)

## What This Command Does

Read the provided Figma design and/or Confluence spec, generate a complete structured test plan,
then **automatically review and fix** — no extra command needed.

The full pipeline runs in one shot:
0. Scan archives for previous sprint context → 1. Fetch specs → 2. Generate test cases → 3. Review for gaps → 4. Auto-fix based on review → 5. Output final result

## Parameters

| Parameter | Required | Notes |
|---|---|---|
| `[Figma URL]` | Either/or | Node or frame URL — fetch via Figma MCP |
| `[Confluence URL]` | Either/or | Page URL or title — fetch via Atlassian MCP |

At least one URL must be provided. If both are given, cross-reference them and use the spec
to fill functional intent and Figma to fill UI state coverage.

If neither URL is provided: ask for at least one before proceeding.

## Live Data Sources

| Tool | Purpose | Call |
|---|---|---|
| Figma MCP (local) | UI structure, component states, layout | `mcp_figma_get_figma_data(fileKey, nodeId, depth=2)` |
| Figma MCP (remote) | Visual screenshot only (use sparingly) | `mcp_figma-remote-_get_screenshot(fileKey, nodeId)` |
| Confluence (Atlassian MCP) | PRD, acceptance criteria, API contracts | `mcp_atlassian_read_confluence_page`, `mcp_atlassian_search_confluence_pages` |

> ⚠️ **Figma strategy:** See `references/figma-strategy.md` for tool selection rules.
> NEVER use `mcp_figma-remote-_get_design_context` — it hangs on complex nodes.

## Execution Steps

### Sprint Folder Resolution

Before any phase runs, determine the target sprint folder for output:

1. **Check for existing sprint folder** at workspace root — look for `agentic-*/` or `sprint-*/`
   directories that are NOT inside `archive/`.
2. **If found** — use it as `{sprint-folder}` (e.g., `agentic-18.3/`).
3. **If not found** — ask the user for the sprint name, then create it:
   ```bash
   mkdir -p {sprint-folder}   # e.g., agentic-18.3/
   ```
   If the user ran `/qa:start-sprint` first, the folder should already exist (Step 4a).

All output files are written to `{sprint-folder}/` — **never** to the workspace root.

---

### Phase 0 — Archive Context Scan (auto, before spec fetch)

Before fetching new specs, check if previous sprints covered related features.
This step is **read-only** and **non-blocking** — if no match is found, proceed normally.

1. **Scan archive directory:**
   - List all folders in `archive/`
   - For each, read `ARCHIVE-SUMMARY.md` (skip folders without it)
   - Extract: feature names, Confluence page IDs, Figma file keys, coverage stats

2. **Match against current spec sources:**
   Compare the user-provided Figma URL's `fileKey` and Confluence URL's `pageId`
   against each archive's `## Data Sources` section.

   | Signal | Match Strength | Action |
   |---|---|---|
   | Same Confluence page ID | **Strong** — same spec document, continued work | Read archived test plan + CSV coverage summary |
   | Same Figma file key | **Strong** — same design, iterated | Read archived test plan + CSV coverage summary |
   | Feature name keyword overlap in title | **Moderate** — similar feature area | Read archived ARCHIVE-SUMMARY only |
   | No match at all | **None** — new feature | Skip, proceed fresh |

   If multiple archived sprints match, use the **most recent** one (by archived date).

3. **If Strong match found** — read these archived files:
   - `archive/{sprint}/*-test-plan.md` → Coverage Summary, Known Gaps, Scope, Test Strategy
   - `archive/{sprint}/*-testcases.csv` → Count cases per Section (don't load full content, just group/count)

   Present to user:
   ```
   📂 Previous Sprint Context Found:
      Sprint: Agentic 18.1 (archive/agentic/agentic-18.1/)
      Feature: EkoAI Scheduled Jobs
      Match: Same Confluence pages (3488645131, 3518726148, ...)
      Previous coverage: 131 test cases across 13 groups
      Known gaps: [list from previous plan]

      This context will be used to:
      ✅ Avoid duplicating identical test scenarios
      ✅ Address known gaps from previous sprint
      ✅ Build on existing coverage structure
      ✅ Reference previous test case groups for continuity
   ```

4. **If Moderate match found:**
   ```
   📂 Possibly related previous sprint:
      Sprint: Agentic 18.1 — feature "EkoAI Scheduled Jobs" (keyword overlap)
      Previous coverage: 131 test cases
      ⚠️ Specs differ — using as light reference only.
   ```

5. **If no match found:**
   ```
   📂 Archive scan: No related previous sprint found.
      Proceeding with fresh test plan generation.
   ```

**How archived context is used in Phase 1:**
- The archive data is **supplementary input**, NOT a replacement for spec analysis.
- Specs may have changed between sprints — ALL test cases are still generated from the current spec.
- Use archive context to:
  - Keep consistent Section naming across sprints when the feature is the same
  - Reference known gaps and ensure they're addressed this time
  - Avoid generating test cases that are exact duplicates of already-imported TestRail cases
  - Note in test plan output what was carried forward vs. what's new

---

### Phase 1 — Test Plan Generation

1. **Fetch specs in parallel:**

   **Figma URL** (see `references/figma-strategy.md`):
   ```
   mcp_figma_get_figma_data(fileKey, nodeId, depth=2)      → Component structure, layout, variants (FAST — use this)
   mcp_figma-remote-_get_screenshot(fileKey, nodeId)        → Visual reference only (use sparingly, can be slow)
   ```
   ⚠️ NEVER use `mcp_figma-remote-_get_design_context` — hangs indefinitely on complex nodes.
   Fetch nodes ONE AT A TIME (sequential, not parallel) to avoid MCP overload.

   **Confluence URL** — extract **numeric page ID** from URL path (`/pages/XXXXXXXX/`):
   ```
   mcp_atlassian_read_confluence_page(pageId="3488645131")
   ```
   ⚠️ CRITICAL: Pass only the numeric pageId, NOT the full URL.
   There is NO cloudId parameter — the MCP server is already configured with the instance.

   Or search by feature name:
   ```
   mcp_atlassian_search_confluence_pages(
     cql='space = "EP" AND title ~ "[feature name]"'
   )
   ```

2. **Extract testable requirements** — follow the requirements extraction process in [agent-test-planner.md](../references/agent-test-planner.md) Step 1.
   Flag any ambiguities or untestable ACs before generating test cases.

3. **Generate test cases** — use the coverage requirements per surface from [agent-test-planner.md](../references/agent-test-planner.md) Step 2.
   Produce test cases for all applicable surfaces: Web/Mobile, API/Backend, AI/LLM (if present in spec).

4. **Format test plan output** — see Output Format below.

### Phase 2 — Automatic Review (runs immediately after Phase 1, NO user prompt needed)

After the test plan is written, **do not stop — immediately continue** and run the review agent:

5. **Re-use the already-fetched spec data** (no need to re-fetch Figma/Confluence).
   Apply the review steps from [agent-test-case-reviewer.md](../references/agent-test-case-reviewer.md):
   - Compare each test case against spec ACs (numbered cross-reference)
   - Check all UI states from Figma are covered (loading/empty/error/success/disabled)
   - Check API error codes: 400/401/403/404/409/429/500
   - Check AI/LLM mandatory scenarios M1–M5
   - Check auth/permission boundaries
   - Flag missing Positive/Negative/Edge Case coverage per group

6. **Output the review table + gap summary** — see Review Output Format below.

7. **State next step:** proceed immediately to Phase 3.

### Phase 3 — Auto-Fix (runs immediately after Phase 2, NO user prompt needed)

After the review is complete, **do not stop — immediately apply all review findings:**

8. **Process each review finding:**
   - **❌ MISSING** → Generate new test cases following the same format and add them to the test plan
   - **⚠️ NEEDS REVISION** → Revise the flagged test cases based on the suggested fix
   - **✅ PASS** → Keep as-is, no changes needed

9. **Ensure coverage completeness after fixes:**
   - Every feature group must have ≥2 Positive + ≥2 Negative + ≥2 Edge Case
   - All UI states from Figma covered (loading/empty/error/success/disabled)
   - All API error codes covered (400/401/403/404/409/429/500)
   - All AI/LLM mandatory scenarios M1–M5 covered (if applicable)
   - Auth/permission boundaries covered for all roles

10. **Output the final consolidated test cases** — see Part 3 output format below.
    This is the definitive version ready for `/qa:sync-testrail`.

11. **State next step:** suggest `/qa:sync-testrail` to push the final test cases to TestRail.

## Output Format

⚠️ **CRITICAL**: This command produces **TWO separate files** in the sprint folder.
Test cases are **ALWAYS in TestRail CSV format** — NEVER markdown tables.
See [testrail-csv.md](../references/testrail-csv.md) for the exact 15-column schema and formatting rules.

### Output File 1 — Test Plan (Markdown)

**File:** `{sprint-folder}/{feature-slug}-test-plan.md`

This file contains ONLY the strategy, scope, and coverage summary — NO test case rows.

```markdown
# Test Plan: [Feature Name from Spec]

> **Feature**: [Feature name]
> **Sprint**: [Sprint name]
> **Date**: [YYYY-MM-DD]
> **QA Lead**: [Name]

## Sources
| Type | Document | Page ID |
|------|----------|---------|
| Tech Spec | [Title] | [page_id] |
| Figma | [Node name] (nodeId) | — |

## Previous Sprint Context
<!-- Include ONLY if Phase 0 found a match. Omit this section entirely if no match. -->
- **Archived sprint:** [sprint name] (archive/{folder}/)
- **Match type:** Strong (same Confluence pages) / Moderate (keyword)
- **Previous coverage:** [N] test cases across [M] groups
- **Known gaps addressed:** [list gaps from previous sprint that are now covered]
- **Carried forward:** [what was reused — e.g., Section naming, test strategy]
- **New in this sprint:** [what's different — new groups, changed scope, etc.]

## Scope
### In Scope
- [Functional areas covered]
### Out of Scope
- [Explicitly excluded areas]

## Assumptions & Flagged Ambiguities
- [Any spec gaps, assumptions made, clarifications needed]

## Test Strategy
| Surface | Approach |
|---------|----------|
| Web | Manual — [details] |
| API | Manual — [details] |

## Coverage Summary
| Group | Test Cases | P0 | P1 | P2 |
|-------|-----------|----|----|-----|
| [Group Name] | N | N | N | N |
| **TOTAL** | **N** | **N** | **N** | **N** |

## Known Gaps
- [Any area not covered and why]

## Test Cases
See: `{feature-slug}-testcases.csv` (TestRail-importable format)
```

---

### Output File 2 — Test Cases (TestRail CSV)

**File:** `{sprint-folder}/{feature-slug}-testcases.csv`

⚠️ This is the ONLY format for test cases. Follow [testrail-csv.md](../references/testrail-csv.md) EXACTLY.

**Column order (15 columns, this exact header row):**
```
Section,Role,Channel,Title,Test Data,Preconditions,Steps,Expected Result,Platform,TestMethod,Type,P,References,Release version,QA Responsibility
```

**Column mapping rules:**
| Column | How to determine value |
|--------|----------------------|
| Section | `Agentic > [Feature] > [Group Name]` — hierarchy with ` > ` separator |
| Role | `Admin` (console), `User` (end-user), `Super Admin` (system) |
| Channel | `Web` (console UI), `API` (backend), `iOS`/`Android` (mobile) |
| Title | "Check/Verify" style — see Title Style Guide in [testrail-csv.md](../references/testrail-csv.md) |
| Test Data | Specific input data needed (leave empty if none) |
| Preconditions | Required state — use ` / ` separator, NEVER commas |
| Steps | Numbered items with REAL NEWLINES: `"1. Do X\n2. Do Y\n3. Check Z"` |
| Expected Result | Numbered items with REAL NEWLINES: `"1. X is visible\n2. Y displays correctly"` |
| Platform | Matches Channel unless cross-platform |
| TestMethod | `Manual` (default) or `Automated` |
| Type | See Type Mapping below |
| P | `P0` (blocker), `P1` (high), `P2` (medium/low) |
| References | Short feature tag, e.g. `SJ-1.1` |
| Release version | Sprint/release identifier (e.g. `Eko 18.0`) — leave empty if unknown |
| QA Responsibility | Assignee name — leave empty if unassigned |

**Title Style (MANDATORY):**
- Always start with `Check` or `Verify`
- Include the condition: "when [X]" / "after [X]" / "on [page]"
- Include expected behavior: "should be [state]" / "should [action]"
- Use plain language — avoid technical jargon and variable names
- BAD: `View dashboard with jobs` → GOOD: `Check scheduled jobs list should be displayed on Dashboard page`
- BAD: `HMAC signature verification` → GOOD: `Verify HMAC signature should be valid when external server receives request`

**Steps and Expected Result Format (MANDATORY):**
- Each item numbered: `1.` / `2.` / `3.` etc.
- Items separated by REAL NEWLINES (`\n`) — TestRail renders each item on its own line
- Python csv.writer with `csv.QUOTE_ALL` auto-quotes these fields
- Do NOT put all steps on one line — TestRail needs newlines for readable rendering

**Type Mapping:**
| Category | Type |
|----------|------|
| Positive — core happy path | `Smoke Test` |
| Positive — secondary valid scenario | `Sanity Test` |
| Negative — invalid/auth/rejection | `Regression Test` |
| Edge Case — boundary/empty/extreme | `Regression Test` |

**Formatting Rules (MANDATORY):**
1. NO commas inside cell values — replace with ` / `
2. Steps and Expected Result: use REAL NEWLINES between numbered items (TestRail renders as separate lines)
3. All other fields: NO newlines
4. ALWAYS generate CSV via Python `csv.writer` with `csv.QUOTE_ALL`
5. ALWAYS validate: every row has 15 columns / no commas / newlines only in Steps+Expected
6. Minimum per feature group: ≥2 Positive + ≥2 Negative + ≥2 Edge Case

**Generation process:**
1. Write all test case data to a Python list of dicts
2. Use `csv.DictWriter` to write to CSV file
3. Run validation script (see testrail-csv.md CRITICAL RULE 3)
4. Report: `Generated N test cases → {filename}`

---

### Review & Auto-Fix (runs inline during generation)

The review and auto-fix process is embedded within the generation pipeline (Phase 2 and Phase 3).
Review findings are applied BEFORE writing the CSV — the CSV output is always the final, reviewed version.

After generating both files, summarize review actions in the test plan markdown:

```markdown
## Review Actions Applied
| Action | Count | Details |
|--------|-------|---------|
| ✅ Kept as-is | N | No changes needed |
| ✏️ Revised | N | [What changed] |
| ➕ Added | N | [What gap was filled] |
```

---

**Next step:** Once files are created, suggest `/qa:sync-testrail` to push the CSV to TestRail.
