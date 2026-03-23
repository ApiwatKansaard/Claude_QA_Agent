# /qa:fetch-testrail [suite link or suite_id] [section_filter]

**Triggers:** testrail-manager agent
**References:** [testrail-api.md](../references/testrail-api.md), [testrail-csv.md](../references/testrail-csv.md)

## What This Command Does

Fetch all test cases from a TestRail suite via the REST API. Creates a local cache
for future use by `/qa:import-testrail` and other commands. Returns a structured summary:
total count by section, full case list, and optional gap analysis.

## Parameters

| Parameter | Required | Notes |
|---|---|---|
| `[suite link or suite_id]` | No | TestRail suite URL or ID — defaults to `3924` ([Main] Agentic suite) |
| `[section_filter]` | No | Section name substring to narrow results (e.g., "AI Scheduled Job") |

**URL parsing:** Same as `/qa:import-testrail` — extract suite_id from URL or use number directly.

**Team defaults:**
- Host: `ekoapp20.testrail.io`
- Projects: `1` (Eko/EGT — Suite 3924), `6` (Amity Solutions — Suite 3923)

## Credentials

This command requires a TestRail API key. Do **not** use your login password.

**To get your API key:**
1. Go to `https://ekoapp20.testrail.io`
2. Click your username → **My Settings** → **API Keys** tab
3. Click **Add Key** → **Generate Key** → copy it

At runtime, ask the user:
> "Please provide your TestRail email and API key to proceed.
> (Your API key is in TestRail → My Settings → API Keys. It's different from your login password.)"

## Execution Steps

1. **Check cache** — look for `testrail-cache/S{suite_id}/`:
   - If cache exists AND user hasn't asked for re-fetch: report cached data and ask if refresh is needed.
   - If no cache OR user wants fresh data: proceed to step 2.

2. **Collect credentials** — ask user for email and API key if not already provided in this session.

2. **Fetch suite info** — verify the suite exists:
   ```
   GET /get_suites/1
   ```
   Confirm the target suite name and ID.

3. **Fetch sections** — get the section hierarchy:
   ```
   GET /get_sections/1?suite_id={suite_id}
   ```
   Build a section ID → name map for use in the output.

4. **Fetch all cases** — paginate through all results:
   ```
   GET /get_cases/1?suite_id={suite_id}&limit=250&offset=0
   GET /get_cases/1?suite_id={suite_id}&limit=250&offset=250
   ... (continue until page returns < 250 cases)
   ```

5. **Apply section filter** (if provided) — filter cases whose section name contains `[section_filter]`.

6. **Save to cache** — create or update `testrail-cache/S{suite_id}/`:
   - `summary.md` — Suite overview with section tree, case counts, priority/type stats
   - `cases.csv` — Full case dump in 15-column CSV format (same schema as sprint testcases)
   See [import-testrail.md](import-testrail.md) for the cache format specification.

7. **Produce output** — format as the output spec below.

## Implementation via Bash

Execute using Python (available on the VM):

```python
import requests, sys, json
from requests.auth import HTTPBasicAuth

BASE = "https://ekoapp20.testrail.io/index.php?/api/v2"
PROJECT_ID = 1
EMAIL = sys.argv[1]
API_KEY = sys.argv[2]
SUITE_ID = int(sys.argv[3]) if len(sys.argv) > 3 else 3924
SECTION_FILTER = sys.argv[4].lower() if len(sys.argv) > 4 else ""

auth = HTTPBasicAuth(EMAIL, API_KEY)
headers = {"Content-Type": "application/json"}

# Fetch sections
r = requests.get(f"{BASE}/get_sections/{PROJECT_ID}?suite_id={SUITE_ID}", auth=auth, headers=headers)
r.raise_for_status()
sections_data = r.json()
sections = sections_data.get("sections", sections_data if isinstance(sections_data, list) else [])
section_map = {s["id"]: s["name"] for s in sections}

# Fetch all cases (paginated)
all_cases = []
offset = 0
while True:
    r = requests.get(f"{BASE}/get_cases/{PROJECT_ID}?suite_id={SUITE_ID}&limit=250&offset={offset}",
                     auth=auth, headers=headers)
    r.raise_for_status()
    data = r.json()
    cases = data.get("cases", data if isinstance(data, list) else [])
    all_cases.extend(cases)
    if len(cases) < 250:
        break
    offset += 250

# Apply section filter
if SECTION_FILTER:
    all_cases = [c for c in all_cases if SECTION_FILTER in section_map.get(c.get("section_id",""), "").lower()]

# Group by section
from collections import defaultdict
by_section = defaultdict(list)
for c in all_cases:
    sec = section_map.get(c.get("section_id"), "Uncategorized")
    by_section[sec].append(c)

print(json.dumps({"total": len(all_cases), "by_section": {k: [{"id": c["id"], "title": c["title"]} for c in v] for k, v in by_section.items()}}))
```

Save as `/tmp/fetch_testrail.py` and run:
```bash
pip install requests --break-system-packages -q
python3 /tmp/fetch_testrail.py "email" "api_key" 3924 "section_filter"
```

Parse the JSON output and format into the output structure below.

## Output Format

```markdown
# TestRail Fetch — [Suite Name] (Suite ID: XXXX)
**Project:** Amity solutions (ID: 6)
**Total cases fetched:** N
**Filter applied:** [section_filter or "none"]

---

## Summary by Section

| Section | Case Count |
|---|---|
| [Section Name] | N |
| [Section Name] | N |

---

## Full Case List

### [Section Name] (N cases)

| ID | Title |
|---|---|
| C10001 | [case title] |
| C10002 | [case title] |

### [Section Name] (N cases)
...

---

## Gap Analysis (if spec or test plan was provided)

| Expected Coverage Area | Cases Found | Status |
|---|---|---|
| [area] | N | ✅ Covered |
| [area] | 0 | ❌ Missing |
```

**If the suite is empty (0 cases):**
State clearly: "Suite [name] (ID: XXXX) has 0 test cases. It is ready for first import."
Offer to run `/qa:import-testrail` with the suite link to import sprint cases directly.

## Error Handling

| Error | Response |
|---|---|
| 401 Unauthorized | "API key is invalid or email is incorrect. Please check My Settings → API Keys in TestRail." |
| 403 Forbidden | "Your account doesn't have API access. Ask your TestRail admin to enable API access." |
| 404 Not Found | "Suite ID XXXX not found in project 6. Run `/qa:fetch-testrail` without a suite_id to list available suites." |
| Connection error | "Cannot reach ekoapp20.testrail.io. Check your network connection." |
