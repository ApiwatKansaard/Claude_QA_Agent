#!/usr/bin/env python3
"""
Delete old AC comments from Jira tickets via REST API.
Requires: JIRA_EMAIL and JIRA_TOKEN environment variables.

Usage:
  export JIRA_EMAIL="apiwat@amitysolutions.com"
  export JIRA_TOKEN="your-api-token"
  python3 scripts/delete-old-ac-comments.py
"""
import json
import os
import sys
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

# Signatures to identify QA-generated AC comments
AC_SIGNATURES = [
    "Acceptance Criteria",
    "QA Generated",
    "Bug Fix",
    "Icon Legend",
    "by QA Agent from test plan",
]


def api_request(method, path, data=None):
    url = f"{BASE_URL}{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status == 204:
                return None
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code}: {e.read().decode()[:200]}")
        return None


def get_comments(issue_key):
    result = api_request("GET", f"/rest/api/3/issue/{issue_key}/comment")
    if not result:
        return []
    return result.get("comments", [])


def extract_text(adf_node):
    """Recursively extract text from ADF node."""
    if isinstance(adf_node, str):
        return adf_node
    if isinstance(adf_node, dict):
        text = adf_node.get("text", "")
        for child in adf_node.get("content", []):
            text += extract_text(child)
        return text
    if isinstance(adf_node, list):
        return "".join(extract_text(item) for item in adf_node)
    return ""


def is_ac_comment(comment):
    body = comment.get("body", {})
    text = extract_text(body).lower()
    return any(sig.lower() in text for sig in AC_SIGNATURES)


def delete_comment(issue_key, comment_id):
    return api_request("DELETE", f"/rest/api/3/issue/{issue_key}/comment/{comment_id}")


def main():
    total_deleted = 0
    for ticket in TICKETS:
        comments = get_comments(ticket)
        ac_comments = [c for c in comments if is_ac_comment(c)]
        if not ac_comments:
            print(f"  {ticket}: no AC comments found")
            continue
        for c in ac_comments:
            cid = c["id"]
            created = c.get("created", "")[:19]
            print(f"  {ticket}: deleting comment #{cid} ({created})")
            delete_comment(ticket, cid)
            total_deleted += 1
    print(f"\nDone: {total_deleted} comments deleted across {len(TICKETS)} tickets")


if __name__ == "__main__":
    main()
