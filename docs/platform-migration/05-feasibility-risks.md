# 05 — Feasibility Assessment & Risks

---

## Feasibility: ✅ ทำได้ 100%

ทุก integration ที่ใช้อยู่ปัจจุบัน สามารถ port ไป web backend ได้:

| Concern | Answer | Confidence |
|---|---|---|
| MCP ใช้จาก web ได้ไหม? | **ไม่ต้องใช้ MCP** — เรียก REST API ตรง | 100% |
| Jira API จาก web backend? | **ได้** — Basic Auth, same endpoints | 100% |
| TestRail API จาก web backend? | **ได้** — Basic Auth, same endpoints | 100% |
| Figma API จาก web backend? | **ได้** — Bearer token, simple REST | 100% |
| Run Playwright จาก web? | **ได้** — BullMQ worker spawns child process | 95% |
| AI features (test plan, AC)? | **ได้** — Claude API replaces Claude Code | 90% |
| Multi-user support? | **ได้** — per-user encrypted credentials | 100% |
| Real-time test progress? | **ได้** — Redis pub/sub + SSE | 95% |

---

## Risk Analysis

### 🟢 Low Risk (ทำได้เลย ไม่มีอุปสรรค)

| Risk | Mitigation |
|---|---|
| Jira/TestRail API breaking change | Version-pin API endpoints, monitor deprecation notices |
| CORS issues with external APIs | All API calls from backend (no CORS needed) |
| Credential leakage | AES-256 encryption + never return tokens to frontend |

### 🟡 Medium Risk (ต้องระวัง)

| Risk | Mitigation |
|---|---|
| **Playwright resource heavy** — each run uses 200-500MB RAM + CPU | BullMQ concurrency=1 initially, scale with Docker workers |
| **Test data isolation** — parallel runs may interfere with each other | Queue-based serial execution, environment-specific test data |
| **Cognito token refresh** — JWT expires every hour | Auth.js handles refresh automatically, add retry on 401 |
| **TestRail rate limiting** — heavy sync operations | Add delay between requests (0.3s like current Python scripts) |
| **Report accuracy** — porting Python logic to TypeScript may have subtle differences | Run both generators in parallel during migration, compare outputs |

### 🔴 High Risk (ต้องวางแผนดี)

| Risk | Mitigation |
|---|---|
| **AI feature parity** — Claude Code has full conversation context; Claude API needs structured prompts | Start with simple features (triage, classification). Complex multi-turn flows (test plan generation) need careful prompt engineering. Consider using Claude API with tool use for complex workflows. |
| **Playwright environment access** — tests need network access to staging environment from the server | Deploy worker on infrastructure that can reach `ekoai.staging.ekoapp.com`. VPN/firewall rules may be needed. |
| **User adoption** — team is used to CLI; web UI may feel different | Keep both systems running in parallel during transition. Web UI should be simpler, not harder. |

---

## Questions for the Builder

ก่อนเริ่ม dev ควรตอบคำถามเหล่านี้:

1. **Hosting:** Deploy ที่ไหน? (Vercel, AWS, on-prem Docker)
   - ถ้า Vercel → Playwright worker ต้องแยกเป็น external service (Vercel doesn't support long-running processes)
   - ถ้า AWS/Docker → ทุกอย่างอยู่ที่เดียว

2. **Database:** ใช้ managed PostgreSQL (RDS, Supabase) หรือ self-hosted?

3. **Users:** กี่คนจะใช้ platform? (4-8 QA engineers? หรือ broader team?)
   - ถ้าแค่ QA team → single-tenant, simple auth
   - ถ้า company-wide → multi-tenant, role-based access

4. **AI budget:** Claude API key + usage cost acceptable?
   - Test plan generation ใช้ ~$0.10-0.50 per generation
   - AC writing ใช้ ~$0.05-0.20 per ticket

5. **Timeline priority:** Phase 1 first? หรือจะ skip ไปทำ Phase 2 (runner + reports) ก่อน?

---

## Alternative Approaches Considered

### Option A: Full Custom (Recommended) ⭐
Build from scratch with Next.js as described above.
- **Pro:** Full control, exact feature parity, extensible
- **Con:** More dev work upfront

### Option B: Grafana + Custom Plugins
Use Grafana for dashboards, custom plugins for Jira/TestRail.
- **Pro:** Beautiful dashboards out of the box
- **Con:** Limited interactivity (can't run tests or file bugs from Grafana)

### Option C: Retool / Appsmith (Low-Code)
Use a low-code platform with custom API connectors.
- **Pro:** Fastest to prototype
- **Con:** Hard to customize deeply (risk reports, AI features), vendor lock-in

### Option D: Keep CLI + Add Web Report Viewer Only
Don't migrate the full platform — just add a web UI for viewing reports.
- **Pro:** Minimal effort
- **Con:** Doesn't solve the collaboration/multi-user problem

**Recommendation: Option A** — gives full control and best long-term value.
