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

Scan the workspace for QA artifacts created during this sprint:

1. **Spec files** — `specs/*.md` (feature spec files from `/qa:write-ac`)
2. **Test plan files** — `*-test-plan.md` in workspace root
3. **TestRail CSV files** — `*-testrail.csv` in workspace root
4. **Generator scripts** — `generate-testrail-csv.py` or similar helper scripts
5. **Any other `.md` files** that reference the sprint (e.g., `create-new-*-test-cases.md`)

⚠️ Do NOT touch:
- `.github/` folder (skill definitions)
- `.vscode/` folder (editor config)
- `archive/` folder (previous sprint archives)
- `scripts/` folder (reusable utility scripts)

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
📦 Sprint Archive Plan: Agentic 18.1
   Target: archive/agentic-18.1/

   Files to archive:
   ├── specs/ekoai-scheduled-jobs.md          → archive/agentic-18.1/specs/
   ├── ekoai-scheduled-jobs-test-plan.md      → archive/agentic-18.1/
   ├── ekoai-scheduled-jobs-testrail.csv      → archive/agentic-18.1/
   ├── generate-testrail-csv.py               → archive/agentic-18.1/
   └── create-new-scheduler-test-cases.md     → archive/agentic-18.1/

   ⚠️ Files NOT touched:
   ├── .github/  (skill definitions)
   ├── .vscode/  (editor config)
   ├── scripts/  (utility scripts)
   └── archive/  (previous sprints)

   Total: {N} files to move
```

**Wait for user confirmation before proceeding.**

### Step 4 — Execute Archive

1. Create the archive directory structure:
   ```bash
   mkdir -p archive/{sprint-name}/specs
   ```

2. Move each file preserving folder structure:
   ```bash
   mv specs/ekoai-scheduled-jobs.md archive/{sprint-name}/specs/
   mv ekoai-scheduled-jobs-test-plan.md archive/{sprint-name}/
   mv ekoai-scheduled-jobs-testrail.csv archive/{sprint-name}/
   ```

3. If the `specs/` folder is now empty, remove it:
   ```bash
   rmdir specs/   # only if empty
   ```

### Step 5 — Generate Archive Summary

Create `archive/{sprint-name}/ARCHIVE-SUMMARY.md` with:

```markdown
# Sprint Archive: {Sprint Name}
*Archived: {date} · Sprint ID: {sprint-id}*
*Quick Filter: Broccoli*

## Artifacts

| File | Type | Description |
|---|---|---|
| specs/ekoai-scheduled-jobs.md | Feature Spec | {N} requirements · {M} UI states |
| ekoai-scheduled-jobs-test-plan.md | Test Plan | {N} test cases across {M} groups |
| ekoai-scheduled-jobs-testrail.csv | TestRail CSV | {N} rows, ready for import |
| generate-testrail-csv.py | Script | CSV generator |

## Sprint Stats
- **Test cases generated:** {N}
- **Tickets with AC posted:** {N} of {M}
- **Features covered:** [list]

## How to Access
These files can be read anytime for reference. They are preserved exactly as they were
at the end of the sprint — no modifications after archiving.
```

### Step 6 — Verify & Report

1. Verify all files were moved successfully (check existence in archive, absence in root)
2. Report:

```
✅ Sprint archived: archive/agentic-18.1/
   {N} files moved · ARCHIVE-SUMMARY.md created
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
- **Always confirm** with the user before moving any file.
- **Preserve directory structure** — `specs/` files go to `archive/{sprint}/specs/`.
