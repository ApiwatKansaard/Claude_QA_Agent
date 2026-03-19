# /qa:regression-check [release scope or changelog]

**Triggers:** test-planner + test-case-reviewer agents
**References:** [agent-test-planner.md](../references/agent-test-planner.md), [agent-test-case-reviewer.md](../references/agent-test-case-reviewer.md), [test-lifecycle.md](../references/test-lifecycle.md)

## What This Command Does

Given the release scope or changelog, assess regression risk for each changed component.
Map existing test coverage to changes, identify uncovered or at-risk areas, and produce
a risk matrix the QA team can use to prioritize regression effort.

This command combines two agents:
- **test-planner** → identifies what needs to be tested given the changes
- **test-case-reviewer** logic → evaluates whether existing coverage is sufficient

## Parameters

| Parameter | Required | Notes |
|---|---|---|
| `[release scope or changelog]` | Yes | List of what changed: new features, refactored modules, bug fixes, config changes |

If the user also provides existing test case information or TestRail suite contents, use that
to assess coverage. If not, perform the risk analysis based on change type heuristics.

## Live Data Sources

| Tool | Purpose | Call |
|---|---|---|
| Google Calendar MCP | Read sprint end date and release schedule | `mcp_google-calend_list-calendars`, `mcp_google-calend_list-events` |
| Jira (Atlassian MCP) | Check recent bug history for risk multipliers | `searchJiraIssuesUsingJql` |

**Sprint and release context from Google Calendar:**
```
mcp_google-calend_list-calendars()
mcp_google-calend_list-events(calendarId, timeMin=today, timeMax=+21d)
```
Look for events with "sprint", "release", "RC", or "milestone" — use them to add timing
context to the risk matrix (e.g., "Release in 5 days — only P0+P1 regression feasible").

**Bug history for risk multipliers from Jira:**
```
searchJiraIssuesUsingJql(
  jql="project = AE AND issuetype = Bug AND component = '[component name]' AND created >= -90d",
  cloudId="ekoapp.atlassian.net"
)
```
If a component had 2+ bugs in the last 3 sprints, escalate its risk level by one tier.

## Execution Steps

1. **Parse the release scope** — categorize each change:
   - New feature (no existing coverage → needs full test plan)
   - Refactored component (existing tests may still be valid but should be verified)
   - Bug fix (targeted test for the fix + no-regression spot check)
   - Configuration / infra change (smoke test only)
   - AI/LLM model or prompt change (full LLM regression battery required)

2. **Apply risk multipliers** from [test-lifecycle.md](../references/test-lifecycle.md) — the following areas escalate risk:
   - Auth / session handling changes → always high risk
   - Payment, billing, PII data flows → always high risk
   - Core user journey components → high risk
   - Areas with recent bug history (2+ bugs in last 3 sprints) → elevated risk
   - AI/LLM model version change → requires probabilistic regression

3. **Map coverage status** — for each changed component:
   - **Ready**: existing P0/P1 test cases cover this change, no update needed
   - **Needs Test**: change introduces new behavior not covered by existing tests
   - **At Risk**: existing tests exist but may be stale or misaligned with the change

4. **Output the risk matrix** — see format below.

## Output Format

```markdown
# Regression Risk Assessment — [Release Name / Sprint]
*Scope analyzed: [brief summary of changes]*

## Risk Matrix

| Component | Change Type | Coverage Status | Risk Level | Action Required |
|---|---|---|---|---|
| Auth service | Refactored (SSO) | ⚠️ Needs Test | 🔴 High | Run full auth regression; add SSO-specific test cases |
| AI summarizer | New feature | ❌ At Risk | 🔴 High | No existing coverage — run /qa:test-plan against this feature |
| Mobile notification | Bug fix | ✅ Ready | 🟡 Medium | Run targeted fix test + P0 smoke |
| API rate limiter | Config only | ✅ Ready | 🟢 Low | Smoke test only — verify config applied |

**Risk levels:** 🔴 High (must test before release) | 🟡 Medium (should test) | 🟢 Low (smoke only)
**Coverage status:** ✅ Ready | ⚠️ Needs Test | ❌ At Risk

## Recommended Test Effort

| Surface | Focus Areas | Suggested Scope | Estimated Time |
|---|---|---|---|
| Auth / SSO | Full regression | All P0+P1 auth cases + new SSO cases | ~Xh |
| AI summarizer | Full new feature | /qa:test-plan then /qa:sync-testrail | ~Xh |
| Mobile notifications | Targeted | Fix test + P0 smoke | ~Xh |
| Rate limiter | Smoke | 2–3 critical path checks | ~30m |

## Coverage Gaps Requiring Action

1. **[High]** [Component] has no test cases for [specific scenario] — run /qa:test-plan before release
2. **[High]** [Component] tests not updated since [change] — review for staleness
3. **[Medium]** [Component] lacks AI/LLM regression cases — add consistency + adversarial tests

## Go/No-Go Recommendation

**Blockers (must resolve before release):**
- [ ] [Component]: [what needs to be done]

**Recommended (should resolve):**
- [ ] [Component]: [what would reduce risk]
```
