import csv

OUTFILE = "/Users/amity/Documents/Claude_QA_Agent/console-morning-brief-18.0/console-morning-brief-testcases.csv"

HEADER = [
    "Section", "Role", "Channel", "Title", "Test Data", "Preconditions",
    "Steps", "Expected Result", "Platform", "TestMethod", "Type", "P",
    "References", "Release version", "QA Responsibility"
]

SEC = "Agentic > Console Morning Brief > "

rows = [HEADER]

# ============================================================
# GROUP 1: Dashboard (9 cases)
# ============================================================
g = "Dashboard"
s = SEC + g

rows.append([s, "Admin", "Web",
    "Check scheduled jobs list should be displayed on Dashboard page",
    "At least 1 scheduled job exists",
    "Admin is logged in to EkoAI Console",
    "1. Navigate to EkoAI Console\n2. Click Morning Brief on sidebar\n3. Observe Dashboard page",
    "1. Dashboard page loads\n2. Scheduled jobs list is displayed with job name / status / next run columns\n3. Each job shows correct status badge",
    "Web", "Manual", "Smoke Test", "P1", "Dashboard", "", ""])

rows.append([s, "Admin", "Web",
    "Check empty state should be shown when no scheduled jobs exist on Dashboard",
    "No scheduled jobs in the system",
    "Admin is logged in to EkoAI Console",
    "1. Navigate to Morning Brief Dashboard\n2. Observe the page content",
    "1. Empty state illustration is displayed\n2. Message prompts user to create first job\n3. Create button is visible",
    "Web", "Manual", "Smoke Test", "P1", "Dashboard", "", ""])

rows.append([s, "Admin", "Web",
    "Check job list should be filtered correctly when selecting status filter on Dashboard",
    "Multiple jobs with different statuses (Active / Inactive)",
    "Admin is on Dashboard with multiple jobs",
    "1. Click status filter dropdown\n2. Select Active status\n3. Observe filtered results",
    "1. Only Active jobs are displayed\n2. Job count updates to match filter\n3. Inactive jobs are hidden",
    "Web", "Manual", "Sanity Test", "P2", "Dashboard", "", ""])

rows.append([s, "Admin", "Web",
    "Check job list should be sorted correctly when changing sort order on Dashboard",
    "Multiple jobs with different creation dates",
    "Admin is on Dashboard with multiple jobs",
    "1. Click sort dropdown\n2. Select sort by Created Date descending\n3. Observe list order",
    "1. Jobs are reordered by creation date (newest first)\n2. Sort indicator shows active direction",
    "Web", "Manual", "Sanity Test", "P2", "Dashboard", "", ""])

rows.append([s, "Admin", "Web",
    "Check sidebar navigation should highlight Morning Brief when Dashboard is active",
    "",
    "Admin is logged in to EkoAI Console",
    "1. Navigate to Morning Brief Dashboard\n2. Observe sidebar navigation state",
    "1. Morning Brief menu item is highlighted in sidebar\n2. Dashboard sub-item shows active state",
    "Web", "Manual", "Regression Test", "P2", "Dashboard", "", ""])

rows.append([s, "Admin", "Web",
    "Check Dashboard should handle gracefully when API returns error loading job list",
    "Backend returns 500 error on GET /scheduled-jobs",
    "Admin is logged in to EkoAI Console",
    "1. Navigate to Morning Brief Dashboard\n2. Simulate API error response\n3. Observe page behavior",
    "1. Error message is displayed to user\n2. Retry option is available\n3. Page does not crash or show blank content",
    "Web", "Manual", "Regression Test", "P1", "Dashboard", "", ""])

rows.append([s, "Admin", "Web",
    "Check Dashboard should display correct status badge colors for each job status",
    "Jobs with statuses: Active / Inactive / Processing",
    "Admin is on Dashboard with jobs in various states",
    "1. Navigate to Morning Brief Dashboard\n2. Observe status badges on each job row",
    "1. Active jobs show green badge\n2. Inactive jobs show gray badge\n3. Each badge label matches job status",
    "Web", "Manual", "Regression Test", "P2", "Dashboard", "", ""])

rows.append([s, "Admin", "Web",
    "Check Dashboard should load correctly when there are 100+ scheduled jobs",
    "100+ scheduled jobs created in the system",
    "Admin is logged in to EkoAI Console",
    "1. Navigate to Morning Brief Dashboard\n2. Scroll through the job list\n3. Observe pagination or lazy loading",
    "1. Page loads without timeout\n2. Pagination or infinite scroll is functional\n3. All jobs are accessible",
    "Web", "Manual", "Regression Test", "P1", "Dashboard", "", ""])

rows.append([s, "Admin", "Web",
    "Check Dashboard should update job list in real-time when a new job is created from another session",
    "Another admin session creates a new job",
    "Admin is on Dashboard page",
    "1. Keep Dashboard open\n2. From another session / create a new scheduled job\n3. Observe Dashboard list",
    "1. New job appears in the list without manual refresh\n2. Job shows correct initial status",
    "Web", "Manual", "Regression Test", "P2", "Dashboard", "", ""])

# ============================================================
# GROUP 2: Create Scheduled Job (13 cases)
# ============================================================
g = "Create Scheduled Job"
s = SEC + g

rows.append([s, "Admin", "Web",
    "Check Create wizard should open when clicking Create button on Dashboard",
    "",
    "Admin is on Morning Brief Dashboard",
    "1. Click Create Scheduled Job button\n2. Observe wizard dialog",
    "1. Multi-step wizard opens\n2. Step 1 (Job Name) is active\n3. Name field is focused and empty",
    "Web", "Manual", "Smoke Test", "P1", "Create Wizard", "", ""])

rows.append([s, "Admin", "Web",
    "Check job should be created successfully when all required fields are filled in wizard",
    "Job name: Test Morning Brief / Schedule: Daily at 9 AM / Process endpoint: https://api.example.com/process / Audience: 1 user group",
    "Admin is on Create wizard Step 1",
    "1. Enter job name\n2. Configure daily schedule\n3. Enter process endpoint URL\n4. Select audience group\n5. Click Create button",
    "1. Job is created successfully\n2. Success message is displayed\n3. User is redirected to Dashboard\n4. New job appears in job list",
    "Web", "Manual", "Smoke Test", "P1", "Create Wizard", "", ""])

rows.append([s, "Admin", "Web",
    "Check schedule configuration should support iCalendar RRULE format in Create wizard",
    "RRULE: FREQ=WEEKLY;BYDAY=MO / WE / FR;DTSTART=20260401T090000Z",
    "Admin is on Create wizard schedule step",
    "1. Select custom recurrence option\n2. Configure weekly schedule for Monday / Wednesday / Friday\n3. Set start date and time\n4. Observe preview",
    "1. RRULE is generated correctly\n2. Schedule preview shows next 3 occurrences\n3. Days of week are highlighted in selector",
    "Web", "Manual", "Smoke Test", "P1", "Create Wizard", "", ""])

rows.append([s, "Admin", "Web",
    "Check termination condition should be configurable when setting runUntilTimes in Create wizard",
    "runUntilTimes: 5",
    "Admin is on Create wizard schedule step",
    "1. Enable termination condition\n2. Select Run Until Times option\n3. Enter value of 5\n4. Observe validation",
    "1. Termination field accepts value 5\n2. Preview shows job will run 5 times\n3. Field validates within 1-10 range",
    "Web", "Manual", "Sanity Test", "P1", "Create Wizard", "", ""])

rows.append([s, "Admin", "Web",
    "Check termination condition should be configurable when setting endDate in Create wizard",
    "endDate: 2026-06-30",
    "Admin is on Create wizard schedule step",
    "1. Enable termination condition\n2. Select End Date option\n3. Pick date 2026-06-30\n4. Observe validation",
    "1. Date picker accepts future date\n2. Preview shows runs until end date\n3. RRULE includes UNTIL parameter",
    "Web", "Manual", "Sanity Test", "P2", "Create Wizard", "", ""])

rows.append([s, "Admin", "Web",
    "Check action mode selection should display IMMEDIATE and SCHEDULED options in Create wizard",
    "",
    "Admin is on Create wizard action step",
    "1. Navigate to action configuration step\n2. Observe action mode options",
    "1. IMMEDIATE option is displayed with description\n2. SCHEDULED option is displayed with description\n3. Default selection is IMMEDIATE",
    "Web", "Manual", "Smoke Test", "P1", "Create Wizard", "", ""])

rows.append([s, "Admin", "Web",
    "Check SCHEDULED action mode should require delivery time when selected in Create wizard",
    "",
    "Admin is on Create wizard action step",
    "1. Select SCHEDULED action mode\n2. Observe additional fields\n3. Attempt to proceed without setting time",
    "1. Delivery time picker appears\n2. Validation error shows when time is not set\n3. Cannot proceed to next step without time",
    "Web", "Manual", "Smoke Test", "P2", "Create Wizard", "", ""])

rows.append([s, "Admin", "Web",
    "Check validation error should appear when job name is empty in Create wizard",
    "Empty job name field",
    "Admin is on Create wizard Step 1",
    "1. Leave job name field empty\n2. Click Next or attempt to proceed\n3. Observe validation",
    "1. Validation error message appears below name field\n2. Field is highlighted in red\n3. User cannot proceed to next step",
    "Web", "Manual", "Regression Test", "P1", "Create Wizard", "", ""])

rows.append([s, "Admin", "Web",
    "Check validation error should appear when process endpoint URL is not HTTPS",
    "Process endpoint: http://api.example.com/process",
    "Admin is on Create wizard process step",
    "1. Enter HTTP (not HTTPS) URL in process endpoint field\n2. Attempt to proceed\n3. Observe validation",
    "1. Validation error shows HTTPS is required\n2. Field is highlighted with error state\n3. User cannot proceed with HTTP URL",
    "Web", "Manual", "Regression Test", "P1", "Create Wizard", "", ""])

rows.append([s, "Admin", "Web",
    "Check validation error should appear when audience is empty in Create wizard",
    "No users or groups selected",
    "Admin is on Create wizard audience step",
    "1. Do not select any users or groups\n2. Attempt to create job\n3. Observe validation",
    "1. Validation error shows audience is required\n2. Create button remains disabled\n3. Error message indicates at least 1 user or group needed",
    "Web", "Manual", "Regression Test", "P1", "Create Wizard", "", ""])

rows.append([s, "Admin", "Web",
    "Check validation should reject runUntilTimes when value exceeds maximum of 10",
    "runUntilTimes: 11",
    "Admin is on Create wizard schedule step with termination enabled",
    "1. Select Run Until Times option\n2. Enter value 11\n3. Observe validation",
    "1. Validation error shows maximum is 10\n2. Field shows error state\n3. Cannot proceed with invalid value",
    "Web", "Manual", "Regression Test", "P2", "Create Wizard", "", ""])

rows.append([s, "Admin", "Web",
    "Check Create wizard should handle correctly when navigating back and forth between steps",
    "Partially filled form data in each step",
    "Admin is on Create wizard with data entered in steps 1-3",
    "1. Navigate to step 3\n2. Click Back to step 2\n3. Click Back to step 1\n4. Click Next through all steps",
    "1. All previously entered data is preserved\n2. No data loss when navigating between steps\n3. Validation state is maintained",
    "Web", "Manual", "Regression Test", "P2", "Create Wizard", "", ""])

rows.append([s, "Admin", "Web",
    "Check Create wizard should prevent duplicate job names when name already exists",
    "Job name: Existing Morning Brief (already in use)",
    "Admin is on Create wizard Step 1 / a job with same name exists",
    "1. Enter a job name that already exists\n2. Attempt to proceed or create\n3. Observe validation",
    "1. Validation error shows name already exists\n2. User is prompted to choose a different name",
    "Web", "Manual", "Regression Test", "P2", "Create Wizard", "", ""])

# ============================================================
# GROUP 3: Job Configuration (11 cases)
# ============================================================
g = "Job Configuration"
s = SEC + g

rows.append([s, "Admin", "Web",
    "Check job configuration page should display all fields when opening an existing job",
    "Existing scheduled job with all fields configured",
    "Admin is logged in to EkoAI Console",
    "1. Navigate to Dashboard\n2. Click on an existing job\n3. Observe configuration page",
    "1. Job name field is populated\n2. Schedule configuration shows current RRULE\n3. Process endpoint URL is displayed\n4. Action mode is shown\n5. Audience section shows current selection",
    "Web", "Manual", "Smoke Test", "P1", "Job Configuration", "", ""])

rows.append([s, "Admin", "Web",
    "Check job name should be updated successfully when editing on configuration page",
    "New job name: Updated Morning Brief",
    "Admin is on job configuration page",
    "1. Clear existing job name\n2. Enter new job name\n3. Click Save\n4. Observe result",
    "1. Job name is updated\n2. Success message is displayed\n3. Dashboard reflects new name",
    "Web", "Manual", "Smoke Test", "P1", "Job Configuration", "", ""])

rows.append([s, "Admin", "Web",
    "Check active/inactive toggle should update job status on configuration page",
    "",
    "Admin is on configuration page of an Active job",
    "1. Click active/inactive toggle\n2. Confirm status change\n3. Observe result",
    "1. Toggle switches to Inactive state\n2. Job status updates immediately\n3. isEnabled field is set to false",
    "Web", "Manual", "Smoke Test", "P1", "Job Configuration", "", ""])

rows.append([s, "Admin", "Web",
    "Check schedule change should recalculate nextRun when RRULE is modified on configuration page",
    "Change from daily to weekly schedule",
    "Admin is on configuration page of an existing job",
    "1. Modify schedule from daily to weekly (Monday)\n2. Save configuration\n3. Observe nextRun display",
    "1. nextRun is recalculated based on new RRULE\n2. Next occurrence shows correct Monday date\n3. Schedule preview updates",
    "Web", "Manual", "Smoke Test", "P1", "Job Configuration", "", ""])

rows.append([s, "Admin", "Web",
    "Check delete confirmation dialog should appear when clicking delete button on configuration page",
    "",
    "Admin is on job configuration page",
    "1. Click Delete button\n2. Observe confirmation dialog",
    "1. Confirmation dialog appears\n2. Dialog shows job name\n3. Cancel and Confirm buttons are present",
    "Web", "Manual", "Sanity Test", "P2", "Job Configuration", "", ""])

rows.append([s, "Admin", "Web",
    "Check job should be deleted successfully when confirming deletion on configuration page",
    "",
    "Admin is on job configuration page / delete dialog is open",
    "1. Click Confirm Delete button\n2. Observe result",
    "1. Job is deleted successfully\n2. User is redirected to Dashboard\n3. Deleted job is no longer in list",
    "Web", "Manual", "Regression Test", "P1", "Job Configuration", "", ""])

rows.append([s, "Admin", "Web",
    "Check validation error should appear when saving configuration with empty required fields",
    "Job name cleared to empty",
    "Admin is on job configuration page",
    "1. Clear the job name field\n2. Click Save\n3. Observe validation",
    "1. Validation error appears for empty name\n2. Save is prevented\n3. Error message is descriptive",
    "Web", "Manual", "Regression Test", "P1", "Job Configuration", "", ""])

rows.append([s, "Admin", "Web",
    "Check configuration should reject invalid process endpoint URL format",
    "Process endpoint: not-a-valid-url",
    "Admin is on job configuration page",
    "1. Enter invalid URL in process endpoint field\n2. Click Save\n3. Observe validation",
    "1. Validation error shows invalid URL format\n2. Save is prevented\n3. Field shows error state",
    "Web", "Manual", "Regression Test", "P2", "Job Configuration", "", ""])

rows.append([s, "Admin", "Web",
    "Check configuration should handle concurrent edits when two admins edit the same job",
    "Two admin sessions with same job open",
    "Admin A and Admin B both have same job configuration open",
    "1. Admin A changes job name and saves\n2. Admin B changes schedule and saves\n3. Observe conflict handling",
    "1. Second save either shows conflict warning or merges changes\n2. No silent data loss occurs\n3. Final state is consistent",
    "Web", "Manual", "Regression Test", "P2", "Job Configuration", "", ""])

rows.append([s, "Admin", "Web",
    "Check configuration page should preserve unsaved changes when navigating away accidentally",
    "Unsaved form edits",
    "Admin has made changes on configuration page",
    "1. Modify job name\n2. Click sidebar navigation to leave page\n3. Observe browser behavior",
    "1. Unsaved changes warning appears\n2. User can choose to stay or leave\n3. Choosing stay preserves edits",
    "Web", "Manual", "Regression Test", "P2", "Job Configuration", "", ""])

rows.append([s, "Admin", "Web",
    "Check process timeout field should accept values within valid range on configuration page",
    "Timeout values: 1s / 100s / maximum",
    "Admin is on job configuration page",
    "1. Set process timeout to 1 second\n2. Save and verify\n3. Set process timeout to 100 seconds (default)\n4. Save and verify",
    "1. Both values are accepted\n2. Default shows 100s\n3. Field validates within allowed range",
    "Web", "Manual", "Regression Test", "P1", "Job Configuration", "", ""])

# ============================================================
# GROUP 4: Recipients / Audience (11 cases)
# ============================================================
g = "Recipients"
s = SEC + g

rows.append([s, "Admin", "Web",
    "Check audience table should display selected users when users are added to job",
    "2 individual users selected as audience",
    "Admin is on Recipients page of a job with users assigned",
    "1. Navigate to Recipients page\n2. Observe audience table",
    "1. Table shows 2 user rows\n2. Each row displays user name and email\n3. Total audience count shows 2",
    "Web", "Manual", "Smoke Test", "P1", "Recipients", "", ""])

rows.append([s, "Admin", "Web",
    "Check audience table should display group members when a group is added to job",
    "1 user group with 5 members",
    "Admin is on Recipients page of a job with 1 group assigned",
    "1. Navigate to Recipients page\n2. Observe audience table and group display",
    "1. Group name is displayed\n2. Member count shows 5\n3. Expandable view shows individual members",
    "Web", "Manual", "Smoke Test", "P1", "Recipients", "", ""])

rows.append([s, "Admin", "Web",
    "Check user should be added to audience when selecting from user search on Recipients page",
    "User to add: testuser@example.com",
    "Admin is on Recipients page",
    "1. Click Add User button\n2. Search for testuser@example.com\n3. Select the user\n4. Observe audience table",
    "1. User search returns matching results\n2. Selected user appears in audience table\n3. Audience count increments by 1",
    "Web", "Manual", "Smoke Test", "P1", "Recipients", "", ""])

rows.append([s, "Admin", "Web",
    "Check group should be added to audience when selecting from group search on Recipients page",
    "Group to add: QA Team (10 members)",
    "Admin is on Recipients page",
    "1. Click Add Group button\n2. Search for QA Team\n3. Select the group\n4. Observe audience table",
    "1. Group appears in audience list\n2. Member count shows 10\n3. Audience total updates",
    "Web", "Manual", "Sanity Test", "P1", "Recipients", "", ""])

rows.append([s, "Admin", "Web",
    "Check user should be removed from audience when clicking remove button on Recipients page",
    "Existing user in audience list",
    "Admin is on Recipients page with at least 1 user",
    "1. Click remove button next to a user\n2. Confirm removal\n3. Observe audience table",
    "1. User is removed from audience list\n2. Audience count decrements by 1\n3. Removed user no longer appears",
    "Web", "Manual", "Sanity Test", "P2", "Recipients", "", ""])

rows.append([s, "Admin", "Web",
    "Check audience count should display correct total when both users and groups are combined",
    "2 individual users + 1 group with 5 members = 7 total",
    "Admin is on Recipients page with mixed audience",
    "1. Add 2 individual users\n2. Add 1 group with 5 members\n3. Observe total audience count",
    "1. Total count shows 7\n2. Breakdown shows 2 users + 1 group (5 members)\n3. No duplicate counting for overlapping members",
    "Web", "Manual", "Regression Test", "P1", "Recipients", "", ""])

rows.append([s, "Admin", "Web",
    "Check audience resolution should happen at trigger time not at configuration time",
    "Group membership changes between config and trigger",
    "Admin configures job with group of 5 members / then 2 new members are added to group",
    "1. Configure job with group audience\n2. Add 2 new members to the group via Eko Platform\n3. Trigger the job\n4. Observe audience count at run time",
    "1. Job processes 7 users (5 original + 2 new)\n2. Audience was resolved at trigger time\n3. Run log shows 7 recipients",
    "API", "Manual", "Regression Test", "P1", "Recipients", "", ""])

rows.append([s, "Admin", "Web",
    "Check validation error should appear when attempting to save job with empty audience",
    "No users or groups selected",
    "Admin is on Recipients page with empty audience",
    "1. Remove all users and groups\n2. Attempt to save configuration\n3. Observe validation",
    "1. Validation error shows audience cannot be empty\n2. Save is prevented\n3. Error message is descriptive",
    "Web", "Manual", "Regression Test", "P1", "Recipients", "", ""])

rows.append([s, "Admin", "Web",
    "Check Recipients page should handle correctly when a user in audience is deactivated",
    "User in audience list has been deactivated on Eko Platform",
    "Admin is on Recipients page / one audience user is deactivated",
    "1. Navigate to Recipients page\n2. Observe deactivated user row\n3. Check job trigger behavior",
    "1. Deactivated user is marked or flagged in audience list\n2. System handles deactivated user gracefully at trigger time",
    "Web", "Manual", "Regression Test", "P2", "Recipients", "", ""])

rows.append([s, "Admin", "Web",
    "Check audience table should handle correctly when audience contains 500+ users across groups",
    "Multiple groups totaling 500+ unique users",
    "Admin is on Recipients page with large audience",
    "1. Add multiple groups totaling 500+ members\n2. Observe audience table performance\n3. Check audience count accuracy",
    "1. Table loads without timeout\n2. Pagination or virtual scrolling is functional\n3. Total count is accurate",
    "Web", "Manual", "Regression Test", "P2", "Recipients", "", ""])

rows.append([s, "Admin", "Web",
    "Check duplicate user should not be counted twice when same user exists in multiple groups",
    "User exists in Group A and Group B",
    "Admin adds both Group A and Group B to audience",
    "1. Add Group A (contains user X)\n2. Add Group B (also contains user X)\n3. Observe total audience count",
    "1. User X is not double-counted\n2. Total audience count reflects unique users only\n3. Deduplication is handled correctly",
    "Web", "Manual", "Regression Test", "P2", "Recipients", "", ""])

# ============================================================
# GROUP 5: History Logs (10 cases)
# ============================================================
g = "History Logs"
s = SEC + g

rows.append([s, "Admin", "Web",
    "Check history logs should display run records when job has been executed at least once",
    "Job with 3 completed runs",
    "Admin is logged in / job has execution history",
    "1. Navigate to job detail\n2. Click History Logs tab\n3. Observe run history table",
    "1. History table shows 3 run records\n2. Each row shows run date / status / duration\n3. Records are sorted by date descending",
    "Web", "Manual", "Smoke Test", "P1", "History Logs", "", ""])

rows.append([s, "Admin", "Web",
    "Check run status should display correct color coding for SUCCESS / FAILED / PARTIAL / PROCESSING states",
    "Runs with each status type",
    "Admin is on History Logs with mixed-status runs",
    "1. Navigate to History Logs\n2. Observe status badges for each run",
    "1. SUCCESS shows green badge\n2. FAILED shows red badge\n3. PARTIAL shows orange badge\n4. PROCESSING shows blue/spinning badge",
    "Web", "Manual", "Smoke Test", "P1", "History Logs", "", ""])

rows.append([s, "Admin", "Web",
    "Check run detail view should open when clicking on a history log entry",
    "Completed run with 10 users processed",
    "Admin is on History Logs tab",
    "1. Click on a completed run entry\n2. Observe detail view",
    "1. Detail view opens\n2. Shows per-user processing status\n3. Total / success / failed counts are displayed\n4. Timestamps are shown",
    "Web", "Manual", "Smoke Test", "P1", "History Logs", "", ""])

rows.append([s, "Admin", "Web",
    "Check failure logs should display error details when viewing a failed run in History Logs",
    "Run with 3 failed user processes",
    "Admin is on History Logs / a failed run exists",
    "1. Click on a failed run entry\n2. Observe failure details\n3. Check per-user error information",
    "1. Failure log section is visible\n2. Each failed user shows error message\n3. Error details include HTTP status and response body summary",
    "Web", "Manual", "Sanity Test", "P1", "History Logs", "", ""])

rows.append([s, "Admin", "Web",
    "Check per-user status should be visible when expanding a run detail in History Logs",
    "Run with 5 SUCCESS and 2 FAILED users",
    "Admin is on History Logs detail view",
    "1. Open run detail\n2. Observe per-user status list",
    "1. Each user shows individual status (SUCCESS or FAILED)\n2. Success count shows 5\n3. Failed count shows 2\n4. Total matches 7",
    "Web", "Manual", "Sanity Test", "P2", "History Logs", "", ""])

rows.append([s, "Admin", "Web",
    "Check History Logs should show empty state when job has never been executed",
    "Newly created job with no runs",
    "Admin is on History Logs of a new job",
    "1. Navigate to History Logs tab of a new job\n2. Observe page content",
    "1. Empty state message is displayed\n2. Message indicates no runs yet\n3. No table rows are shown",
    "Web", "Manual", "Regression Test", "P2", "History Logs", "", ""])

rows.append([s, "Admin", "Web",
    "Check History Logs should handle correctly when a run is currently in PROCESSING state",
    "Active run in progress",
    "Admin is on History Logs / a run is currently processing",
    "1. Navigate to History Logs during an active run\n2. Observe the processing run entry",
    "1. Processing run shows at top of list\n2. Status shows PROCESSING with loading indicator\n3. Run detail shows real-time per-user progress",
    "Web", "Manual", "Regression Test", "P1", "History Logs", "", ""])

rows.append([s, "Admin", "Web",
    "Check History Logs pagination should work correctly when job has 50+ run records",
    "Job with 50+ historical runs",
    "Admin is on History Logs with many records",
    "1. Navigate to History Logs\n2. Scroll or click to page 2\n3. Observe pagination behavior",
    "1. First page shows default number of records\n2. Pagination controls are visible\n3. Page 2 loads next batch of records correctly",
    "Web", "Manual", "Regression Test", "P2", "History Logs", "", ""])

rows.append([s, "Admin", "Web",
    "Check PARTIAL status should be shown correctly when a run has mixed success and failure results",
    "Run with 7 SUCCESS / 3 FAILED out of 10 users",
    "Admin is on History Logs",
    "1. Locate a run with partial completion\n2. Observe status badge\n3. Open detail view",
    "1. Run status shows PARTIAL (not SUCCESS or FAILED)\n2. Badge shows orange color\n3. Detail shows 7 success / 3 failed breakdown",
    "Web", "Manual", "Regression Test", "P1", "History Logs", "", ""])

rows.append([s, "Admin", "Web",
    "Check History Logs should display correct duration for long-running jobs that took over 1 hour",
    "Run that took 1 hour 23 minutes",
    "Admin is on History Logs with a long-running completed job",
    "1. Locate the long-running job in History Logs\n2. Observe the duration column",
    "1. Duration shows 1h 23m format (not raw milliseconds)\n2. Time format is human-readable",
    "Web", "Manual", "Regression Test", "P2", "History Logs", "", ""])

# ============================================================
# GROUP 6: Trigger Step (10 cases)
# ============================================================
g = "Trigger Step"
s = SEC + g

rows.append([s, "Admin", "API",
    "Check scheduler should trigger job when nextRun time is reached",
    "Job with nextRun set to current time",
    "Active scheduled job exists with upcoming nextRun",
    "1. Create job with nextRun in 1 minute\n2. Wait for trigger time\n3. Observe job execution",
    "1. Scheduler picks up the job at nextRun time\n2. Job run is created with PROCESSING status\n3. Audience is resolved from users[] and groups[]",
    "API", "Manual", "Smoke Test", "P1", "Trigger Step", "", ""])

rows.append([s, "Admin", "API",
    "Check nextRun should be recalculated based on RRULE after successful job execution",
    "Job with FREQ=DAILY RRULE",
    "Job has just completed a run",
    "1. Trigger a daily scheduled job\n2. After run completes / check nextRun\n3. Verify RRULE calculation",
    "1. nextRun is updated to next occurrence per RRULE\n2. Date matches expected DTSTART + RRULE calculation\n3. isEnabled remains true",
    "API", "Manual", "Smoke Test", "P1", "Trigger Step", "", ""])

rows.append([s, "Admin", "API",
    "Check job should create frozen config snapshot at trigger time",
    "Job with specific configuration",
    "Active scheduled job exists",
    "1. Trigger the job\n2. Inspect ScheduledJobRun record\n3. Verify snapshot contains config at trigger time",
    "1. Run record contains frozen copy of job config\n2. Snapshot includes RRULE / audience / process / action settings\n3. Subsequent config changes do not affect running job",
    "API", "Manual", "Sanity Test", "P1", "Trigger Step", "", ""])

rows.append([s, "Admin", "API",
    "Check RRULE with BYSETPOS should calculate correct occurrence dates for complex schedules",
    "RRULE: FREQ=MONTHLY;BYDAY=MO;BYSETPOS=1 (first Monday of each month)",
    "Job configured with complex RRULE",
    "1. Create job with first-Monday-of-month RRULE\n2. Check nextRun calculations for 3 months\n3. Verify accuracy",
    "1. nextRun correctly identifies first Monday of each month\n2. Edge cases (month starting on Monday) are handled\n3. No off-by-one errors",
    "API", "Manual", "Sanity Test", "P2", "Trigger Step", "", ""])

rows.append([s, "Admin", "API",
    "Check scheduler should NOT trigger job when isEnabled is false",
    "Inactive job with past nextRun",
    "Job exists with isEnabled=false and nextRun in the past",
    "1. Set job to inactive (isEnabled=false)\n2. Wait past the nextRun time\n3. Observe scheduler behavior",
    "1. Scheduler does not pick up the job\n2. No run record is created\n3. nextRun is not recalculated",
    "API", "Manual", "Regression Test", "P1", "Trigger Step", "", ""])

rows.append([s, "Admin", "API",
    "Check job should terminate when runUntilTimes limit is reached",
    "runUntilTimes: 3 / job has completed 3 runs",
    "Job has run exactly 3 times / runUntilTimes is set to 3",
    "1. Verify job has completed 3 runs\n2. Check job status after 3rd run\n3. Verify no 4th run is triggered",
    "1. Job is automatically disabled after 3rd run\n2. isEnabled is set to false\n3. No further runs are scheduled",
    "API", "Manual", "Regression Test", "P1", "Trigger Step", "", ""])

rows.append([s, "Admin", "API",
    "Check job should terminate when endDate is reached",
    "endDate: yesterday's date / nextRun: today",
    "Job with endDate that has passed",
    "1. Check job with expired endDate\n2. Verify scheduler behavior\n3. Check job status",
    "1. Scheduler does not trigger job past endDate\n2. Job status shows completed or disabled\n3. No new runs are created",
    "API", "Manual", "Regression Test", "P1", "Trigger Step", "", ""])

rows.append([s, "Admin", "API",
    "Check scheduler should handle correctly when RRULE generates no more occurrences",
    "RRULE with COUNT=1 and job has already run once",
    "Job with finite RRULE that has exhausted all occurrences",
    "1. Create job with RRULE COUNT=1\n2. Run once\n3. Check nextRun after completion",
    "1. nextRun is null or empty\n2. Job is disabled (no more occurrences)\n3. No error is thrown",
    "API", "Manual", "Regression Test", "P2", "Trigger Step", "", ""])

rows.append([s, "Admin", "API",
    "Check trigger should prevent concurrent execution when same job is triggered while already running",
    "Job already in PROCESSING state",
    "An active run exists for the same job",
    "1. Trigger job while a run is still PROCESSING\n2. Observe system behavior",
    "1. Second trigger is rejected or queued\n2. No duplicate run is created\n3. Active run continues unaffected",
    "API", "Manual", "Regression Test", "P1", "Trigger Step", "", ""])

rows.append([s, "Admin", "API",
    "Check trigger should handle timezone correctly when DTSTART uses different timezone offset",
    "DTSTART with UTC+7 offset / server in UTC",
    "Job with timezone-aware RRULE",
    "1. Create job with DTSTART in UTC+7\n2. Verify nextRun conversion to server timezone\n3. Check trigger accuracy",
    "1. nextRun is correctly converted to server timezone\n2. Job triggers at expected local time\n3. No DST or offset miscalculation",
    "API", "Manual", "Regression Test", "P2", "Trigger Step", "", ""])

# ============================================================
# GROUP 7: Process Step & Throttling (12 cases)
# ============================================================
g = "Process Step"
s = SEC + g

rows.append([s, "Admin", "API",
    "Check process step should dispatch individual request for each audience user to external endpoint",
    "10 users in audience / process endpoint configured",
    "Job is triggered / audience resolved to 10 users",
    "1. Trigger job with 10 audience users\n2. Monitor requests to process endpoint\n3. Verify per-user dispatch",
    "1. External endpoint receives 10 individual requests\n2. Each request contains unique user context\n3. All 10 requests are dispatched",
    "API", "Manual", "Smoke Test", "P1", "Process Step", "", ""])

rows.append([s, "Admin", "API",
    "Check process step should use slow-start adaptive throttling algorithm",
    "50 users in audience",
    "Job is triggered with large audience",
    "1. Trigger job with 50 users\n2. Monitor request dispatch timing\n3. Observe throttling pattern",
    "1. Initial requests are dispatched slowly\n2. Rate increases gradually (slow-start)\n3. No burst of all 50 requests at once",
    "API", "Manual", "Smoke Test", "P1", "Process Step", "", ""])

rows.append([s, "Admin", "API",
    "Check webhook should be sent to process endpoint with correct payload format",
    "Expected payload: POST {endpoint}/webhook with x-api-key header",
    "Job is triggered / process step is executing",
    "1. Trigger job\n2. Capture webhook request at process endpoint\n3. Verify payload structure",
    "1. Request method is POST\n2. URL is {endpoint}/webhook\n3. x-api-key header is present\n4. Payload contains user context and job metadata",
    "API", "Manual", "Smoke Test", "P1", "Process Step", "", ""])

rows.append([s, "Admin", "API",
    "Check process step should timeout after configured limit when endpoint does not respond",
    "Process endpoint configured to delay 120s / timeout set to 100s",
    "Job with process timeout of 100s",
    "1. Configure process endpoint to delay response\n2. Trigger job\n3. Wait for timeout period",
    "1. Process request times out after 100s\n2. User status is marked as FAILED\n3. Timeout error is logged",
    "API", "Manual", "Sanity Test", "P1", "Process Step", "", ""])

rows.append([s, "Admin", "API",
    "Check webhook ack timeout should fail after 10 seconds when endpoint does not acknowledge",
    "Endpoint delays ack beyond 10s",
    "Job is triggered / process step starts",
    "1. Configure endpoint to delay ack beyond 10s\n2. Trigger job\n3. Observe timeout behavior",
    "1. Webhook ack timeout occurs after 10s\n2. Request is marked for retry\n3. Error is logged with timeout reason",
    "API", "Manual", "Sanity Test", "P2", "Process Step", "", ""])

rows.append([s, "Admin", "API",
    "Check process step should retry 3 times when endpoint returns 5xx error",
    "Endpoint returns 500 Internal Server Error",
    "Job is triggered / process step hits server error",
    "1. Configure endpoint to return 500 error\n2. Trigger job\n3. Observe retry behavior",
    "1. System retries the request 3 times\n2. Each retry is logged\n3. After 3 failures / user status is FAILED",
    "API", "Manual", "Regression Test", "P1", "Process Step", "", ""])

rows.append([s, "Admin", "API",
    "Check process step should NOT retry when endpoint returns 4xx client error",
    "Endpoint returns 400 Bad Request",
    "Job is triggered / process step hits client error",
    "1. Configure endpoint to return 400 error\n2. Trigger job\n3. Observe retry behavior",
    "1. System does NOT retry the request\n2. User status is immediately marked FAILED\n3. Error response is logged",
    "API", "Manual", "Regression Test", "P1", "Process Step", "", ""])

rows.append([s, "Admin", "API",
    "Check process step should retry 3 times when endpoint times out",
    "Endpoint does not respond within timeout",
    "Job is triggered with default timeout",
    "1. Configure endpoint to not respond\n2. Trigger job\n3. Observe timeout retry behavior",
    "1. System retries 3 times after each timeout\n2. Each retry resets the timeout timer\n3. After 3 timeout failures / user status is FAILED",
    "API", "Manual", "Regression Test", "P1", "Process Step", "", ""])

rows.append([s, "Admin", "API",
    "Check process step should mark user as SUCCESS when endpoint returns 200 with valid response",
    "Endpoint returns 200 OK with valid JSON body",
    "Job is triggered / process step executing",
    "1. Configure endpoint to return 200 OK\n2. Trigger job\n3. Observe user process status",
    "1. User process status is SUCCESS\n2. Response body is stored for callback\n3. Process duration is recorded",
    "API", "Manual", "Regression Test", "P2", "Process Step", "", ""])

rows.append([s, "Admin", "API",
    "Check process step should handle correctly when audience contains 1000 users",
    "Audience with 1000 users",
    "Job is triggered with large audience",
    "1. Trigger job with 1000 user audience\n2. Monitor system resources and queue\n3. Observe completion",
    "1. All 1000 requests are dispatched via throttling\n2. BullMQ queue handles load without memory issues\n3. Run completes with all users processed",
    "API", "Manual", "Regression Test", "P1", "Process Step", "", ""])

rows.append([s, "Admin", "API",
    "Check process step should create dynamic BullMQ queue for each job run",
    "Job triggered twice in sequence",
    "Two separate job runs",
    "1. Trigger job run A\n2. After completion / trigger job run B\n3. Inspect queue names",
    "1. Run A creates its own dynamic queue\n2. Run B creates a separate dynamic queue\n3. Queues are isolated per run",
    "API", "Manual", "Regression Test", "P2", "Process Step", "", ""])

rows.append([s, "Admin", "API",
    "Check process step should handle correctly when external endpoint returns empty response body",
    "Endpoint returns 200 with empty body",
    "Job is triggered / process step executing",
    "1. Configure endpoint to return 200 with empty body\n2. Trigger job\n3. Observe handling",
    "1. User process status is SUCCESS (200 is still success)\n2. Empty response is stored without error\n3. Callback can proceed",
    "API", "Manual", "Regression Test", "P2", "Process Step", "", ""])

# ============================================================
# GROUP 8: Callback (10 cases)
# ============================================================
g = "Callback"
s = SEC + g

rows.append([s, "Admin", "API",
    "Check callback should be accepted when valid scheduled_job_api_key is provided",
    "Callback payload: id / status=success / quotaConsumed / result.homePage",
    "Job run is in PROCESSING state / callback key exists",
    "1. Send POST /v1/scheduled-jobs/runs/callback\n2. Include valid scheduled_job_api_key header\n3. Include correct payload",
    "1. Callback is accepted (200 OK)\n2. Run user status is updated to SUCCESS\n3. HomePage data from result.homePage is stored",
    "API", "Manual", "Smoke Test", "P1", "Callback", "", ""])

rows.append([s, "Admin", "API",
    "Check callback should update user status to FAILED when status is fail in payload",
    "Callback payload: id / status=fail",
    "Job run is in PROCESSING state",
    "1. Send callback with status=fail\n2. Observe user status update",
    "1. Callback is accepted\n2. User status is updated to FAILED\n3. Failure reason is stored from payload",
    "API", "Manual", "Smoke Test", "P1", "Callback", "", ""])

rows.append([s, "Admin", "API",
    "Check callback auth key should be generated when creating a new ScheduledJob",
    "",
    "No scheduled job exists yet",
    "1. Create a new ScheduledJob via API\n2. Inspect the generated callback key",
    "1. Callback key is generated in scbk_<uuid> format\n2. Key is stored with the ScheduledJob record\n3. Key is unique per job",
    "API", "Manual", "Smoke Test", "P1", "Callback", "", ""])

rows.append([s, "Admin", "API",
    "Check callback should be rejected when invalid or missing scheduled_job_api_key is provided",
    "Missing or wrong API key in header",
    "Job run is in PROCESSING state",
    "1. Send callback without scheduled_job_api_key\n2. Send callback with invalid key\n3. Observe responses",
    "1. Missing key returns 401 Unauthorized\n2. Invalid key returns 401 Unauthorized\n3. No status update occurs",
    "API", "Manual", "Regression Test", "P1", "Callback", "", ""])

rows.append([s, "Admin", "API",
    "Check callback should be rejected when run ID does not match any active run",
    "Callback with non-existent run ID",
    "No matching run exists",
    "1. Send callback with fabricated run ID\n2. Observe response",
    "1. Callback returns 404 Not Found\n2. No data is modified",
    "API", "Manual", "Regression Test", "P1", "Callback", "", ""])

rows.append([s, "Admin", "API",
    "Check callback should store quotaConsumed value when provided in payload",
    "Callback with quotaConsumed: 5",
    "Job run is in PROCESSING state",
    "1. Send callback with quotaConsumed=5\n2. Verify stored value",
    "1. quotaConsumed value is stored in run record\n2. Value matches sent payload (5)",
    "API", "Manual", "Sanity Test", "P2", "Callback", "", ""])

rows.append([s, "Admin", "API",
    "Check callback should handle correctly when same user sends callback twice for same run",
    "Duplicate callback for same user and run",
    "First callback already processed successfully",
    "1. Send callback for user A in run X (success)\n2. Send second callback for same user A in run X\n3. Observe behavior",
    "1. Second callback is handled idempotently\n2. No duplicate status records created\n3. Final status reflects latest callback",
    "API", "Manual", "Regression Test", "P1", "Callback", "", ""])

rows.append([s, "Admin", "API",
    "Check callback should handle correctly when payload contains malformed JSON",
    "Malformed JSON: {id: missing-quote}",
    "Job run is in PROCESSING state",
    "1. Send callback with invalid JSON body\n2. Observe response",
    "1. Server returns 400 Bad Request\n2. Error message indicates JSON parse failure\n3. No partial update occurs",
    "API", "Manual", "Regression Test", "P2", "Callback", "", ""])

rows.append([s, "Admin", "API",
    "Check callback should process result.homePage data when status is success",
    "Callback with result.homePage containing content blocks",
    "Job run is in PROCESSING state",
    "1. Send success callback with result.homePage data\n2. Verify HomePage record creation",
    "1. HomePage record is created with content from result.homePage\n2. refId is set to run_id:run_user_id format\n3. expiresAt is set to 24h from creation",
    "API", "Manual", "Regression Test", "P1", "Callback", "", ""])

rows.append([s, "Admin", "API",
    "Check callback should handle correctly when result.homePage is null or missing on success status",
    "Callback with status=success but no result.homePage",
    "Job run is in PROCESSING state",
    "1. Send success callback without result.homePage\n2. Observe behavior",
    "1. Callback is accepted\n2. User status is SUCCESS\n3. No HomePage record is created\n4. No error is thrown",
    "API", "Manual", "Regression Test", "P2", "Callback", "", ""])

# ============================================================
# GROUP 9: Action Step (11 cases)
# ============================================================
g = "Action Step"
s = SEC + g

rows.append([s, "Admin", "API",
    "Check IMMEDIATE action should deliver HomePage when process completes successfully",
    "Action mode: IMMEDIATE / user process status: SUCCESS",
    "Job with IMMEDIATE action mode / process completed for user",
    "1. Configure job with IMMEDIATE action mode\n2. Trigger job\n3. Process completes for a user\n4. Observe delivery",
    "1. HomePage is delivered immediately after process success\n2. No delay between process completion and delivery\n3. Push notification HOME_PAGE_DELIVERED is sent",
    "API", "Manual", "Smoke Test", "P1", "Action Step", "", ""])

rows.append([s, "Admin", "API",
    "Check SCHEDULED action should deliver HomePage at specified time",
    "Action mode: SCHEDULED / delivery time: 09:00 AM",
    "Job with SCHEDULED action mode / all users processed",
    "1. Configure job with SCHEDULED action at 09:00\n2. Trigger job and complete processing\n3. Wait until 09:00\n4. Observe delivery",
    "1. HomePage is NOT delivered immediately after processing\n2. Delivery occurs at 09:00 AM\n3. All processed users receive HomePage at scheduled time",
    "API", "Manual", "Smoke Test", "P1", "Action Step", "", ""])

rows.append([s, "Admin", "API",
    "Check push notification should be sent with HOME_PAGE_DELIVERED event on first delivery",
    "First-time HomePage delivery for user",
    "User has no existing HomePage for this run",
    "1. Complete process for a user\n2. Deliver HomePage (first time)\n3. Observe push notification",
    "1. Push notification is sent\n2. Event type is HOME_PAGE_DELIVERED\n3. Notification contains relevant HomePage info",
    "API", "Manual", "Smoke Test", "P1", "Action Step", "", ""])

rows.append([s, "Admin", "API",
    "Check push notification should be sent with HOME_PAGE_UPDATED event on retry/update delivery",
    "Same run retry for existing HomePage",
    "User already has HomePage record for this run",
    "1. Deliver initial HomePage to user\n2. Retry delivery for same run\n3. Observe push notification",
    "1. Push notification is sent\n2. Event type is HOME_PAGE_UPDATED (not DELIVERED)\n3. Existing HomePage record is updated via PUT",
    "API", "Manual", "Sanity Test", "P1", "Action Step", "", ""])

rows.append([s, "Admin", "API",
    "Check real-time event should be dispatched via DeviceQueueService with home_page event type",
    "HomePage delivery triggered",
    "User has active device connection",
    "1. Deliver HomePage to user\n2. Monitor DeviceQueueService\n3. Observe real-time event",
    "1. DeviceQueueService dispatches event\n2. Event type is home_page\n3. Event payload contains HomePage reference",
    "API", "Manual", "Regression Test", "P1", "Action Step", "", ""])

rows.append([s, "Admin", "API",
    "Check action step should skip delivery for users with FAILED process status",
    "User process status: FAILED",
    "Job with IMMEDIATE action mode / one user process failed",
    "1. Trigger job where one user process fails\n2. Observe action step for failed user",
    "1. Action step skips delivery for failed user\n2. No HomePage record created for failed user\n3. No push notification sent for failed user",
    "API", "Manual", "Regression Test", "P1", "Action Step", "", ""])

rows.append([s, "Admin", "API",
    "Check same-run retry should use PUT to update existing HomePage record",
    "Retry callback for same run_id and user_id",
    "User already has HomePage for current run",
    "1. Deliver initial HomePage\n2. Receive retry callback for same run\n3. Trigger redelivery",
    "1. Existing HomePage record is updated via PUT (not POST)\n2. Content is replaced with retry data\n3. HOME_PAGE_UPDATED notification is sent",
    "API", "Manual", "Regression Test", "P1", "Action Step", "", ""])

rows.append([s, "Admin", "API",
    "Check different-run delivery should use POST to create new HomePage record",
    "New run for same user",
    "User has HomePage from previous run",
    "1. Complete run 1 with HomePage for user\n2. Trigger run 2 for same user\n3. Deliver new HomePage",
    "1. New HomePage record is created via POST\n2. Both records coexist (append model)\n3. Each has unique refId (run_id:run_user_id)",
    "API", "Manual", "Regression Test", "P1", "Action Step", "", ""])

rows.append([s, "Admin", "API",
    "Check SCHEDULED action should handle correctly when delivery time is in the past at trigger time",
    "SCHEDULED delivery at 08:00 / job triggered at 10:00",
    "Job with SCHEDULED action / delivery time already passed",
    "1. Configure SCHEDULED action at 08:00\n2. Trigger job at 10:00\n3. Observe delivery behavior",
    "1. System handles past delivery time gracefully\n2. Either delivers immediately or queues for next day\n3. No error or silent failure",
    "API", "Manual", "Regression Test", "P2", "Action Step", "", ""])

rows.append([s, "Admin", "API",
    "Check action step should handle correctly when all users in a run have FAILED process status",
    "All 5 users in audience have FAILED status",
    "Job run with 5 users / all process steps failed",
    "1. Trigger job where all user processes fail\n2. Observe action step behavior\n3. Check final run status",
    "1. Action step has no users to deliver to\n2. Run status is set to FAILED (not PARTIAL)\n3. No HomePage records created",
    "API", "Manual", "Regression Test", "P2", "Action Step", "", ""])

rows.append([s, "Admin", "API",
    "Check action step should handle correctly when HomePage content exceeds maximum allowed size",
    "result.homePage with very large content blocks (>1MB)",
    "Job run in PROCESSING state",
    "1. Send callback with oversized homePage content\n2. Observe action step behavior",
    "1. System rejects or truncates oversized content\n2. Error is logged with size details\n3. User status reflects the failure",
    "API", "Manual", "Regression Test", "P2", "Action Step", "", ""])

# ============================================================
# GROUP 10: Cutoff Timeout (8 cases)
# ============================================================
g = "Cutoff Timeout"
s = SEC + g

rows.append([s, "Admin", "API",
    "Check cutoff should timeout stuck run after 24 hours default period",
    "Run stuck in PROCESSING for 24+ hours",
    "Job run started 24+ hours ago / still in PROCESSING",
    "1. Create a run that gets stuck in PROCESSING\n2. Wait for 24h cutoff period\n3. Observe cutoff behavior",
    "1. BullMQ cron job detects the stuck run\n2. Run status is updated to FAILED\n3. Remaining unprocessed users are marked as timed out",
    "API", "Manual", "Smoke Test", "P1", "Cutoff Timeout", "", ""])

rows.append([s, "Admin", "API",
    "Check cutoff BullMQ cron should run every 1 minute to detect stuck runs",
    "",
    "System is running with active jobs",
    "1. Monitor BullMQ cron job execution\n2. Verify interval timing",
    "1. Cutoff cron executes every 1 minute\n2. Each execution checks for runs exceeding timeout\n3. No runs are missed between intervals",
    "API", "Manual", "Smoke Test", "P1", "Cutoff Timeout", "", ""])

rows.append([s, "Admin", "API",
    "Check cutoff should use scheduledJobRunId for deduplication when processing timeouts",
    "Two cutoff checks for same stuck run",
    "Stuck run detected by consecutive cron executions",
    "1. Allow cutoff cron to detect stuck run\n2. Observe next cron execution for same run\n3. Verify deduplication",
    "1. Cutoff timeout is applied only once per run\n2. Second detection is deduplicated via scheduledJobRunId\n3. No duplicate status updates",
    "API", "Manual", "Sanity Test", "P1", "Cutoff Timeout", "", ""])

rows.append([s, "Admin", "API",
    "Check cutoff should NOT timeout a run that completes just before the 24h mark",
    "Run completes at 23h 59m",
    "Job run completing near the cutoff boundary",
    "1. Create a run that takes 23h 59m to complete\n2. Run completes just before cutoff\n3. Observe status",
    "1. Run status is SUCCESS (not timed out)\n2. Cutoff does not override completed status\n3. Completion timestamp is before cutoff check",
    "API", "Manual", "Regression Test", "P1", "Cutoff Timeout", "", ""])

rows.append([s, "Admin", "API",
    "Check cutoff should handle correctly when multiple runs are stuck simultaneously",
    "3 different runs all stuck past 24h",
    "Multiple stuck runs from different jobs",
    "1. Create 3 stuck runs from different jobs\n2. Wait for cutoff period\n3. Observe cutoff processing",
    "1. All 3 runs are detected and timed out\n2. Each run is processed independently\n3. No run is missed or double-processed",
    "API", "Manual", "Regression Test", "P1", "Cutoff Timeout", "", ""])

rows.append([s, "Admin", "API",
    "Check cutoff should apply etag-based check to prevent race condition with action completion",
    "Action completing simultaneously with cutoff check",
    "Run is completing action while cutoff cron runs",
    "1. Simulate action completion at same time as cutoff\n2. Observe etag conflict handling",
    "1. Etag check prevents conflicting updates\n2. Either action or cutoff wins based on etag\n3. No data corruption occurs",
    "API", "Manual", "Regression Test", "P1", "Cutoff Timeout", "", ""])

rows.append([s, "Admin", "API",
    "Check cutoff should only mark unprocessed users as timed out / not override completed users",
    "Run with 7 SUCCESS users and 3 still PROCESSING at cutoff",
    "Partial completion when cutoff triggers",
    "1. Create run where 7 users succeed but 3 are still processing\n2. Cutoff triggers after 24h\n3. Observe per-user status",
    "1. 7 users retain SUCCESS status\n2. 3 unprocessed users are marked as TIMED_OUT\n3. Run status is PARTIAL (not FAILED)",
    "API", "Manual", "Regression Test", "P2", "Cutoff Timeout", "", ""])

rows.append([s, "Admin", "API",
    "Check cutoff should handle correctly when Redis is temporarily unavailable during cron execution",
    "Redis connection interrupted during cutoff check",
    "BullMQ cron is running / Redis goes down",
    "1. Simulate Redis connection failure during cutoff cron\n2. Observe error handling\n3. Check next cron execution",
    "1. Cutoff cron handles Redis failure gracefully\n2. Error is logged\n3. Next cron execution retries successfully when Redis recovers",
    "API", "Manual", "Regression Test", "P2", "Cutoff Timeout", "", ""])

# ============================================================
# GROUP 11: Home Page Delivery (13 cases)
# ============================================================
g = "Home Page Delivery"
s = SEC + g

rows.append([s, "Admin", "API",
    "Check HomePage record should be created with correct schema after successful delivery",
    "Valid callback with result.homePage containing content blocks",
    "Action step delivers to user",
    "1. Deliver HomePage to user\n2. Retrieve HomePage record\n3. Verify schema",
    "1. Record contains content.blocks (Mixed/JSON)\n2. refId is set to run_id:run_user_id format\n3. expiresAt is set to 24h from creation\n4. Record is accessible via API",
    "API", "Manual", "Smoke Test", "P1", "Home Page Delivery", "", ""])

rows.append([s, "Admin", "API",
    "Check HomePage should use append model creating new record per run",
    "Two runs for same user",
    "User has HomePage from run 1",
    "1. Deliver HomePage for run 1\n2. Deliver HomePage for run 2\n3. Query all HomePage records for user",
    "1. Two separate HomePage records exist\n2. Each has unique refId\n3. No 1-per-day limit enforced\n4. Both records are accessible",
    "API", "Manual", "Smoke Test", "P1", "Home Page Delivery", "", ""])

rows.append([s, "Admin", "API",
    "Check same-run retry should PUT update existing HomePage record not create new one",
    "Retry callback for same run",
    "User has existing HomePage for current run",
    "1. Deliver initial HomePage for run X\n2. Receive retry callback for same run X\n3. Verify record count",
    "1. Only 1 HomePage record exists for this run+user\n2. Record was updated via PUT\n3. Content reflects retry data",
    "API", "Manual", "Smoke Test", "P1", "Home Page Delivery", "", ""])

rows.append([s, "Admin", "API",
    "Check HomePage expiresAt should default to 24 hours from creation",
    "HomePage record just created",
    "Fresh HomePage delivery",
    "1. Deliver HomePage\n2. Retrieve record\n3. Check expiresAt timestamp",
    "1. expiresAt is approximately 24h after creation\n2. Calculation uses default from com.ekoapp.homepage config",
    "API", "Manual", "Sanity Test", "P1", "Home Page Delivery", "", ""])

rows.append([s, "Admin", "API",
    "Check HomePage expiresAt should respect dynamic config when expiresInMinutes is changed",
    "com.ekoapp.homepage.expiresInMinutes set to 720 (12h)",
    "Dynamic config updated before delivery",
    "1. Set expiresInMinutes to 720\n2. Deliver HomePage\n3. Check expiresAt",
    "1. expiresAt is 12h from creation (not 24h)\n2. Dynamic config override is applied\n3. Other HomePage records are unaffected",
    "API", "Manual", "Sanity Test", "P2", "Home Page Delivery", "", ""])

rows.append([s, "Admin", "API",
    "Check push notification HOME_PAGE_DELIVERED should be sent on new HomePage creation",
    "First HomePage delivery for user",
    "User has no existing HomePage for this run",
    "1. Deliver HomePage to user (first time)\n2. Monitor push notifications",
    "1. HOME_PAGE_DELIVERED notification is sent\n2. Notification payload references the new HomePage\n3. User receives notification on device",
    "API", "Manual", "Regression Test", "P1", "Home Page Delivery", "", ""])

rows.append([s, "Admin", "API",
    "Check push notification HOME_PAGE_UPDATED should be sent on existing HomePage update",
    "Retry delivery for existing HomePage",
    "User already has HomePage for this run",
    "1. Update existing HomePage via retry\n2. Monitor push notifications",
    "1. HOME_PAGE_UPDATED notification is sent (not DELIVERED)\n2. Notification references the updated record",
    "API", "Manual", "Regression Test", "P1", "Home Page Delivery", "", ""])

rows.append([s, "Admin", "API",
    "Check DeviceQueueService should dispatch real-time event with home_page type on delivery",
    "HomePage delivery with active device connection",
    "User has active device session",
    "1. Deliver HomePage to user with active device\n2. Monitor DeviceQueueService events",
    "1. Event is dispatched with type home_page\n2. Event is received in real-time\n3. Payload contains HomePage reference",
    "API", "Manual", "Regression Test", "P2", "Home Page Delivery", "", ""])

rows.append([s, "Admin", "API",
    "Check HomePage record should NOT be created when callback status is fail",
    "Callback with status=fail",
    "Process step failed for user",
    "1. Send fail callback\n2. Check HomePage records for user",
    "1. No HomePage record is created\n2. User status remains FAILED\n3. No push notification sent",
    "API", "Manual", "Regression Test", "P1", "Home Page Delivery", "", ""])

rows.append([s, "Admin", "API",
    "Check expired HomePage records should not be returned in user queries",
    "HomePage with expiresAt in the past",
    "HomePage created 25 hours ago (expired)",
    "1. Wait for HomePage to expire (expiresAt < now)\n2. Query user's HomePage records\n3. Observe results",
    "1. Expired record is not returned in query\n2. Only non-expired records are visible\n3. Record may still exist in DB but filtered",
    "API", "Manual", "Regression Test", "P2", "Home Page Delivery", "", ""])

rows.append([s, "Admin", "API",
    "Check HomePage should handle correctly when content.blocks contains empty array",
    "Callback with result.homePage.content.blocks = []",
    "Valid callback with empty blocks",
    "1. Send callback with empty content blocks\n2. Verify HomePage creation",
    "1. HomePage record is created with empty blocks\n2. No rendering error occurs\n3. Record is valid but has no displayable content",
    "API", "Manual", "Regression Test", "P2", "Home Page Delivery", "", ""])

rows.append([s, "Admin", "API",
    "Check HomePage refId format should be run_id:run_user_id and be unique per record",
    "Multiple deliveries for different users in same run",
    "Run with 3 users",
    "1. Deliver HomePage to 3 users in same run\n2. Retrieve all records\n3. Compare refIds",
    "1. Each refId follows run_id:run_user_id format\n2. All 3 refIds are unique\n3. refId can be used to identify specific delivery",
    "API", "Manual", "Regression Test", "P1", "Home Page Delivery", "", ""])

rows.append([s, "Admin", "API",
    "Check HomePage delivery should handle correctly when 50 users receive delivery simultaneously",
    "50 concurrent HomePage deliveries",
    "Run with 50 users / all process steps completed",
    "1. Trigger delivery for 50 users at once\n2. Monitor record creation\n3. Verify all records",
    "1. All 50 HomePage records are created\n2. No duplicate or missing records\n3. Each record has correct refId and content",
    "API", "Manual", "Regression Test", "P1", "Home Page Delivery", "", ""])

# ============================================================
# GROUP 12: Widget Rendering (12 cases)
# ============================================================
g = "Widget Rendering"
s = SEC + g

rows.append([s, "User", "Web",
    "Check recognized widget types should render correctly when HomePage contains valid widgets",
    "HomePage with text / image / list widget types",
    "User has a HomePage with multiple recognized widgets",
    "1. Open HomePage on user device\n2. Observe widget rendering",
    "1. Text widget renders with correct content\n2. Image widget displays the image\n3. List widget shows items in order\n4. All widgets render without error",
    "Web", "Manual", "Smoke Test", "P1", "Widget Rendering", "", ""])

rows.append([s, "User", "Web",
    "Check widgets should render in array order as defined in content.blocks",
    "HomePage with 3 widgets in specific order: header / image / footer",
    "User has a HomePage with ordered widgets",
    "1. Open HomePage\n2. Verify widget display order",
    "1. Header widget appears first\n2. Image widget appears second\n3. Footer widget appears last\n4. Order matches content.blocks array index",
    "Web", "Manual", "Smoke Test", "P1", "Widget Rendering", "", ""])

rows.append([s, "User", "Web",
    "Check unrecognized widget type should be silently ignored during rendering",
    "HomePage with unknown widget type: custom_chart_v2",
    "User has a HomePage containing an unrecognized widget type",
    "1. Open HomePage with unrecognized widget\n2. Observe rendering behavior",
    "1. Unrecognized widget is skipped\n2. Other widgets render normally\n3. No error message shown to user\n4. Page layout is not broken",
    "Web", "Manual", "Sanity Test", "P1", "Widget Rendering", "", ""])

rows.append([s, "User", "Web",
    "Check corrupted widget config should be ignored without generating errors",
    "HomePage with one widget having malformed JSON structure",
    "User has a HomePage with corrupted widget config",
    "1. Open HomePage with corrupted widget\n2. Observe rendering behavior",
    "1. Corrupted widget is ignored\n2. Other valid widgets render normally\n3. No error is shown to user\n4. No crash or blank page",
    "Web", "Manual", "Sanity Test", "P2", "Widget Rendering", "", ""])

rows.append([s, "User", "Web",
    "Check nested wrapper widgets should render correctly up to maximum 3 levels deep",
    "HomePage with 3-level nested wrapper structure",
    "User has a HomePage with nested wrappers",
    "1. Open HomePage with 3-level nested widgets\n2. Observe rendering of each level",
    "1. Level 1 wrapper renders correctly\n2. Level 2 nested wrapper renders inside level 1\n3. Level 3 nested wrapper renders inside level 2\n4. All content at each level is visible",
    "Web", "Manual", "Regression Test", "P1", "Widget Rendering", "", ""])

rows.append([s, "User", "Web",
    "Check widget rendering should handle correctly when nesting exceeds 3 levels",
    "HomePage with 4-level nested wrapper structure",
    "User has a HomePage with excessive nesting",
    "1. Open HomePage with 4-level nested widgets\n2. Observe rendering behavior",
    "1. First 3 levels render correctly\n2. 4th level is either ignored or rendered flat\n3. No error or crash occurs\n4. Page remains usable",
    "Web", "Manual", "Regression Test", "P1", "Widget Rendering", "", ""])

rows.append([s, "User", "Web",
    "Check wrapper widget should enforce maximum 10 widgets per wrapper limit",
    "Wrapper with 11 child widgets",
    "User has a HomePage with wrapper containing 11 widgets",
    "1. Open HomePage with 11-widget wrapper\n2. Observe rendering behavior",
    "1. First 10 widgets render correctly\n2. 11th widget is either ignored or handled gracefully\n3. No layout overflow or crash",
    "Web", "Manual", "Regression Test", "P1", "Widget Rendering", "", ""])

rows.append([s, "User", "Web",
    "Check widget structure should include type / mode / structure / more fields",
    "Widget JSON: { type: text / mode: default / structure: {...} / more: {...} }",
    "User has a HomePage with fully structured widget",
    "1. Inspect widget JSON structure\n2. Verify all required fields are present",
    "1. Widget has type field (determines rendering)\n2. Widget has mode field\n3. Widget has structure field with content\n4. Widget has more field for expansion",
    "API", "Manual", "Regression Test", "P2", "Widget Rendering", "", ""])

rows.append([s, "User", "Web",
    "Check carousel widget should render with swipeable navigation when type is carousel",
    "HomePage with carousel widget containing 5 items",
    "User has a HomePage with carousel widget",
    "1. Open HomePage\n2. Locate carousel widget\n3. Swipe through items",
    "1. Carousel renders with first item visible\n2. Swipe navigation works between items\n3. All 5 items are accessible\n4. Indicator shows current position",
    "Web", "Manual", "Regression Test", "P2", "Widget Rendering", "", ""])

rows.append([s, "User", "Web",
    "Check widget rendering should handle correctly when content.blocks is completely empty",
    "HomePage with content.blocks = []",
    "User has a HomePage with no widgets",
    "1. Open HomePage with empty blocks\n2. Observe page rendering",
    "1. Page renders without widgets\n2. Empty state or blank content area shown\n3. No error or crash\n4. Page chrome (header / footer) still renders",
    "Web", "Manual", "Regression Test", "P2", "Widget Rendering", "", ""])

rows.append([s, "User", "Web",
    "Check widget rendering should handle correctly when a single widget has very large content payload",
    "Text widget with 10000+ characters",
    "User has a HomePage with oversized widget content",
    "1. Open HomePage with very large text widget\n2. Observe rendering and scrolling",
    "1. Widget renders without timeout\n2. Content is scrollable or truncated gracefully\n3. Other widgets are not affected\n4. Page performance remains acceptable",
    "Web", "Manual", "Regression Test", "P2", "Widget Rendering", "", ""])

rows.append([s, "User", "Web",
    "Check image widget should display placeholder when image URL is broken or returns 404",
    "Image widget with broken URL: https://example.com/missing.png",
    "User has a HomePage with image widget pointing to invalid URL",
    "1. Open HomePage with broken image widget\n2. Observe image area",
    "1. Broken image shows placeholder or fallback\n2. Other widgets render normally\n3. No error overlay on the page\n4. Layout is not broken by missing image",
    "Web", "Manual", "Regression Test", "P2", "Widget Rendering", "", ""])

# ============================================================
# GROUP 13: Security & Auth (10 cases)
# ============================================================
g = "Security"
s = SEC + g

rows.append([s, "Admin", "API",
    "Check API request should be authenticated when valid EkoApiKey is provided",
    "Valid API key with correct scope",
    "API key exists with appropriate permissions",
    "1. Send API request with valid EkoApiKey in header\n2. Observe response",
    "1. Request is authenticated successfully\n2. Response returns expected data\n3. No auth error",
    "API", "Manual", "Smoke Test", "P1", "Security", "", ""])

rows.append([s, "Admin", "API",
    "Check API request should be rejected when invalid EkoApiKey is provided",
    "Invalid or expired API key",
    "None",
    "1. Send API request with invalid API key\n2. Observe response",
    "1. Request returns 401 Unauthorized\n2. Error message indicates invalid API key\n3. No data is returned",
    "API", "Manual", "Smoke Test", "P1", "Security", "", ""])

rows.append([s, "Admin", "API",
    "Check HMAC signature should be valid when external server receives EkoAI webhook request",
    "Webhook request to process endpoint",
    "Process endpoint has HMAC verification enabled",
    "1. Trigger job with HMAC-enabled process endpoint\n2. Capture webhook request\n3. Verify HMAC signature",
    "1. x-hmac-signature header is present\n2. Signature is valid when verified with shared secret\n3. Payload matches signed content",
    "API", "Manual", "Sanity Test", "P1", "Security", "", ""])

rows.append([s, "Admin", "API",
    "Check callback endpoint should enforce scheduled_job_api_key auth independently from EkoApiKey",
    "Callback request with EkoApiKey but no scbk_ key",
    "Valid EkoApiKey exists but callback key is missing",
    "1. Send callback with valid EkoApiKey only\n2. Omit scheduled_job_api_key\n3. Observe response",
    "1. Callback returns 401 Unauthorized\n2. EkoApiKey alone is not sufficient for callbacks\n3. scbk_ key is required separately",
    "API", "Manual", "Sanity Test", "P1", "Security", "", ""])

rows.append([s, "Admin", "API",
    "Check API request should be rejected when API key scope does not match required permission",
    "API key with read-only scope / attempting write operation",
    "API key exists with limited scope",
    "1. Send POST request with read-only API key\n2. Observe response",
    "1. Request returns 403 Forbidden\n2. Error indicates insufficient scope\n3. Write operation is not executed",
    "API", "Manual", "Regression Test", "P1", "Security", "", ""])

rows.append([s, "Admin", "API",
    "Check API request should be rejected when no authentication header is provided",
    "Request without any auth header",
    "None",
    "1. Send API request without any auth header\n2. Observe response",
    "1. Request returns 401 Unauthorized\n2. Error indicates missing authentication",
    "API", "Manual", "Regression Test", "P1", "Security", "", ""])

rows.append([s, "Admin", "API",
    "Check callback key should be unique per ScheduledJob and not reusable across jobs",
    "Two different ScheduledJobs",
    "Two jobs exist with different callback keys",
    "1. Create Job A and note its scbk_ key\n2. Create Job B\n3. Attempt to use Job A key for Job B callback",
    "1. Job A and Job B have different scbk_ keys\n2. Using wrong key returns 401\n3. Each key only works for its own job",
    "API", "Manual", "Regression Test", "P1", "Security", "", ""])

rows.append([s, "Admin", "API",
    "Check PassportJS EkoApiKey strategy should handle correctly when key format is malformed",
    "Malformed key: not-a-valid-key-format",
    "None",
    "1. Send request with malformed API key\n2. Observe PassportJS handling",
    "1. Request returns 401 Unauthorized\n2. No server error or crash\n3. Error is logged for monitoring",
    "API", "Manual", "Regression Test", "P2", "Security", "", ""])

rows.append([s, "Admin", "API",
    "Check API should prevent cross-tenant data access when using valid key from different tenant",
    "Valid API key from Tenant A / accessing Tenant B data",
    "Multi-tenant setup with separate API keys",
    "1. Use Tenant A API key\n2. Request data belonging to Tenant B\n3. Observe response",
    "1. Request returns 403 or 404\n2. No Tenant B data is returned\n3. Cross-tenant isolation is enforced",
    "API", "Manual", "Regression Test", "P1", "Security", "", ""])

rows.append([s, "Admin", "API",
    "Check webhook HMAC should reject tampered payload at process endpoint",
    "Modified webhook payload with original HMAC signature",
    "Process endpoint verifies HMAC",
    "1. Capture a valid webhook request\n2. Modify the payload body\n3. Replay with original HMAC signature",
    "1. HMAC verification fails\n2. Endpoint rejects the tampered request\n3. Integrity violation is detectable",
    "API", "Manual", "Regression Test", "P2", "Security", "", ""])

# ============================================================
# GROUP 14: Status Check (8 cases)
# ============================================================
g = "Status Check"
s = SEC + g

rows.append([s, "Admin", "API",
    "Check status check should return current run status when valid job and run IDs are provided",
    "POST {endpoint}/status-check with valid IDs",
    "Job run is in PROCESSING state",
    "1. Send POST to status-check endpoint\n2. Include valid job ID and run ID\n3. Observe response",
    "1. Response returns 200 OK\n2. Status shows current run state (PROCESSING)\n3. Per-user breakdown is included",
    "API", "Manual", "Smoke Test", "P1", "Status Check", "", ""])

rows.append([s, "Admin", "API",
    "Check status check should return completed status after run finishes successfully",
    "Completed run with all users SUCCESS",
    "Job run has completed",
    "1. Send status-check for completed run\n2. Observe response",
    "1. Status shows SUCCESS\n2. All users show SUCCESS status\n3. Completion timestamp is present",
    "API", "Manual", "Smoke Test", "P1", "Status Check", "", ""])

rows.append([s, "Admin", "API",
    "Check status check should return PARTIAL status when run has mixed results",
    "Run with 7 SUCCESS / 3 FAILED",
    "Job run has completed with mixed results",
    "1. Send status-check for partially successful run\n2. Observe response",
    "1. Status shows PARTIAL\n2. Success count shows 7\n3. Failed count shows 3\n4. Per-user details are available",
    "API", "Manual", "Sanity Test", "P1", "Status Check", "", ""])

rows.append([s, "Admin", "API",
    "Check status check should return 404 when run ID does not exist",
    "Non-existent run ID",
    "None",
    "1. Send status-check with fabricated run ID\n2. Observe response",
    "1. Response returns 404 Not Found\n2. Error message indicates run not found",
    "API", "Manual", "Regression Test", "P1", "Status Check", "", ""])

rows.append([s, "Admin", "API",
    "Check status check should require authentication",
    "Status-check request without auth header",
    "None",
    "1. Send status-check without authentication\n2. Observe response",
    "1. Response returns 401 Unauthorized\n2. No run data is returned",
    "API", "Manual", "Regression Test", "P1", "Status Check", "", ""])

rows.append([s, "Admin", "API",
    "Check status check should return FAILED status when all users in run have failed",
    "Run where all 5 users failed",
    "Job run completed with all failures",
    "1. Send status-check for fully failed run\n2. Observe response",
    "1. Status shows FAILED\n2. All 5 users show FAILED status\n3. Error details are available per user",
    "API", "Manual", "Regression Test", "P2", "Status Check", "", ""])

rows.append([s, "Admin", "API",
    "Check status check should handle correctly when called rapidly in succession",
    "10 rapid status-check requests within 1 second",
    "Job run is in PROCESSING state",
    "1. Send 10 rapid status-check requests\n2. Observe all responses",
    "1. All 10 requests return valid responses\n2. No rate-limit error (unless configured)\n3. Status data is consistent across calls",
    "API", "Manual", "Regression Test", "P2", "Status Check", "", ""])

rows.append([s, "Admin", "API",
    "Check status check should return real-time progress during long-running job with 100 users",
    "Long-running job with 100 users / partial completion",
    "Job run is actively processing 100 users",
    "1. Send status-check while job is processing\n2. Check progress after 30 seconds\n3. Check again after 60 seconds",
    "1. First check shows partial progress (e.g. 20/100)\n2. Second check shows increased progress (e.g. 50/100)\n3. Per-user status updates in real-time",
    "API", "Manual", "Regression Test", "P2", "Status Check", "", ""])

# ============================================================
# GROUP 15: Database & Infra (11 cases)
# ============================================================
g = "Database and Infra"
s = SEC + g

rows.append([s, "Admin", "API",
    "Check ScheduledJob CRUD operations should work correctly on CosmosDB",
    "Standard CRUD payloads",
    "CosmosDB is the active database",
    "1. Create a ScheduledJob on CosmosDB\n2. Read the record\n3. Update a field\n4. Delete the record",
    "1. Create returns success with generated ID\n2. Read returns correct data\n3. Update reflects changes\n4. Delete removes the record",
    "API", "Manual", "Smoke Test", "P1", "Database", "", ""])

rows.append([s, "Admin", "API",
    "Check ScheduledJob CRUD operations should work correctly on DynamoDB",
    "Standard CRUD payloads",
    "DynamoDB is the active database",
    "1. Create a ScheduledJob on DynamoDB\n2. Read the record\n3. Update a field\n4. Delete the record",
    "1. Create returns success with generated ID\n2. Read returns correct data\n3. Update reflects changes\n4. Delete removes the record",
    "API", "Manual", "Smoke Test", "P1", "Database", "", ""])

rows.append([s, "Admin", "API",
    "Check repository abstraction should produce identical results for CosmosDB and DynamoDB operations",
    "Same CRUD operations on both databases",
    "Both databases are accessible",
    "1. Perform create/read/update/delete on CosmosDB\n2. Perform identical operations on DynamoDB\n3. Compare results",
    "1. Response structures are identical\n2. Data types are consistent\n3. Query ordering is the same\n4. No database-specific behavior leaks through abstraction",
    "API", "Manual", "Sanity Test", "P1", "Database", "", ""])

rows.append([s, "Admin", "API",
    "Check BullMQ dynamic queue should be created with unique name per job run",
    "Multiple job runs",
    "Redis is available for BullMQ",
    "1. Trigger run A\n2. Trigger run B\n3. Inspect Redis queue names",
    "1. Run A queue has unique name containing run ID\n2. Run B queue has different unique name\n3. Queues are isolated",
    "API", "Manual", "Sanity Test", "P2", "Database", "", ""])

rows.append([s, "Admin", "API",
    "Check Redis should clean up completed BullMQ queues after job run finishes",
    "Completed job run",
    "Job run has finished processing all users",
    "1. Complete a job run\n2. Wait for cleanup interval\n3. Check Redis for orphan queues",
    "1. Dynamic queue is cleaned up after completion\n2. Redis memory is released\n3. No orphan queues remain",
    "API", "Manual", "Regression Test", "P1", "Database", "", ""])

rows.append([s, "Admin", "API",
    "Check DynamoDB TTL should automatically remove expired records",
    "HomePage record with expired TTL",
    "DynamoDB TTL is configured on expiresAt field",
    "1. Create HomePage record with short TTL\n2. Wait for TTL expiration\n3. Verify record removal",
    "1. Record is automatically deleted after TTL\n2. Query no longer returns expired record\n3. Cleanup happens without manual intervention",
    "API", "Manual", "Regression Test", "P1", "Database", "", ""])

rows.append([s, "Admin", "API",
    "Check database should handle concurrent writes when multiple callbacks arrive simultaneously",
    "10 concurrent callbacks for same run",
    "10 users completing process at same time",
    "1. Simulate 10 concurrent callback writes\n2. Verify all writes succeed\n3. Check data integrity",
    "1. All 10 writes are processed\n2. No data corruption or lost updates\n3. Each user status is correctly recorded",
    "API", "Manual", "Regression Test", "P1", "Database", "", ""])

rows.append([s, "Admin", "API",
    "Check system should handle gracefully when Redis is temporarily unavailable",
    "Redis connection interrupted",
    "System is running normally / Redis goes down",
    "1. Simulate Redis connection failure\n2. Observe BullMQ behavior\n3. Restore Redis\n4. Observe recovery",
    "1. Error is logged when Redis is unavailable\n2. No data loss for in-progress runs\n3. System recovers when Redis comes back\n4. Queued jobs resume processing",
    "API", "Manual", "Regression Test", "P1", "Database", "", ""])

rows.append([s, "Admin", "API",
    "Check CosmosDB query should return results in consistent order for pagination",
    "Query with limit and offset for 50 records",
    "50 ScheduledJob records exist in CosmosDB",
    "1. Query page 1 (limit 10 / offset 0)\n2. Query page 2 (limit 10 / offset 10)\n3. Verify no duplicates or gaps",
    "1. Page 1 returns first 10 records\n2. Page 2 returns next 10 records\n3. No record appears in both pages\n4. Total across pages matches 50",
    "API", "Manual", "Regression Test", "P2", "Database", "", ""])

rows.append([s, "Admin", "API",
    "Check system should handle gracefully when CosmosDB request units are throttled (429)",
    "CosmosDB returns 429 Too Many Requests",
    "High load on CosmosDB partition",
    "1. Simulate CosmosDB 429 response\n2. Observe retry behavior",
    "1. System retries with backoff\n2. No data loss\n3. Request eventually succeeds\n4. 429 is logged for monitoring",
    "API", "Manual", "Regression Test", "P2", "Database", "", ""])

rows.append([s, "Admin", "API",
    "Check BullMQ should handle correctly when Redis memory is near capacity during large job run",
    "Redis at 90% memory / job with 500 users",
    "Redis memory is nearly full",
    "1. Trigger job with 500 users when Redis is near capacity\n2. Monitor queue behavior\n3. Observe error handling",
    "1. System detects memory pressure\n2. Either queues are processed in batches or error is raised\n3. No silent data loss\n4. Alert or log is generated",
    "API", "Manual", "Regression Test", "P2", "Database", "", ""])

# ============================================================
# GROUP 16: Race Conditions (7 cases)
# ============================================================
g = "Race Conditions"
s = SEC + g

rows.append([s, "Admin", "API",
    "Check etag-based update should prevent data corruption when cutoff and action complete simultaneously",
    "Cutoff timeout and last action completing at same time",
    "Run is at 24h mark / last user action is completing",
    "1. Simulate cutoff trigger at same time as final action completion\n2. Observe etag conflict resolution",
    "1. Etag check detects concurrent modification\n2. One operation succeeds / other retries or fails gracefully\n3. Final run status is consistent (not corrupted)",
    "API", "Manual", "Smoke Test", "P1", "Race Conditions", "", ""])

rows.append([s, "Admin", "API",
    "Check concurrent callbacks for different users in same run should not cause data corruption",
    "5 callbacks arriving within 100ms for different users",
    "Run with 5 users / all processes completing simultaneously",
    "1. Send 5 callbacks for different users nearly simultaneously\n2. Verify all user statuses\n3. Check run aggregate status",
    "1. All 5 user statuses are correctly updated\n2. No status is lost or overwritten\n3. Run aggregate counts match (5 success)",
    "API", "Manual", "Smoke Test", "P1", "Race Conditions", "", ""])

rows.append([s, "Admin", "API",
    "Check job config update should not affect currently running job run",
    "Config update during active run",
    "Job run is in PROCESSING state",
    "1. Start a job run\n2. While run is processing / update job configuration\n3. Observe running job behavior",
    "1. Running job uses frozen snapshot from trigger time\n2. Config changes do not affect active run\n3. Next run will use updated config",
    "API", "Manual", "Regression Test", "P1", "Race Conditions", "", ""])

rows.append([s, "Admin", "API",
    "Check scheduler should handle correctly when job is disabled while being triggered",
    "isEnabled set to false during trigger processing",
    "Job nextRun is due / admin disables job simultaneously",
    "1. At trigger time / simultaneously set isEnabled=false\n2. Observe whether run starts or is aborted",
    "1. System handles the race condition without error\n2. Either run starts (was triggered before disable) or is prevented\n3. No partial/corrupt state",
    "API", "Manual", "Regression Test", "P1", "Race Conditions", "", ""])

rows.append([s, "Admin", "API",
    "Check audience deletion should be handled when group is removed during active run",
    "Group deleted from Eko Platform during run processing",
    "Run is processing users from a group / group gets deleted",
    "1. Start run with group audience\n2. Delete the group during processing\n3. Observe per-user processing",
    "1. Already-dispatched user requests continue\n2. Not-yet-dispatched users may fail with clear error\n3. Run completes without crash",
    "API", "Manual", "Regression Test", "P1", "Race Conditions", "", ""])

rows.append([s, "Admin", "API",
    "Check HomePage PUT update should handle etag conflict when two retries arrive simultaneously",
    "Two retry callbacks for same user and run at same instant",
    "User has existing HomePage / two retry callbacks race",
    "1. Send two PUT callbacks for same user at same time\n2. Observe conflict resolution",
    "1. One PUT succeeds\n2. Second PUT either retries with new etag or fails gracefully\n3. Final record is consistent\n4. No data corruption",
    "API", "Manual", "Regression Test", "P1", "Race Conditions", "", ""])

rows.append([s, "Admin", "API",
    "Check job deletion should be handled gracefully when delete occurs during active run processing",
    "Job delete request while run is PROCESSING",
    "Active run in progress / admin deletes the job",
    "1. Start a job run\n2. While processing / delete the job\n3. Observe run behavior",
    "1. Active run either completes or is gracefully terminated\n2. No orphan records left in database\n3. No server error or crash",
    "API", "Manual", "Regression Test", "P2", "Race Conditions", "", ""])

# ============================================================
# GROUP 17: API Endpoints (12 cases)
# ============================================================
g = "API Endpoints"
s = SEC + g

rows.append([s, "Admin", "API",
    "Check GET /v1/scheduled-jobs should return paginated list of scheduled jobs",
    "10 scheduled jobs exist",
    "Admin is authenticated with valid API key",
    "1. Send GET /v1/scheduled-jobs\n2. Observe response",
    "1. Response returns 200 OK\n2. Response body contains array of jobs\n3. Pagination fields (page / limit / total) are present\n4. Jobs contain expected fields",
    "API", "Manual", "Smoke Test", "P1", "API Endpoints", "", ""])

rows.append([s, "Admin", "API",
    "Check POST /v1/scheduled-jobs should create a new scheduled job",
    "Valid payload: name / rrule / process endpoint / audience / action mode",
    "Admin is authenticated with valid API key",
    "1. Send POST /v1/scheduled-jobs with valid payload\n2. Observe response",
    "1. Response returns 201 Created\n2. Response body contains job ID\n3. Job appears in GET list\n4. scbk_ callback key is generated",
    "API", "Manual", "Smoke Test", "P1", "API Endpoints", "", ""])

rows.append([s, "Admin", "API",
    "Check GET /v1/scheduled-jobs/:id should return single job details",
    "Valid job ID",
    "Admin is authenticated / job exists",
    "1. Send GET /v1/scheduled-jobs/:id\n2. Observe response",
    "1. Response returns 200 OK\n2. Response contains all job configuration fields\n3. nextRun / isEnabled / RRULE are present",
    "API", "Manual", "Smoke Test", "P1", "API Endpoints", "", ""])

rows.append([s, "Admin", "API",
    "Check PUT /v1/scheduled-jobs/:id should update existing job configuration",
    "Updated payload: new name and schedule",
    "Admin is authenticated / job exists",
    "1. Send PUT /v1/scheduled-jobs/:id with updated fields\n2. Observe response\n3. GET the job to verify",
    "1. Response returns 200 OK\n2. Updated fields are reflected\n3. nextRun is recalculated if schedule changed",
    "API", "Manual", "Smoke Test", "P1", "API Endpoints", "", ""])

rows.append([s, "Admin", "API",
    "Check DELETE /v1/scheduled-jobs/:id should remove the job",
    "Valid job ID",
    "Admin is authenticated / job exists",
    "1. Send DELETE /v1/scheduled-jobs/:id\n2. Observe response\n3. GET the deleted job",
    "1. Response returns 200 OK or 204 No Content\n2. Subsequent GET returns 404\n3. Job no longer appears in list",
    "API", "Manual", "Smoke Test", "P1", "API Endpoints", "", ""])

rows.append([s, "Admin", "API",
    "Check POST /v1/scheduled-jobs should return 400 when required fields are missing",
    "Payload missing cron / process / audience fields",
    "Admin is authenticated with valid API key",
    "1. Send POST /v1/scheduled-jobs with incomplete payload\n2. Observe response",
    "1. Response returns 400 Bad Request\n2. Error body lists missing required fields\n3. No job is created",
    "API", "Manual", "Regression Test", "P1", "API Endpoints", "", ""])

rows.append([s, "Admin", "API",
    "Check GET /v1/scheduled-jobs/:id should return 404 when job ID does not exist",
    "Non-existent job ID",
    "Admin is authenticated with valid API key",
    "1. Send GET /v1/scheduled-jobs/:nonexistent\n2. Observe response",
    "1. Response returns 404 Not Found\n2. Error message indicates job not found",
    "API", "Manual", "Regression Test", "P1", "API Endpoints", "", ""])

rows.append([s, "Admin", "API",
    "Check POST /v1/scheduled-jobs/runs/callback should process valid callback payload",
    "Valid callback: id / status / quotaConsumed / result",
    "Job run exists / valid callback key",
    "1. Send POST /v1/scheduled-jobs/runs/callback with valid payload\n2. Observe response",
    "1. Response returns 200 OK\n2. User run status is updated\n3. Callback data is stored",
    "API", "Manual", "Regression Test", "P1", "API Endpoints", "", ""])

rows.append([s, "Admin", "API",
    "Check HomePage API should return user's active HomePage records",
    "User with 2 active HomePage records",
    "API key with read scope",
    "1. Send GET request for user's HomePage records\n2. Observe response",
    "1. Response returns 200 OK\n2. Array contains 2 active records\n3. Expired records are excluded\n4. Each record has content.blocks and refId",
    "API", "Manual", "Regression Test", "P2", "API Endpoints", "", ""])

rows.append([s, "Admin", "API",
    "Check API should return 405 Method Not Allowed when using wrong HTTP method",
    "GET request to callback endpoint (expects POST)",
    "Admin is authenticated",
    "1. Send GET /v1/scheduled-jobs/runs/callback\n2. Observe response",
    "1. Response returns 405 Method Not Allowed\n2. Error indicates POST is required",
    "API", "Manual", "Regression Test", "P2", "API Endpoints", "", ""])

rows.append([s, "Admin", "API",
    "Check API pagination should handle correctly when requesting page beyond total results",
    "page=100 when only 10 jobs exist",
    "Admin is authenticated / 10 jobs exist",
    "1. Send GET /v1/scheduled-jobs?page=100\n2. Observe response",
    "1. Response returns 200 OK\n2. Empty array in results\n3. Total count still shows 10\n4. No error thrown",
    "API", "Manual", "Regression Test", "P2", "API Endpoints", "", ""])

rows.append([s, "Admin", "API",
    "Check API should handle correctly when request body exceeds maximum allowed size",
    "POST body with 10MB payload",
    "Admin is authenticated",
    "1. Send POST /v1/scheduled-jobs with oversized body\n2. Observe response",
    "1. Response returns 413 Payload Too Large or 400\n2. Error message indicates size limit\n3. No server crash",
    "API", "Manual", "Regression Test", "P2", "API Endpoints", "", ""])

# ============================================================
# VALIDATION + WRITE
# ============================================================

# Write CSV
with open(OUTFILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f, quoting=csv.QUOTE_ALL)
    writer.writerows(rows)

# Validate
STEPS_COL = 6
EXPECTED_COL = 7

with open(OUTFILE, 'r', encoding='utf-8') as f:
    read_rows = list(csv.reader(f))

bad_cols = [(i+1, len(r)) for i, r in enumerate(read_rows) if len(r) != 15]
comma_cells = []
newline_wrong_col = []
for i, r in enumerate(read_rows[1:], 2):
    for j, cell in enumerate(r):
        if ',' in cell:
            comma_cells.append((i, j, cell[:60]))
        if ('\n' in cell or '\r' in cell) and j not in (STEPS_COL, EXPECTED_COL):
            newline_wrong_col.append((i, j))

# Count per group
from collections import Counter
sections = Counter()
types = Counter()
priorities = Counter()
for r in read_rows[1:]:
    group = r[0].split('>')[-1].strip()
    sections[group] += 1
    types[r[10]] += 1
    priorities[r[11]] += 1

print("=== CSV Validation Results ===")
print(f"Total test cases: {len(read_rows)-1}")
print(f"Column count errors: {bad_cols if bad_cols else 'NONE'}")
print(f"Embedded commas: {len(comma_cells)} found")
if comma_cells:
    for row, col, preview in comma_cells[:5]:
        print(f"  Row {row} Col {col}: {preview}")
print(f"Newlines in wrong columns: {newline_wrong_col if newline_wrong_col else 'NONE'}")
print()
print("=== Per-Group Counts ===")
for s, c in sorted(sections.items(), key=lambda x: -x[1]):
    print(f"  {s}: {c}")
print()
print("=== Type Distribution ===")
for t, c in types.items():
    print(f"  {t}: {c}")
print()
print("=== Priority Distribution ===")
for p, c in priorities.items():
    print(f"  {p}: {c}")

assert not bad_cols, f"FAIL: Column count errors: {bad_cols}"
assert not comma_cells, f"FAIL: Embedded commas found: {comma_cells}"
assert not newline_wrong_col, f"FAIL: Newlines in wrong columns: {newline_wrong_col}"
print()
print("PASS: All validations passed")
