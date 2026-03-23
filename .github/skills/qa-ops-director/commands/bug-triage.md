# /qa:bug-triage [Jira bug list or filter URL]

**Triggers:** bug-analyzer agent
**References:** [agent-bug-analyzer.md](../references/agent-bug-analyzer.md), [jira-workflows.md](../references/jira-workflows.md)

## What This Command Does

Analyze a set of Jira bugs, classify each by severity and root cause, identify AI/model-specific
failure modes separately, and produce a prioritized triage table the dev team can act on.

## Parameters

| Parameter | Required | Notes |
|---|---|---|
| `[Jira bug list or filter URL]` | Yes | Jira issue keys (e.g. AE-5001, AE-5002), a filter URL, a JQL query, or bugs pasted inline |

**Input formats accepted:**
- Jira filter URL → extract filter ID and fetch via `fetchAtlassian`
- Jira issue keys → fetch each via `mcp_atlassian_read_jira_issue`
- JQL query text → run via `mcp_atlassian_search_jira_issues`
- Bug descriptions pasted inline → parse directly

If no bugs are provided at all, offer to pull using a default JQL:
```
project = AE AND issuetype = Bug AND sprint in openSprints() AND status not in (Done, Closed, Passed, "Won't fix", "Can't reproduce") ORDER BY priority ASC
```

## Live Data Sources

| Tool | Purpose | Call |
|---|---|---|
| Jira (Atlassian MCP) | Fetch bug details, comments, metadata | `mcp_atlassian_read_jira_issue`, `mcp_atlassian_search_jira_issues` |

**Fetching strategies by input type:**

| Input | How to fetch |
|---|---|
| Jira issue keys (e.g., AE-5001) | `mcp_atlassian_read_jira_issue(issueKey="AE-5001")` for each |
| JQL query text | `mcp_atlassian_search_jira_issues(jql="...")` |
| Jira filter URL | Extract filter ID, use JQL from filter |
| Bug text pasted inline | Parse directly, no MCP call needed |

## Execution Steps

1. **Fetch all bugs** from the provided source. For each bug collect:
   title, description, steps to reproduce, priority, status, assignee, labels, environment.

2. **Analyze each bug** using the framework in [agent-bug-analyzer.md](../references/agent-bug-analyzer.md):
   - Assign severity (S1–S4) — reconcile with Jira priority if they differ
   - Identify root cause area (Frontend / Backend/API / **AI Behavior** / Infrastructure / Data / Integration)
   - Assess reproducibility (always / sometimes / rare / probabilistic)
   - For **AI Behavior** bugs: classify the failure type (output quality / format failure / safety / prompt regression / non-determinism / graceful degradation)
   - Apply priority routing: deterministic AI bugs → P1/P0; probabilistic AI bugs → lower Dev priority, **higher QA monitoring priority**
   - Assign recommended owner team

3. **Detect clusters** — if 2+ bugs share the same root cause area AND the same feature component,
   call them out in the pattern summary. Clusters suggest a systemic issue worth a single investigation
   rather than N separate fixes.

4. **Flag enrichment gaps** — for any S1 or S2 bug missing critical info (no steps, no env, no model version),
   call out exactly what's missing so QA can add it before handing off.

## Output Format

```markdown
# Bug Triage — [Date] | [Sprint or filter context]

**Bugs analyzed:** N  |  S1: N  |  S2: N  |  S3: N  |  S4: N

## Triage Table

| Bug ID | Title | Severity | Root Cause Area | Reproducibility | Recommended Owner | Action |
|---|---|---|---|---|---|---|
| AE-XXXX | [title] | S1 — Critical | Backend/API | always | Backend team | Fix this sprint — blocks [flow] |
| AE-XXXX | [title] | S2 — High | AI Behavior | probabilistic (3/10) | ML team | Dev: P2 (lower); QA monitoring: HIGH — add to LLM regression battery |
| AE-XXXX | [title] | S3 — Medium | Frontend | sometimes | FE team | Reproduce in staging; check component state |
| AE-XXXX | [title] | S4 — Low | Data | rare | QA | Low priority; verify with production data |

## Pattern Summary

[Only include if 2+ bugs form a cluster]

**Cluster: [Root cause area] — [Feature] (N bugs)**
[Bug IDs]: [1–2 sentence description of the shared pattern]
Recommend: [single investigation ticket / joint owner / root cause review]

## Enrichment Needed

[List S1/S2 bugs missing critical info]
- AE-XXXX: missing — [exact info needed, e.g. "API request payload, model version at time of failure"]
```
