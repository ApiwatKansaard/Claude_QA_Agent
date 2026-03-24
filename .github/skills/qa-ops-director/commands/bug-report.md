# /qa:bug-report [bug description or screenshot]

**Triggers:** bug-reporter
**References:** [agent-bug-reporter.md](../references/agent-bug-reporter.md), [jira-workflows.md](../references/jira-workflows.md), [templates.md](../references/templates.md)

> **Independence:** This command works standalone — it does NOT depend on `/qa:write-ac`.
> Phase 6 generates a lightweight Bug Fix Criteria comment (3-5 items, no 6-point review).
> If `/qa:write-ac` runs later on the same sprint, it may replace the Bug Fix Criteria
> with a full Acceptance Criteria (Bug Fix) comment that includes the 6-point review.

## What This Command Does

Compose a well-structured Jira bug ticket from a user-provided screenshot, description, or conversation,
enriched with context from the current sprint's test plan, test cases, and spec documents.
Preview the ticket for user approval, then create it in Jira via MCP.

## Parameters

| Parameter | Required | Notes |
|---|---|---|
| `[bug description or screenshot]` | Yes | Screenshot image, text description, error message, or URL where the bug occurs |

**Input formats accepted:**
- Screenshot pasted in chat → describe what you see (UI state, error, unexpected behavior)
- Text description of the bug → parse directly
- URL of the page where the bug occurs → note in bug report
- Combination of the above

## Execution Steps (6-Phase Pipeline)

### Phase 1: Gather Bug Context from User

Extract from the user's input:
- **What happened** (actual behavior)
- **What was expected** (if stated or inferable)
- **Where** (URL, screen, feature area)
- **Visual evidence** (screenshot, error message)
- **Environment** (if mentioned: browser, device, build version)

If critical info is missing, ask the user **once** with a focused question — don't block on nice-to-haves.
Minimum viable input: a screenshot OR a 1-sentence description of the bug. The agent fills in the rest.

### Phase 2: Enrich from Sprint Artifacts

Read the current sprint folder to build context. Locate the active sprint folder by checking
the workspace root for non-archived sprint directories (e.g., `agentic-18.2/`).

**Files to read (in order):**

1. **Test plan** (`{sprint-folder}/*-test-plan.md`)
   - Extract: feature scope, spec links, in-scope components, test approach
   - Use to: identify which feature area the bug belongs to, find the correct epic/story link

2. **Test cases** (`{sprint-folder}/*-testcases.csv`)
   - Extract: related test case IDs, steps that match the bug scenario
   - Use to: link the bug to specific test cases, infer expected behavior if user didn't state it

3. **Release notes** (`{sprint-folder}/release-notes-*.md`)
   - Extract: what changed in this sprint, new features, known limitations
   - Use to: determine if this is a regression vs. new feature bug

4. **Confluence spec** (if referenced in test plan)
   - Extract: acceptance criteria, business rules
   - Use to: validate expected behavior and write precise description

**Mapping logic:**
- Match the bug's feature area (from user description + screenshot) to test plan sections
- Find the closest test case(s) and reference their IDs in the bug description
- If the bug matches a test case's expected result that was NOT met → mark as `regression`
- If the bug is in a NEW feature area from this sprint → label accordingly

### Phase 3: Compose Bug Ticket

Build the Jira issue payload using insights from Phase 1 + Phase 2.

**Field mapping:**

| Field | Source | Rule |
|---|---|---|
| `summary` | User description + agent analysis | Concise, specific: "[Component] Actual behavior (context)" — max 120 chars |
| `description` | Structured ADF | Environment + Evidence + Related TCs + Additional Context (see ADF template below) |
| `issueType` | Always | `"Bug"` |
| `projectKey` | Always | `"AE"` |
| `priority` | Agent assessment | Map severity → Jira priority (see severity table) |
| `labels` | Agent analysis | From standard label set (see jira-workflows.md) |
| `components` | Feature area mapping | If known from test plan |
| `customfield_11536` | Squad mapping | **REQUIRED** — EKO Squad. Use `{"id": "14379"}` for Broccoli (default). Options: EGT=11641, Broccoli=14379, Carrot=14544, Spinach=14545 |
| `customfield_11435` | Actual results | **ADF doc** — What actually happened (from user description/screenshot) |
| `customfield_11436` | Expected results | **ADF doc** — What should happen (from test case, AC, or user statement) |
| `customfield_11437` | Step to reproduce | **ADF doc** — Numbered steps + environment info |
| `customfield_11390` | Severity | **Select option** — S1=`11005`, S2=`11006`, S3=`11007`, S4=`11008`, S5=`11875` |
| `customfield_11389` | Platform | **Select option** — All Platforms=`10995`, All Web Apps=`10996`, All Mobile Apps=`10997` |

⚠️ **IMPORTANT — ADF format required for text custom fields:**
`customfield_11435`, `customfield_11436`, `customfield_11437` must be Atlassian Document Format (ADF), NOT plain strings.
Convert plain text to ADF: each line becomes a paragraph node.
```python
def text_to_adf(text):
    lines = text.split('\n')
    content = []
    for line in lines:
        if line.strip():
            content.append({"type": "paragraph", "content": [{"type": "text", "text": line}]})
        else:
            content.append({"type": "paragraph", "content": []})
    return {"type": "doc", "version": 1, "content": content}
```

**Description field** still contains supplementary context (environment, evidence, related TCs, additional context).
The main bug data goes into the dedicated custom fields:

| Custom Field | Contains |
|---|---|
| `customfield_11437` (Step to reproduce) | Numbered steps + environment/browser info |
| `customfield_11436` (Expected results) | What should happen |
| `customfield_11435` (Actual results) | What actually happened |
| `description` | Environment, Evidence, Related TCs, Additional Context |

**Severity assessment:**

| Severity | Jira Priority | `customfield_11390` id | Criteria |
|---|---|---|---|
| S1 — Critical | Highest | `11005` | App crash, data loss, security breach, blocks core flow 100% |
| S2 — High | High | `11006` | Major feature broken, significant user impact, no workaround |
| S3 — Medium | Medium | `11007` | Feature partially broken, workaround exists, limited impact |
| S4 — Low | Low | `11008` | Minor cosmetic, edge case, minimal impact |

### Phase 4: Preview for User Approval

Present the complete ticket to the user in a readable format:

```markdown
## 📋 Bug Ticket Preview

**Summary:** [title]
**Project:** AE
**Type:** Bug
**Priority:** [priority] ([severity rationale])
**Labels:** [labels]

---

### Description

[Full description as it will appear in Jira]

---

✅ **Approve** — I'll create this ticket in Jira
✏️ **Edit** — Tell me what to change (e.g., "change priority to High", "add label regression")
❌ **Cancel** — Discard this ticket
```

**Wait for explicit user confirmation before proceeding to Phase 5.**
If the user requests edits, apply them and show the updated preview. Loop until approved or cancelled.

### Phase 5: Create in Jira (2-Step Process)

Once approved, create the issue using **Jira REST API v3 via Python script** (not MCP — `mcp_atlassian_create_jira_issue` returns `undefined` on project AE due to required custom fields).

**⚠️ Creation requires TWO steps — Sprint cannot be set during creation, only after.**

#### Step 1: Create the issue (POST)

Write payload to `/tmp/jira-bug-payload.json` and run script:

```json
{
  "fields": {
    "project": {"key": "AE"},
    "issuetype": {"name": "Bug"},
    "summary": "...",
    "priority": {"name": "Low"},
    "labels": ["api"],
    "customfield_11536": {"id": "14379"},
    "customfield_11435": { ADF doc — actual results },
    "customfield_11436": { ADF doc — expected results },
    "customfield_11437": { ADF doc — steps to reproduce },
    "customfield_11390": {"id": "11008"},
    "customfield_11389": {"id": "10996"},
    "description": { ADF doc — environment + evidence + related TCs + context }
  }
}
```

#### Step 2: Assign Sprint (POST to Agile API)

Sprint field uses a **different format** — must use the Agile REST API **after** issue creation:

```python
# Move issue to sprint via Agile API
req = urllib.request.Request(
    f'https://ekoapp.atlassian.net/rest/agile/1.0/sprint/{sprint_id}/issue',
    data=json.dumps({"issues": ["AE-XXXXX"]}).encode(),
    headers={'Content-Type': 'application/json', 'Authorization': f'Basic {creds}'},
    method='POST'
)
```

**Active Sprint IDs** (discover via `GET /rest/agile/1.0/board/257/sprint?state=active`):
- Broccoli - F = `4077` (current Agentic sprint)
- EGT 18.1 = `4011`

#### Required custom fields reference:

| Field | ID | Format | Values |
|---|---|---|---|
| EKO Squad | `customfield_11536` | `{"id": "..."}` | Broccoli=14379, EGT=11641, Carrot=14544, Spinach=14545 |
| Actual results | `customfield_11435` | ADF doc | Free text |
| Expected results | `customfield_11436` | ADF doc | Free text |
| Step to reproduce | `customfield_11437` | ADF doc | Free text |
| Severity | `customfield_11390` | `{"id": "..."}` | S1=11005, S2=11006, S3=11007, S4=11008, S5=11875 |
| Platform | `customfield_11389` | `{"id": "..."}` | All Platforms=10995, All Web=10996, All Mobile=10997 |
| Sprint | `customfield_10006` | Agile API (see Step 2) | Board 257 sprints |

**Auth:** Email `apiwat@amitysolutions.com` + token from macOS Keychain (`jira-api-token`)

**After creation — ALWAYS do ALL of the following:**
1. **Send the link immediately:** `✅ Created: [AE-XXXXX](https://ekoapp.atlassian.net/browse/AE-XXXXX)`
2. Show summary + priority + labels + sprint
3. Note that screenshot attachments must be added manually (API does not support file upload)

> **Rule: ALWAYS send the Jira link back to the user after creating a ticket. No exceptions.**

### Phase 6: Generate & Post Bug Fix Criteria (AC)

After the bug ticket is created and the link is sent, **automatically** generate and post
Bug Fix Criteria as an ADF table comment on the newly created ticket.

⚠️ This phase runs AUTOMATICALLY after Phase 5 — no user prompt needed.
It uses the same AC format as `/qa:write-ac` (Bug template) to keep consistency.

#### 6.1 — Read the Ticket Back

Fetch the full ticket data (including all fields and comments) to confirm creation:
```
mcp_atlassian_read_jira_issue(issueKey="AE-XXXXX")
```

Extract from the ticket:
- Summary, description, priority, labels, status
- `customfield_11435` (Actual results)
- `customfield_11436` (Expected results)
- `customfield_11437` (Step to reproduce)
- Existing comments (to detect if AC was already posted)

#### 6.2 — Generate Bug Fix Criteria

> **Note:** This is a lightweight AC generation (no 6-point ac-reviewer checklist).
> If the full `/qa:write-ac` pipeline runs later, it may replace this comment with a
> higher-quality AC using the 6-point review. That's expected behavior.

Using data from Phase 2 (sprint artifacts) + Phase 3 (composed ticket), generate 3-5 AC items:

| # | Type | Source | Purpose |
|---|---|---|---|
| 1 | ✅ Positive | Bug fix verification | The specific bug described is fixed — verify the exact scenario |
| 2 | ✅ Positive | Related behavior | A closely related flow still works after the fix |
| 3 | ❌ Negative | Error handling | Invalid/edge input around the fix area is handled correctly |
| 4 | ⚠️ Edge case | Boundary condition | Edge case near the bug scenario (e.g., empty data, max values) |
| 5 | ✅ Positive | Regression check | Another feature in the same area is not broken by the fix |

**Rules:**
- Min 3 items, max 5 items (bugs are narrower scope than stories)
- Always start with the **specific bug fix verification** as item #1
- Reference test case IDs from Phase 2 if matched
- Title: `"Bug Fix Criteria — QA Generated"`
- If bug didn't match any test cases, use generic regression criteria

#### 6.3 — Post as ADF Table Comment

Post the Bug Fix Criteria as an ADF table comment using Jira REST API v3:
```
POST /rest/api/3/issue/{issueKey}/comment
```

Use the **same ADF table structure** as `daily-ac-agent.py` and `/qa:write-ac`:
- Heading: `Bug Fix Criteria — QA Generated`
- Table: `# | Type | Criteria | TC Ref`
- Footer: Icon Legend + Ref line + Generated date

```json
{
  "body": {
    "version": 1,
    "type": "doc",
    "content": [
      {"type": "heading", "attrs": {"level": 3}, "content": [{"type": "text", "text": "Bug Fix Criteria — QA Generated"}]},
      {
        "type": "table",
        "attrs": {"isNumberColumnEnabled": false, "layout": "default"},
        "content": [
          {"type": "tableRow", "content": [
            {"type": "tableHeader", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "#", "marks": [{"type": "strong"}]}]}]},
            {"type": "tableHeader", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Type", "marks": [{"type": "strong"}]}]}]},
            {"type": "tableHeader", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Criteria", "marks": [{"type": "strong"}]}]}]},
            {"type": "tableHeader", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "TC Ref", "marks": [{"type": "strong"}]}]}]}
          ]},
          ... data rows ...
        ]
      },
      {"type": "rule"},
      {"type": "paragraph", "content": [
        {"type": "text", "text": "Icon Legend: ", "marks": [{"type": "strong"}]},
        {"type": "text", "text": "✅ Positive (expected behavior) · ❌ Negative (error/rejection) · ⚠️ Edge case (boundary/race condition)"}
      ]},
      {"type": "paragraph", "content": [
        {"type": "text", "text": "Ref: ", "marks": [{"type": "strong"}]},
        {"type": "text", "text": "[Matched spec group] · Test Cases: [TC-IDs]"}
      ]},
      {"type": "paragraph", "content": [
        {"type": "text", "text": "Generated: ", "marks": [{"type": "strong"}]},
        {"type": "text", "text": "[date] by QA Agent (bug-reporter)"}
      ]}
    ]
  }
}
```

#### 6.4 — Verify & Report

After posting, re-read the ticket to verify the comment was posted:
```
mcp_atlassian_read_jira_issue(issueKey="AE-XXXXX")
```

Report to the user:
```markdown
🎯 **Bug Fix Criteria posted on AE-XXXXX:**

| # | Type | Criteria | TC Ref |
|---|---|---|---|
| 1 | ✅ Positive | [specific fix verification] | TC-XXX |
| 2 | ✅ Positive | [related behavior check] | TC-XXX |
| 3 | ❌ Negative | [error handling check] | — |
| 4 | ⚠️ Edge case | [boundary condition] | TC-XXX |

✅ Comment verified on ticket.
```

If posting fails, show the AC as markdown and note the error.

## Error Handling

| Scenario | Action |
|---|---|
| No sprint folder found | Skip Phase 2 enrichment; compose from user input only; warn user |
| Test plan/cases not found in sprint folder | Skip artifact matching; note "No test plan context available" |
| User provides only a screenshot with no text | Describe what you see in the screenshot; ask one clarifying question |
| Jira API error on creation | Show the error; offer to retry or output the ticket as markdown for manual creation |
| User cancels | Confirm cancellation; offer to save the draft as a markdown file |

## Output

The final output is:
- A created Jira ticket (issue key + link) **with Bug Fix Criteria AC comment**, OR
- A markdown-formatted bug report (if user cancels or Jira is unavailable)

**Full output includes:**
1. Jira ticket link (Phase 5)
2. Bug Fix Criteria table posted as comment (Phase 6)
3. Summary: priority + labels + sprint + AC item count
