# Jira Workflows Reference

## Jira Instance
- Domain: `ekoapp.atlassian.net`
- All API calls use the Atlassian MCP with this domain

---

## Useful JQL Queries

### Daily QA Standup Queries

```jql
-- Bugs opened in the last 24 hours
project = AE AND issuetype = Bug AND created >= -1d ORDER BY priority ASC

-- Bugs actively being worked (assigned to QA team) — includes all active board columns
project = AE AND issuetype = Bug AND status in ("In Progress", "In Code Review", "Ready For Test", "In Test", "Blocked") AND assignee in membersOf("QA Team") ORDER BY priority ASC

-- Bugs resolved in the last 24 hours
project = AE AND issuetype = Bug AND status in (Resolved, Done) AND updated >= -1d ORDER BY resolutiondate DESC

-- High-priority open bugs not yet assigned
project = AE AND issuetype = Bug AND priority in (Critical, High) AND status = Open AND assignee is EMPTY

-- Bugs blocking a current sprint
project = AE AND issuetype = Bug AND sprint in openSprints() AND priority = Critical
```

### Regression and Release Queries

```jql
-- All bugs in current sprint
project = AE AND issuetype = Bug AND sprint in openSprints() ORDER BY priority ASC

-- Bugs opened against a specific version/release
project = AE AND issuetype = Bug AND fixVersion = "v2.1.0" ORDER BY priority ASC

-- Unresolved bugs older than 14 days
project = AE AND issuetype = Bug AND status not in (Resolved, Done, Closed) AND created <= -14d ORDER BY priority ASC

-- Test tasks/QA stories in current sprint
project = AE AND issuetype in (Task, Story, "Test Task") AND sprint in openSprints() AND labels = QA
```

### Triage Queries

```jql
-- Critical/High bugs without a fix version (unplanned)
project = AE AND issuetype = Bug AND priority in (Critical, High) AND fixVersion is EMPTY AND status not in (Done, Closed)

-- Bugs reported by QA (for QA-originated defects)
project = AE AND issuetype = Bug AND reporter in membersOf("QA Team") AND status not in (Done, Closed)
```

---

## Bug Report Field Mapping

When using `createJiraIssue`, map our bug report fields to Jira fields:

| Bug Report Field | Jira Field | Notes |
|---|---|---|
| Title / Summary | `summary` | Max 255 chars |
| Severity | `priority` | Critical → Highest, High, Medium, Low |
| Environment | `environment` | Custom field or description |
| Steps to Reproduce | `description` (Steps section) | Use structured format |
| Expected Result | `description` (Expected section) | |
| Actual Result | `description` (Actual section) | |
| Attachments | `attachments` | Screenshots, logs, videos |
| Affected Version | `versions` | AffectsVersion field |
| Fix Version | `fixVersions` | Set during triage, not bug creation |
| Labels | `labels` | e.g., `regression`, `ai-feature`, `api`, `mobile` |
| Epic Link | `customfield_10014` | If the bug belongs to an epic |

### Standard Labels to Use
- `regression` — found during regression testing
- `ai-feature` — related to AI/LLM functionality
- `api` — backend/API issue
- `mobile-ios` / `mobile-android` — platform-specific
- `flaky` — intermittent / hard to reproduce
- `blocker` — blocks release or other work
- `data-issue` — caused by bad test/production data

---

## Bug Severity vs. Jira Priority Mapping

| Severity (our definition) | Jira Priority | When to use |
|---|---|---|
| S1 - Critical | Highest | App crash, data loss, security breach, 100% blocker |
| S2 - High | High | Major feature broken, no workaround, affects many users |
| S3 - Medium | Medium | Feature partially broken, workaround exists |
| S4 - Low | Low | Minor cosmetic issue, edge case, low user impact |

---

## Triage Workflow

When triaging a set of open bugs for the dev team:

1. Pull bugs with `searchJiraIssuesUsingJql`
2. Group by: **Priority** (Critical/High first), then **Component/Feature area**
3. For each Critical/High bug, check:
   - Is it reproducible? (if unclear, flag for QA to re-verify)
   - Is it a regression? (tag `regression` if yes)
   - Does it have enough info for a dev to fix? (if not, flag for more details)
   - Does it have a fix version assigned?
4. Output triage summary with recommended actions per bug

### Triage Output Format

```
## Bug Triage Summary — [Date]

### 🔴 Critical (immediate action required)
- [AE-XXX] Title — Status: Open — Owner: Unassigned
  → Recommended: Assign to [dev name], target this sprint

### 🟠 High (this sprint)
- [AE-XXX] Title — Status: In Progress — Owner: Dev A
  → On track

### 🟡 Medium (next sprint or backlog)
...

### Notes
- N bugs are unassigned and high priority (needs triage meeting)
- N bugs are older than 14 days with no update (needs follow-up)
```

---

## Adding Comments to Jira

When updating a Jira issue with QA findings, use `addCommentToJiraIssue`:
- Keep comments factual and reproducible-step focused
- Include environment details (browser, OS, build version)
- Tag the relevant dev or PM with `@mention` in the comment body
- For probabilistic LLM bugs, include run count and repro rate
