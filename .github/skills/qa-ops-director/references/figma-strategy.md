# Figma Fetch Strategy for QA

## Tool Selection

### USE: `mcp_figma_get_figma_data` (Local MCP — figma-developer-mcp)
- **Speed:** Instant (1-3 seconds per node)
- **Size:** ~16KB at depth=2, ~50KB at depth=3
- **Data:** Component names, types, layout, variants, text content
- **Purpose:** Structure analysis for test case generation
- **Parameters:** `fileKey`, `nodeId`, `depth` (use 2-3)

### USE: `mcp_figma-remote-_get_screenshot` (Remote MCP — for visual reference only)
- **Speed:** 5-15 seconds per node
- **Risk:** Can hang on complex/large frames — use only when visual check is needed
- **Purpose:** Visual confirmation of layout, not primary data source

### NEVER USE: `mcp_figma-remote-_get_design_context`
- **Hangs indefinitely** on complex design nodes (full pages/frames)
- No timeout mechanism — process stalls with zero progress
- Returns 300KB-1MB per node — context overflow risk
- Designed for code generation, NOT for QA/test planning

## Fetch Strategy

1. **Fetch nodes ONE AT A TIME** (sequential, not parallel) to avoid MCP overload
2. **Use depth=2 first**, only increase to depth=3 if component details are insufficient
3. **The spec text is in Confluence** — Figma gives structure/layout/states only
4. **Parse URL correctly:**
   - `figma.com/design/:fileKey/:fileName?node-id=:nodeId`
   - Convert `node-id` dashes to colons: `341-7657` → `341:7657`

## What to Extract from Figma (for QA)

- Component names → map to test case sections
- Input fields, buttons, dropdowns → map to test steps
- States (empty, loading, error, populated) → map to test scenarios
- Variants (enabled/disabled, selected/unselected) → map to conditions
- Navigation patterns → map to user flows
- DO NOT extract pixel-perfect styling details — not needed for QA
