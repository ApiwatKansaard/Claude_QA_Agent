# 03 — MCP to REST API Migration Guide

> ข้อกังวลหลัก: MCP ใช้ stdio (child process) → จะใช้จาก web browser ได้อย่างไร?
> คำตอบ: Bypass MCP ทั้งหมด → เรียก REST API ตรงจาก backend

---

## ทำไม MCP ใช้จาก Web ไม่ได้

MCP (Model Context Protocol) ใช้ **stdio transport** — หมายความว่า:
- MCP server รันเป็น **child process** ของ VS Code
- สื่อสารผ่าน **stdin/stdout** (JSON-RPC)
- ต้องการ **local filesystem** access สำหรับ credential files
- **ไม่มี HTTP server** ที่ browser จะเรียกได้

```
VS Code ──stdin/stdout──→ mcp-atlassian binary ──HTTP──→ Jira REST API
                    ↑
                    │
            ไม่มีทาง web browser
            จะเข้าถึง stdio ได้
```

---

## Solution: ทุก MCP เป็นแค่ REST API Wrapper

**ข่าวดี:** MCP servers ทั้งหมดแค่ wrap REST API ธรรมดา ข้างในมันเรียก HTTP request เหมือน `fetch()` ปกติ

### Atlassian MCP → Jira/Confluence REST API

**MCP ทำอะไร:**
```
mcp-atlassian binary
  → reads env: ATLASSIAN_EMAIL, ATLASSIAN_API_TOKEN
  → makes HTTP requests to: https://ekoapp.atlassian.net/rest/api/3/*
  → returns JSON via stdout
```

**Web backend ทำเหมือนกัน:**
```typescript
// packages/integrations/jira.ts
export class JiraClient {
  private baseUrl = 'https://ekoapp.atlassian.net';
  private authHeader: string;

  constructor(email: string, token: string) {
    this.authHeader = 'Basic ' + Buffer.from(`${email}:${token}`).toString('base64');
  }

  async getIssue(issueKey: string) {
    const res = await fetch(`${this.baseUrl}/rest/api/3/issue/${issueKey}`, {
      headers: {
        'Authorization': this.authHeader,
        'Content-Type': 'application/json',
      },
    });
    return res.json();
  }

  async createBug(projectKey: string, summary: string, description: string, fields: Record<string, any>) {
    const res = await fetch(`${this.baseUrl}/rest/api/3/issue`, {
      method: 'POST',
      headers: {
        'Authorization': this.authHeader,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        fields: {
          project: { key: projectKey },
          issuetype: { id: '10004' }, // Bug
          summary,
          description, // ADF format
          ...fields,
        },
      }),
    });
    return res.json();
  }
}
```

---

### Figma MCP → Figma REST API

**MCP ทำอะไร:**
```
figma-developer-mcp binary
  → reads env: FIGMA_API_KEY
  → makes HTTP requests to: https://api.figma.com/v1/*
  → returns JSON via stdout
```

**Web backend ทำเหมือนกัน:**
```typescript
// packages/integrations/figma.ts
export class FigmaClient {
  private baseUrl = 'https://api.figma.com/v1';

  constructor(private token: string) {}

  async getFile(fileKey: string) {
    const res = await fetch(`${this.baseUrl}/files/${fileKey}?depth=2`, {
      headers: { 'X-FIGMA-TOKEN': this.token },
    });
    return res.json();
  }

  async getNodeScreenshot(fileKey: string, nodeId: string) {
    const res = await fetch(`${this.baseUrl}/images/${fileKey}?ids=${nodeId}&format=png`, {
      headers: { 'X-FIGMA-TOKEN': this.token },
    });
    return res.json();
  }
}
```

---

### TestRail (ปัจจุบันเป็น REST อยู่แล้ว)

**ปัจจุบัน (Python):**
```python
# จาก import-new-testrail-cases.py
token = base64.b64encode(f"{TR_EMAIL}:{TR_KEY}".encode()).decode()
url = f"{TR_HOST}/index.php?/api/v2/add_case/{sec_id}"
req = urllib.request.Request(url, data=data, headers={
    'Content-Type': 'application/json',
    'Authorization': f'Basic {token}'
})
```

**Web backend (TypeScript port):**
```typescript
// packages/integrations/testrail.ts
export class TestRailClient {
  private baseUrl: string;
  private authHeader: string;

  constructor(host: string, email: string, apiKey: string) {
    this.baseUrl = `${host}/index.php?/api/v2`;
    this.authHeader = 'Basic ' + Buffer.from(`${email}:${apiKey}`).toString('base64');
  }

  async getCases(projectId: number, suiteId: number) {
    const allCases = [];
    let offset = 0;
    while (true) {
      const res = await this.get(`get_cases/${projectId}&suite_id=${suiteId}&limit=250&offset=${offset}`);
      allCases.push(...(res.cases || []));
      if ((res.cases || []).length < 250) break;
      offset += 250;
    }
    return allCases;
  }

  async addCase(sectionId: number, data: any) {
    return this.post(`add_case/${sectionId}`, data);
  }

  async addRun(projectId: number, data: any) {
    return this.post(`add_run/${projectId}`, data);
  }

  async pushResults(runId: number, results: any[]) {
    return this.post(`add_results_for_cases/${runId}`, { results });
  }

  private async get(endpoint: string) {
    const res = await fetch(`${this.baseUrl}/${endpoint}`, {
      headers: { 'Authorization': this.authHeader, 'Content-Type': 'application/json' },
    });
    return res.json();
  }

  private async post(endpoint: string, data: any) {
    const res = await fetch(`${this.baseUrl}/${endpoint}`, {
      method: 'POST',
      headers: { 'Authorization': this.authHeader, 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return res.json();
  }
}
```

---

## Migration Matrix

| Service | ปัจจุบัน (CLI) | Web Platform | Port Effort | Notes |
|---|---|---|---|---|
| **Jira** | MCP stdio (`mcp-atlassian`) | `JiraClient.ts` (REST) | **ต่ำ** | Copy endpoints จาก `daily-ac-agent.py` |
| **Confluence** | MCP stdio (same binary) | `ConfluenceClient.ts` (REST) | **ต่ำ** | Same Atlassian token |
| **TestRail** | Python REST (`push_testrail.py`) | `TestRailClient.ts` (REST) | **ต่ำ** | Direct port, same endpoints |
| **Figma** | MCP stdio (`figma-developer-mcp`) | `FigmaClient.ts` (REST) | **ต่ำ** | Simple REST API |
| **EkoAI API** | Playwright HTTP (Bearer JWT) | Same — keep Playwright | **ไม่ต้อง port** | Playwright handles auth |
| **Claude AI** | Claude Code (CLI LLM) | `ClaudeClient.ts` (Anthropic API) | **ปานกลาง** | Port SKILL.md prompts to API calls |

---

## API Endpoints ที่ต้อง Implement (Complete List)

### Jira (8 endpoints)

```
GET  /rest/agile/1.0/board/{boardId}/sprint          # Active sprints
GET  /rest/agile/1.0/sprint/{sprintId}/issue          # Sprint issues (paginated)
GET  /rest/api/3/issue/{issueKey}                      # Issue details
POST /rest/api/3/issue                                 # Create issue (bug)
PUT  /rest/api/3/issue/{issueKey}                      # Update issue
POST /rest/api/3/issue/{issueKey}/comment              # Post comment (AC)
GET  /rest/api/3/issue/{issueKey}/comment              # List comments
DELETE /rest/api/3/issue/{issueKey}/comment/{commentId} # Delete comment
```

### TestRail (8 endpoints)

```
GET  /api/v2/get_sections/{projectId}&suite_id={suiteId}  # Sections
GET  /api/v2/get_cases/{projectId}&suite_id={suiteId}     # Cases (paginated!)
POST /api/v2/add_case/{sectionId}                          # Create case
POST /api/v2/update_case/{caseId}                          # Update case
POST /api/v2/add_milestone/{projectId}                     # Create milestone
POST /api/v2/add_run/{projectId}                           # Create run
POST /api/v2/add_results_for_cases/{runId}                 # Push results
POST /api/v2/close_run/{runId}                             # Close run
```

### Figma (2 endpoints)

```
GET  /v1/files/{fileKey}?depth=2          # File structure
GET  /v1/images/{fileKey}?ids={nodeIds}   # Node screenshots
```

### Confluence (2 endpoints)

```
GET  /wiki/api/v2/pages/{pageId}?body-format=storage  # Read page
GET  /wiki/rest/api/content/search?cql=...             # Search pages
```

---

## Security: Credential Flow

```
User enters tokens in Settings page (browser)
  → HTTPS POST to /api/settings/credentials
  → Backend encrypts with AES-256-GCM (key from CREDENTIALS_KEY env var)
  → Stores encrypted blob in PostgreSQL
  → Returns { success: true }

When making API call (e.g. Jira bug filing):
  → Backend reads encrypted credential from DB
  → Decrypts with CREDENTIALS_KEY
  → Makes REST API call server-side
  → Returns response to frontend
  → Token NEVER leaves the backend
```

---

## Known Pitfalls from Current System

จาก memory ที่สะสมมา ระหว่างทำงาน มีหลาย gotcha ที่ต้องระวัง:

### TestRail API
- **Pagination:** `get_cases` returns max 250 per page — ต้อง loop with offset
- **Array fields:** `custom_qa_responsibility` ต้องเป็น `[26]` ไม่ใช่ `26`
- **Section filter:** ต้อง filter by section_id ไม่งั้นจะได้ cases จากทุก release

### Jira API
- **EKO Squad required:** `customfield_11536` ต้องใส่ทุกครั้ง (metadata บอก optional แต่ workflow บังคับ)
- **Fix Version = Board Lane:** ถ้าไม่ใส่ `fixVersions` issue จะไปอยู่ "Everything Else"
- **Sprint field:** `customfield_10006` ต้องเป็น number ไม่ใช่ object
- **ADF format:** Comments ต้องเป็น Atlassian Document Format (JSON) ไม่ใช่ markdown

### Ant Design (for future reference if building similar UI)
- Select dropdown ใช้ React fiber `onChange()` ไม่ใช่ native click
- Day button selection ใช้ CSS class `bg-primary` ไม่ใช่ `aria-pressed`
- Modal buttons อยู่ใน `.ant-modal-content` ไม่ใช่ `.ant-modal-footer`
