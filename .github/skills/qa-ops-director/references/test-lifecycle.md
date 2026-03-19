# Test Lifecycle Reference

## API/Backend Testing Patterns

### REST API Test Case Categories

**Contract Testing**
- Verify response schema matches OpenAPI/Swagger spec
- Check required fields presence and correct types
- Test nullable vs. non-nullable field behavior

**Happy Path**
- Valid request → expected 2xx response + correct payload
- Pagination: first page, middle page, last page, empty set
- Filtering and sorting parameters behave correctly

**Negative / Error Cases**
- Missing required fields → 400 with descriptive error message
- Invalid field types → 400 with field-level validation errors
- Unauthorized access → 401 (missing token) / 403 (insufficient permissions)
- Non-existent resource → 404
- Duplicate/conflict → 409
- Rate limiting → 429 (if applicable)

**Boundary Conditions**
- Empty strings, null values, whitespace-only inputs
- Max length strings (at limit, over limit)
- Numeric: 0, negative, max int, float precision
- Date/time: past, future, timezone edge cases, DST transitions
- Array: empty, single item, max allowed items

**Security**
- SQL injection in query params and body fields
- XSS in text fields
- Mass assignment (unexpected fields accepted?)
- IDOR: can user A access user B's resources?
- Token expiry and refresh behavior

**Performance Baselines**
- P95 response time under normal load
- Behavior under concurrent requests (race conditions)
- Large payload responses (pagination working correctly?)

### GraphQL Specifics
- Test query depth limits
- Test field aliasing and introspection permissions
- Verify mutations return correct updated state
- N+1 query detection on list resolvers

---

## Regression Planning Decision Tree

```
CHANGE SURFACE ANALYSIS
│
├── Core business logic changed?
│   └── YES → Include all P1 + P2 test cases for that module
│
├── Database schema changed?
│   └── YES → Include data integrity tests, migration tests, rollback tests
│
├── API contract changed (new fields / removed fields)?
│   └── YES → Include all API contract tests + any dependent UI flows
│
├── Authentication/authorization changed?
│   └── YES → Include full auth regression suite (high priority)
│
├── AI/LLM model or prompt changed?
│   └── YES → Include LLM regression battery (see ai-llm-testing.md)
│
├── UI component library or design system changed?
│   └── YES → Cross-browser smoke tests + visual regression
│
└── Config / infrastructure only?
    └── YES → Smoke test critical paths only (P1 tests)
```

### Regression Suite Scoping

| Sprint Type | Scope |
|---|---|
| Feature sprint | P1 (new feature full), P1+P2 (affected areas) |
| Bug fix sprint | P1 smoke + affected module regression |
| Release candidate | P1+P2 full suite + P3 for high-risk areas |
| Hotfix | P1 smoke + targeted test for fix + no-regression spot check |

### Risk Multipliers (increase priority by 1 level)
- Payment or billing flows
- User data / PII handling
- Authentication flows
- Any feature used by >50% of users
- Features with recent bug history (>2 bugs in last 3 sprints)

---

## Coverage Metrics

Track and report the following coverage dimensions:

| Dimension | What it measures |
|---|---|
| Requirement coverage | % of AC / user stories with at least one test case |
| Happy path coverage | % of features with documented positive flow tests |
| Negative coverage | % of features with documented failure/error tests |
| AI surface coverage | % of LLM features with output quality tests |
| Regression coverage | % of P1+P2 cases in active regression suite |

**Healthy coverage targets:**
- Requirement coverage: ≥ 90%
- Happy path: ≥ 95%
- Negative/error: ≥ 70%
- P1 regression: 100%
- P2 regression: ≥ 85%

When reporting coverage gaps, group by: surface (AI/API/Web/Mobile), priority, and feature area.

---

## Web/Mobile Testing Patterns

### Web UI Test Priorities
1. **Critical user journeys** (P1): Login/logout, core feature flows, data submission
2. **Form validation** (P2): Required fields, format validation, error messages
3. **Navigation and routing** (P2): Deep links, back button, redirect behavior
4. **Responsive layout** (P3): Mobile/tablet breakpoints, overflow issues
5. **Cross-browser** (P3): Chrome, Safari, Firefox (as defined by team's support matrix)
6. **Accessibility** (P2-P3 depending on compliance requirements): ARIA labels, keyboard nav, contrast

### Mobile-Specific Additions
- App state after OS interruptions (calls, notifications, background/foreground)
- Offline mode behavior and reconnection
- Deep link handling
- Push notification receipt and tap-to-navigate
- Orientation change (portrait/landscape)
- Different OS versions (min supported version and latest)
