# /qa:end-sprint [Sprint Name or ID]

**Triggers:** report-compiler
**References:** [templates.md](../references/templates.md)

## What This Command Does

Archives all QA artifacts (specs, test plans, test cases, CSV files) from the current sprint
into a named folder so the workspace is clean for the next sprint.

**Key guarantee:** Files are **MOVED, never deleted**. All archived artifacts remain readable
and accessible under the `archive/` folder for future reference.

## Parameters

| Parameter | Required | Notes |
|---|---|---|
| `[Sprint Name or ID]` | Optional | Sprint name (e.g., "Agentic 18.1") or sprint ID (e.g., `4077`). If omitted, auto-detect from existing spec files or ask the user. |

## Sprint Scope

- This command is used **once at the end of each sprint** before starting the next one.
- Quick Filter context: **Broccoli** — only Broccoli-related artifacts are managed.
- Sprint version numbers (18.0, 18.1, etc.) change each sprint — the archive folder preserves
  the sprint name as-is for historical record.

## Execution Steps

### Step 1 — Identify Current Sprint Artifacts

Scan the workspace in two locations:

**1a. Sprint folder** (primary — all artifacts should be here):
Locate the active sprint folder at the workspace root (e.g., `agentic-18.2/`).
Sprint folders follow the pattern `agentic-*/` or `sprint-*/`.

Expected contents:
1. **Test plan** — `{feature-slug}-test-plan.md`
2. **Test cases CSV** — `{feature-slug}-testcases.csv`
3. **Generator script** — `generate-csv.py` or `generate-*.py`
4. **Release notes** — `release-notes-{sprint-name}.md` (from `/qa:write-ac` Phase 10)
5. **Other sprint files** — any `.md` or `.csv` files created during the sprint

**1b. Root-level stray files** (secondary — should not be here):
Check workspace root for any stray artifacts that belong in the sprint folder:
- `*-test-plan.md`, `*-testcases.csv`, `*-testrail.csv`, `generate-*.py`, `release-notes-*.md`
- These will be moved INTO the sprint archive folder alongside the sprint folder contents.

**If no sprint folder AND no stray files found** → abort:
> "❌ Nothing to archive — no sprint folder or stray artifacts found at workspace root.
> Are you sure this sprint has active artifacts? Check `archive/` if the sprint was already archived."

⚠️ Do NOT touch:
- `.github/` folder (skill definitions)
- `.vscode/` folder (editor config)
- `archive/` folder (previous sprint archives)
- `scripts/` folder (reusable utility scripts)
- `testrail-cache/` folder (persists across sprints — NOT archived)

### Step 2 — Determine Archive Folder Name

Create a folder name based on the sprint:

**Format:** `archive/{sprint-name-sanitized}/`

**Sanitization rules:**
- Replace spaces with `-`
- Lowercase
- Remove special characters except `-` and `.`
- Examples: "Agentic 18.1" → `archive/agentic-18.1/`, Sprint ID 4077 → `archive/sprint-4077/`

If a sprint name is available (from the spec file header or user input), prefer the name.
If only a sprint ID is available, use `sprint-{id}`.

### Step 3 — Preview Archive Plan

Show the user what will be moved before executing:

```
📦 Sprint Archive Plan: Agentic 18.2
   Target: archive/agentic-18.2/

   Sprint folder (move entire folder):
   └── agentic-18.2/                           → archive/agentic-18.2/
       ├── ekoai-scheduled-jobs-test-plan.md
       ├── ekoai-scheduled-jobs-testcases.csv
       ├── generate-csv.py
       └── release-notes-broccoli-f.md

   Root stray files (move into archive):
   ├── ekoai-scheduled-jobs-test-plan.md       → archive/agentic-18.2/  (stray)
   └── (none found)

   ⚠️ Files NOT touched:
   ├── .github/        (skill definitions)
   ├── .vscode/        (editor config)
   ├── scripts/        (utility scripts)
   ├── archive/        (previous sprints)
   └── testrail-cache/ (persists across sprints)

   Total: {N} files to archive
```

**Wait for user confirmation before proceeding.**

### Step 4 — Execute Archive

1. **Move the entire sprint folder** to `archive/`:
   ```bash
   mv {sprint-folder} archive/{sprint-folder}
   # Example: mv agentic-18.2 archive/agentic-18.2
   ```

2. **Move any root-level stray files** into the same archive:
   ```bash
   # Only if stray files were found in Step 1b
   mv ekoai-scheduled-jobs-test-plan.md archive/{sprint-folder}/
   ```

3. **Verify** the workspace root is clean — no sprint artifacts remaining.

### Step 5 — Generate Archive Summary

Create `archive/{sprint-name}/ARCHIVE-SUMMARY.md` with:

```markdown
# Sprint Archive: {Sprint Name}
*Archived: {date} · Sprint ID: {sprint-id}*
*Quick Filter: Broccoli*

## Artifacts

| File | Type | Description |
|---|---|---|
| {feature-slug}-test-plan.md | Test Plan | {N} test cases across {M} groups |
| {feature-slug}-testcases.csv | Test Cases CSV | {N} rows, TestRail-ready (15 columns) |
| generate-csv.py | Script | CSV generator/validator |
| release-notes-{sprint-name}.md | Release Notes | AC summary: {N} tickets, {M} AC items |

## Sprint Stats
- **Test cases generated:** {N}
- **Tickets with AC posted:** {N} of {M}
- **Bugs filed this sprint:** {N} (via /qa:bug-report)
- **TestRail import:** {N} cases imported to suite S{suite-id}
- **Features covered:** [list]

## Data Sources
- **Confluence:** pages {page-ids}
- **Figma:** file {file-key} (nodes: {node-ids})
- **Jira:** project AE, board 257, sprint {sprint-id}

## How to Access
These files can be read anytime for reference. They are preserved exactly as they were
at the end of the sprint — no modifications after archiving.
```

### Step 6 — Verify & Report

1. Verify the sprint folder was moved successfully (check existence in archive)
2. Verify no stray files remain at workspace root
3. Verify `testrail-cache/` is untouched
4. Report:

```
✅ Sprint archived: archive/{sprint-folder}/
   📁 Sprint folder moved ({N} files)
   📄 Root stray files cleaned ({N} files)
   📝 ARCHIVE-SUMMARY.md created
   Workspace is now clean for the next sprint.

   Next: /qa:start-sprint to begin the new sprint.
```

## Output Format

### Part 1 — Archive Plan (before confirmation)
The preview from Step 3.

### Part 2 — Archive Result (after execution)
The report from Step 6.

## Safety Rules

- **NEVER delete files** — only move to `archive/`.
- **NEVER overwrite** existing archives — if `archive/{sprint-name}/` already exists,
  append a suffix: `archive/{sprint-name}-2/`.
- **NEVER touch `testrail-cache/`** — it persists across sprints as the baseline for comparison.
- **Always confirm** with the user before moving any file.
- **Move the sprint folder as a whole** — don't move files individually.
