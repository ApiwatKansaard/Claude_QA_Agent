# QA Ops Director — CTO Briefing Pack

> **Purpose:** ข้อมูลสำหรับ PM ทำ Slide Present ให้ CTO
> **Date:** 2026-03-25
> **Product:** QA Ops Director — AI-Powered QA Assistant

---

## 1. Executive Summary

QA Ops Director คือ AI QA Assistant ที่ทำงานบน VS Code + GitHub Copilot
ทำให้ QA Engineer สั่งงานทั้ง QA lifecycle ผ่าน slash command ได้ทันที
โดย AI orchestrate 5 external systems (Jira, Confluence, Figma, TestRail, Gmail/Calendar) ให้อัตโนมัติ

**Key value:** ลดงาน manual QA ที่ซ้ำซาก เพิ่ม consistency และ traceability ครบ loop

---

## 2. Problem → Solution

| # | Pain Point (Before) | Solution (After) |
|---|---|---|
| 1 | เขียน test plan จาก spec เอง — ใช้เวลา 2-4 ชม./feature | AI อ่าน Figma + Confluence → generate test plan + cases + auto-review ภายในนาที |
| 2 | Copy test cases เข้า TestRail ทีละ case — tedious, error-prone | Import ทั้ง batch ผ่าน API ตรงจาก VS Code, พร้อม diff check กับ existing cases |
| 3 | เขียน bug report ใน Jira เอง, ลืมกรอก field | AI สร้าง Jira ticket ครบทุก custom field ตาม template |
| 4 | รวบรวมข้อมูล standup / EOD เอง | AI ดึง sprint data → compile report → draft email |
| 5 | เขียน Acceptance Criteria เอง + post เอง | 10-phase pipeline: generate → AI review → fix → approve → post to Jira |
| 6 | Ticket ไม่มี AC ตกหล่น | GitHub Actions daily scan ตรวจทุกเช้า 09:00 + auto-post |
| 7 | Test plan sprint ใหม่ไม่ reference sprint เก่า | Cross-sprint memory — AI อ้าง archived data ให้ consistent |

---

## 3. Demo Flow — End-to-End Sprint QA Lifecycle

```
╔══════════════════════════════════════════════════════════════════╗
║                    SPRINT START → SPRINT END                     ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  STEP 1: Start Sprint                                           ║
║  ┌─────────────────────────────────────────────────────────┐    ║
║  │  User types: /qa:start-sprint                           │    ║
║  │  → AI checks Jira sprint board readiness                │    ║
║  │  → Creates sprint folder (agentic-18.2/)                │    ║
║  │  → Reports sprint status                                │    ║
║  └─────────────────────────────────────────────────────────┘    ║
║                          │                                       ║
║                          ▼                                       ║
║  STEP 2: Generate Test Plan (per feature)                       ║
║  ┌─────────────────────────────────────────────────────────┐    ║
║  │  User types: /qa:test-plan [Figma URL] [Confluence URL] │    ║
║  │                                                          │    ║
║  │  Phase 0: Scan archive/ for previous sprint context     │    ║
║  │  Phase 1: Fetch Figma design + Confluence spec          │    ║
║  │           → Generate test cases (AI)                    │    ║
║  │  Phase 2: AI self-review → Gap analysis report          │    ║
║  │  Phase 3: Auto-fix gaps → Final output                  │    ║
║  │                                                          │    ║
║  │  Output: {feature}-test-plan.md                         │    ║
║  │          {feature}-testcases.csv (TestRail format)      │    ║
║  └─────────────────────────────────────────────────────────┘    ║
║                          │                                       ║
║                          ▼                                       ║
║  STEP 3: Import to TestRail                                     ║
║  ┌─────────────────────────────────────────────────────────┐    ║
║  │  User types: /qa:import-testrail [TestRail suite URL]   │    ║
║  │                                                          │    ║
║  │  → Fetch existing cases from TestRail (cache locally)   │    ║
║  │  → Compare CSV vs existing → show diff                  │    ║
║  │  → User approves → Import via REST API                  │    ║
║  │  → Verify import count                                  │    ║
║  └─────────────────────────────────────────────────────────┘    ║
║                          │                                       ║
║                          ▼                                       ║
║  STEP 4: Write Acceptance Criteria                              ║
║  ┌─────────────────────────────────────────────────────────┐    ║
║  │  User types: /qa:write-ac [Sprint Board URL]            │    ║
║  │                                                          │    ║
║  │  Phase 1-3: Select tickets → Check existing AC → Read   │    ║
║  │             test plan from sprint folder                 │    ║
║  │  Phase 4-5: Fetch ticket details → Generate AC per      │    ║
║  │             ticket (mapped to test cases)                │    ║
║  │  Phase 6-7: Internal AI review → Auto-fix               │    ║
║  │  Phase 8:   User preview & approval                     │    ║
║  │  Phase 9:   Post to Jira as ADF table comments          │    ║
║  │  Phase 10:  Generate release-notes.md                   │    ║
║  └─────────────────────────────────────────────────────────┘    ║
║                          │                                       ║
║                          ▼                                       ║
║  STEP 5: Daily Operations (repeat throughout sprint)            ║
║  ┌─────────────────────────────────────────────────────────┐    ║
║  │  /qa:morning-standup → Compile QA standup from Jira     │    ║
║  │  /qa:bug-report      → Create bug tickets instantly     │    ║
║  │  /qa:bug-triage      → AI prioritize bug backlog        │    ║
║  │  /qa:eod-report      → End-of-day QA summary           │    ║
║  │                                                          │    ║
║  │  ⚡ GitHub Actions: daily AC scan (auto, 09:00 BKK)    │    ║
║  └─────────────────────────────────────────────────────────┘    ║
║                          │                                       ║
║                          ▼                                       ║
║  STEP 6: Pre-Release                                            ║
║  ┌─────────────────────────────────────────────────────────┐    ║
║  │  /qa:regression-check  → Regression checklist           │    ║
║  │  /qa:create-regression → TestRail milestone + run       │    ║
║  └─────────────────────────────────────────────────────────┘    ║
║                          │                                       ║
║                          ▼                                       ║
║  STEP 7: End Sprint                                             ║
║  ┌─────────────────────────────────────────────────────────┐    ║
║  │  User types: /qa:end-sprint                             │    ║
║  │  → Archive sprint folder to archive/                    │    ║
║  │  → Generate ARCHIVE-SUMMARY.md                          │    ║
║  │  → Ready for next sprint (data preserved for reference) │    ║
║  └─────────────────────────────────────────────────────────┘    ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## 4. Efficiency Metrics — Before vs After

### 4.1 Time Savings Per Task

| Task | Manual (Before) | With QA Ops Director | Savings |
|---|---|---|---|
| Write test plan (1 feature) | 2-4 hours | 10-15 min (AI generate + human review) | **~85-90%** |
| Write test cases (20-40 cases) | 3-5 hours | 15-20 min | **~85-90%** |
| Review test cases for gaps | 1-2 hours | 5 min (auto-review built-in) | **~90%** |
| Import cases to TestRail | 30-60 min (manual copy) | 2 min (API batch import) | **~95%** |
| Write Acceptance Criteria (10 tickets) | 2-3 hours | 15-20 min (10-phase pipeline) | **~85%** |
| Create Jira bug report | 10-15 min/bug | 2-3 min/bug | **~80%** |
| Bug triage (10 bugs) | 30-45 min | 5-10 min | **~75%** |
| Morning standup prep | 15-20 min | 2-3 min | **~85%** |
| EOD report | 10-15 min | 2-3 min | **~80%** |
| Regression checklist | 1-2 hours | 5-10 min | **~90%** |

### 4.2 Sprint-Level Impact (2-week sprint, 5 features)

| Metric | Manual | With QA Ops Director | Delta |
|---|---|---|---|
| Total test planning time | ~20-30 hrs | ~2-3 hrs | **-90%** |
| TestRail sync time | ~3-5 hrs | ~10 min | **-97%** |
| AC writing + posting | ~10-15 hrs | ~1.5-2 hrs | **-87%** |
| Bug reports created | ~10-15 hrs | ~2-3 hrs | **-80%** |
| Daily reporting overhead | ~5-7 hrs/sprint | ~1 hr/sprint | **-85%** |
| **Total QA overhead saved** | — | — | **~40-50 hrs/sprint** |

### 4.3 Quality Metrics

| Quality Dimension | Manual | With QA Ops Director |
|---|---|---|
| Test case format consistency | Varies by person | 100% consistent (template-enforced) |
| Coverage gap detection | Reviewer-dependent | Built-in AI review (Phase 2) |
| AC completeness | Often missed tickets | Daily auto-scan catches 100% |
| Bug report completeness | Fields often missing | All custom fields auto-populated |
| Cross-sprint traceability | Rarely done | Auto-referenced from archive |
| Test case ↔ Spec traceability | Manual mapping | AI maps cases to spec sections |

---

## 5. Comparison Chart — QA Ops Director vs Alternatives

### 5.1 vs Manual QA Process

| Dimension | Manual QA | QA Ops Director |
|---|---|---|
| Speed | Slow (hours per feature) | Fast (minutes per feature) |
| Consistency | Depends on individual | Template + AI enforced |
| Tool switching | Jira → TestRail → Figma → Docs | Single interface (VS Code) |
| Review quality | Peer review (async, delayed) | Built-in AI review (instant) |
| Onboarding | Days to learn all tools | 5 min setup, slash commands |
| Cost | QA engineer time | Copilot subscription (already have) |

### 5.2 vs Other QA Automation Tools

| Feature | QA Ops Director | Testim / Katalon | Zephyr / Xray | PractiTest |
|---|---|---|---|---|
| AI test generation from specs | ✅ From Figma + Confluence | ❌ Code-based only | ❌ Manual | ❌ Manual |
| AI-powered review | ✅ Built-in multi-phase | ❌ | ❌ | ❌ |
| Jira integration | ✅ Native (MCP) | ✅ Plugin | ✅ Native | ✅ Plugin |
| TestRail integration | ✅ Full CRUD API | ❌ | ❌ (competitor) | ❌ (competitor) |
| Figma design input | ✅ MCP Protocol | ❌ | ❌ | ❌ |
| Auto AC posting | ✅ + Daily CI scan | ❌ | ❌ | ❌ |
| Bug report generation | ✅ AI-powered | ❌ | ❌ | ❌ |
| IDE integration | ✅ VS Code native | Separate app | Jira plugin | Separate app |
| Additional infra needed | ❌ None (runs locally) | ✅ Cloud platform | ✅ Jira plugin | ✅ Cloud platform |
| Per-seat license cost | $0 extra (uses Copilot) | $450-$900/yr | $10-$30/user/mo | $35-$49/user/mo |
| Setup time | 5 minutes | Hours-days | Hours | Hours |

### 5.3 vs Building Custom Internal Tool

| Aspect | QA Ops Director | Custom Internal QA Tool |
|---|---|---|
| Development time | Already built | 3-6 months engineering |
| Maintenance | Skill files + prompts only | Full-stack app maintenance |
| Infrastructure | Zero (VS Code local) | Servers, DB, CI/CD, monitoring |
| AI capability | LLM-powered (Claude via Copilot) | Must integrate + pay for LLM API |
| Extensibility | Add new command file = new feature | Code new feature + deploy |
| Team adoption | Same IDE they already use | New tool to learn + maintain |
| Cost to build | QA team lead time (~2 weeks) | 1-2 engineers × 3-6 months |
| Ongoing cost | GitHub Copilot license (shared) | Server + maintenance + LLM API costs |

---

## 6. Architecture Diagram (for slide)

```
┌──────────────────────────────────────────────────────────────────────┐
│                        QA Engineer's VS Code                         │
│                                                                      │
│   ┌────────────────────────────────────────────────────────────┐    │
│   │              GitHub Copilot Chat (Agent Mode)              │    │
│   │                                                            │    │
│   │   /qa:test-plan   /qa:bug-report   /qa:write-ac   ...    │    │
│   └──────────────────────────┬─────────────────────────────────┘    │
│                              │                                       │
│   ┌──────────────────────────▼─────────────────────────────────┐    │
│   │              QA Ops Director (SKILL.md)                    │    │
│   │              ═══════════════════════════                    │    │
│   │   Orchestrator: routes commands → workflows → agents       │    │
│   │                                                            │    │
│   │   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │    │
│   │   │  Test    │ │  Bug     │ │ TestRail │ │ Report   │   │    │
│   │   │ Planner  │ │ Reporter │ │ Manager  │ │ Compiler │   │    │
│   │   │  Agent   │ │  Agent   │ │  Agent   │ │  Agent   │   │    │
│   │   └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘   │    │
│   └────────┼────────────┼────────────┼────────────┼──────────┘    │
│            │            │            │            │                │
└────────────┼────────────┼────────────┼────────────┼────────────────┘
             │            │            │            │
    ┌────────▼────┐ ┌─────▼──────┐ ┌──▼───────┐ ┌─▼──────────────┐
    │   Figma     │ │   Jira     │ │ TestRail │ │ Gmail          │
    │   (MCP)     │ │   (MCP)    │ │ (REST)   │ │ Calendar (MCP) │
    │             │ │            │ │          │ │                │
    │ • Designs   │ │ • Tickets  │ │ • Cases  │ │ • Draft emails │
    │ • Components│ │ • Bugs     │ │ • Suites │ │ • Sprint dates │
    │ • Layouts   │ │ • Sprints  │ │ • Runs   │ │                │
    │             │ │ • AC posts │ │ • Miles. │ │                │
    ├─────────────┤ ├────────────┤ ├──────────┤ ├────────────────┤
    │ Confluence  │ │            │ │          │ │ GitHub Actions │
    │ (MCP)       │ │            │ │          │ │                │
    │ • PRDs      │ │            │ │          │ │ • Daily AC     │
    │ • Tech Specs│ │            │ │          │ │   auto-scan    │
    └─────────────┘ └────────────┘ └──────────┘ └────────────────┘
```

---

## 7. Security & Compliance

| Concern | How We Handle It |
|---|---|
| Credential storage | **Zero credentials in repo** — VS Code `${input:}` prompts each user at runtime |
| Per-user isolation | Each engineer uses their own API keys (Jira, TestRail, Figma) |
| Code protection | CODEOWNERS + pre-commit hook block unauthorized infra changes |
| Data locality | All processing runs locally in VS Code — no external AI servers beyond Copilot |
| Email safety | Gmail MCP creates **drafts only** — never auto-sends; requires human confirmation |
| Audit trail | All actions go through standard APIs (Jira, TestRail) with individual user attribution |
| No new attack surface | No servers to deploy, no databases, no exposed endpoints |

---

## 8. Capabilities Matrix — 15 Commands

| # | Command | Category | Input Source | Output | AI Phases |
|---|---|---|---|---|---|
| 1 | `/qa:test-plan` | Planning | Figma + Confluence | test-plan.md + testcases.csv | 4 (Fetch→Gen→Review→Fix) |
| 2 | `/qa:review-testcases` | Planning | Existing CSV | Gap report + fixes | 2 |
| 3 | `/qa:write-ac` | Planning | Test plan + Jira sprint | AC on Jira + release-notes.md | 10 |
| 4 | `/qa:sync-testrail` | TestRail | CSV file | TestRail CSV + milestone + run | 3 |
| 5 | `/qa:fetch-testrail` | TestRail | TestRail suite URL | Cached cases for analysis | 2 |
| 6 | `/qa:import-testrail` | TestRail | CSV file | Cases in TestRail via API | 5 (Cache→Compare→Plan→Import→Verify) |
| 7 | `/qa:edit-testrail` | TestRail | Case IDs + changes | Updated cases in TestRail | 3 |
| 8 | `/qa:create-regression` | TestRail | Suite + milestone info | Regression milestone + test run | 3 |
| 9 | `/qa:bug-report` | Bugs | Bug description | Jira ticket (all custom fields) | 4 |
| 10 | `/qa:bug-triage` | Bugs | Bug list / JQL query | Prioritized bug list + recommendations | 3 |
| 11 | `/qa:regression-check` | Release | Sprint scope | Regression checklist | 2 |
| 12 | `/qa:morning-standup` | Reporting | Jira + Calendar | Standup report + email draft | 2 |
| 13 | `/qa:eod-report` | Reporting | Jira activity | EOD summary + email draft | 2 |
| 14 | `/qa:start-sprint` | Sprint Mgmt | Sprint name | Sprint folder + readiness report | 3 |
| 15 | `/qa:end-sprint` | Sprint Mgmt | Active sprint | Archive + summary | 3 |

---

## 9. ROI Summary (Talking Points for CTO)

### Cost

| Item | Cost |
|---|---|
| GitHub Copilot license | Already included in existing subscription |
| Additional infrastructure | **$0** — runs locally in VS Code |
| New tools / SaaS licenses | **$0** — integrates with existing Jira, TestRail, Figma |
| Development effort | ~2 weeks (QA team lead, one-time) |
| Ongoing maintenance | Minimal — update skill files as needed |

### Return

| Benefit | Impact |
|---|---|
| QA engineer time saved | **~40-50 hrs/sprint** across team |
| Faster test plan delivery | Tests ready on sprint day 1, not day 3-5 |
| Higher consistency | Every output follows same template + AI review |
| Better coverage | AI catches gaps humans miss; daily AC scan catches 100% tickets |
| Lower onboarding cost | New QA member productive in 5 min, not days |
| No infra maintenance | Zero servers, DBs, or deployments to manage |

### Bottom Line

> **ลงทุน:** เวลา QA Lead ~2 สัปดาห์ + Copilot license ที่มีอยู่แล้ว
>
> **ผลตอบแทน:** ประหยัดเวลา QA team ~40-50 ชม./sprint + เพิ่ม quality consistency + zero maintenance overhead

---

## 10. Appendix: Tech Stack

| Layer | Technology | Notes |
|---|---|---|
| AI Engine | GitHub Copilot (Claude LLM) | Existing license |
| Agent Framework | VS Code Agent Mode | Custom skills/commands/references |
| Integration Protocol | MCP (Model Context Protocol) | Connects LLM to external tools |
| Test Management | TestRail REST API | Full CRUD — cases, suites, milestones, runs |
| Project Tracking | Jira + Confluence (Atlassian Cloud) | Existing team tools |
| Design Source | Figma | Existing team tools |
| CI/CD | GitHub Actions | Daily automated AC scan |
| Scripts | Python 3.8+ (stdlib only) | Zero external dependencies |
| Deployment | **None** | Runs locally in each engineer's VS Code |
