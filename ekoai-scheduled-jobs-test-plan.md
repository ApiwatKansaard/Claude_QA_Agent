# EkoAI Scheduled Jobs — Test Plan

> **Feature**: EkoAI | Eko | AI Scheduled Jobs  
> **Sprint**: Current  
> **Generated**: Auto-generated from Confluence specs + Figma designs  
> **Sources**:  
> - [TP] EkoAI | Eko | AI Scheduled Jobs (Tech Proposal)  
> - [TS] EkoAI | Eko | AI Scheduled Jobs (Tech Spec)  
> - [TS] EkoAI | Eko | AI Scheduled Jobs; Morning Brief Actions  
> - [Doc] Project Team Guide | Scheduled Job  
> - [Doc] Project Team Guide | Home Page  
> - Figma: Dashboard, Create, Job Configuration, Recipients, History Logs  

---

## Group 1: Dashboard — Job List & Filtering

| # | Test Case | Priority | Steps | Expected Result |
|---|-----------|----------|-------|-----------------|
| 1.1 | View dashboard with scheduled jobs | High | 1. Navigate to EkoAI Console → Scheduled Jobs | Dashboard displays list of scheduled jobs with name, status (enabled/disabled), schedule, last run, next run |
| 1.2 | Dashboard shows empty state | Medium | 1. Navigate to dashboard when no jobs exist | Empty state is displayed with guidance to create a new job |
| 1.3 | Filter jobs by status | Medium | 1. Open dashboard with multiple jobs 2. Select a filter from the Menu List dropdown | Only jobs matching the filter criteria are shown |
| 1.4 | Dashboard navbar in collapsed state | Low | 1. Open dashboard | Left navbar renders in Collapse variant as per Figma design |
| 1.5 | Dashboard menu list supports up to 20 items | Medium | 1. Create 20+ scheduled jobs 2. Open dashboard | Menu List component renders up to 20 items; pagination or scrolling is available for overflow |
| 1.6 | View job details from dashboard | High | 1. Click on a scheduled job row in the dashboard | Navigates to Job Configuration page showing full job details |

## Group 2: Create Scheduled Job — Multi-Step Wizard

| # | Test Case | Priority | Steps | Expected Result |
|---|-----------|----------|-------|-----------------|
| 2.1 | Access create job wizard | High | 1. Navigate to Dashboard 2. Click "Create" button | Step 1 of create wizard is displayed with main container and form fields |
| 2.2 | Create job — fill name and description | High | 1. Open create wizard 2. Enter job name 3. Enter job description | Name and description fields accept input; name is required |
| 2.3 | Create job — configure cron trigger | High | 1. In trigger step, enter cron expression (e.g., `0 8 * * 1-5`) | Cron expression is saved; system interprets as "weekdays at 08:00" |
| 2.4 | Create job — select repeat dropdown | High | 1. Open create wizard → trigger config 2. Click repeat dropdown | Dropdown Menu List opens showing repeat options (daily, weekly, custom cron) |
| 2.5 | Create job — configure end date (optional) | Medium | 1. Open Date picker component 2. Select end date | Date picker (Type=One Date, Preset=False) allows selecting a single end date |
| 2.6 | Create job — configure runUntilTimes (optional) | Medium | 1. Enter a number in runUntilTimes field | Field accepts positive integer; job will auto-stop after this many runs |
| 2.7 | Create job — configure process endpoint | High | 1. Enter HTTPS endpoint URL 2. Enter API key 3. Optionally adjust timeout | Process step stores endpoint, apiKey, and timeoutSeconds |
| 2.8 | Create job — validate endpoint requires HTTPS | High | 1. Enter HTTP (non-HTTPS) endpoint URL | Validation error: endpoint must use HTTPS |
| 2.9 | Create job — configure action type | High | 1. Select action type = MORNING_BRIEF 2. Configure schedule (immediate or time-triggered) | Action step saved with type and schedule configuration |
| 2.10 | Create job — configure audience | High | 1. Add user IDs to audience 2. Add directory IDs | Audience configuration saved with type="Eko", userIds, and directoriesIds |
| 2.11 | Create job — submit and save | High | 1. Complete all steps 2. Click Create/Save | Job is persisted as ScheduleJob entity. Toast notification (Status=Success) appears |
| 2.12 | Create job — required fields validation | High | 1. Try to submit without filling required fields | Validation errors shown for missing required fields (name, endpoint, audience) |
| 2.13 | Create job — default timeout value | Medium | 1. Create job without modifying timeout | Default timeoutSeconds = 100 is applied |

## Group 3: Job Configuration — View & Edit

| # | Test Case | Priority | Steps | Expected Result |
|---|-----------|----------|-------|-----------------|
| 3.1 | View job configuration (Default state) | High | 1. Navigate to an existing job configuration | Job Configuration page displays in Default state showing all config fields |
| 3.2 | Edit job configuration — enter editing mode | High | 1. Open job configuration 2. Click edit button | Page transitions to Updating state; fields become editable |
| 3.3 | Save job configuration changes | High | 1. Modify job fields (name, schedule, etc.) 2. Click save | Page transitions to Updated state; Toast (Status=Success) shown; changes persisted |
| 3.4 | Edit job — toggle isEnabled | High | 1. Open job config 2. Toggle isEnabled on/off | Job enable/disable status is updated; disabled jobs won't be picked by scheduler |
| 3.5 | Edit job — update cron expression | High | 1. Change cron expression 2. Save | nextRun is recalculated by system based on new cron definition |
| 3.6 | Edit job — update process endpoint | Medium | 1. Change endpoint URL 2. Save | New endpoint URL is persisted; next runs use updated endpoint |
| 3.7 | Edit job — update action schedule | Medium | 1. Change action schedule from immediate to time-triggered 2. Save | Action schedule updated; next runs respect new delivery timing |
| 3.8 | Confirm before delete (modal) | High | 1. Click delete on a job 2. Modal (Type=Basic modal) appears | Confirmation modal shown before soft-delete (isDeleted=true) |
| 3.9 | Soft-delete a scheduled job | High | 1. Confirm delete in modal | Job is marked isDeleted=true; no longer appears in active list but retained for history |
| 3.10 | Edit job — nextRun is read-only | Medium | 1. View job config | nextRun field is displayed but not editable (maintained by scheduler) |

## Group 4: Recipients (Audience Management)

| # | Test Case | Priority | Steps | Expected Result |
|---|-----------|----------|-------|-----------------|
| 4.1 | View audience group (Default state) | High | 1. Navigate to Recipients tab of a job | Audience Group displayed in Default state with user IDs and directory IDs |
| 4.2 | Edit audience — add users | High | 1. Enter Updating state 2. Add Eko user IDs | User IDs added to audience.userIds array |
| 4.3 | Edit audience — add directories | High | 1. Enter Updating state 2. Add Eko directory/group IDs | Directory IDs added to audience.directoriesIds array |
| 4.4 | Save audience changes | High | 1. Make audience changes 2. Click save | Transitions to Updated state; Toast (Success) shown; changes persisted |
| 4.5 | Audience resolution at trigger time | High | 1. Configure audience with userIds + directoryIds 2. Wait for trigger | At trigger time, system calls Eko APIs to resolve directories → users, filters out deleted/disabled users |
| 4.6 | Audience snapshot is static per run | High | 1. Trigger a job run 2. Modify audience on Eko after run starts | Running job uses the snapshot taken at trigger time; changes don't affect current run |
| 4.7 | Audience type is always "Eko" | Medium | 1. View audience config | audience.type shows "Eko" (only supported type in phase 1) |
| 4.8 | Audience modal for bulk operations | Medium | 1. Click manage audience 2. Modal (Desktop) appears | Modal allows adding/removing users and directories in bulk |
| 4.9 | Deleted/disabled Eko users excluded | High | 1. Configure audience with a user that is deleted on Eko 2. Trigger job | Deleted/disabled user is excluded from ScheduleJobRun.scheduleJobAudience |
| 4.10 | Eko API called for user resolution | High | 1. Trigger job with userIds configured | EkoAI calls Eko APIs (Query Users, Get Users by IDs) using Network.ekoConfig |
| 4.11 | Eko API called for directory resolution | High | 1. Trigger job with directoryIds configured | EkoAI calls Eko APIs (Query Directories, Query Users from Directory) to resolve groups into individual users |
| 4.12 | Eko API failure during audience resolution | High | 1. Eko API is unavailable during trigger | Run should fail gracefully or retry audience resolution |

## Group 5: History Logs & Job Run Tracking

| # | Test Case | Priority | Steps | Expected Result |
|---|-----------|----------|-------|-----------------|
| 5.1 | View history logs — populated state | High | 1. Navigate to History Logs tab of a job with past runs | Table shows job runs with status (RUNNING/SUCCESS/FAILED), startedAt, finishedAt |
| 5.2 | History logs — empty state | Medium | 1. Navigate to History Logs for a job with no runs | Empty state frame displayed with appropriate message |
| 5.3 | Select all entries on this page | Medium | 1. In history logs 2. Click "Select all → This page" | All visible entries on current page are selected |
| 5.4 | Select all entries (400 audiences) | Medium | 1. View job run with 400 audience members 2. Select all | All 400 audience entries are selected across pages |
| 5.5 | Retry failed executions | High | 1. Select failed ScheduleJobRunUser entries 2. Click Retry | Retrying state shown; selected entries are re-enqueued for processing |
| 5.6 | View per-user execution details | High | 1. Click on a ScheduleJobRunUser entry | Details show: process status, action status, fail reasons (if any), timestamps |
| 5.7 | History shows ScheduleJobRun status | High | 1. View history after run completes | ScheduleJobRun shows aggregated status: RUNNING → SUCCESS or FAILED |
| 5.8 | History shows ScheduleJobRunUser statuses | High | 1. Expand a run to see per-user details | Each user shows: PENDING → PROCESSING → EXECUTING → SUCCESS/FAILED |
| 5.9 | History logs — modal for details | Medium | 1. Click on a run for extended details | Modal (Type=Basic modal) displays full run details and snapshot |

## Group 6: Trigger Step — Scheduler Logic

| # | Test Case | Priority | Steps | Expected Result |
|---|-----------|----------|-------|-----------------|
| 6.1 | Scheduler picks up due jobs | High | 1. Create enabled job with nextRun <= now 2. Wait for scheduler tick | Scheduler creates ScheduleJobRun with snapshot of config + audience |
| 6.2 | Scheduler skips disabled jobs | High | 1. Create job with isEnabled=false 2. Wait for scheduler tick | Job is NOT picked up by scheduler |
| 6.3 | Scheduler respects endDate | High | 1. Create job with endDate in the past | After endDate, job is no longer triggered |
| 6.4 | Scheduler respects runUntilTimes | High | 1. Create job with runUntilTimes=3 2. Run job 3 times | After 3rd run, job is no longer triggered; runTimes matches runUntilTimes |
| 6.5 | nextRun is updated after each trigger | High | 1. Trigger job with cron `0 8 * * 1-5` | After trigger, nextRun is updated to next weekday 08:00 based on iCalendar definition |
| 6.6 | ScheduleJobRun snapshot captures config | High | 1. Trigger a job run | ScheduleJobRun.scheduleJobStep contains frozen snapshot of trigger, process, and action config |
| 6.7 | ScheduleJobRun snapshot captures audience | High | 1. Trigger a job run | ScheduleJobRun.scheduleJobAudience contains resolved users + groups with id and name |
| 6.8 | Internal trigger endpoint | High | 1. POST `/_internal/scheduled-job-action-orchestrator/trigger` | Endpoint processes eligible jobs within the tick interval (~1 minute) |
| 6.9 | lastRun updated after trigger | Medium | 1. Trigger a job | ScheduleJob.step.trigger.lastRun is updated to the trigger datetime |
| 6.10 | runTimes incremented after each run | Medium | 1. Trigger a job multiple times | ScheduleJob.step.trigger.runTimes increments by 1 after each trigger |

## Group 7: Process Step — External Endpoint & Throttling

| # | Test Case | Priority | Steps | Expected Result |
|---|-----------|----------|-------|-----------------|
| 7.1 | Per-user request dispatched to endpoint | High | 1. Job triggers with 5 audience users | 5 separate requests sent to process endpoint; each contains scheduleJobRunUserId + user context |
| 7.2 | Request includes API key header | High | 1. Inspect outbound request to external endpoint | Request contains `X-API-KEY` header with the configured apiKey |
| 7.3 | Request includes HMAC signature | High | 1. Inspect outbound request | EkoAI-Signature header present with HMAC-SHA256 over the JSON payload |
| 7.4 | 200/202 acknowledgement — status to EXECUTING | High | 1. External endpoint returns 200 OK | ScheduleJobRunUser.status advances to EXECUTING; awaits callback |
| 7.5 | 4xx response — immediate FAILED, no retry | High | 1. External endpoint returns 400/403 | ScheduleJobRunUser.status = FAILED; failReasonCode = VALIDATION_ERROR; no retry |
| 7.6 | 5xx response — retry with backoff | High | 1. External endpoint returns 500 | EkoAI retries up to configured retry times (default 3); if exhausted → FAILED |
| 7.7 | Webhook ack timeout (10s) | High | 1. External endpoint does not respond within 10s | Treated as transient failure; retried up to retry times |
| 7.8 | Slow-start throttling algorithm | High | 1. Trigger job with large audience (100+ users) | Starts with low concurrency; increases on success; decreases on failure |
| 7.9 | Configurable timeout (default 100s) | Medium | 1. Job run with default timeout 2. External callback doesn't arrive within 100s | ScheduleJobRunUser marked FAILED after timeout |
| 7.10 | Custom timeout value | Medium | 1. Set timeoutSeconds=300 in process config | System waits up to 300s for callback |
| 7.11 | Request payload format is locked | High | 1. Inspect outbound request payload | Payload contains: id (scheduleJobRunUserId), data.userId, data.username; guaranteed fields present |
| 7.12 | Optional user fields in payload | Medium | 1. Audience user has email, firstname, lastname, position | Optional fields (email, firstname, lastname, position, ad_domain, extras) included when available |
| 7.13 | ScheduleJobRunUser created per user | High | 1. Trigger job with N users | N ScheduleJobRunUser records created, each with status PENDING initially |
| 7.14 | Processing status tracking | High | 1. Monitor ScheduleJobRunUser during process step | Status transitions: PENDING → PROCESSING → (callback) → result stored |
| 7.15 | 24-hour backstop for stuck PROCESSING | High | 1. ScheduleJobRunUser remains PROCESSING for >24h | Background scheduler marks it FAILED automatically |

## Group 8: Callback (Response from External Service)

| # | Test Case | Priority | Steps | Expected Result |
|---|-----------|----------|-------|-----------------|
| 8.1 | Successful callback with result | High | 1. External service sends POST callback with status="success", result.homePage | ScheduleJobRunUser.run.process.status = FINISHED; result stored |
| 8.2 | Failed callback | High | 1. External service sends callback with status="fail", failReason | ScheduleJobRunUser.run.process.status = FAILED; failReason stored |
| 8.3 | Callback echoes correct ID | High | 1. Callback payload contains id matching scheduleJobRunUserId | System matches and updates correct ScheduleJobRunUser record |
| 8.4 | Callback with invalid/missing ID | High | 1. Callback with unrecognized id | HTTP 400 returned; no record updated |
| 8.5 | Callback authorization (X-API-KEY) | High | 1. Callback request includes correct X-API-KEY header | Request accepted and processed |
| 8.6 | Callback with wrong API key | High | 1. Callback with incorrect X-API-KEY | HTTP 401 returned; no retry by EkoAI |
| 8.7 | Callback timeout handling | High | 1. External service never sends callback within configured timeout | EkoAI treats as failure; retries up to retry times then FAILED |
| 8.8 | Callback after ID already FINISHED | Medium | 1. Send callback for already SUCCESS/FAILED user | HTTP 200 returned (idempotent); data not overwritten |
| 8.9 | Callback includes quotaConsumed | Medium | 1. Callback has quotaConsumed=5 | EkoAI charges the network accordingly |
| 8.10 | Callback result.homePage stored | High | 1. Callback with result.homePage content | run.process.result.homePage populated in ScheduleJobRunUser |

## Group 9: Action Step — Delivery Orchestration

| # | Test Case | Priority | Steps | Expected Result |
|---|-----------|----------|-------|-----------------|
| 9.1 | Immediate delivery — orchestrator picks up candidates | High | 1. Action schedule is null 2. Process step completes for a user | On next orchestrator scan, user with PENDING action + populated result is picked up |
| 9.2 | Time-triggered delivery — waits until nextRun | High | 1. Action schedule.nextRun = tomorrow 09:00 2. Process completes today | User waits in PENDING until 09:00; orchestrator picks up at/after that time |
| 9.3 | Time-triggered — process data arrives late (after nextRun) | High | 1. Action schedule.nextRun = 09:00 2. Process completes at 10:00 | nextRun is already past; orchestrator picks up immediately on next scan |
| 9.4 | Action queue message published | High | 1. Orchestrator identifies delivery candidate | Message published to action queue with scheduleJobRunUserId, actionType, etc. |
| 9.5 | Action worker claims and processes | High | 1. Worker consumes queue message | Worker executes delivery (e.g., create HomePage via Eko API), claims using optimistic concurrency |
| 9.6 | Action worker commits user status | High | 1. Worker completes delivery | ScheduleJobRunUser.run.actions.homePage.status = SUCCESS |
| 9.7 | Action worker aggregates run status | High | 1. All users for a run complete their actions | ScheduleJobRun.status updated to SUCCESS or FAILED based on aggregation |
| 9.8 | Duplicate queue messages handled | High | 1. Orchestrator publishes same candidate twice | Worker uses optimistic concurrency (_etag); only one succeeds, other retries and sees terminal status |
| 9.9 | Dead-letter queue for undeliverable messages | Medium | 1. Action queue message fails all retry attempts | Message moves to dead-letter queue; alerting triggered |
| 9.10 | Action FAILED — failReasonCode stored | High | 1. Delivery fails (Eko API unavailable) | run.actions.homePage.status = FAILED; failReasonCode + failReasonMessage stored |
| 9.11 | Partial success — some users succeed, some fail | High | 1. Run with 10 users; 7 succeed, 3 fail | Per-user statuses correctly reflect SUCCESS or FAILED; run status = PARTIAL_SUCCESS or FAILED |

## Group 10: Cutoff Timeout

| # | Test Case | Priority | Steps | Expected Result |
|---|-----------|----------|-------|-----------------|
| 10.1 | Cutoff orchestrator scans timed-out runs | High | 1. ScheduleJobRun.startedAt > 24h ago, status still PROCESSING | Cutoff orchestrator identifies run and enqueues to cutoff queue |
| 10.2 | Cutoff worker marks stuck users FAILED | High | 1. Cutoff worker processes a timed-out run | All non-terminal ScheduleJobRunUser marked FAILED with failReasonCode = CUTOFF_TIMEOUT |
| 10.3 | Job deduplication via scheduledJobRunId | Medium | 1. Cutoff orchestrator runs twice for same run | BullMQ silently ignores duplicate job IDs; only one cutoff worker job processes |
| 10.4 | Cutoff vs. action worker race condition | High | 1. Action worker completes at exact moment cutoff fires | _etag optimistic concurrency: whoever writes first wins; loser retries and sees terminal state |
| 10.5 | Cutoff threshold configurable | Medium | 1. Set SCHEDULED_JOB_RUN_CUTOFF_TIMEOUT_MINUTES=60 | Cutoff fires after 60 minutes instead of default 24 hours |
| 10.6 | Cutoff worker is idempotent | Medium | 1. Cutoff worker crashes mid-way, BullMQ retries | Worker skips already-terminal users; no duplicate failures |
| 10.7 | Already terminal users not affected by cutoff | High | 1. Run has mix of SUCCESS and PROCESSING users after 24h | Only PROCESSING users are marked FAILED; SUCCESS users unchanged |

## Group 11: Home Page Delivery (Morning Brief Actions)

| # | Test Case | Priority | Steps | Expected Result |
|---|-----------|----------|-------|-----------------|
| 11.1 | Create new HomePage record | High | 1. Action worker delivers Morning Brief for a user | New HomePage record created via POST /api/v1/home-page with content.blocks, refId, expiresAt |
| 11.2 | Multiple records per user per day allowed | High | 1. Two different job runs deliver to same user on same day | Two separate HomePage records exist; getLatest returns the newest by createdAt |
| 11.3 | Retry uses update (PUT) not create | High | 1. Same job run re-delivers to a user | Uses PUT /api/v1/home-page/:id with homePageId from run.actions.homePage.id |
| 11.4 | expiresAt set to createdAt + 24h | High | 1. Create a HomePage record | expiresAt = createdAt + 24 hours; after expiry, widget not shown on home screen |
| 11.5 | getLatest returns most recent non-expired | High | 1. User has multiple HomePage records, some expired | v0/homePage.getLatest returns latest non-expired sorted by createdAt desc |
| 11.6 | Push notification on create | High | 1. HomePage record created for user | PushNotificationService dispatches HOME_PAGE_DELIVERED notification |
| 11.7 | Push notification on update | Medium | 1. HomePage record updated (retry) | PushNotificationService dispatches HOME_PAGE_UPDATED notification |
| 11.8 | Real-time event on delivery | High | 1. HomePage delivered | DeviceQueueService.scheduleEnqueue dispatches real-time event for connected users |
| 11.9 | API key authentication (EkoApiKey strategy) | High | 1. EkoAI → EkoNode/EkoCore request with x-api-key header | Request authenticated via EkoApiKey PassportJS strategy; scope checked for "home-page" |
| 11.10 | Invalid API key rejected | High | 1. Request with wrong/missing x-api-key | HTTP 401/403; request rejected |
| 11.11 | HomePage content is opaque (no server validation) | Medium | 1. Send HomePage with arbitrary content.blocks JSON | EkoNode stores content as-is without validation |
| 11.12 | readAt initially null | Medium | 1. Create HomePage record | readAt = null (unread) until user first views it |
| 11.13 | Dynamic config com.ekoapp.homepage | Medium | 1. Check dynamic config settings | Homepage settings available; used to calculate expiresAt |
| 11.14 | refId format contains run IDs | Medium | 1. Check created HomePage record | refId = `<run_id>:<run_user_id>` format |

## Group 12: Home Page Widget Rendering

| # | Test Case | Priority | Steps | Expected Result |
|---|-----------|----------|-------|-----------------|
| 12.1 | HomePage renders recognized widgets | High | 1. Create HomePage with valid widget JSON 2. Open app home screen | Widgets rendered in order they appear in the array |
| 12.2 | Unrecognized widgets are ignored | Medium | 1. Include an unknown widget type in JSON | Unknown widget silently skipped; no errors; other widgets render normally |
| 12.3 | Corrupted configuration handled gracefully | Medium | 1. Send widget with partial/invalid config | Widget renders with available config; corrupted parts ignored; no errors generated |
| 12.4 | Text Block widget renders | High | 1. Include text block widget in HomePage | Text block displayed with configured content |
| 12.5 | Progress Bar widget renders | Medium | 1. Include progress bar widget | Progress bar displayed with correct percentage |
| 12.6 | Horizontal Cards widget renders | Medium | 1. Include horizontal cards widget | Cards rendered horizontally with configured content |
| 12.7 | Widget "more" drill-down | Medium | 1. Widget has "more" object with label, pageTitle, widgets/tabs | "More" button shown; clicking navigates to next Page Level with extended content |
| 12.8 | Multiple widget levels (items in items) | Medium | 1. Configure widget with nested items hierarchy | Nested levels rendered correctly; transition UI between levels works |
| 12.9 | Widgets rendered in array order | Medium | 1. Send 3 widgets in specific order | Widgets display in exact order as listed in JSON array |
| 12.10 | Empty content.blocks | Medium | 1. Create HomePage with empty blocks array | Home screen shows no widgets; no crash or error |

## Group 13: Security & Authentication

| # | Test Case | Priority | Steps | Expected Result |
|---|-----------|----------|-------|-----------------|
| 13.1 | HMAC signature verification by external server | High | 1. External server receives request from EkoAI 2. Verify EkoAI-Signature header | Signature matches HMAC-SHA256 computed over payload with shared symmetric key |
| 13.2 | Reject request with missing signature | High | 1. External server receives request without EkoAI-Signature | Returns HTTP 401/403; request rejected |
| 13.3 | Reject request with tampered payload | High | 1. Modify request body after signing | Signature mismatch; external server rejects with 401/403 |
| 13.4 | API key stored encrypted | High | 1. Check process step config storage | apiKey is stored encrypted; not exposed in plaintext via APIs |
| 13.5 | ApiKey hash stored (SHA-256) | High | 1. Create API key for Eko integration | keyHash = SHA-256 of key; raw key shown only once at creation |
| 13.6 | ApiKey prefix for identification | Low | 1. View API key in admin UI | keyPrefix shows first 8 chars (e.g., "sak_a1b2") for identification |
| 13.7 | Revoked API key rejected | High | 1. Revoke an API key (status=revoked) 2. Use it in request | verify() fails; request rejected |
| 13.8 | API key scope enforcement | High | 1. Use API key with scope="home-page" for a different scope | Request rejected; scope doesn't match |
| 13.9 | Network-scoped API key listing | Medium | 1. List API keys for a specific networkId | Only keys belonging to that network returned |

## Group 14: Status Check Endpoint (Health Check)

| # | Test Case | Priority | Steps | Expected Result |
|---|-----------|----------|-------|-----------------|
| 14.1 | Status check returns 200 — proceed | High | 1. EkoAI calls /status-check on external endpoint 2. Returns 200 | ScheduledJobRun proceeds with audience resolution and processing |
| 14.2 | Status check returns 4xx — run FAILED | High | 1. Status check returns 400/404 | ScheduledJobRun immediately marked FAILED; no processing started |
| 14.3 | Status check returns 5xx — run FAILED | High | 1. Status check returns 500/503 | ScheduledJobRun immediately marked FAILED |
| 14.4 | Status check timeout (10s) — run FAILED | High | 1. Status check doesn't respond within 10s | ScheduledJobRun immediately marked FAILED |

## Group 15: Database & Infrastructure

| # | Test Case | Priority | Steps | Expected Result |
|---|-----------|----------|-------|-----------------|
| 15.1 | ScheduleJob CRUD operations | High | 1. Create, read, update, delete a ScheduleJob | All CRUD operations work correctly; soft-delete preserves record |
| 15.2 | ScheduleJobRun created with snapshots | High | 1. Trigger a run | scheduleJobStep + scheduleJobAudience frozen at trigger time |
| 15.3 | ScheduleJobRunUser tracks per-user execution | High | 1. Run processes a user | Record contains: run.process.status, run.process.result, run.actions.homePage.status |
| 15.4 | Network ekoConfig stores Eko connection | Medium | 1. Configure network with ekoConfig.baseUrl and ekoConfig.apiKey | Network uses these to call Eko APIs for audience resolution and actions |
| 15.5 | CosmosDB _etag optimistic concurrency | High | 1. Two workers attempt to update same ScheduleJobRunUser simultaneously | One succeeds; other gets conflict, retries, and sees updated state |
| 15.6 | BullMQ queue per run and action type | Medium | 1. Trigger a run | Dynamic queue created for this run; cleaned up after completion |
| 15.7 | Redis cleanup after run (queue.obliterate) | Medium | 1. Run completes | Orphaned Redis keys cleaned up to prevent accumulation |
| 15.8 | HomePage indexes support fast lookups | Medium | 1. Query homePage.getLatest for a user | Index on { userId, networkId, expiresAt, createdAt } enables efficient query |
| 15.9 | ApiKey indexes for verification | Medium | 1. Verify API key | Index on { keyHash, status } enables O(1) lookup |

## Group 16: Race Conditions & Concurrency

| # | Test Case | Priority | Steps | Expected Result |
|---|-----------|----------|-------|-----------------|
| 16.1 | Multi-action race — two workers finish last actions | High | 1. Two action workers complete last two actions for same user concurrently | _etag concurrency: one write succeeds, other retries and aggregates correctly |
| 16.2 | Cutoff vs. action completion race | High | 1. Action completes at exact moment cutoff processes same user | Whoever writes _etag first wins; terminal states are not overwritable |
| 16.3 | Duplicate orchestrator invocations | Medium | 1. Two orchestrator scans overlap | Workers use _etag on ScheduleJobRunUser; only one claims and processes |
| 16.4 | Cutoff worker and action worker write same record | High | 1. Simulate concurrent writes | Optimistic concurrency (CosmosDB _etag / DynamoDB version); loser retries |

## Group 17: API Endpoints

| # | Test Case | Priority | Steps | Expected Result |
|---|-----------|----------|-------|-----------------|
| 17.1 | CRUD — Create ScheduleJob | High | 1. POST to create ScheduleJob endpoint with valid payload | Job created; 201 response with job ID |
| 17.2 | CRUD — Get ScheduleJob | High | 1. GET ScheduleJob by ID | Returns full job configuration |
| 17.3 | CRUD — Update ScheduleJob | High | 1. PUT/PATCH ScheduleJob with updated fields | Job updated; nextRun recalculated if trigger changed |
| 17.4 | CRUD — Delete ScheduleJob | High | 1. DELETE ScheduleJob by ID | Soft-delete: isDeleted=true |
| 17.5 | List ScheduleJobs | Medium | 1. GET all ScheduleJobs for a network | Returns paginated list of jobs |
| 17.6 | Trigger endpoint (internal) | High | 1. POST /_internal/scheduled-job-action-orchestrator/trigger | Triggers scheduler tick; picks up due jobs |
| 17.7 | Process callback endpoint | High | 1. POST callback with run result | Processes callback, updates ScheduleJobRunUser |
| 17.8 | Get job run history | Medium | 1. GET ScheduleJobRuns for a job | Returns list of past runs with statuses |
| 17.9 | Get run user details | Medium | 1. GET ScheduleJobRunUsers for a run | Returns per-user execution details |
| 17.10 | Audience search/verification endpoint | Medium | 1. Call audience search endpoint | Returns matched Eko users based on search criteria |
| 17.11 | HomePage create endpoint | High | 1. POST /api/v1/home-page with valid payload and x-api-key | HomePage record created; 201 response |
| 17.12 | HomePage update endpoint | High | 1. PUT /api/v1/home-page/:id with updated content | HomePage record updated |
| 17.13 | HomePage getLatest (RPC) | High | 1. v0/homePage.getLatest with user session | Returns latest non-expired HomePage for authenticated user |
| 17.14 | Enable/Disable job endpoint | High | 1. PATCH job isEnabled=true/false | Job enable status toggled |
| 17.15 | Get job run stats | Medium | 1. GET stats endpoint for a job | Returns run statistics (total runs, success rate, etc.) |

---

## Summary

| Group | Name | Test Cases | High | Medium | Low |
|-------|------|------------|------|--------|-----|
| 1 | Dashboard — Job List & Filtering | 6 | 2 | 3 | 1 |
| 2 | Create Scheduled Job — Multi-Step Wizard | 13 | 8 | 5 | 0 |
| 3 | Job Configuration — View & Edit | 10 | 5 | 4 | 1 |
| 4 | Recipients (Audience Management) | 12 | 8 | 3 | 1 |
| 5 | History Logs & Job Run Tracking | 9 | 4 | 5 | 0 |
| 6 | Trigger Step — Scheduler Logic | 10 | 7 | 3 | 0 |
| 7 | Process Step — External Endpoint & Throttling | 15 | 10 | 5 | 0 |
| 8 | Callback (Response from External Service) | 10 | 7 | 3 | 0 |
| 9 | Action Step — Delivery Orchestration | 11 | 8 | 2 | 1 |
| 10 | Cutoff Timeout | 7 | 3 | 4 | 0 |
| 11 | Home Page Delivery (Morning Brief Actions) | 14 | 7 | 7 | 0 |
| 12 | Home Page Widget Rendering | 10 | 2 | 8 | 0 |
| 13 | Security & Authentication | 9 | 6 | 2 | 1 |
| 14 | Status Check Endpoint (Health Check) | 4 | 4 | 0 | 0 |
| 15 | Database & Infrastructure | 9 | 3 | 6 | 0 |
| 16 | Race Conditions & Concurrency | 4 | 3 | 1 | 0 |
| 17 | API Endpoints | 15 | 9 | 6 | 0 |
| **TOTAL** | | **168** | **96** | **67** | **5** |
