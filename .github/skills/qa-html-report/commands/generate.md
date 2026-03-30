# /qa-html-report — Generate Team HTML Report

## Trigger
`/qa-html-report [results-json] [output-path] [project-name] [environment]`

## What This Command Does

1. **Reads** `reports/{env}/results.json` (Playwright JSON reporter output)
2. **Generates** `reports/{env}/team-report.html` — single-file standalone HTML report
3. **Produces** a Python script `generate_report.py` in the QA_Automation root for re-running

## Phase 1 — Locate results.json

Search in order:
1. Provided path argument
2. `reports/staging/results.json` (default env = staging)
3. `reports/dev/results.json`
4. `test-results/results.json`

If not found → tell user to run tests first: `npx playwright test --reporter=json`

## Phase 2 — Parse Results

Parse the Playwright JSON structure:
```json
{
  "config": { "workers": N, "projects": [...] },
  "suites": [
    {
      "title": "describe block title",
      "specs": [
        {
          "title": "test title",
          "ok": true/false,
          "tests": [
            {
              "status": "passed|failed|flaky|skipped",
              "duration": 1234,
              "annotations": [{"type": "TestRail", "description": "C1548xxx"}, {"type": "tag", ...}],
              "results": [
                {
                  "status": "passed|failed",
                  "duration": 1234,
                  "error": { "message": "...", "stack": "..." },
                  "attachments": [
                    { "name": "screenshot", "path": "...", "contentType": "image/png" },
                    { "name": "network-log", "body": "...", "contentType": "text/plain" }
                  ],
                  "steps": [{ "title": "...", "duration": N, "error": {...} }]
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

Key parsing rules:
- `test.status === 'flaky'` = passed on retry (Playwright marks these)
- If `test.results.length > 1` and last result passes = flaky
- `test.annotations` contains `{ type: 'TestRail', description: 'C1548xxx' }` for TestRail IDs
- Extract tags from annotation type `'tag'` or from title `@smoke @P1`

## Phase 3 — Build HTML

Generate the HTML inline using a Python f-string template (no external template engine needed).

### Template structure:
```html
<!DOCTYPE html>
<html lang="th">
<head>
  <!-- CSS from SKILL.md design system -->
  <!-- Inline <style> block — no external CSS files -->
</head>
<body>
  <!-- 1. HEADER — gradient banner -->
  <!-- 2. SCORE CARDS — Total/Passed/Flaky/Failed -->
  <!-- 3. RING + MODULE BARS -->
  <!-- 4. MODULE GRID CARDS -->
  <!-- 5. ISSUES (failed + flaky cards) -->
  <!-- 6. FULL TEST TABLE + FILTER TABS -->
  <!-- 7. RECOMMENDATIONS -->
  <!-- 8. VERDICT (GO/CONDITIONAL/NO-GO) -->
  <!-- 9. FOOTER -->
  <!-- MODAL OVERLAY (hidden by default) -->
  <!-- INLINE JAVASCRIPT for filter + modal -->
</body>
</html>
```

### SVG Donut Ring:
```python
def make_donut(pct, r=80, stroke=14):
    cx = cy = r + stroke
    circumference = 2 * math.pi * r
    dash = circumference * pct / 100
    return f'''
    <svg width="{2*(r+stroke)}" height="{2*(r+stroke)}">
      <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#e5e7eb" stroke-width="{stroke}"/>
      <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#0e7c61" stroke-width="{stroke}"
        stroke-dasharray="{dash:.1f} {circumference:.1f}"
        stroke-linecap="round"
        transform="rotate(-90 {cx} {cy})"/>
      <text x="{cx}" y="{cy}" text-anchor="middle" dominant-baseline="middle"
        font-size="22" font-weight="700" fill="#0e7c61">{pct:.0f}%</text>
    </svg>'''
```

### Root Cause Classification:
```python
def classify(error_msg: str) -> str:
    msg = (error_msg or '').lower()
    if any(k in msg for k in ['timeout', 'err_', 'econnrefused', 'network', '502', '503', '504']):
        return 'INFRA'
    if any(k in msg for k in ['already exist', 'duplicate', 'cannot delete', 'state pollution']):
        return 'CLEANUP'
    if any(k in msg for k in ['expect', 'tohave', 'tobe', 'assertion', 'expected']):
        return 'BUG'
    return 'UNKNOWN'
```

### Verdict Logic:
```python
def verdict(pass_pct, p1_failures):
    if pass_pct >= 80 and p1_failures == 0:
        return 'GO', '✅ พร้อม Release — ผลทดสอบผ่านตามเกณฑ์'
    if pass_pct >= 60 or p1_failures == 0:
        return 'CONDITIONAL', '⚠️ Release ได้แบบมีเงื่อนไข — ตรวจสอบ issues ก่อน'
    return 'NO-GO', '❌ ไม่พร้อม Release — มี P1 failures หรือ pass rate ต่ำกว่า 60%'
```

## Phase 4 — Write Output

```python
output_path = args.output or f"reports/{env}/team-report.html"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"✅ Report generated: {output_path}")
print(f"   Total: {total} | Passed: {passed} | Failed: {failed} | Flaky: {flaky}")
print(f"   Pass rate: {pass_pct:.1f}% | Verdict: {verdict}")
```

Then optionally open: `import subprocess; subprocess.run(['open', output_path])`

## Output Files

| File | Description |
|---|---|
| `reports/{env}/team-report.html` | Standalone HTML report (shareable) |
| `reports/{env}/generate_report.py` | Re-runnable Python script |

## Error Handling

| Situation | Action |
|---|---|
| `results.json` not found | Print "Run tests first: npx playwright test --reporter=json" |
| 0 test results | Print warning: "No test results found in JSON" |
| Missing screenshots | Skip screenshot section (don't fail) |
| Very large JSON (>10MB) | Stream parse, truncate long error messages to 500 chars |
