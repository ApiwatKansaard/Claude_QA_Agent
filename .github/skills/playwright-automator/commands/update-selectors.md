# /auto:update-selectors — Re-inspect URL and Update Selectors

## Trigger
`/auto:update-selectors [URL] [selector-file]`

## Parameters
- `[URL]` — The URL to re-inspect
- `[selector-file]` — Optional: specific selector file in `selectors/` to update

## Pipeline

### Phase 1: Load Previous Selectors

1. Find the matching selector JSON in `selectors/` (in QA_Automation)
2. If `selector-file` specified, use that directly
3. Load previous element map for comparison

### Phase 2: Re-inspect URL

1. Use `fetch_webpage` to get current HTML
2. Extract elements (same as `/auto:inspect` Phase 2)
3. Build new selector map

### Phase 3: Diff

Compare old vs new:
- **Added** — new elements not in previous map
- **Removed** — elements no longer present
- **Changed** — element exists but selector changed (attribute/text/class)
- **Unchanged** — same as before

### Phase 4: Update

1. Update the selector JSON file
2. Find all page objects that use changed selectors
3. Update page object locators
4. Flag test files that might be affected

### Phase 5: Output

```markdown
## 🔄 Selector Update: {page-name}

| Element | Old Selector | New Selector | Status |
|---------|-------------|-------------|--------|
| createButton | `button:has-text('Create')` | `[data-testid='create-btn']` | 🟡 Changed |
| jobList | `[data-testid='job-list']` | `[data-testid='job-list']` | ✅ Same |
| newFilter | — | `[data-testid='date-filter']` | 🟢 Added |
| oldWidget | `#legacy-widget` | — | 🔴 Removed |

### Files Updated
- `selectors/scheduled-jobs-dashboard.json` ✅
- `src/pages/scheduled-jobs/dashboard.page.ts` ✅ (1 locator updated)

### ⚠️ Tests to Verify
- `tests/e2e/scheduled-jobs/dashboard.spec.ts` — uses changed createButton
```
