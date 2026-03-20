# /qa:create-regression [feature or sprint name] [suite_id] [impact description]

**Triggers:** testrail-manager agent
**References:** [agent-testrail-manager.md](../references/agent-testrail-manager.md), [testrail-api.md](../references/testrail-api.md), [ai-llm-testing.md](../references/ai-llm-testing.md)

## What This Command Does

Create a TestRail milestone and regression test run for a sprint or feature release.
Analyzes which sections are impacted by the new feature, proposes a scoped regression plan,
shows it for user review, then creates the milestone and test run via API with the correct case IDs.

## Parameters

| Parameter | Required | Notes |
|---|---|---|
| `[feature or sprint name]` | Yes | e.g., "AI Scheduled Jobs", "Sprint Broccoli-F", "EGT 18.0" |
| `[suite_id]` | No | TestRail suite to scope the run to — defaults to `3924` ([Main] Agentic) |
| `[impact description]` | No | What areas this feature touches — used to select regression sections |

**Team defaults:** project `1`, host `ekoapp20.testrail.io`

If `[impact description]` is not provided, ask:
> "Which feature areas does [feature name] impact? (e.g., 'Base Skill, Internal Library, Chat UI') — or should I include all P0/P1 cases?"

## Execution Steps

### 1. Gather Context

- If Jira sprint is available, fetch sprint issues via Atlassian MCP:
  ```
  mcp_atlassian_search_jira_issues(jql="project = AE AND sprint = '[sprint name]' AND issuetype in (Story, Task)")
  ```
  Use issue summaries to infer which feature areas are affected.

- If impact description is provided, use it directly to identify affected sections.

### 2. Fetch Suite Structure

```
GET /get_sections/{project_id}&suite_id={suite_id}&limit=250
GET /get_cases/{project_id}&suite_id={suite_id}&limit=250  (+ paginate)
```

Build section tree and case list with priorities.

### 3. Build Regression Scope

Select cases based on impact analysis:

**Priority rules:**
1. All P0 cases in impacted sections → always include
2. All P1 cases in impacted sections → always include
3. P0/P1 cases in adjacent sections (may be affected indirectly) → include with note
4. P2 cases in directly impacted sections → optional (ask user)
5. AI Mandatory scenarios (M1–M5 from [ai-llm-testing.md](../references/ai-llm-testing.md)) → always include if feature is AI/LLM

**Exclusion rules:**
- Platform-specific cases (iOS/Android) unless platform is explicitly in scope
- Cases marked as blocked or obsolete (if detectable)

### 4. Show Regression Plan for Review (REQUIRED)

```markdown
## Regression Plan — [Feature/Sprint Name]

**Milestone:** [feature name] Release — [auto-suggested due date from calendar or ask]
**Suite:** [suite name] (S[suite_id])
**Total cases proposed:** N

### Scope by Section

| Section | P0 | P1 | P2 | Total | Included? |
|---|---|---|---|---|---|
| Agentic > Base Skill > Internal Library | 3 | 5 | 4 | 12 | ✅ Direct impact |
| Agentic > Functional | 2 | 3 | 6 | 11 | ✅ Direct impact |
| Agentic > UI | 1 | 2 | 3 | 6 | ⚠️ Adjacent |
| Agentic > iOS > Chat | 2 | 4 | 5 | 11 | ❌ Not in scope (mobile) |

**P0 cases included:** N
**P1 cases included:** N
**P2 cases included:** N (optional)

### Proposed Milestone
**Name:** [name]
**Due date:** [date from calendar or suggested]

### Proposed Test Run
**Name:** [feature/sprint] Regression — P0+P1
**Scope:** N cases from X sections

Confirm? (yes / adjust scope / cancel)
```

### 5. Check Google Calendar for Release Date

```
mcp_google-calend_list-calendars()
mcp_google-calend_list-events(calendarId, timeMin=today, timeMax=+30d)
```
Look for events with "release", "RC", or sprint name. Use as milestone due date suggestion.

### 6. Create Milestone (after confirmation)

```
POST /add_milestone/{project_id}
{
  "name": "[feature] Release",
  "description": "Regression coverage for [feature name]. Sprint: [sprint]. Sections: [list].",
  "due_on": [unix_timestamp_of_due_date]
}
```

### 7. Create Test Run (after milestone created)

```
POST /add_run/{project_id}
{
  "suite_id": [suite_id],
  "name": "[feature/sprint] Regression — P0+P1",
  "description": "Auto-generated regression run. Impact: [description].",
  "milestone_id": [created_milestone_id],
  "case_ids": [array_of_selected_case_ids]
}
```

### 8. Report Results

```markdown
## Regression Created ✅

**Milestone:** [name]
🔗 https://ekoapp20.testrail.io/index.php?/milestones/view/{milestone_id}

**Test Run:** [name]
🔗 https://ekoapp20.testrail.io/index.php?/runs/view/{run_id}

**Cases in run:** N (P0: X | P1: Y | P2: Z)
**Sections covered:** [list]

Next step: assign the run to your QA engineers and start execution.
```

## AI Feature Regression Rules

When the feature involves AI/LLM behavior, always include these mandatory scenarios
from [ai-llm-testing.md](../references/ai-llm-testing.md):

| Scenario | Section to add to |
|---|---|
| M1 — Prompt injection resistance | Agentic > Security |
| M2 — Hallucination rate (3-run consistency) | Agentic > Functional |
| M3 — Output format compliance | Agentic > Functional |
| M4 — Latency under load | Agentic > Functional |
| M5 — Graceful degradation | Agentic > Functional |

If these cases don't exist in TestRail yet, offer to create them via `/qa:import-testrail`.
