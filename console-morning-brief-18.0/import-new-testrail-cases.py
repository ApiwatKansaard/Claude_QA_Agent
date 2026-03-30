#!/usr/bin/env python3
"""
Import NEW test cases (empty TestRailID) from CSV to TestRail.
Reads creds from .env file. Updates CSV with returned IDs.
Suite: S3865, Project: 1
"""
import csv, os, re, json, base64, urllib.request, urllib.error

# ── Load .env ─────────────────────────────────────────────────────────────
ENV_PATH = os.path.join(os.path.dirname(__file__), '..', '.env')
creds = {}
with open(ENV_PATH) as f:
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            creds[k.strip()] = v.strip()

TR_EMAIL   = creds['TESTRAIL_EMAIL']
TR_KEY     = creds['TESTRAIL_API_KEY']
TR_HOST    = 'https://ekoapp20.testrail.io'
PROJECT_ID = 1
SUITE_ID   = 3865

CSV_PATH = os.path.join(os.path.dirname(__file__), 'console-morning-brief-testcases.csv')

# ── Auth helper ───────────────────────────────────────────────────────────
def tr_post(endpoint, payload):
    url = f"{TR_HOST}/index.php?/api/v2/{endpoint}"
    token = base64.b64encode(f"{TR_EMAIL}:{TR_KEY}".encode()).decode()
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={
        'Content-Type': 'application/json',
        'Authorization': f'Basic {token}'
    })
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  HTTP {e.code}: {body[:200]}")
        return None

def tr_get(endpoint):
    url = f"{TR_HOST}/index.php?/api/v2/{endpoint}"
    token = base64.b64encode(f"{TR_EMAIL}:{TR_KEY}".encode()).decode()
    req = urllib.request.Request(url, headers={
        'Authorization': f'Basic {token}',
        'Content-Type': 'application/json'
    })
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

# ── Get sections ──────────────────────────────────────────────────────────
print("Fetching TestRail sections...")
secs_data = tr_get(f"get_sections/{PROJECT_ID}&suite_id={SUITE_ID}")
sections = secs_data.get('sections', secs_data) if isinstance(secs_data, dict) else secs_data

sec_map = {}  # name → id
for s in (sections if isinstance(sections, list) else []):
    sec_map[s.get('name', '')] = s.get('id')
    # Also store by partial match
    depth_name = s.get('name', '')
    sec_map[depth_name] = s.get('id')

print(f"  Found {len(sec_map)} sections")

# Known section name → ID mapping from previous imports
KNOWN_SECTIONS = {
    'Create Scheduled Job (UI)': None,
    'Job Configuration (UI)': None,
    'Audience (UI)': None,
    'Dashboard (UI)': None,
    'Recipients (UI)': None,
    'History Log (UI)': None,
}
for s in (sections if isinstance(sections, list) else []):
    n = s.get('name', '')
    sid = s.get('id')
    for k in KNOWN_SECTIONS:
        if k in n or n in k:
            KNOWN_SECTIONS[k] = sid
            break

print("Section IDs found:", KNOWN_SECTIONS)

# ── Type map ──────────────────────────────────────────────────────────────
TYPE_MAP = {
    'Smoke Test': 19,
    'Sanity Test': 11,
    'Regression Test': 9,
    'Manual': 11,  # fallback
}

PRIORITY_MAP = {
    'P1': 2,
    'P2': 3,
    'P3': 4,
}

# ── Read CSV ──────────────────────────────────────────────────────────────
with open(CSV_PATH, 'r', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)

new_rows_idx = [i for i, r in enumerate(rows) if not r.get('TestRailID', '').strip()]
print(f"\nFound {len(new_rows_idx)} rows without TestRail ID")

# ── Import each new row ───────────────────────────────────────────────────
for idx in new_rows_idx:
    row = rows[idx]
    title = row.get('Title', '').strip()
    section_csv = row.get('Section', '')

    # Find section ID
    sec_id = None
    for k, v in KNOWN_SECTIONS.items():
        if k in section_csv:
            sec_id = v
            break

    if not sec_id:
        # Try direct match
        for s in (sections if isinstance(sections, list) else []):
            if s.get('name', '') in section_csv or section_csv in s.get('name', ''):
                sec_id = s.get('id')
                break

    if not sec_id:
        print(f"  SKIP (no section): {title[:50]}")
        continue

    type_id = TYPE_MAP.get(row.get('Type', ''), 11)
    priority_id = PRIORITY_MAP.get(row.get('P', 'P2'), 3)

    # Build steps string
    steps_raw = row.get('Steps', '')
    expected_raw = row.get('Expected Result', '')

    payload = {
        'title': title,
        'type_id': type_id,
        'priority_id': priority_id,
        'refs': row.get('References', ''),
        'custom_steps': steps_raw,
        'custom_expected': expected_raw,
        'custom_preconds': row.get('Preconditions', ''),
        'custom_qa_responsibility': [26],
    }

    print(f"  Importing: {title[:60]}...")
    result = tr_post(f"add_case/{sec_id}", payload)

    if result and result.get('id'):
        case_id = f"C{result['id']}"
        rows[idx]['TestRailID'] = case_id
        print(f"    → Created {case_id}")
    else:
        print(f"    → FAILED: {result}")

# ── Write updated CSV ─────────────────────────────────────────────────────
with open(CSV_PATH, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"\nDone. CSV updated at {CSV_PATH}")
