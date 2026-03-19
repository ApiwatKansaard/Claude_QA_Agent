# Output Templates

## 1. Bug Report Template

Use this when writing bug reports for the dev team or creating Jira issues.

```markdown
## Bug Report

**ID:** [AE-XXXX or TBD]
**Title:** [Concise description — what broke, where]
**Severity:** S1-Critical / S2-High / S3-Medium / S4-Low
**Priority:** P1 / P2 / P3 / P4
**Surface:** AI/LLM | API | Web | Mobile
**Labels:** [regression, ai-feature, api, mobile-ios, flaky, etc.]

---

### Environment
- **Build / Version:** [e.g., v2.1.0-staging, commit abc123]
- **Environment:** Staging / Production / Local
- **Browser / Device:** [e.g., Chrome 124, iPhone 15 iOS 17.4]
- **User role / account:** [e.g., Admin, Free tier user]

---

### Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Expected Result
[What should happen]

### Actual Result
[What actually happened — be specific, include error messages verbatim]

---

### Evidence
- [ ] Screenshot attached
- [ ] Video attached
- [ ] Network logs attached
- [ ] Console errors noted

---

### Additional Context
[For LLM bugs: include exact prompt, model version, run count, repro rate]
[For API bugs: include request/response payload, HTTP status code]
[For performance bugs: include latency measurements]

---

**Reported by:** [QA Engineer name]
**Date:** [YYYY-MM-DD]
**Linked story/epic:** [AE-XXXX]
```

---

## 2. Test Plan Template

Use this when creating a feature test plan document.

```markdown
# Test Plan: [Feature Name]

**Version:** 1.0
**Date:** [YYYY-MM-DD]
**Author:** [QA Lead / Engineer name]
**Sprint / Release:** [Sprint XX / vX.X.X]
**Status:** Draft / In Review / Approved

---

## 1. Scope

### In Scope
- [Feature or component being tested]
- [Specific user flows]

### Out of Scope
- [What is explicitly NOT being tested and why]

---

## 2. Test Objectives

- Verify [primary functional requirement]
- Validate [edge case or integration point]
- Ensure [non-functional requirement: performance, security, etc.]

---

## 3. Test Approach

| Surface | Approach | Tools |
|---|---|---|
| AI/LLM | Prompt testing, consistency runs, adversarial inputs | Manual + automated rubric |
| API | Contract, functional, negative, security | Postman / automated |
| Web | User journey, form validation, cross-browser | Manual + Selenium/Playwright |
| Mobile | Device matrix, OS versions, interruption testing | Manual + Appium |

---

## 4. Entry Criteria

- [ ] Feature deployed to staging environment
- [ ] Acceptance criteria defined and signed off
- [ ] Test data prepared
- [ ] Figma / Confluence spec accessible to QA

---

## 5. Exit Criteria

- [ ] All P1 test cases passed
- [ ] All P2 test cases passed or deferred with documented risk
- [ ] Zero open S1/S2 bugs
- [ ] Test results logged in TestRail
- [ ] QA sign-off provided

---

## 6. Test Cases Summary

| ID | Title | Surface | Priority | Type | Status |
|---|---|---|---|---|---|
| TC-001 | ... | Web | P1 | Functional | Pending |

[Full test cases in TestRail: [Link to TestRail suite]]

---

## 7. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| [e.g., LLM output non-determinism] | High | Medium | Run N=5 consistency checks |
| [e.g., Third-party API unavailable in staging] | Medium | High | Use mock/stub for those tests |

---

## 8. Dependencies

- [e.g., Feature flag enabled in staging]
- [e.g., Test accounts created with specific roles]
- [e.g., AI model version pinned for consistency]

---

## 9. Schedule

| Milestone | Target Date | Owner |
|---|---|---|
| Test case review | [date] | [name] |
| Test execution start | [date] | [name] |
| Test execution complete | [date] | [name] |
| QA sign-off | [date] | [name] |
```

---

## 3. QA Standup Report Template

Use this for daily QA standups. Keep it brief and action-oriented.

```markdown
## QA Standup — [Date]

### ✅ Completed Yesterday
- [Feature/ticket]: [What was done — e.g., "Completed TC-001–TC-015 for AI Chat feature. 13 passed, 2 failed (AE-4521, AE-4522 filed)"]
- [Feature/ticket]: ...

### 🔄 In Progress Today
- [Feature/ticket]: [What's being done — e.g., "Running API regression for v2.1 release. ~60% complete."]
- [Feature/ticket]: ...

### 🚧 Blockers / Risks
- [Blocker]: [e.g., "Staging environment down — API tests blocked. ETA from DevOps: 2pm"]
- [Risk]: [e.g., "AI Chat prompt change not yet deployed to staging — LLM tests not startable"]

### 📊 Bug Status (Sprint)
- Open: [N]  |  In Progress: [N]  |  Resolved: [N]
- Critical/High open: [N] (list them if >0)

### 📋 TestRail Status
- Test Suite: [Suite name] — [N/Total] cases executed — Pass rate: [X%]
```

---

## 4. Regression Checklist Template

Use this for sprint/release regression planning output.

```markdown
# Regression Checklist — [Sprint XX / Release vX.X.X]

**Date:** [YYYY-MM-DD]
**Scope:** [Full Regression / Focused Regression]
**Change Summary:** [What changed this sprint — brief, e.g., "New AI summarization feature, Auth service refactor, 3 P1 bug fixes"]

---

## Risk-Based Scope

**High Risk Areas (must test):**
- [ ] [Feature area] — reason: [why it's high risk]
- [ ] [Feature area] — reason: [direct code change]

**Medium Risk Areas (should test):**
- [ ] [Feature area] — reason: [indirect dependency]

**Low Risk / Smoke Only:**
- [ ] [Feature area] — reason: [no changes in this area]

---

## P1 Test Cases (Mandatory)

| TestRail ID | Title | Surface | Assigned To | Status |
|---|---|---|---|---|
| C1001 | ... | Web | [name] | Pending |

## P2 Test Cases (Recommended)

| TestRail ID | Title | Surface | Assigned To | Status |
|---|---|---|---|---|
| C2001 | ... | API | [name] | Pending |

---

## Estimated Effort

| Surface | Cases | Est. Time | Assignee |
|---|---|---|---|
| AI/LLM | [N] | [Xh] | [name] |
| API | [N] | [Xh] | [name] |
| Web | [N] | [Xh] | [name] |
| Mobile | [N] | [Xh] | [name] |
| **Total** | **[N]** | **[Xh]** | |

---

## Go/No-Go Criteria

- All P1 cases passed: [ ]
- Zero S1 bugs open: [ ]
- S2 bugs either fixed or risk-accepted by PM: [ ]
- TestRail results uploaded: [ ]
```
