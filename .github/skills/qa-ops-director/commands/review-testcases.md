# /qa:review-testcases [test cases] [Figma URL] [Confluence URL]

**Triggers:** test-case-reviewer agent
**Reference:** [agent-test-case-reviewer.md](../references/agent-test-case-reviewer.md)

> **Note:** This command also runs automatically as Phase 2 of `/qa:test-plan`.
> When invoked from the pipeline, spec data is already fetched — skip re-fetching and go straight to Step 2.

## What This Command Does

Compare a set of test cases against the original Figma design and/or Confluence spec.
Identify gaps, misalignments, redundant cases, and AI-specific coverage holes.
Output a review table the team can act on immediately, ready to feed into `/qa:sync-testrail`.

## Parameters

| Parameter | Required | Notes |
|---|---|---|
| `[test cases]` | Yes | Pasted inline, or piped automatically from `/qa:test-plan` |
| `[Figma URL]` | Either/or | Fetch via Figma MCP for UI state comparison — skip if already fetched in Phase 1 |
| `[Confluence URL]` | Either/or | Fetch via Atlassian MCP to verify AC alignment — skip if already fetched in Phase 1 |

If no spec URL is provided, perform structural review only (step quality, priority consistency,
coverage completeness by type) and note that AC alignment couldn't be verified.

## Live Data Sources

| Tool | Purpose | Call |
|---|---|---|
| Figma MCP | Verify UI states present in design | `get_design_context`, `get_screenshot` |
| Confluence (Atlassian MCP) | Verify AC alignment | `mcp_atlassian_read_confluence_page`, `mcp_atlassian_search_confluence_pages` |

## Execution Steps

1. **Fetch spec in parallel with parsing test cases:**

   **Figma:**
   ```
   mcp_figma-remote-_get_design_context(fileKey, nodeId)   → Extract every named state and interaction
   mcp_figma-remote-_get_screenshot(fileKey, nodeId)       → Visually confirm states — loading/empty/error/success
   ```

   **Confluence:** extract numeric pageId from URL `/pages/XXXXXXXX/`:
   ```
   mcp_atlassian_read_confluence_page(pageId="3488645131")
   -- or by search:
   mcp_atlassian_search_confluence_pages(
     cql='space = "EP" AND title ~ "[feature name]"'
   )
   ```
   ⚠️ Pass only the numeric pageId — NOT the full URL. No cloudId parameter.
   Number each AC extracted from Confluence so you can cross-reference in the review table.

2. **Review each test case** across the 5 dimensions in [agent-test-case-reviewer.md](../references/agent-test-case-reviewer.md):
   spec alignment, UI state coverage, test case quality, redundancy, AI/LLM gaps.

3. **Scan for systematically missing categories** — the most impactful gaps are never individual
   test cases but whole scenarios nobody thought to write:
   - All UI states: loading, empty, error, success, disabled
   - All error codes: 400, 401, 403, 404, 409, 429, 500
   - AI/LLM: consistency, adversarial, format compliance, latency
   - Auth: each role type, expired session, cross-user isolation (IDOR)

4. **Produce review table + gap summary** — see output format below.

## Output Format

```markdown
# Test Case Review: [Feature Name]
*Reviewed against: [Figma URL if provided] | [Confluence URL if provided]*

## Review Table

| TC ID | Title | Status | Issue | Suggested Fix |
|---|---|---|---|---|
| TC-001 | ... | ✅ PASS | — | — |
| TC-004 | ... | ⚠️ NEEDS REVISION | Expected result vague — 'works correctly' is not observable | Specify exact UI change: button becomes disabled, confirmation toast appears |
| TC-007 | ... | ⚠️ NEEDS REVISION | Steps don't match spec AC-03 (spec says optional field, test treats it as required) | Remove required-field assumption from Step 2 |
| — | Loading state for suggestions | ❌ MISSING | No test case for loading spinner during API call | Add: while POST /suggest-reply is in flight, spinner is visible in Suggest button |
| — | Empty state (0 messages) | ❌ MISSING | Feature should gracefully handle empty conversation — no test covers this | Add: empty conversation → Suggest Reply button disabled or shows 'No messages to summarize' |

## Coverage Assessment

| Area | Status | Notes |
|---|---|---|
| Acceptance Criteria | X/Y covered (Z%) | [Which ACs are missing] |
| UI States (Figma) | ✅ / ⚠️ / ❌ | [Missing states] |
| API Error Codes | ✅ / ⚠️ / ❌ | [Missing codes] |
| AI/LLM Dimensions | ✅ / ⚠️ / ❌ | [Missing: M1–M5 mandatory scenarios] |
| Auth / Permissions | ✅ / ⚠️ / ❌ | [Missing role coverage] |
| Positive/Negative/Edge | ✅ / ⚠️ / ❌ | [Feature groups missing any of the 3 categories] |

**Overall: [N/N areas fully covered — ready for TestRail / needs N fixes first]**

## Priority Fixes (resolve before syncing to TestRail)

1. **[Critical]** [Most important gap — why it matters]
2. **[High]** [Second gap]
3. **[Medium]** [Third gap]
```

**Next step hint:** Once gaps are resolved, pass the updated test cases to `/qa:sync-testrail [test cases] [suite name] [milestone name] [release date]`.
