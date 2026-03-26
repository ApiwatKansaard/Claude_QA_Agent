# Release Notes: Broccoli-F (Sprint 18.2)
*Generated: 2026-03-24 · Sprint ID: 4077*

## Summary

| Metric | Value |
|--------|-------|
| Tickets with AC | 15 |
| Total AC items | 66 |
| Positive (/) | 27 |
| Negative (x) | 22 |
| Edge case (!) | 17 |
| Test groups covered | 10 of 17 |
| Test cases referenced | TC-001 to TC-147 |

## AC Posted by Category

### UI Stories (Pakkawat Suwannasam) — 6 tickets

| # | Ticket | Summary | Status | AC Items |
|---|--------|---------|--------|----------|
| 1 | AE-14288 | Dashboard page (ui) | In Code Review | 5 |
| 2 | AE-14290 | Failure Log page (ui) | In Code Review | 4 |
| 3 | AE-14292 | Create page (ui) | In Code Review | 6 |
| 4 | AE-14294 | Recipients (ui) | In Code Review | 5 |
| 5 | AE-14296 | Job configuration (ui) | WIP | 5 |
| 6 | AE-14298 | History logs (ui) | WIP | 5 |

### Bug (Pakkawat Suwannasam) — 1 ticket

| # | Ticket | Summary | Status | AC Items |
|---|--------|---------|--------|----------|
| 7 | AE-14249 | Table scroll bug (rows 1–6 only) | Backlog | 3 |

### BE Stories (Jugkapong Pooban) — 8 tickets

| # | Ticket | Summary | Status | AC Items |
|---|--------|---------|--------|----------|
| 8 | AE-14468 | [BE] script to create collection and index | In Code Review | 4 |
| 9 | AE-14344 | [BE] HomePage Mongoose model + indexes | In Code Review | 4 |
| 10 | AE-14346 | [BE] HomePageService CRUD + endpoint | In Code Review | 5 |
| 11 | AE-14348 | [BE] Push notifications for Home Page | In Code Review | 4 |
| 12 | AE-14350 | [BE] Real-time event dispatch | In Code Review | 4 |
| 13 | AE-14353 | [BE] HomePageActionDelivery create API | In Code Review | 4 |
| 14 | AE-14355 | [BE] HomePageActionDelivery update API | In Code Review | 4 |
| 15 | AE-14357 | [BE] Retry logic exponential backoff | In Code Review | 5 |

## Test Group Coverage Map

| Test Group | TC Range | Referenced By |
|------------|----------|---------------|
| Dashboard | TC-001 to TC-007 | AE-14288, AE-14249 |
| Create Job | TC-008 to TC-019 | AE-14292 |
| Job Configuration | TC-020 to TC-029 | AE-14296 |
| Recipients | TC-030 to TC-040 | AE-14294 |
| History Logs | TC-041 to TC-049 | AE-14290, AE-14298 |
| Process Step | TC-059 to TC-072 | AE-14357 |
| Action Step | TC-083 to TC-092 | AE-14353, AE-14355 |
| Cutoff Timeout | TC-093 to TC-099 | AE-14357 |
| Home Page Delivery | TC-100 to TC-112 | AE-14344, AE-14346, AE-14348, AE-14350, AE-14353, AE-14355 |
| Database and Infra | TC-138 to TC-147 | AE-14468, AE-14344 |

## Groups Not Covered This Sprint

| Test Group | TC Range | Reason |
|------------|----------|--------|
| Trigger Step | TC-050 to TC-058 | No ticket in sprint |
| Callback | TC-073 to TC-082 | No ticket in sprint |
| Widget Rendering | TC-113 to TC-121 | No ticket in sprint |
| Security | TC-122 to TC-130 | No ticket in sprint |
| Status Check | TC-131 to TC-137 | No ticket in sprint |
| Race Conditions | TC-148 to TC-153 | No ticket in sprint |
| API Endpoints | TC-154 to TC-168 | No ticket in sprint |

## Skill Update

- Updated `write-ac.md` — mandatory Icon Legend panel added to AC comment template
- Legend explains `(/)`, `(x)`, `(!)` icons in every Jira comment
