# /qa:test-plan [Figma URL] [Confluence URL]

**Triggers:** test-planner agent → auto-chains to test-case-reviewer agent → auto-fix agent
**Reference:** [agent-test-planner.md](../references/agent-test-planner.md), [agent-test-case-reviewer.md](../references/agent-test-case-reviewer.md)

## What This Command Does

Read the provided Figma design and/or Confluence spec, generate a complete structured test plan,
then **automatically review and fix** — no extra command needed.

The full pipeline runs in one shot:
1. Fetch specs → 2. Generate test cases → 3. Review for gaps → 4. Auto-fix based on review → 5. Output final result

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
| Figma MCP | UI flows, component states, interaction details | `get_design_context`, `get_screenshot`, `get_metadata` |
| Confluence (Atlassian MCP) | PRD, acceptance criteria, API contracts | `mcp_atlassian_read_confluence_page`, `mcp_atlassian_search_confluence_pages` |

## Execution Steps

### Phase 1 — Test Plan Generation

1. **Fetch specs in parallel:**

   **Figma URL:**
   ```
   mcp_figma-remote-_get_design_context(fileKey, nodeId)   → UI hierarchy, annotations, interaction flows
   mcp_figma-remote-_get_screenshot(fileKey, nodeId)       → Visual — identify loading/empty/error/success states
   get_metadata(node_url)         → Component variants and named states
   ```

   **Confluence URL** — extract **numeric page ID** from URL path (`/pages/XXXXXXXX/`):
   ```
   mcp_atlassian_read_confluence_page(page_id="3488645131")
   ```
   ⚠️ CRITICAL: Pass only the numeric page_id, NOT the full URL.
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
