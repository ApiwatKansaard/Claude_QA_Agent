#!/usr/bin/env python3
"""
Repost AC comments as ADF tables on Jira tickets.
1. Fetch existing AC comments from each ticket
2. Parse AC items from Round 2 format (numbered list with emoji)
3. Delete ALL old AC comments
4. Build ADF table JSON
5. Post new ADF table comment

Requires: JIRA_EMAIL and JIRA_TOKEN environment variables.

Usage:
  export JIRA_EMAIL="apiwat@amitysolutions.com"
  export JIRA_TOKEN="your-api-token"
  python3 scripts/repost-ac-tables.py
"""
import json
import os
import re
import sys
import time
import urllib.request
import base64

BASE_URL = "https://ekoapp.atlassian.net"
EMAIL = os.environ.get("JIRA_EMAIL", "")
TOKEN = os.environ.get("JIRA_TOKEN", "")

if not EMAIL or not TOKEN:
    print("ERROR: Set JIRA_EMAIL and JIRA_TOKEN environment variables first")
    print('  export JIRA_EMAIL="apiwat@amitysolutions.com"')
    print('  export JIRA_TOKEN="your-api-token"')
    sys.exit(1)

AUTH = base64.b64encode(f"{EMAIL}:{TOKEN}".encode()).decode()
HEADERS = {
    "Authorization": f"Basic {AUTH}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

TICKETS = [
    "AE-14288", "AE-14290", "AE-14292", "AE-14294", "AE-14296", "AE-14298",
    "AE-14249",
    "AE-14468", "AE-14344", "AE-14346", "AE-14348", "AE-14350",
    "AE-14353", "AE-14355", "AE-14357",
]

AC_SIGNATURES = [
    "acceptance criteria",
    "qa generated",
    "bug fix criteria",
    "icon legend",
    "by qa agent",
]


def api_request(method, path, data=None):
    url = f"{BASE_URL}{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status == 204:
                return {"status": 204}
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        err = e.read().decode()[:300]
        print(f"    HTTP {e.code}: {err}")
        return None


def extract_text(node):
    """Recursively extract plain text from ADF node."""
    if isinstance(node, str):
        return node
    if isinstance(node, dict):
        t = node.get("text", "")
        for child in node.get("content", []):
            t += extract_text(child)
        return t
    if isinstance(node, list):
        return "".join(extract_text(i) for i in node)
    return ""


def is_ac_comment(comment):
    body = comment.get("body", {})
    text = extract_text(body).lower()
    return any(sig in text for sig in AC_SIGNATURES)


def get_comments(issue_key):
    result = api_request("GET", f"/rest/api/3/issue/{issue_key}/comment")
    if not result:
        return []
    return result.get("comments", [])


def parse_ac_items(text):
    """Parse numbered AC items from Round 2 format.
    Format: N. EMOJI Type — Description (TC-XXX)
    Returns list of dicts: {num, emoji, type, criteria, tc_ref}
    """
    items = []
    # Match patterns like: 1. ✅ Positive — Some criteria text (TC-066)
    # or: 1. ✅ Positive — Some criteria text TC-066
    pattern = re.compile(
        r'(\d+)\.\s*([✅❌⚠️]+)\s*(Positive|Negative|Edge case|Edge Case)\s*[—–-]\s*(.+?)(?:\s*\(?(TC-\d+(?:\s*,\s*TC-\d+)*)\)?)?$',
        re.MULTILINE
    )
    for m in pattern.finditer(text):
        items.append({
            "num": m.group(1),
            "emoji": m.group(2).strip(),
            "type": m.group(3),
            "criteria": m.group(4).strip().rstrip(')').rstrip(),
            "tc_ref": m.group(5) if m.group(5) else "",
        })
    return items


def parse_ref_line(text):
    """Extract the Ref: line content."""
    m = re.search(r'Ref:\s*(.+?)(?:\n|$)', text)
    if m:
        return m.group(1).strip()
    return ""


def parse_tc_range(text):
    """Extract test case range from Ref line."""
    m = re.search(r'Test Cases?:\s*(TC-[\d\s,to–-]+)', text)
    if m:
        return m.group(1).strip()
    return ""


def build_adf_table(items, ref_line, tc_range, title="Acceptance Criteria — QA Generated"):
    """Build ADF JSON document with heading + table + legend."""

    # Table header row
    header_row = {
        "type": "tableRow",
        "content": [
            {"type": "tableHeader", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "#", "marks": [{"type": "strong"}]}]}]},
            {"type": "tableHeader", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Type", "marks": [{"type": "strong"}]}]}]},
            {"type": "tableHeader", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Criteria", "marks": [{"type": "strong"}]}]}]},
            {"type": "tableHeader", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "TC Ref", "marks": [{"type": "strong"}]}]}]},
        ]
    }

    # Data rows
    data_rows = []
    for item in items:
        type_text = f'{item["emoji"]} {item["type"]}'
        data_rows.append({
            "type": "tableRow",
            "content": [
                {"type": "tableCell", "content": [{"type": "paragraph", "content": [{"type": "text", "text": item["num"]}]}]},
                {"type": "tableCell", "content": [{"type": "paragraph", "content": [{"type": "text", "text": type_text}]}]},
                {"type": "tableCell", "content": [{"type": "paragraph", "content": [{"type": "text", "text": item["criteria"]}]}]},
                {"type": "tableCell", "content": [{"type": "paragraph", "content": [{"type": "text", "text": item["tc_ref"]}]}]},
            ]
        })

    # Build ref text
    ref_display = ref_line
    if tc_range and tc_range not in ref_line:
        ref_display = f"{ref_line} · Test Cases: {tc_range}" if ref_line else f"Test Cases: {tc_range}"

    doc = {
        "version": 1,
        "type": "doc",
        "content": [
            # Heading
            {"type": "heading", "attrs": {"level": 3}, "content": [{"type": "text", "text": title}]},
            # Table
            {
                "type": "table",
                "attrs": {"isNumberColumnEnabled": False, "layout": "default"},
                "content": [header_row] + data_rows
            },
            # Horizontal rule
            {"type": "rule"},
            # Icon Legend
            {"type": "paragraph", "content": [
                {"type": "text", "text": "Icon Legend: ", "marks": [{"type": "strong"}]},
                {"type": "text", "text": "✅ Positive (expected behavior) · ❌ Negative (error/rejection) · ⚠️ Edge case (boundary/race condition)"},
            ]},
            # Ref line
            {"type": "paragraph", "content": [
                {"type": "text", "text": "Ref: ", "marks": [{"type": "strong"}]},
                {"type": "text", "text": ref_display},
            ]},
            # Generated
            {"type": "paragraph", "content": [
                {"type": "text", "text": "Generated: ", "marks": [{"type": "strong"}]},
                {"type": "text", "text": "2026-03-24 by QA Agent from test plan"},
            ]},
        ]
    }
    return doc


def delete_comment(issue_key, comment_id):
    return api_request("DELETE", f"/rest/api/3/issue/{issue_key}/comment/{comment_id}")


def post_comment(issue_key, adf_doc):
    return api_request("POST", f"/rest/api/3/issue/{issue_key}/comment", {"body": adf_doc})


def main():
    print("=" * 60)
    print("AC Table Repost Script")
    print("=" * 60)

    stats = {"deleted": 0, "posted": 0, "failed": 0}

    for ticket in TICKETS:
        print(f"\n--- {ticket} ---")

        # 1. Fetch comments
        comments = get_comments(ticket)
        ac_comments = [c for c in comments if is_ac_comment(c)]

        if not ac_comments:
            print(f"  No AC comments found — skipping")
            stats["failed"] += 1
            continue

        # 2. Get the LATEST AC comment to extract content
        latest_ac = ac_comments[-1]
        body_text = extract_text(latest_ac.get("body", {}))

        # 3. Parse AC items
        items = parse_ac_items(body_text)
        if not items:
            print(f"  WARNING: Could not parse AC items from comment #{latest_ac['id']}")
            print(f"  Body preview: {body_text[:200]}")
            stats["failed"] += 1
            continue

        ref_line = parse_ref_line(body_text)
        tc_range = parse_tc_range(body_text)

        # Determine title
        title = "Acceptance Criteria — QA Generated"
        if "bug fix" in body_text.lower():
            title = "Bug Fix Criteria — QA Generated"

        print(f"  Found {len(items)} AC items from comment #{latest_ac['id']}")
        for item in items:
            print(f"    {item['num']}. {item['emoji']} {item['type']} — {item['criteria'][:50]}...")

        # 4. Delete ALL old AC comments
        for c in ac_comments:
            cid = c["id"]
            print(f"  Deleting comment #{cid}")
            delete_comment(ticket, cid)
            stats["deleted"] += 1
            time.sleep(0.2)  # Rate limit

        # 5. Build ADF table
        adf_doc = build_adf_table(items, ref_line, tc_range, title)

        # 6. Post new comment
        result = post_comment(ticket, adf_doc)
        if result and result.get("id"):
            print(f"  ✅ Posted new table comment #{result['id']}")
            stats["posted"] += 1
        else:
            print(f"  ❌ Failed to post new comment")
            stats["failed"] += 1

        time.sleep(0.3)  # Rate limit

    print(f"\n{'=' * 60}")
    print(f"DONE: {stats['deleted']} deleted, {stats['posted']} posted, {stats['failed']} failed")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
