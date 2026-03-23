# TestRail REST API Reference

## Overview

TestRail exposes a REST API at:
```
https://ekoapp20.testrail.io/index.php?/api/v2/{endpoint}
```

**Team defaults:**
- Host: `ekoapp20.testrail.io`
- Project ID: `1` (Main Eko project — Suite 3924=[Main] Agentic)
- Project ID: `6` (Amity solutions — Suite 3923=Agentic)
- Auth: `apiwat@amitysolutions.com` + API key stored in repo memory

---

## Authentication

TestRail API uses HTTP Basic Auth:
- **Username:** your TestRail email (e.g., `apiwat@amitysolutions.com`)
- **Password:** your API key (NOT your login password)

### Getting Your API Key

1. Log in to TestRail at `https://ekoapp20.testrail.io`
2. Click your username (top right) → **My Settings**
3. Go to the **API Keys** tab
4. Click **Add Key** → give it a name → **Generate Key**
5. Copy the key — it's shown once

### Using the Key

**curl:**
```bash
curl -u "your@email.com:YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  "https://ekoapp20.testrail.io/index.php?/api/v2/get_suites/6"
```

**Python (requests):**
```python
import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "https://ekoapp20.testrail.io/index.php?/api/v2"
AUTH = HTTPBasicAuth("your@email.com", "YOUR_API_KEY")
headers = {"Content-Type": "application/json"}

resp = requests.get(f"{BASE_URL}/get_suites/6", auth=AUTH, headers=headers)
data = resp.json()
```

---

## Key Endpoints

### List Suites
```
GET /get_suites/{project_id}
```
Returns all suites in the project. Use to discover `suite_id` values.

**Response:**
```json
[
  {"id": 3923, "name": "Agentic", "description": "...", "is_master": false},
  {"id": 1234, "name": "Core", "description": "..."}
]
```

---

### List Sections
```
GET /get_sections/{project_id}?suite_id={suite_id}
```
Returns all sections (folders) within a suite.

**Response:**
```json
{
  "sections": [
    {"id": 101, "name": "AI Scheduled Job", "parent_id": null, "depth": 0},
    {"id": 102, "name": "Empty State", "parent_id": 101, "depth": 1}
  ]
}
```

---

### Get Test Cases (Paginated)
```
GET /get_cases/{project_id}?suite_id={suite_id}&limit={limit}&offset={offset}
```

**Key parameters:**

| Param | Type | Notes |
|---|---|---|
| `suite_id` | int | Required — which suite to fetch from |
| `section_id` | int | Optional — narrow to a specific section |
| `limit` | int | Max 250 per page |
| `offset` | int | For pagination (0, 250, 500, …) |
| `type_id` | int | Filter by case type |
| `priority_id` | int | Filter by priority |
| `refs_filter` | string | Filter by reference tag |
| `updated_after` | unix timestamp | Cases updated since this time |

**Response format (v2 API):**
```json
{
  "offset": 0,
  "limit": 250,
  "size": 87,
  "cases": [
    {
      "id": 10001,
      "title": "Verify user can enable internal library mode",
      "section_id": 102,
      "type_id": 1,
      "priority_id": 2,
      "refs": "Library Mode UI",
      "custom_preconds": "User logged in and has permission to use internal library",
      "custom_steps_separated": [
        {"content": "Login to the system", "expected": ""},
        {"content": "Open Agentic chat", "expected": ""},
        {"content": "Turn on 'Use internal library' option", "expected": "Internal library mode is activated and shown as enabled"}
      ],
      "created_on": 1710000000,
      "updated_on": 1710100000,
      "created_by": 3,
      "updated_by": 3
    }
  ]
}
```

---

### Get a Single Case
```
GET /get_case/{case_id}
```

---

### Add Test Cases (POST)
```
POST /add_case/{section_id}
Content-Type: application/json

{
  "title": "Verify user can enable internal library mode",
  "type_id": 9,
  "priority_id": 2,
  "refs": "Library Mode UI",
  "custom_preconds": "User logged in",
  "custom_steps": "1. Login\n2. Open chat\n3. Enable library",
  "custom_expected": "Library mode is activated",
  "custom_supportversion": [156],
  "custom_qa_responsibility": [2]
}
```

> **CRITICAL:** `custom_supportversion` (array of int) and `custom_qa_responsibility` (array of int) are **required**.
> Omitting them causes a 400 error. Call `GET /get_case_fields` to verify required fields on your instance.

---

## Pagination Pattern

TestRail API returns max 250 cases per page. To fetch all cases:

```python
import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "https://ekoapp20.testrail.io/index.php?/api/v2"
AUTH = HTTPBasicAuth("your@email.com", "YOUR_API_KEY")

def fetch_all_cases(project_id, suite_id):
    all_cases = []
    offset = 0
    limit = 250
    while True:
        url = f"{BASE_URL}/get_cases/{project_id}?suite_id={suite_id}&limit={limit}&offset={offset}"
        resp = requests.get(url, auth=AUTH, headers={"Content-Type": "application/json"})
        data = resp.json()
        cases = data.get("cases", data if isinstance(data, list) else [])
        all_cases.extend(cases)
        if len(cases) < limit:
            break
        offset += limit
    return all_cases
```

> **Note:** Older TestRail versions return a plain array instead of `{"cases": [...]}`. The code above handles both.

---

## Priority ID Mapping

| Priority ID | Label | CSV Value |
|---|---|---|
| 1 | Low | — |
| 2 | Medium | — |
| 3 | High | P2 |
| 4 | Critical | P1 |

> **Team convention:** P1 = Critical (4), P2 = High (3).
> This is confirmed by the TestRail import config mapping: `p1→4, p2→3`.

---

## Type ID Mapping (Actual — from ekoapp20.testrail.io)

| Type ID | Label | CSV "Type" column |
|---|---|---|
| 9 | Regression | `Regression Test` |
| 11 | Sanity case | `Sanity Test` |
| 19 | Smoke case | `Smoke Test` |
| 17 | Acceptance | `Acceptance` |
| 20 | Exploratory | `Exploratory` |
| 7 | Other | `Other` |
| 4 | Compatibility | — |
| 18 | Google analytics | — |

> **Important:** Type IDs 1–3, 5–6, 8, 10, 12 do NOT exist on this instance. Always use the IDs above.

---

## Required Custom Fields (add_case WILL FAIL without these)

| Field | API key | Type | Values | Notes |
|---|---|---|---|---|
| Support Version | `custom_supportversion` | multi-select (array of int) | e.g. `[156]`=Eko 17.27, `[160]`=Eko 18.0 — get values via `get_case_fields` **must be an array** | Mapped from CSV "Release version" column |
| QA Responsibility | `custom_qa_responsibility` | multi-select (array of int) | e.g. `[2]`=Beer, `[26]`=Sharp — **must be an array** even for single value | Mapped from CSV "QA Responsibility" column |
| Fix version | `custom_fix_version` | dropdown (int) | e.g. `33`=Soul, `32`=Rome, `31`=Queens | Internal release codename — verify if required via `get_case_fields` |

> **Note:** `custom_supportversion` (product version) and `custom_fix_version` (release codename) are
> TWO DIFFERENT fields. The CSV import config maps "Release version" → `custom_supportversion`.
> Call `GET /get_case_fields` to verify which fields are actually required on your instance.

Example `add_case` payload with required fields:
```json
{
  "title": "Verify user can enable library mode",
  "type_id": 9,
  "priority_id": 4,
  "custom_preconds": "User logged in",
  "custom_steps": "1. Open chat\n2. Enable library",
  "custom_expected": "Library mode activated",
  "custom_supportversion": [156],
  "custom_qa_responsibility": [2]
}
```

### QA Responsibility ID Mapping

| ID | Name | ID | Name | ID | Name |
|---|---|---|---|---|---|
| 1 | Fon | 10 | Boss | 19 | Lin Lin |
| 2 | Beer | 11 | Kim | 20 | Thu |
| 3 | Pang | 12 | Madhuri | 21 | Deli |
| 4 | Fifa | 13 | Red | 22 | Winne |
| 5 | Maroof | 14 | Gate | 23 | Fah |
| 6 | Mick | 15 | Andrew | 24 | Nav |
| 7 | Heart | 16 | Belle | 25 | Jash |
| 8 | Noor | 17 | Yeen | 26 | Sharp |
| 9 | Can | 18 | Tif | 27 | Kong |
| | | | | 28 | May |

---

## Write Endpoints

All write operations use `POST` with `Content-Type: application/json`.

### Add Section
```
POST /add_section/{project_id}
Body: {"name": "AI Scheduled Job", "suite_id": 3924, "parent_id": 265253}
```
- `parent_id` is optional — omit for root-level section
- Returns: `{"id": 265300, "name": "AI Scheduled Job", ...}`

### Add Test Case
```
POST /add_case/{section_id}
Body:
{
  "title": "Verify user can create a new scheduler",
  "type_id": 9,
  "priority_id": 2,
  "refs": "AI Scheduled Job",
  "custom_preconds": "User is logged in and has admin role",
  "custom_steps": "1. Navigate to Scheduled Jobs\n2. Click Add Scheduler\n3. Fill in required fields\n4. Click Save",
  "custom_expected": "Scheduler is created and appears in the list",
  "custom_supportversion": [156],
  "custom_qa_responsibility": [2]
}
```
Returns: full case object with assigned `id`

### Update Test Case
```
POST /update_case/{case_id}
Body: (only include fields you want to change)
{
  "title": "Updated title",
  "custom_steps": "1. New step 1\n2. New step 2",
  "custom_expected": "Updated expected result"
}
```
Returns: updated case object

### Add Milestone
```
POST /add_milestone/{project_id}
Body:
{
  "name": "EGT 18.0 — AI Scheduled Jobs Release",
  "description": "Regression coverage for AI Scheduled Jobs feature",
  "due_on": 1748736000
}
```
- `due_on` is a Unix timestamp
- Returns: `{"id": 123, "name": "...", "url": "https://ekoapp20.testrail.io/..."}`

### Add Test Run
```
POST /add_run/{project_id}
Body:
{
  "suite_id": 3924,
  "name": "Sprint Broccoli-F Regression — AI Scheduled Jobs",
  "description": "Regression run for EGT 18.0 release",
  "milestone_id": 123,
  "case_ids": [10001, 10002, 10003],
  "assignedto_id": null
}
```
- `case_ids`: array of case IDs to include (omit to include all cases in suite)
- Returns: `{"id": 456, "name": "...", "url": "https://ekoapp20.testrail.io/..."}`

### Update Test Run (add/remove cases)
```
POST /update_run/{run_id}
Body: {"case_ids": [10001, 10002, 10005]}
```

---

## Section Resolution Pattern

When creating cases from a Section path like `Agentic > AI Scheduled Job > Create Scheduler`:

```python
def resolve_or_create_section(project_id, suite_id, path, auth):
    """Walk the path, creating missing sections as needed. Returns leaf section_id."""
    parts = [p.strip() for p in path.split(">")]

    # Fetch existing sections
    # Note: BASE already contains '?' so we use '&' for query params
    url = f"{BASE}/get_sections/{project_id}&suite_id={suite_id}&limit=250"
    sections = requests.get(url, auth=auth, headers=HEADERS).json().get("sections", [])
    name_map = {}  # (name, parent_id) -> section_id
    for s in sections:
        name_map[(s["name"], s.get("parent_id"))] = s["id"]

    parent_id = None
    for part in parts:
        key = (part, parent_id)
        if key in name_map:
            parent_id = name_map[key]
        else:
            # Create new section
            body = {"name": part, "suite_id": suite_id}
            if parent_id:
                body["parent_id"] = parent_id
            r = requests.post(f"{BASE}/add_section/{project_id}",
                              auth=auth, headers=HEADERS, json=body)
            parent_id = r.json()["id"]
            name_map[key] = parent_id
    return parent_id
```

---

## Import Cases Pattern

```python
def import_cases(project_id, suite_id, cases_data, auth):
    """
    cases_data: list of dicts with keys matching the 15-column CSV schema
    Returns: list of (case_id, title) for created cases
    """
    created = []
    for row in cases_data:
        section_id = resolve_or_create_section(project_id, suite_id, row["Section"], auth)
        body = {
            "title": row["Title"],
            "type_id": 9,  # Regression (valid: 9=Regression, 11=Sanity, 19=Smoke, 17=Acceptance, 20=Exploratory)
            "priority_id": {"P1": 4, "P2": 3}.get(row.get("P", "P2"), 3),
            "refs": row.get("References", ""),
            "custom_preconds": row.get("Preconditions", ""),
            "custom_steps": row.get("Steps", ""),
            "custom_expected": row.get("Expected Result", ""),
            "custom_supportversion": [156],
            "custom_qa_responsibility": [2],
        }
        r = requests.post(f"{BASE}/add_case/{section_id}", auth=auth,
                          headers=HEADERS, json=body)
        c = r.json()
        created.append((c["id"], c["title"]))
    return created
```

---

## Error Handling

| HTTP Status | Meaning |
|---|---|
| 200 | Success |
| 400 | Bad request — invalid parameters |
| 401 | Unauthorized — wrong email or API key |
| 403 | Forbidden — insufficient permissions |
| 404 | Resource not found — invalid ID |
| 429 | Rate limited — wait and retry |

Always check `resp.status_code` before parsing the response body.

**Rate limiting:** TestRail may throttle rapid sequential writes. Add a small delay (0.15–0.2s) between `add_case` calls for large imports (>50 cases).

---

## Known Pitfalls & Lessons Learned

These are real issues encountered during production imports. Follow these rules strictly.

### 1. Multi-select fields MUST be arrays

Both `custom_supportversion` and `custom_qa_responsibility` are **multi-select** dropdown fields.
The API requires **array format** even for single values:

```python
# ✅ CORRECT — array format
"custom_supportversion": [160],
"custom_qa_responsibility": [26],

# ❌ WRONG — bare int causes 400 error
"custom_supportversion": 160,    # → "Field :custom_supportversion is not a valid array."
"custom_qa_responsibility": 26,  # → "Field :custom_qa_responsibility is not a valid array."
```

**Rule:** Any field returned as `type: 12` (multi-select) in `GET /get_case_fields` MUST use `[id]` array syntax.

### 2. Large imports MUST use background process + progress file

Importing > 30 cases sequentially can take 30–120+ seconds depending on API latency.
Running in a foreground terminal with a timeout causes the script to be killed mid-import:

```python
# ✅ CORRECT — write progress incrementally
with open('/tmp/import_progress.jsonl', 'a') as pf:
    for row in cases_to_import:
        result = api_post(f'add_case/{section_id}', case_data)
        pf.write(json.dumps({'id': result['id'], 'title': row['Title']}) + '\n')
        pf.flush()  # ensure written to disk immediately
        time.sleep(0.15)

# ❌ WRONG — only saves at the end (lost if script crashes)
results = []
for row in cases_to_import:
    result = api_post(...)
    results.append(result)
# If script crashes here, all progress is lost
with open('/tmp/results.json', 'w') as f:
    json.dump(results, f)
```

**Execution pattern:**
```bash
# Run as background process, capture output to file
python3 /tmp/import_script.py > /tmp/import_log.txt 2>&1
# Poll for completion
cat /tmp/import_results.json  # written at script end
wc -l /tmp/import_progress.jsonl  # check incremental progress
```

### 3. Resume pattern for crashed imports

If an import crashes mid-way, NEVER re-run the full script. Instead:
1. Fetch actual suite state: `GET /get_cases/{project_id}&suite_id={suite_id}`
2. Compare imported titles against source CSV
3. Generate a resume script importing only missing cases
4. Run resume script using the same background + progress pattern

### 4. Use urllib.request (not requests)

The `requests` module is NOT always installed. All import scripts should use `urllib.request`:
```python
import urllib.request, json, base64, ssl
ctx = ssl.create_default_context()
creds = base64.b64encode(f'{email}:{api_key}'.encode()).decode()
headers = {'Authorization': f'Basic {creds}', 'Content-Type': 'application/json'}

def api_post(endpoint, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(f'{base_url}/{endpoint}', data=body, headers=headers, method='POST')
    return json.loads(urllib.request.urlopen(req, context=ctx).read().decode())
```

### 5. Discover dropdown IDs before importing

Always call `GET /get_case_fields` before the first import to discover:
- `custom_supportversion` dropdown options (e.g., `Eko 18.0` → `160`)
- `custom_qa_responsibility` dropdown options (e.g., `Sharp` → `26`)
- Which fields are required vs optional

Parse the `configs[].options.items` string (newline-separated `"id, label"` pairs).
