#!/usr/bin/env python3
"""
Daily AC Agent — Dynamic Sprint Ticket Discovery & AC Posting.

Fetches ALL tickets from a Jira sprint dynamically (no hardcoded lists),
detects which tickets need AC comments, and posts ADF table comments.

Modes:
  1. Sprint ID mode:  python3 daily-ac-agent.py --sprint-id 4077
  2. Board URL mode:   python3 daily-ac-agent.py --board-url "https://ekoapp.atlassian.net/jira/software/c/projects/AE/boards/257?sprints=4077"
  3. Auto-discover:    python3 daily-ac-agent.py --project AE  (finds active sprints)
  4. Dry-run:          python3 daily-ac-agent.py --sprint-id 4077 --dry-run
  5. Report-only:      python3 daily-ac-agent.py --sprint-id 4077 --report-only

Environment variables:
  JIRA_EMAIL  — Jira user email
  JIRA_TOKEN  — Jira API token
  TEST_PLAN_CSV — (optional) path to test cases CSV, defaults to auto-detect

GitHub Actions sets JIRA_EMAIL and JIRA_TOKEN from repository secrets.
Local dev reads from macOS Keychain if env vars are not set.
"""

import argparse
import base64
import csv
import json
import os
import platform
import re
import subprocess
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

# ── Configuration ──────────────────────────────────────────────────────────

BASE_URL = "https://ekoapp.atlassian.net"
DEFAULT_PROJECT = "AE"
RATE_LIMIT_DELAY = 0.3  # seconds between API calls

# Signatures that identify QA-generated AC comments
AC_SIGNATURES = [
    "acceptance criteria",
    "qa generated",
    "bug fix criteria",
    "icon legend",
    "by qa agent",
]

# Keywords to match ticket summaries → test plan groups
# Each key is a test group name, value is a list of keyword patterns (regex)
GROUP_KEYWORD_MAP = {
    "Dashboard": [
        r"dashboard", r"job\s*list", r"scheduled\s*jobs?\s*(?:list|page|menu)",
        r"statistics", r"home\s*page\s*(?!delivery)",
    ],
    "Create Job": [
        r"create\s*(?:new\s*)?(?:job|scheduler)", r"wizard",
        r"new\s*scheduled?\s*job",
    ],
    "Job Configuration": [
        r"(?:job\s*)?config(?:uration)?", r"edit\s*(?:job|scheduler)",
        r"job\s*(?:details|settings)", r"schedule\s*(?:config|setting)",
    ],
    "Recipients": [
        r"recipient", r"target\s*(?:user|audience|group)",
        r"delivery\s*(?:target|scope)", r"user.*group",
    ],
    "History Logs": [
        r"history", r"(?:execution|run)\s*log", r"failure\s*log",
        r"audit\s*(?:log|trail)",
    ],
    "Trigger Step": [
        r"trigger", r"cron", r"schedule\s*(?:type|trigger)",
        r"time[\s-]*(?:based|triggered)", r"immediate\s*(?:delivery|trigger)",
    ],
    "Process Step": [
        r"process\s*step", r"execution\s*(?:step|flow|pipeline)",
        r"job\s*lifecycle.*process",
    ],
    "Callback": [
        r"callback", r"webhook", r"(?:post|after)[\s-]*execution\s*(?:hook|notify)",
    ],
    "Action Step": [
        r"action\s*(?:step|orchestrat|worker)", r"claim.*dispatch",
        r"commit.*(?:run|status)", r"worker.*(?:claim|commit|dispatch)",
        r"action\s*worker",
    ],
    "Cutoff Timeout": [
        r"cutoff", r"timeout", r"time[\s-]*limit",
        r"cutoff\s*timeout\s*(?:orchestrat|worker)",
    ],
    "Home Page Delivery": [
        r"home\s*page\s*delivery", r"widget\s*delivery",
        r"(?:card|content)\s*delivery",
    ],
    "Widget Rendering": [
        r"widget", r"rendering", r"(?:card|component)\s*render",
    ],
    "Security": [
        r"security", r"permission", r"(?:auth|access)\s*(?:control|check)",
        r"rbac", r"role[\s-]*based",
    ],
    "Status Check": [
        r"status\s*check", r"health\s*check", r"(?:job\s*)?status\s*(?:monitor|endpoint)",
    ],
    "Database and Infra": [
        r"database", r"infra", r"(?:db|data)\s*(?:model|schema|migration)",
        r"cosmos", r"mongo",
    ],
    "Race Conditions": [
        r"race\s*condition", r"concurren", r"parallel\s*(?:execution|run)",
        r"(?:lock|mutex|latch)",
    ],
    "API Endpoints": [
        r"\bapi\b", r"endpoint", r"rest\s*api", r"(?:crud|http)\s*(?:endpoint|api)",
        r"(?:get|post|put|delete|patch)\s*/",
    ],
}


# ── Authentication ─────────────────────────────────────────────────────────

def get_credentials():
    """Get Jira credentials from env vars or macOS Keychain."""
    email = os.environ.get("JIRA_EMAIL", "")
    token = os.environ.get("JIRA_TOKEN", "")

    if email and token:
        return email, token

    # Try macOS Keychain as fallback for local dev
    if platform.system() == "Darwin":
        try:
            email = email or "apiwat@amitysolutions.com"
            result = subprocess.run(
                ["security", "find-generic-password",
                 "-a", email, "-s", "jira-api-token", "-w"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                token = result.stdout.strip()
                print(f"  Using Keychain credentials for {email}")
                return email, token
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    print("ERROR: Set JIRA_EMAIL and JIRA_TOKEN environment variables")
    print('  export JIRA_EMAIL="apiwat@amitysolutions.com"')
    print('  export JIRA_TOKEN="your-api-token"')
    sys.exit(1)


# ── Jira API Client ───────────────────────────────────────────────────────

class JiraClient:
    def __init__(self, email, token):
        self.auth = base64.b64encode(f"{email}:{token}".encode()).decode()
        self.headers = {
            "Authorization": f"Basic {self.auth}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def request(self, method, path, data=None):
        url = f"{BASE_URL}{path}"
        body = json.dumps(data).encode() if data else None
        req = urllib.request.Request(url, data=body, headers=self.headers, method=method)
        try:
            with urllib.request.urlopen(req) as resp:
                if resp.status == 204:
                    return {"status": 204}
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            err = e.read().decode()[:500]
            print(f"    HTTP {e.code}: {err}")
            return None

    def get_sprint_issues(self, sprint_id, max_results=50):
        """Fetch ALL issues in a sprint (handles pagination)."""
        all_issues = []
        start_at = 0
        while True:
            result = self.request(
                "GET",
                f"/rest/agile/1.0/sprint/{sprint_id}/issue"
                f"?maxResults={max_results}&startAt={start_at}"
                f"&fields=summary,status,issuetype,assignee,description,comment"
            )
            if not result or "issues" not in result:
                break
            issues = result["issues"]
            all_issues.extend(issues)
            total = result.get("total", 0)
            start_at += len(issues)
            if start_at >= total or not issues:
                break
            time.sleep(RATE_LIMIT_DELAY)
        return all_issues

    def get_active_sprints(self, board_id):
        """Get active sprints for a board."""
        result = self.request("GET", f"/rest/agile/1.0/board/{board_id}/sprint?state=active")
        if not result:
            return []
        return result.get("values", [])

    def get_issue_comments(self, issue_key):
        """Fetch comments for an issue."""
        result = self.request("GET", f"/rest/api/3/issue/{issue_key}/comment")
        if not result:
            return []
        return result.get("comments", [])

    def delete_comment(self, issue_key, comment_id):
        return self.request("DELETE", f"/rest/api/3/issue/{issue_key}/comment/{comment_id}")

    def post_comment(self, issue_key, adf_doc):
        return self.request("POST", f"/rest/api/3/issue/{issue_key}/comment", {"body": adf_doc})


# ── ADF Document Builder ──────────────────────────────────────────────────

def build_adf_table(items, ref_text, title="Acceptance Criteria — QA Generated"):
    """Build ADF JSON document with heading + table + legend."""
    header_row = {
        "type": "tableRow",
        "content": [
            _th("#"), _th("Type"), _th("Criteria"), _th("TC Ref"),
        ],
    }
    data_rows = []
    for item in items:
        data_rows.append({
            "type": "tableRow",
            "content": [
                _td(str(item["num"])),
                _td(f'{item["emoji"]} {item["type"]}'),
                _td(item["criteria"]),
                _td(item.get("tc_ref", "")),
            ],
        })

    now = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%d")
    return {
        "version": 1,
        "type": "doc",
        "content": [
            {"type": "heading", "attrs": {"level": 3},
             "content": [{"type": "text", "text": title}]},
            {"type": "table",
             "attrs": {"isNumberColumnEnabled": False, "layout": "default"},
             "content": [header_row] + data_rows},
            {"type": "rule"},
            {"type": "paragraph", "content": [
                {"type": "text", "text": "Icon Legend: ", "marks": [{"type": "strong"}]},
                {"type": "text", "text": "✅ Positive (expected behavior) · ❌ Negative (error/rejection) · ⚠️ Edge case (boundary/race condition)"},
            ]},
            {"type": "paragraph", "content": [
                {"type": "text", "text": "Ref: ", "marks": [{"type": "strong"}]},
                {"type": "text", "text": ref_text},
            ]},
            {"type": "paragraph", "content": [
                {"type": "text", "text": "Generated: ", "marks": [{"type": "strong"}]},
                {"type": "text", "text": f"{now} by QA Agent (daily-ac-agent)"},
            ]},
        ],
    }


def _th(text):
    return {"type": "tableHeader", "content": [
        {"type": "paragraph", "content": [
            {"type": "text", "text": text, "marks": [{"type": "strong"}]}
        ]}
    ]}


def _td(text):
    return {"type": "tableCell", "content": [
        {"type": "paragraph", "content": [
            {"type": "text", "text": text}
        ]}
    ]}


# ── Text Extraction ───────────────────────────────────────────────────────

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


def has_ac_comment(comments):
    """Check if any comment is a QA-generated AC comment."""
    for c in comments:
        text = extract_text(c.get("body", {})).lower()
        if any(sig in text for sig in AC_SIGNATURES):
            return True
    return False


def get_ac_comment_ids(comments):
    """Return IDs of AC comments (for deletion before re-posting)."""
    ids = []
    for c in comments:
        text = extract_text(c.get("body", {})).lower()
        if any(sig in text for sig in AC_SIGNATURES):
            ids.append(c["id"])
    return ids


# ── Test Plan Loader ──────────────────────────────────────────────────────

def find_test_plan_csv():
    """Auto-detect the test plan CSV in workspace."""
    workspace = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for dirpath, _dirnames, filenames in os.walk(workspace):
        for f in filenames:
            if f.endswith("-testcases.csv"):
                return os.path.join(dirpath, f)
    return None


def load_test_groups(csv_path):
    """Load test case groups and their TC ranges from the CSV."""
    groups = {}
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 1):
            parts = row["Section"].split(" > ")
            group = parts[2].strip() if len(parts) >= 3 else row["Section"]
            if group not in groups:
                groups[group] = {"count": 0, "first_tc": i, "last_tc": i, "titles": []}
            groups[group]["count"] += 1
            groups[group]["last_tc"] = i
            groups[group]["titles"].append(row["Title"])
    return groups


# ── Ticket Matching ───────────────────────────────────────────────────────

def match_ticket_to_groups(summary, description=""):
    """Match a ticket to test plan groups using keyword patterns."""
    text = f"{summary} {description}".lower()
    matches = []
    for group, patterns in GROUP_KEYWORD_MAP.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                matches.append(group)
                break
    return matches


def generate_ac_from_group(group_name, test_groups, summary):
    """Generate AC items for a ticket based on its matched test group(s)."""
    if group_name not in test_groups:
        return []

    g = test_groups[group_name]
    tc_range = f"TC-{g['first_tc']:03d} to TC-{g['last_tc']:03d}"
    titles = g["titles"]

    # Select representative test cases as AC items (max 6)
    items = []
    # Categorize titles heuristically
    positive = [t for t in titles if not any(kw in t.lower() for kw in
                ["error", "invalid", "fail", "reject", "empty", "exceed", "unauthorized",
                 "boundary", "edge", "race", "concurrent", "overflow", "timeout"])]
    negative = [t for t in titles if any(kw in t.lower() for kw in
                ["error", "invalid", "fail", "reject", "unauthorized"])]
    edge = [t for t in titles if any(kw in t.lower() for kw in
            ["empty", "exceed", "boundary", "edge", "race", "concurrent",
             "overflow", "timeout", "large", "special"])]

    num = 1
    # Add up to 2 positive
    for t in positive[:2]:
        idx = titles.index(t) + g["first_tc"]
        items.append({
            "num": num, "emoji": "✅", "type": "Positive",
            "criteria": _title_to_criteria(t), "tc_ref": f"TC-{idx:03d}",
        })
        num += 1

    # Add up to 2 negative
    for t in negative[:2]:
        idx = titles.index(t) + g["first_tc"]
        items.append({
            "num": num, "emoji": "❌", "type": "Negative",
            "criteria": _title_to_criteria(t), "tc_ref": f"TC-{idx:03d}",
        })
        num += 1

    # Add up to 2 edge
    for t in edge[:2]:
        idx = titles.index(t) + g["first_tc"]
        items.append({
            "num": num, "emoji": "⚠️", "type": "Edge case",
            "criteria": _title_to_criteria(t), "tc_ref": f"TC-{idx:03d}",
        })
        num += 1

    # Ensure at least 3 items — fill from remaining positive
    remaining = [t for t in titles if t not in [x for x in positive[:2] + negative[:2] + edge[:2]]]
    while len(items) < 3 and remaining:
        t = remaining.pop(0)
        idx = titles.index(t) + g["first_tc"]
        items.append({
            "num": num, "emoji": "✅", "type": "Positive",
            "criteria": _title_to_criteria(t), "tc_ref": f"TC-{idx:03d}",
        })
        num += 1

    return items[:6], tc_range  # Max 6 items


def _title_to_criteria(title):
    """Convert a test case title to an AC criterion."""
    # Remove "Check " prefix and normalize
    t = re.sub(r"^Check\s+", "", title, flags=re.IGNORECASE)
    # Capitalize first letter
    if t:
        t = t[0].upper() + t[1:]
    return t


# ── URL Parsing ───────────────────────────────────────────────────────────

def parse_board_url(url):
    """Parse Jira board URL to extract project, board, and sprint IDs."""
    result = {"project": None, "board_id": None, "sprint_id": None}

    m = re.search(r"projects/([A-Z]+)", url)
    if m:
        result["project"] = m.group(1)

    m = re.search(r"boards/(\d+)", url)
    if m:
        result["board_id"] = int(m.group(1))

    m = re.search(r"sprints?=(\d+)", url)
    if m:
        result["sprint_id"] = int(m.group(1))

    return result


# ── Main Pipeline ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Daily AC Agent — Dynamic Sprint Ticket Discovery & AC Posting"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--sprint-id", type=int, help="Jira sprint ID (e.g., 4077)")
    group.add_argument("--board-url", type=str, help="Jira board URL with optional ?sprints=ID")
    group.add_argument("--project", type=str, help="Jira project key for auto-discover mode")

    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be posted without actually posting")
    parser.add_argument("--report-only", action="store_true",
                        help="Only report tickets missing AC, don't generate or post")
    parser.add_argument("--board-id", type=int, default=257,
                        help="Jira board ID for auto-discover (default: 257)")
    parser.add_argument("--test-plan-csv", type=str,
                        help="Path to test cases CSV (auto-detected if not set)")
    parser.add_argument("--force", action="store_true",
                        help="Re-post AC even on tickets that already have it")
    parser.add_argument("--summary-file", type=str,
                        help="Write HTML summary report to file (for email)")
    args = parser.parse_args()

    # ── Step 0: Authenticate ──
    print("=" * 65)
    print("  Daily AC Agent — Dynamic Sprint Ticket Discovery")
    print("=" * 65)
    email, token = get_credentials()
    jira = JiraClient(email, token)

    # ── Step 1: Determine Sprint ──
    sprint_id = None
    sprint_name = None

    if args.sprint_id:
        sprint_id = args.sprint_id
        print(f"\n[1/6] Sprint: ID {sprint_id} (direct)")

    elif args.board_url:
        parsed = parse_board_url(args.board_url)
        if parsed["sprint_id"]:
            sprint_id = parsed["sprint_id"]
            print(f"\n[1/6] Sprint: ID {sprint_id} (from URL)")
        elif parsed["board_id"]:
            sprints = jira.get_active_sprints(parsed["board_id"])
            if not sprints:
                print("ERROR: No active sprints found on board")
                sys.exit(1)
            sprint_id = sprints[0]["id"]
            sprint_name = sprints[0].get("name", "")
            print(f"\n[1/6] Sprint: {sprint_name} (ID {sprint_id}, auto-discovered)")
        else:
            print("ERROR: Could not parse board URL")
            sys.exit(1)

    elif args.project:
        # Auto-discover: find active sprints on the default board
        sprints = jira.get_active_sprints(args.board_id)
        if not sprints:
            print("ERROR: No active sprints found")
            sys.exit(1)
        # Use the first active sprint
        sprint_id = sprints[0]["id"]
        sprint_name = sprints[0].get("name", "")
        print(f"\n[1/6] Sprint: {sprint_name} (ID {sprint_id}, auto-discovered from board {args.board_id})")

    else:
        # Default: auto-discover from default board
        sprints = jira.get_active_sprints(args.board_id)
        if not sprints:
            print("ERROR: No active sprints. Use --sprint-id or --board-url")
            sys.exit(1)
        sprint_id = sprints[0]["id"]
        sprint_name = sprints[0].get("name", "")
        print(f"\n[1/6] Sprint: {sprint_name} (ID {sprint_id}, auto-discovered)")

    # ── Step 2: Load Test Plan ──
    csv_path = args.test_plan_csv or os.environ.get("TEST_PLAN_CSV") or find_test_plan_csv()
    test_groups = {}
    if csv_path and os.path.exists(csv_path):
        test_groups = load_test_groups(csv_path)
        total_cases = sum(g["count"] for g in test_groups.values())
        print(f"[2/6] Test Plan: {csv_path}")
        print(f"       {len(test_groups)} groups, {total_cases} test cases")
    else:
        print("[2/6] Test Plan: NOT FOUND — AC will be generated without TC references")
        print("       Set --test-plan-csv or TEST_PLAN_CSV environment variable")

    # ── Step 3: Fetch Sprint Tickets ──
    print(f"[3/6] Fetching all tickets in sprint {sprint_id}...")
    issues = jira.get_sprint_issues(sprint_id)
    print(f"       Found {len(issues)} tickets")

    if not issues:
        print("No tickets in sprint — nothing to do.")
        return

    # ── Step 4: Classify Tickets ──
    print(f"[4/6] Classifying tickets...")
    tickets_need_ac = []
    tickets_have_ac = []
    tickets_unrelated = []

    for issue in issues:
        key = issue["key"]
        fields = issue.get("fields", {})
        summary = fields.get("summary", "")
        description = extract_text(fields.get("description", {})) if fields.get("description") else ""
        issue_type = fields.get("issuetype", {}).get("name", "")
        status = fields.get("status", {}).get("name", "")
        assignee = fields.get("assignee", {})
        assignee_name = assignee.get("displayName", "Unassigned") if assignee else "Unassigned"

        # Check existing AC comments
        comments = fields.get("comment", {}).get("comments", []) if fields.get("comment") else []
        has_ac = has_ac_comment(comments)
        ac_comment_ids = get_ac_comment_ids(comments) if has_ac else []

        # Match to test groups
        matched_groups = match_ticket_to_groups(summary, description)

        ticket_info = {
            "key": key,
            "summary": summary,
            "type": issue_type,
            "status": status,
            "assignee": assignee_name,
            "has_ac": has_ac,
            "ac_comment_ids": ac_comment_ids,
            "matched_groups": matched_groups,
        }

        if has_ac and not args.force:
            tickets_have_ac.append(ticket_info)
        elif matched_groups:
            tickets_need_ac.append(ticket_info)
        else:
            tickets_unrelated.append(ticket_info)

    print(f"       ✅ Already have AC: {len(tickets_have_ac)}")
    print(f"       🆕 Need AC (matched): {len(tickets_need_ac)}")
    print(f"       ⏭️  Unrelated (no match): {len(tickets_unrelated)}")

    # ── Step 5: Report / Generate ──
    if args.report_only:
        print(f"\n[5/6] REPORT MODE — Tickets needing AC:")
        print("-" * 65)
        if tickets_need_ac:
            for t in tickets_need_ac:
                groups_str = ", ".join(t["matched_groups"])
                print(f"  {t['key']:12s} {t['summary'][:45]:46s} → {groups_str}")
        else:
            print("  (none — all matched tickets already have AC)")
        if tickets_unrelated:
            print(f"\n  Unrelated ({len(tickets_unrelated)}):")
            for t in tickets_unrelated[:10]:
                print(f"  {t['key']:12s} {t['summary'][:55]}")
            if len(tickets_unrelated) > 10:
                print(f"  ... and {len(tickets_unrelated) - 10} more")
        print(f"\n[6/6] Done (report only)")
        _write_summary(args, sprint_id, sprint_name, issues,
                       tickets_have_ac, tickets_need_ac, tickets_unrelated, [])
        return

    if not tickets_need_ac:
        print(f"\n[5/6] No tickets need AC — all matched tickets already have comments.")
        print(f"[6/6] Done (nothing to post)")
        _write_summary(args, sprint_id, sprint_name, issues,
                       tickets_have_ac, tickets_need_ac, tickets_unrelated, [])
        return

    # Generate and post
    print(f"\n[5/6] Generating AC for {len(tickets_need_ac)} tickets...")
    results = []

    for ticket in tickets_need_ac:
        key = ticket["key"]
        primary_group = ticket["matched_groups"][0]  # Use first matched group

        # Generate AC items from test plan
        if test_groups and primary_group in test_groups:
            ac_result = generate_ac_from_group(primary_group, test_groups, ticket["summary"])
            if not ac_result:
                print(f"  {key}: No AC items could be generated — skipping")
                results.append({"key": key, "status": "skipped", "reason": "no items"})
                continue
            items, tc_range = ac_result
            groups_str = ", ".join(ticket["matched_groups"])
            ref_text = f"{groups_str} · Test Cases: {tc_range}"
        else:
            # No test plan match — generate minimal AC
            items = [
                {"num": 1, "emoji": "✅", "type": "Positive",
                 "criteria": f"Feature described in '{ticket['summary'][:50]}' works as specified", "tc_ref": ""},
                {"num": 2, "emoji": "❌", "type": "Negative",
                 "criteria": "Invalid inputs are rejected with appropriate error messages", "tc_ref": ""},
                {"num": 3, "emoji": "⚠️", "type": "Edge case",
                 "criteria": "Edge cases and boundary conditions are handled gracefully", "tc_ref": ""},
            ]
            tc_range = ""
            ref_text = ", ".join(ticket["matched_groups"]) or "Manual review needed"

        # Determine title
        title = "Bug Fix Criteria — QA Generated" if ticket["type"] == "Bug" else "Acceptance Criteria — QA Generated"

        # Build ADF
        adf_doc = build_adf_table(items, ref_text, title)

        if args.dry_run:
            print(f"  {key}: Would post {len(items)} items → {', '.join(ticket['matched_groups'])}")
            results.append({"key": key, "status": "dry-run", "items": len(items)})
            continue

        # Delete existing AC comments if force mode
        if ticket["has_ac"] and args.force:
            for cid in ticket["ac_comment_ids"]:
                jira.delete_comment(key, cid)
                time.sleep(RATE_LIMIT_DELAY)

        # Post comment
        result = jira.post_comment(key, adf_doc)
        if result and result.get("id"):
            comment_id = result["id"]
            print(f"  {key}: ✅ Posted #{comment_id} ({len(items)} items) → {primary_group}")
            results.append({"key": key, "status": "posted", "comment_id": comment_id, "items": len(items)})
        else:
            print(f"  {key}: ❌ Failed to post")
            results.append({"key": key, "status": "failed"})

        time.sleep(RATE_LIMIT_DELAY)

    # ── Step 6: Summary ──
    print(f"\n[6/6] Summary")
    print("=" * 65)
    posted = [r for r in results if r["status"] == "posted"]
    failed = [r for r in results if r["status"] == "failed"]
    skipped = [r for r in results if r["status"] in ("skipped", "dry-run")]

    print(f"  Sprint {sprint_id}: {len(issues)} total tickets")
    print(f"  Already had AC: {len(tickets_have_ac)}")
    print(f"  Unrelated:      {len(tickets_unrelated)}")
    print(f"  Posted:         {len(posted)}")
    print(f"  Failed:         {len(failed)}")
    print(f"  Skipped:        {len(skipped)}")
    print("=" * 65)

    if failed:
        print("\nFailed tickets:")
        for r in failed:
            print(f"  ❌ {r['key']}")
        sys.exit(1)

    if args.dry_run:
        print("\n(Dry run — no changes were made)")

    # ── Write summary file (for email / GHA) ──
    _write_summary(args, sprint_id, sprint_name, issues,
                   tickets_have_ac, tickets_need_ac, tickets_unrelated, results)


def _write_summary(args, sprint_id, sprint_name, issues,
                   tickets_have_ac, tickets_need_ac, tickets_unrelated, results):
    """Write HTML summary report for email and GitHub Step Summary."""
    now = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M")
    mode = "report-only" if args.report_only else ("dry-run" if args.dry_run else "post")
    posted = [r for r in results if r.get("status") == "posted"] if results else []
    failed = [r for r in results if r.get("status") == "failed"] if results else []
    name = sprint_name or str(sprint_id)

    # Build HTML
    html = f"""<h2>Daily AC Scan — {name}</h2>
<p><b>Time:</b> {now} (Bangkok) &nbsp;|&nbsp; <b>Mode:</b> {mode} &nbsp;|&nbsp; <b>Sprint:</b> {sprint_id}</p>

<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse; font-family:sans-serif; font-size:14px;">
<tr style="background:#f0f0f0;"><th>Metric</th><th>Count</th></tr>
<tr><td>Total tickets in sprint</td><td>{len(issues)}</td></tr>
<tr><td>✅ Already have AC</td><td>{len(tickets_have_ac)}</td></tr>
<tr><td>🆕 Need AC (matched)</td><td>{len(tickets_need_ac)}</td></tr>
<tr><td>⏭️ Unrelated (no match)</td><td>{len(tickets_unrelated)}</td></tr>
<tr><td>📝 Posted this run</td><td>{len(posted)}</td></tr>
<tr><td>❌ Failed</td><td>{len(failed)}</td></tr>
</table>
"""

    if tickets_need_ac:
        html += "\n<h3>Tickets needing AC</h3>\n"
        html += '<table border="1" cellpadding="4" cellspacing="0" style="border-collapse:collapse; font-family:sans-serif; font-size:13px;">\n'
        html += '<tr style="background:#f0f0f0;"><th>Ticket</th><th>Summary</th><th>Status</th><th>Matched Group</th><th>Action</th></tr>\n'
        for t in tickets_need_ac:
            groups = ", ".join(t["matched_groups"])
            # Find result for this ticket
            r = next((r for r in (results or []) if r.get("key") == t["key"]), None)
            if r and r.get("status") == "posted":
                action = f'✅ Posted #{r["comment_id"]}'
            elif r and r.get("status") == "dry-run":
                action = "🔍 Dry run"
            elif r and r.get("status") == "failed":
                action = "❌ Failed"
            elif args.report_only:
                action = "📋 Report only"
            else:
                action = "⏭️ Skipped"
            summary_short = t["summary"][:50]
            html += f'<tr><td><a href="https://ekoapp.atlassian.net/browse/{t["key"]}">{t["key"]}</a></td>'
            html += f'<td>{summary_short}</td><td>{t["status"]}</td><td>{groups}</td><td>{action}</td></tr>\n'
        html += "</table>\n"

    if not tickets_need_ac and not posted:
        html += "\n<p>✅ <b>All matched tickets already have AC</b> — nothing to do.</p>\n"

    html += f'\n<hr><p style="color:#888; font-size:12px;">Generated by daily-ac-agent.py | Sprint {sprint_id}</p>'

    # Write to file if requested
    summary_path = args.summary_file or os.environ.get("SUMMARY_FILE")
    if summary_path:
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\n📧 Summary written to: {summary_path}")

    # Write to GitHub Step Summary if available
    step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if step_summary:
        with open(step_summary, "a", encoding="utf-8") as f:
            f.write(html)
        print("📧 Summary appended to GITHUB_STEP_SUMMARY")


if __name__ == "__main__":
    main()
