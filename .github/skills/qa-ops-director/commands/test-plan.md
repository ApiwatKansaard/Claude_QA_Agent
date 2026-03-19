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
| Confluence (Atlassian MCP) | PRD, acceptance criteria, API contracts | `getConfluencePage`, `searchConfluenceUsingCql` |

## Execution Steps

### Phase 1 — Test Plan Generation

1. **Fetch specs in parallel:**

   **Figma URL:**
   ```
   mcp_figma-remote-_get_design_context(fileKey, nodeId)   → UI hierarchy, annotations, interaction flows
   mcp_figma-remote-_get_screenshot(fileKey, nodeId)       → Visual — identify loading/empty/error/success states
   get_metadata(node_url)         → Component variants and named states
   ```

   **Confluence URL** — extract page ID from URL path (`/pages/XXXXXXXX/`):
   ```
   getConfluencePage(pageId, cloudId="ekoapp.atlassian.net")
   ```
   Or search by feature name:
   ```
   searchConfluenceUsingCql(
     cql='space = "EP" AND title ~ "[feature name]"',
     cloudId="ekoapp.atlassian.net"
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

### Part 1 — Test Plan

```markdown
# Test Plan: [Feature Name from Spec]
*Generated from: [Figma URL if provided] | [Confluence URL if provided]*

## Scope
[What is covered / what is explicitly out of scope]

## Assumptions & Flagged Ambiguities
- [Any spec gaps, assumptions made, clarifications needed]

## Test Cases

### [Feature Group / Component]

| ID | Title | Surface | Category | Type | Priority | Preconditions | Steps | Expected Result |
|---|---|---|---|---|---|---|---|---|
| TC-001 | ... | Web | Positive | Smoke Test | P1 | ... | 1. ... 2. ... | ... |
| TC-002 | ... | API | Negative | Regression Test | P2 | ... | ... | ... |
| TC-003 | ... | AI/LLM | Edge Case | Regression Test | P1 | ... | ... | ... |

[Continue grouping by feature/component]

## Coverage Summary

| Surface | Total | Positive | Negative | Edge Case | P0 | P1 | P2 | P3 |
|---|---|---|---|---|---|---|---|---|
| Web / Mobile | N | N | N | N | N | N | N | N |
| API | N | N | N | N | N | N | N | N |
| AI/LLM | N | N | N | N | N | N | N | N |

## Known Gaps
- [Any area not covered and why]
```

---

### Part 2 — Automatic Review (appended immediately after Part 1)

```markdown
---

# Test Case Review: [Feature Name]
*Auto-reviewed against: [Figma URL if provided] | [Confluence URL if provided]*

## Review Table

| TC ID | Title | Status | Issue | Suggested Fix |
|---|---|---|---|---|
| TC-001 | ... | ✅ PASS | — | — |
| TC-004 | ... | ⚠️ NEEDS REVISION | [issue description] | [fix] |
| — | [Missing scenario] | ❌ MISSING | [what's not covered] | [suggested test case] |

## Coverage Assessment

| Area | Status | Notes |
|---|---|---|
| Acceptance Criteria | X/Y covered (Z%) | [Which ACs are missing] |
| UI States (Figma) | ✅ / ⚠️ / ❌ | [Missing states] |
| API Error Codes | ✅ / ⚠️ / ❌ | [Missing codes] |
| AI/LLM Dimensions | ✅ / ⚠️ / ❌ | [Missing: M1–M5] |
| Auth / Permissions | ✅ / ⚠️ / ❌ | [Missing role coverage] |
| Positive/Negative/Edge | ✅ / ⚠️ / ❌ | [Groups with missing categories] |

**Overall: [N/N areas fully covered — ready for TestRail / needs N fixes first]**
```

---

### Part 3 — Final Test Cases (appended immediately after Part 2)

```markdown
---

# Final Test Cases: [Feature Name]
*Auto-fixed based on review findings — ready for TestRail import*

## Changes Applied

| Action | Count | Details |
|---|---|---|
| ✅ Kept as-is | N | No changes needed |
| ✏️ Revised | N | [List of revised TC IDs and what changed] |
| ➕ Added | N | [List of new TC IDs and what gap they fill] |

## Final Test Cases

### [Feature Group / Component]

| ID | Title | Surface | Category | Type | Priority | Preconditions | Steps | Expected Result |
|---|---|---|---|---|---|---|---|---|
| TC-001 | ... | Web | Positive | Smoke Test | P1 | ... | 1. ... 2. ... | ... |
| TC-002 | ... | API | Negative | Regression Test | P2 | ... | ... | ... |
| TC-NEW-001 | [new] ... | Web | Edge Case | Regression Test | P1 | ... | ... | ... |

[All test cases — original + revised + new — in one consolidated table]

## Final Coverage Summary

| Surface | Total | Positive | Negative | Edge Case | P0 | P1 | P2 |
|---|---|---|---|---|---|---|---|
| Web / Mobile | N | N | N | N | N | N | N |
| API | N | N | N | N | N | N | N |
| AI/LLM | N | N | N | N | N | N | N |

**Status: Ready for `/qa:sync-testrail`**

## Priority Fixes (resolve before syncing to TestRail)

1. **[Critical]** [Most important gap — why it matters]
2. **[High]** [Second gap]
3. **[Medium]** [Third gap]
```

**Next step:** Once gaps are resolved, run `/qa:sync-testrail [test cases] [suite name] [milestone name] [release date]`.
