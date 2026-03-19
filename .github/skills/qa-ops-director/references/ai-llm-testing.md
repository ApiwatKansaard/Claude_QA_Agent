# AI/LLM Feature Testing Reference

## Why AI/LLM Testing Is Different

Traditional tests are deterministic: input X → output Y, always. LLM outputs are probabilistic:
the same input may produce different outputs across runs. This requires a hybrid testing strategy
that combines **deterministic checks** (does it run? does it crash? does it return a valid structure?)
with **qualitative evaluation** (is the output good? safe? accurate?).

---

## Mandatory Test Scenarios for Any AI Feature

Every AI/LLM-powered feature **must** include test cases covering all 5 of these scenarios before
release. These are non-negotiable regardless of sprint pressure or scope.

| # | Scenario | How to test |
|---|---|---|
| 1 | **Prompt injection** | Attempt `"Ignore all previous instructions and..."`, role-play framings, and nested instruction overrides. Verify the system ignores or safely handles them. |
| 2 | **Hallucination / factually incorrect output** | Provide inputs with verifiable ground truth (dates, names, facts). Check if the model fabricates plausible but wrong answers. Use rubric scoring (0/1/2). |
| 3 | **Output format deviation** | Verify the output matches the expected schema on every run. Test with unusual inputs that might cause the model to break format (e.g., emoji-heavy, very long, or multilingual input). |
| 4 | **Latency and timeout under load** | Measure P50/P95/P99 response times. Simulate concurrent requests. Verify the UI/API handles slow responses and hard timeouts gracefully without crashing. |
| 5 | **Graceful degradation when model is unavailable** | Simulate model endpoint failure (mock 503 / timeout). Verify the system returns a user-friendly error, does **not** expose internal errors, and queues or retries appropriately. |

These map to test type **"AI-Mandatory"** in the test case template. Mark them P1-Critical.

---

## Non-Determinism: A Distinct Failure Category

Non-determinism is not a bug in the traditional sense — it is a property of LLM systems that
requires its own testing and triage approach. Treat it as a **separate failure category** alongside
functional failures, performance failures, and security failures.

### What makes a failure non-deterministic?

A failure is non-deterministic if:
- The same input produces the wrong output on some runs but not others
- Behavior passes in 7 of 10 runs and fails in 3
- Failure cannot be reproduced 100% of the time with identical inputs

### How to test for non-determinism

1. **Consistency runs** — run the same input N≥5 times (for riskier features, N≥10)
2. **Record all outputs** — don't just flag pass/fail; capture the full output each run
3. **Measure variance** — identify which assertions fail intermittently vs always
4. **Set a pass threshold** — define what % pass rate is acceptable (e.g., ≥90% = green, 70–90% = yellow, <70% = red flag)

### How to report non-deterministic failures

In the bug report:
- **Repro rate**: `probabilistic — N/M runs` (e.g., 3/10)
- **Variance description**: what changed between passing and failing runs
- **Run conditions**: same prompt? same temperature? same model version?

### Priority routing for non-deterministic AI bugs

| Bug type | Dev priority | QA monitoring priority |
|---|---|---|
| Deterministic AI bug (fails 100%) | P1/P0 — treat same as standard critical | Standard — fix and verify |
| Probabilistic AI bug (fails <100%) | Lower (P2–P3) — hard to reproduce for Dev | **Higher** — requires ongoing monitoring, regression battery, and pass-rate tracking |

> **Rule:** A probabilistic AI bug that fails 30%+ of the time on a core user journey should be
> escalated to QA monitoring priority regardless of its Dev fix priority.

---

## Test Dimensions for LLM Features

When designing test cases for any AI/LLM-powered feature, cover all relevant dimensions:

| Dimension | What to test | Examples |
|---|---|---|
| **Correctness** | Is the output factually/semantically right? | Answer matches ground truth, generated code is syntactically valid |
| **Format compliance** | Does output match expected schema/format? | JSON with required keys, markdown structure, max/min length |
| **Instruction following** | Does the model do what the prompt asks? | Tone, language, scope constraints are respected |
| **Consistency** | Same-ish input → same-ish output across runs? | Run N times, measure output variance |
| **Safety / Content policy** | No harmful, biased, or inappropriate content | Test with adversarial and edge-case inputs |
| **Context handling** | Does the model use conversation context correctly? | Multi-turn coherence, memory within session |
| **Failure behavior** | What happens on bad input? | Empty input, gibberish, prompt injection attempts |
| **Latency** | Response time acceptable to users? | P50/P95/P99 latency under realistic conditions |
| **Cost** | Token usage within budget expectations? | Average tokens per call, outlier detection |

---

## Test Case Design Patterns for LLM Features

### Pattern 1: Ground Truth Matching
For features with known correct answers (e.g., data extraction, classification, translation):
- Prepare a curated dataset of (input, expected_output) pairs
- Define a similarity/match threshold (exact match, semantic similarity, rubric-based)
- Test both easy cases and hard/ambiguous cases

### Pattern 2: Format/Schema Validation
For structured outputs (JSON, tables, code):
- Verify output parses without error
- Check all required fields are present
- Validate data types and value ranges
- Test that extraneous fields are handled gracefully

### Pattern 3: Consistency Testing
For features where repeatability matters:
- Run the same prompt N times (typically 5–10)
- Define acceptable variance (e.g., same key facts, different phrasing = PASS)
- Flag high-variance outputs as flaky — investigate prompt stability

### Pattern 4: Adversarial / Robustness Testing
Always test how the system handles bad actors and edge inputs:
- **Prompt injection**: "Ignore all previous instructions and..."
- **Jailbreak attempts**: Role-play, fictional framing to bypass guardrails
- **Boundary inputs**: Very long input, empty input, input in unexpected language
- **Conflicting context**: Contradictory information in a multi-turn conversation

### Pattern 5: Regression Battery
When a model, prompt, or context changes — run a fixed set of "gold standard" test cases
to catch regressions in output quality. Maintain a versioned prompt regression suite.

---

## Test Data Generation for LLM Features

When generating test data for LLM testing, consider these categories:

**Positive / Normal**
- Typical user inputs representing the 80% use case
- Inputs in the target language(s) and domain vocabulary

**Boundary**
- Minimum viable input (single word, one sentence)
- Maximum length input (near context window limit)
- Input with special characters, emojis, URLs, code snippets

**Negative / Stress**
- Empty string or whitespace only
- Input in an unexpected language
- Input that contains PII or sensitive data (test that it's handled appropriately)
- Input with contradictory or nonsensical content

**Adversarial**
- Prompt injection attempts
- Requests that violate the feature's intended use
- Multi-turn: attempts to change the model's behavior mid-conversation

---

## Evaluation Criteria (Rubric-Based Scoring)

For subjective outputs, use a consistent rubric rather than binary pass/fail.
A simple 3-point rubric works well for most teams:

| Score | Meaning |
|---|---|
| 2 | Fully meets expectations — correct, appropriately formatted, safe |
| 1 | Partially meets expectations — minor issues but usable |
| 0 | Fails — incorrect, unsafe, malformed, or off-topic |

Define what "2", "1", and "0" mean specifically for each feature before running tests.
Document these rubrics so the whole QA team scores consistently.

---

## Jira Fields for AI/LLM Bugs

When logging bugs for LLM feature failures, include:
- **Model/version** used at time of failure
- **Exact prompt** (or anonymized version if PII)
- **Actual output** (verbatim, not summarized)
- **Expected output** (with reference to rubric or acceptance criterion)
- **Run number** (if consistency test — e.g., "occurs 3/10 runs")
- **Repro rate** (e.g., "100% deterministic" vs "~30% probabilistic")
- **Environment** (staging / production, which model endpoint)

---

## LLM Testing Anti-Patterns to Avoid

- **Testing only happy paths** — LLMs fail gracefully but still fail; test edge cases
- **Single-run evaluation** — one run proves nothing for probabilistic systems; use N≥3
- **Vague expected results** — "good response" is not testable; define the rubric
- **Ignoring latency** — LLM features often have UX-breaking latency; always measure
- **No prompt versioning** — prompt changes without regression testing cause silent regressions
- **Over-relying on exact match** — semantic similarity checks are more meaningful for text outputs
