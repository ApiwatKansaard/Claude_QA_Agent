# Bug Report: ScheduledJobRun status stuck at PROCESSING when all users FAILED

## Summary

When all `ScheduleJobRunUser` records in a run have reached terminal status `FAILED` (due to process step failure), the parent `ScheduleJobRun.status` remains `PROCESSING` indefinitely instead of aggregating to `FAILED`. This causes the History Log tab in EkoAI Console to show "No Data" because it queries `runs?status=FAILED` which returns empty results.

## Severity

**High** — History Log tab is completely broken for process-step failures. Admins cannot see failed runs in the UI until the 24-hour cutoff timeout fires.

## Environment

- **Platform:** EkoAI Console (Staging)
- **URL:** `https://ekoai-console.staging.ekoapp.com`
- **Date:** 2026-04-02

## Steps to Reproduce

1. Create a scheduled job with:
   - 1 audience user
   - Process endpoint pointing to a server that returns HTTP 500
   - `runUntilTimes: 1`
2. Wait for the job to trigger
3. EkoAI calls `/status-check` → 200 OK
4. EkoAI calls `/webhook` per user → receives 500
5. EkoAI retries 3 times (4 calls total) → all return 500
6. Navigate to **History Log** tab

## Expected Behavior

- `ScheduleJobRunUser.status` = `FAILED` ✅ (this works correctly)
- `ScheduleJobRun.status` = `FAILED` ❌ (should aggregate since all users are terminal)
- History Log tab shows the failed run with user details

## Actual Behavior

- `ScheduleJobRunUser.status` = `FAILED` ✅
- `ScheduleJobRun.status` = `PROCESSING` ❌ **stuck — never aggregates**
- History Log tab shows **"No Data"** because it queries `?status=FAILED` and run is still `PROCESSING`

The run will only change to `FAILED` after the **24-hour cutoff timeout** fires, which is far too late for admins to notice and act.

## Evidence

### API responses

**Run level (parent) — stuck at PROCESSING:**
```
GET /v1/scheduled-jobs/69cd5941b1d83981cdb772cd/runs

{
  "data": [{
    "id": "69cd5a0a4ab0cc29be6d893a",
    "status": "PROCESSING",          ← should be FAILED
    "failReasonCode": null,
    "startedAt": "2026-04-01T17:46:...",
    "finishedAt": null                ← never finished
  }]
}
```

**User level (child) — correctly FAILED:**
```
GET /v1/scheduled-jobs/.../runs/.../run-users

{
  "data": [{
    "user": { "username": "10189955", "firstname": "Thu Hnin Aye" },
    "status": "FAILED",
    "run": {
      "process": {
        "status": "FAILED",
        "failReasonCode": "PROCESS_CALL_FAILED"
      }
    }
  }]
}
```

**History Log tab query — returns empty:**
```
GET /v1/scheduled-jobs/.../runs?status=FAILED&limit=10

{
  "data": [],              ← empty because run status is PROCESSING, not FAILED
  "pagination": { "total": 0 }
}
```

### Webhook call log (from mock server)

EkoAI correctly retried 4 times before marking user as FAILED:

```
Call 1: POST /webhook → 500 (initial attempt)
Call 2: POST /webhook → 500 (retry 1)
Call 3: POST /webhook → 500 (retry 2)
Call 4: POST /webhook → 500 (retry 3 — final)
→ User marked FAILED with PROCESS_CALL_FAILED ✅
→ Run status NOT updated ❌
```

## Root Cause Analysis

Per the Tech Spec ([TS] EkoAI | Eko | AI Scheduled Jobs):

> The action worker takes 3 responsibilities:
> 1. Process the action handler
> 2. Commit/aggregate the status of `ScheduleJobRunUser`
> 3. Commit/aggregate the status of `ScheduleJobRun`

When the **process step fails**, the pipeline never reaches the **action step**. Since run status aggregation is handled by the action worker, it never executes → run status stays `PROCESSING`.

**The aggregation logic only runs in the action worker path, but process-step failures bypass the action worker entirely.**

```
Normal flow:    Trigger → Process ✅ → Action Worker → Aggregate Run Status ✅
Failure flow:   Trigger → Process ❌ → (no action)  → (no aggregation) ❌
```

## Suggested Fix

Add run status aggregation after the process step completes (not just in the action worker). When all `ScheduleJobRunUser` records reach a terminal state (`SUCCESS` or `FAILED`), the `TriggerWorkerService` or a dedicated aggregation check should update `ScheduleJobRun.status`:

- All users `SUCCESS` → Run `SUCCESS`
- All users `FAILED` → Run `FAILED`
- Mix of `SUCCESS` + `FAILED` → Run `PARTIAL_SUCCESS`

This check should run:
1. After each user's process step completes (success or failure)
2. After all retries are exhausted for a user

## Impact

- **Admin visibility:** Admins cannot see process-step failures in History Log until 24h cutoff
- **Monitoring:** Any alerting based on run status will miss these failures
- **Dashboard metrics:** "Success Rate" and "Failure Logs" counters on the dashboard won't reflect process failures

## Test Job Details

| Field | Value |
|---|---|
| Job ID | `69cd5941b1d83981cdb772cd` |
| Run ID | `69cd5a0a4ab0cc29be6d893a` |
| Run User ID | (check via API) |
| Audience | `690c1180b26c660c776ffa10` (Thu Hnin Aye) |
| Process endpoint | ngrok → mock server returning 500 |
