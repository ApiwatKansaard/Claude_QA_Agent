# /auto:map — Test Case to Automation Mapping

## Trigger
`/auto:map [sprint-folder]`

## Parameters
- `[sprint-folder]` — Sprint folder path. Auto-detected if omitted.

## Pipeline

### Phase 1: Load Data

1. Read all test cases from `{sprint-folder}/*-testcases.csv`
2. Read all test files from `tests/` in QA_Automation
3. Read existing mapping file if it exists: `test-mapping.json` (in QA_Automation root)

### Phase 2: Match

For each CSV test case:
1. Match by section + title to `test.describe()` + `test()` names in spec files
2. If no exact match → fuzzy match (Levenshtein or keyword overlap)
3. Classify:
   - `automated` — matching test found
   - `pending` — automatable but no test yet
   - `not-automatable` — infrastructure, manual-only, or device-dependent

### Phase 3: Output

**A. Mapping file** — `test-mapping.json` (in QA_Automation root):
```json
[
  {
    "section": "Agentic > Scheduled Jobs > Dashboard",
    "title": "Check scheduled jobs list should be displayed",
    "type": "Smoke Test",
    "priority": "P1",
    "automationFile": "tests/e2e/scheduled-jobs/dashboard.spec.ts",
    "automationTest": "should display job list on Dashboard page",
    "status": "automated",
    "tags": ["@smoke", "@P1", "@scheduled-jobs"]
  }
]
```

**B. Summary table**:
```markdown
## 📊 Test Automation Map — agentic-18.2

| Section | Total | Automated | Pending | Not Auto |
|---------|-------|-----------|---------|----------|
| Dashboard | 7 | 5 | 1 | 1 |
| Create Job | 12 | 8 | 3 | 1 |
| API Endpoints | 15 | 12 | 3 | 0 |
| ... | | | | |
| **TOTAL** | **168** | **120** | **33** | **15** |

**Coverage: 71.4%**

### 🔴 Pending (High Priority)
- [ ] Dashboard: "Check error state should be displayed..." (P2, Regression)
- [ ] Create Job: "Check wizard should retain data on back..." (P1, Smoke)
- ...

### ⚪ Not Automatable
- Infrastructure: "Check BullMQ queue cleanup..." (requires Redis access)
- Race Conditions: "Check cutoff vs completion race..." (timing-dependent)
```
