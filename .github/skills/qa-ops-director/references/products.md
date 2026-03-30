# Product Registry

Default values per product. Used by `/qa-start-sprint`, `/qa-end-sprint`, and `/auto-generate` to resolve product context.

---

## How to use

When a skill needs product context, it reads `.sprint.json` first. If not found, it falls back to asking the user and then looking up defaults here.

---

## Product: agentic

| Field | Value |
|---|---|
| **Jira project** | `AE` |
| **TestRail suite** | `S3924` (`[Main] Agentic`, Eko app project ID: 1) |
| **Jira board ID** | `530` (Broccoli board) |
| **Archive path** | `archive/agentic/` |
| **E2E test path** | `tests/e2e/agentic/` |
| **API test path** | `tests/api/agentic/` |
| **Pages path** | `src/pages/agentic/` |
| **Selectors path** | `selectors/agentic/` |
| **Features** | scheduled-jobs, sharepoint-km, chat-export, ai-tasks |

---

## Product: bots

| Field | Value |
|---|---|
| **Jira project** | `BOT` |
| **TestRail suite** | *(set when first sprint starts)* |
| **Jira board ID** | *(set when first sprint starts)* |
| **Archive path** | `archive/bots/` |
| **E2E test path** | `tests/e2e/bots/` |
| **API test path** | `tests/api/bots/` |
| **Pages path** | `src/pages/bots/` |
| **Selectors path** | `selectors/bots/` |
| **Features** | *(TBD)* |

---

## Product: asap

| Field | Value |
|---|---|
| **Jira project** | `ASAP` |
| **TestRail suite** | *(set when first sprint starts)* |
| **Jira board ID** | *(set when first sprint starts)* |
| **Archive path** | `archive/asap/` |
| **E2E test path** | `tests/e2e/asap/` |
| **API test path** | `tests/api/asap/` |
| **Pages path** | `src/pages/asap/` |
| **Selectors path** | `selectors/asap/` |
| **Features** | *(TBD)* |

---

## Adding a new product

1. Add a section here with all fields filled in
2. Create `archive/{product}/` with a `.gitkeep` placeholder
3. Create matching dirs in QA_Automation: `tests/e2e/{product}/`, `tests/api/{product}/`, `src/pages/{product}/`, `selectors/{product}/`
4. On first sprint start, a `.sprint.json` will be created at the QA_Automation root
