# Test Plan: SharePoint KM + User Auth Connections

> **Feature**: SharePoint KM Integration + User Auth Connections (Agent-Initiated Sign-In)
> **Sprint**: agentic-sharepoint-km
> **Date**: 2026-03-27
> **Epic**: AE-14305

---

## Sources

| # | Document | Description |
|---|----------|-------------|
| 1 | Spec 1: SharePoint as KM Source — RAG Integration (ASAP side) | Managed resource auto-creation / ETL sync / Delta Sync / Permission enforcement / Ingest & Message endpoints |
| 2 | Spec 2: SharePoint KM Search — EkoAI Integration | sharepoint_km tool / File Preview / MCP tool / Eko FE rendering |
| 3 | Spec 3: User Auth Connections — Agent-Initiated Sign-In | OAuth PKCE flow / AUTH_REQUIRED signal / Token storage & refresh / Disconnect |

---

## Scope

### In Scope

- Managed KM resource and SYSTEM_SHAREPOINT_KM assistant auto-creation when `sharepointConfig.enabled=true`
- ETL content sync: PDF / DOCX / CSV / JPEG / PNG ingestion into Google Discovery Engine
- Delta Sync via Graph API delta query and deltaToken persistence
- 410 Gone handling and full resync fallback
- Permission enforcement: hybrid Option A (Graph Search BM25 intersection) + Option B (per-doc fallback)
- Database constraint relaxation: `(networkId, managed=true, source)` unique key
- `POST /api/v1/ingest/external/sharepoint/entity-changes` endpoint (API Key auth)
- `POST /api/v1/messages/sharepoint-km/text` endpoint (SSE streaming)
- `sharepoint_km_tool.ts` in EkoAI — AUTH_REQUIRED early return / token retrieval
- `useSharepointKm` force invocation flag
- `get_sharepoint_km_data` MCP tool
- File Preview endpoint: `GET /v1/connections/sharepoint/file-preview`
- `<sharepoint_km>` XML tag rendering in Eko FE as document cards with embedded iframe preview
- OAuth PKCE flow: `/authorize` → IdP redirect → `/callback` → token storage
- `AUTH_REQUIRED` signal interception in `tool_agent.ts` and `<auth_required>` XML surfacing
- AES-256-GCM token encryption in `user-auth-connections` Cosmos collection
- Token refresh (silent) and `invalid_grant` handling
- `DELETE /v1/auth/connections/:provider` disconnect
- `GET /v1/auth/connections` status endpoint

### Out of Scope

- PPTX / XLS / HTML file ingestion (pending PM decision)
- SharePoint permission sync (intentionally excluded by design — stale permissions handled at query-time)
- Automatic teardown of managed KM resources when `sharepointConfig.enabled=false`
- Eko Library limit enforcement logic (existing feature, not changed by this spec)
- Google Discovery Engine internals and ranking algorithm
- Azure Logic App scheduling infrastructure
- Provider OAuth configurations for providers other than Microsoft

---

## Assumptions & Flagged Ambiguities

| # | Assumption / Ambiguity | Risk | Recommendation |
|---|------------------------|------|----------------|
| A1 | Files >20MB are silently skipped with no user-visible notification per spec. Unclear if ETL logs this or surfaces a warning anywhere. | Medium | Confirm with dev whether a skip event is emitted to a monitoring channel or audit log. |
| A2 | The spec states "no teardown on disable" — disabling `sharepointConfig.enabled` leaves managed KM and assistant intact. It is unclear whether the ETL sync also stops or continues running against a disabled network. | High | Clarify with dev: does the ETL sync gate on `enabled` flag at runtime? |
| A3 | `microsoftAccessToken` is described as "always present" in the `/messages/sharepoint-km/text` payload. Behavior when the token is absent or expired at this layer is not fully specified — the spec implies Graph Search will simply return empty. | Medium | Confirm error handling path at ASAP layer when token is invalid/absent. |
| A4 | PPTX / XLS / HTML are listed as "pending PM". Uploading these file types during testing — expected behavior (skip/error/queue) is not documented. | Low | Treat as out of scope; add placeholder Regression Tests marked P2. |
| A5 | State JWT TTL for OAuth PKCE is 5 minutes. No spec detail on what happens if the user completes the OAuth flow after TTL expiry (callback receives expired state). | Medium | Verify callback returns a user-friendly error and does NOT silently fail. |
| A6 | Concurrent token refresh scenario is listed as an edge case but no locking mechanism is specified. | Medium | Ask dev if there is optimistic locking or a mutex on the Cosmos record during refresh. |
| A7 | The `oauthProviders` field in the EkoAI `Network` doc is marked optional. Behavior when field is absent but a tool attempts OAuth is not explicitly described. | Medium | Confirm fallback: should return structured error to user rather than a broken sign-in URL. |

---

## Test Strategy

### Approach

- **API tests** (Channel: API) will be executed via direct HTTP calls using a REST client (Postman / curl) against a staging environment. Auth setup (API key / JWT bearer) must be configured per precondition.
- **Web tests** (Channel: Web) will be executed manually in Chrome against the staging Eko FE and EkoAI chat interface.
- **LLM/AI tests** (M1–M5 mandatory scenarios) will be executed in the EkoAI chat UI by sending natural language prompts and observing tool invocation and output.

### Priority Levels

| Priority | Definition |
|----------|------------|
| P0 | Blocker — feature cannot ship without this passing. Core happy paths and critical security controls. |
| P1 | Critical — important functionality; must pass before release. |
| P2 | Important edge cases — should pass; deferral requires PM sign-off. |

### Test Types

| Type | When Used |
|------|-----------|
| Smoke Test | Primary positive happy path (the single most important success scenario per feature area) |
| Sanity Test | Secondary positive paths confirming feature breadth |
| Regression Test | All negative tests and edge case tests |

### Environments

- **ASAP staging** — for ETL / Ingest / KM Message endpoints
- **EkoAI staging** — for sharepoint_km tool / MCP tool / File Preview / OAuth flows
- **Eko FE staging** — for UI rendering / auth UI

---

## Coverage Summary

| Section | Test Cases | P0 | P1 | P2 |
|---------|-----------|----|----|-----|
| Agentic > SharePoint KM > ASAP Integration > Managed Resource Creation | 7 | 2 | 3 | 2 |
| Agentic > SharePoint KM > ASAP Integration > ETL Content Sync | 8 | 2 | 3 | 3 |
| Agentic > SharePoint KM > ASAP Integration > Delta Sync | 8 | 2 | 3 | 3 |
| Agentic > SharePoint KM > ASAP Integration > Permission Enforcement | 8 | 2 | 3 | 3 |
| Agentic > SharePoint KM > ASAP Integration > Ingest Endpoint | 7 | 2 | 3 | 2 |
| Agentic > SharePoint KM > ASAP Integration > KM Message Endpoint | 7 | 2 | 3 | 2 |
| Agentic > SharePoint KM > EkoAI Integration > sharepoint_km Tool | 10 | 3 | 4 | 3 |
| Agentic > SharePoint KM > EkoAI Integration > File Preview | 7 | 2 | 2 | 3 |
| Agentic > SharePoint KM > EkoAI Integration > MCP Tool | 6 | 2 | 2 | 2 |
| Agentic > User Auth Connections > OAuth Sign-In | 9 | 3 | 3 | 3 |
| Agentic > User Auth Connections > AUTH_REQUIRED Signal | 8 | 2 | 3 | 3 |
| Agentic > User Auth Connections > Token Management | 8 | 2 | 3 | 3 |
| **TOTAL** | **93** | **26** | **35** | **32** |

---

## Known Gaps

| # | Gap | Impact | Mitigation |
|---|-----|--------|------------|
| G1 | No automated test coverage for Azure Logic App 15-min trigger interval — cannot be tested directly. | Medium | Manual verification that ETL runs within expected window post-deployment; monitor logs. |
| G2 | PPTX / XLS / HTML ingestion is pending PM — no acceptance criteria defined. | Low | Placeholder Regression Test cases created (P2) to be activated when spec is finalized. |
| G3 | Graph API rate limit behavior under load is not testable in staging without mocking. | Medium | Add mock-based unit test coverage at the ETL service level; note in risk log. |
| G4 | Concurrent token refresh locking behavior not specified in spec (A6 above). | Medium | Test basic concurrent scenario in staging; escalate if non-deterministic. |
| G5 | User closes browser mid-OAuth — no redirect or cleanup mechanism documented. | Low | Manual exploratory test; verify Cosmos does not persist a partial token record. |

---

## Review Actions Applied

| # | Action |
|---|--------|
| R1 | Added explicit negative test cases for each API endpoint covering missing/invalid auth headers. |
| R2 | Added `microsoftAccessToken` absent / expired scenarios to both ASAP KM Message Endpoint and EkoAI sharepoint_km Tool sections. |
| R3 | All 5 AI/LLM mandatory scenarios (M1–M5) included in sharepoint_km Tool section. |
| R4 | Edge cases explicitly called out in spec (410 Gone / >20MB files / Graph Search empty / user has no Microsoft account / provider not in config) all have dedicated test cases. |
| R5 | Database constraint relaxation tested with both same-source and different-source managed KM records per network. |
| R6 | OAuth PKCE state JWT expiry and state forgery scenarios included under OAuth Sign-In. |
| R7 | `invalid_grant` token refresh path included under Token Management with expected AUTH_REQUIRED fallback. |

---

## Test Cases

See: sharepoint-km-testcases.csv
