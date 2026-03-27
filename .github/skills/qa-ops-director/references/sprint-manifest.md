# Sprint Manifest — `.sprint.json`

A `.sprint.json` file at the root of `Claude_QA_Automation` is the single source of truth for the active sprint. Skills read this file to avoid asking repetitive questions about product, suite, and directory paths.

---

## Schema

```json
{
  "sprint": "sprint-name",
  "product": "agentic | bots | asap",
  "feature": "scheduled-jobs",
  "jiraProject": "AE",
  "jiraBoardId": 32,
  "testrailSuiteId": 5137,
  "testrailMilestoneId": 904,
  "dirs": {
    "e2e": "tests/e2e/agentic/scheduled-jobs",
    "api": "tests/api/agentic/scheduled-jobs",
    "pages": "src/pages/agentic/scheduled-jobs",
    "selectors": "selectors/agentic/scheduled-jobs.json",
    "archive": "archive/agentic/sprint-name"
  },
  "previousSprint": "archive/agentic/sharp-test-001",
  "startDate": "2026-03-01",
  "endDate": null
}
```

---

## Field reference

| Field | Required | Description |
|---|---|---|
| `sprint` | ✅ | Sprint identifier (matches archive folder name) |
| `product` | ✅ | Product namespace — must match an entry in `products.md` |
| `feature` | ✅ | Feature name used for tagging and folder naming |
| `jiraProject` | ✅ | Jira project key for issue lookup |
| `jiraBoardId` | ✅ | Jira board ID for sprint issue queries |
| `testrailSuiteId` | ✅ | TestRail suite ID (number without `S` prefix) |
| `testrailMilestoneId` | ✅ | TestRail milestone ID (set after `/qa-start-sprint`) |
| `dirs` | ✅ | Resolved paths for test/page/selector files |
| `previousSprint` | optional | Path to previous sprint archive for regression baseline |
| `startDate` | ✅ | ISO date — sprint start |
| `endDate` | optional | ISO date — set by `/qa-end-sprint` when archiving |

---

## Lifecycle

| Event | `.sprint.json` change |
|---|---|
| `/qa-start-sprint` | Creates file with all fields; sets `testrailMilestoneId` after milestone created |
| `/qa-end-sprint` | Sets `endDate`; moves file to `{archive}/{product}/{sprint}/sprint.json` |
| `/auto-generate` | Reads `dirs.e2e`, `dirs.pages`, `testrailSuiteId`, `feature` |
| `/auto-run` | Reads `dirs.e2e`, `dirs.api` to build test path arguments |
| `/qa-create-regression` | Reads `testrailSuiteId`, `testrailMilestoneId`, `sprint` |

---

## How skills read it

```bash
# At the start of any skill that needs sprint context:
SPRINT_FILE="$(git rev-parse --show-toplevel)/.sprint.json"
if [ -f "$SPRINT_FILE" ]; then
  # Read product, feature, dirs from file — no need to prompt user
else
  # Fall back to asking user, then look up defaults in products.md
fi
```

In practice, skills use Claude's Read tool: `Read .sprint.json` at the start of each command.
