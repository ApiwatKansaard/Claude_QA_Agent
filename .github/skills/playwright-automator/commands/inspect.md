# /auto:inspect — Inspect URL for Selectors

## Trigger
`/auto:inspect [URL] [page-name]`

## Parameters
- `[URL]` — The URL to inspect (e.g., `https://console.ekoai.dev/scheduled-jobs`)
- `[page-name]` — Optional name for the page (e.g., "dashboard"). Auto-derived from URL if omitted.

## Pipeline

### Phase 1: Fetch Page

1. Use `fetch_webpage` tool to get the HTML content of the URL
2. If login is required, note it and suggest manual inspection via `npx playwright codegen`
3. Parse the DOM structure

### Phase 2: Extract Elements

Scan the HTML for interactive and structural elements:

| Element Type | What to Extract |
|---|---|
| **Buttons** | text, id, data-testid, aria-label, class |
| **Inputs** | type, name, id, data-testid, placeholder, label |
| **Links** | href, text, id, data-testid |
| **Tables** | headers, row structure, data-testid |
| **Dropdowns** | options, name, id, data-testid |
| **Navigation** | menu items, active states |
| **Modals/Dialogs** | trigger, content areas |
| **Forms** | action, fields, submit button |
| **Toasts/Alerts** | role="alert", notification areas |
| **Empty states** | fallback content, placeholder areas |

### Phase 3: Build Selector Map

Apply selector strategy (priority order):
1. `data-testid` → `page.getByTestId('...')`
2. ARIA role + name → `page.getByRole('button', { name: '...' })`
3. Label → `page.getByLabel('...')`
4. Visible text → `page.getByText('...')`
5. CSS selector → `page.locator('...')` (last resort)

### Phase 4: Output

**A. Selector map file** — saved to `selectors/{page-name}.json` (in QA_Automation):
```json
{
  "pageName": "scheduled-jobs-dashboard",
  "url": "https://console.ekoai.dev/scheduled-jobs",
  "inspectedAt": "2026-03-25T10:00:00Z",
  "elements": {
    "jobList": {
      "selector": "[data-testid='job-list']",
      "playwright": "page.getByTestId('job-list')",
      "type": "testid",
      "description": "Main job list table"
    },
    "createButton": {
      "selector": "button:has-text('Create')",
      "playwright": "page.getByRole('button', { name: 'Create' })",
      "type": "role",
      "description": "Create new scheduled job button"
    }
  }
}
```

**B. Summary table** — shown to user:
```markdown
## 🔍 Inspection: scheduled-jobs-dashboard

| Element | Selector | Type | Playwright |
|---------|----------|------|------------|
| Job List | `[data-testid='job-list']` | testid | `getByTestId('job-list')` |
| Create Button | `button[Create]` | role | `getByRole('button', { name: 'Create' })` |
| Status Filter | `#status-filter` | id | `locator('#status-filter')` |
| ... | | | |

**Next:** Run `/auto:scaffold dashboard` to generate a Page Object from these selectors.
```

### Phase 5: Optional — Generate Page Object

If user confirms, generate a Page Object from the selector map:
- Read the saved JSON selector map
- Create `src/pages/{feature}/{page-name}.page.ts`
- Map each selector to a class property
- Generate action methods based on element types (click, fill, select)

## Notes

- If the page requires authentication, suggest:
  ```bash
  npx playwright codegen https://console.ekoai.dev/scheduled-jobs
  ```
  This opens a browser with recording. The user can log in manually and the selectors
  will be captured.

- For SPAs: the initial HTML may not have all elements. Note that dynamic content
  requires browser-rendered inspection (codegen is better for this).

- Always suggest re-running `/auto:inspect` after UI updates in new sprints.
