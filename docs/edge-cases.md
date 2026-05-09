# Detailed Edge Cases
**Project:** AI-Powered Restaurant Recommendation System (Zomato Use Case)

This document lists detailed edge cases based on:
- `docs/problemstatement.md`
- `docs/phase-wise-architecture.md`

Each edge case includes:
- **Scenario**
- **Risk**
- **Expected Handling**

## 1) Data Ingestion and Preparation Edge Cases (Phase 2)

### EC-D1: Dataset source unavailable
- **Scenario:** Hugging Face dataset URL is down or returns timeout.
- **Risk:** Pipeline fails; no data available for recommendations.
- **Expected Handling:** Retry with exponential backoff; if still failing, load last known valid snapshot and raise alert.

### EC-D2: Dataset schema changes unexpectedly
- **Scenario:** Column names change (for example `cost_for_two` becomes `average_cost`).
- **Risk:** ETL breaks silently or maps wrong fields.
- **Expected Handling:** Add schema validation at ingestion start; fail fast with explicit error and notify maintainers.

### EC-D3: Missing critical columns
- **Scenario:** One or more required fields (`name`, `location`, `cuisine`, `rating`, `cost`) are missing.
- **Risk:** Downstream filtering and ranking produce invalid output.
- **Expected Handling:** Block pipeline release; only proceed when required columns are present.

### EC-D4: High proportion of null values
- **Scenario:** Many rows have null `rating` or `cost`.
- **Risk:** Candidate quality drops; rankings become biased.
- **Expected Handling:** Define per-field imputation/drop rules and minimum data quality thresholds; reject ingestion if threshold violated.

### EC-D5: Duplicate records with slight text differences
- **Scenario:** Same restaurant appears multiple times with minor spelling differences.
- **Risk:** Repeated recommendations shown to users.
- **Expected Handling:** Use fuzzy deduplication keys (name + area + cuisine + approximate cost); keep best-quality row.

### EC-D6: Non-standard rating formats
- **Scenario:** Ratings appear as `4.2/5`, `NEW`, `-`, or text.
- **Risk:** Numeric comparisons fail.
- **Expected Handling:** Parse rating to numeric safely; mark unknown ratings as null and apply fallback ranking rules.

### EC-D7: Currency and cost inconsistency
- **Scenario:** Cost field includes symbols/text (`₹800 for two`, `INR 1200`, `approx 600`).
- **Risk:** Budget filtering becomes inaccurate.
- **Expected Handling:** Normalize cost into numeric value and mapped budget buckets (`low`, `medium`, `high`).

### EC-D8: Extremely old snapshot
- **Scenario:** Dataset last refreshed many months ago.
- **Risk:** Recommendations become stale.
- **Expected Handling:** Track dataset freshness metadata; flag stale data and warn in monitoring dashboard.

## 2) User Input and Validation Edge Cases (Phase 3)

### EC-U1: Empty submission
- **Scenario:** User submits form with no fields.
- **Risk:** Ambiguous query; irrelevant recommendations.
- **Expected Handling:** Enforce required fields (at least location or cuisine or budget); return actionable validation message.

### EC-U2: Unsupported location
- **Scenario:** User enters city not present in dataset.
- **Risk:** Zero results.
- **Expected Handling:** Suggest nearest/available locations and ask user to confirm fallback.

### EC-U3: Spelling errors and casing differences
- **Scenario:** `banglore`, `DELHI`, `chineese`.
- **Risk:** Filter misses valid matches.
- **Expected Handling:** Apply normalization, synonym dictionary, and fuzzy matching before filtering.

### EC-U4: Out-of-range rating
- **Scenario:** User provides minimum rating `8` or `-1`.
- **Risk:** Invalid comparisons; no meaningful output.
- **Expected Handling:** Validate numeric range (for example `0-5`); reject with clear correction message.

### EC-U5: Contradictory preferences
- **Scenario:** `budget=low` + `minimum_rating=4.8` + premium cuisine in expensive area.
- **Risk:** No candidate set.
- **Expected Handling:** Return "no exact match" with relaxed suggestions by priority rules (relax one constraint at a time).

### EC-U6: Special characters or injection-like input
- **Scenario:** Input contains SQL/JSON/script payload.
- **Risk:** Security and parser instability.
- **Expected Handling:** Sanitize and escape all user-provided text; enforce strict API schema.

### EC-U7: Ambiguous preferences
- **Scenario:** `good food`, `cheap and best`, `near me`.
- **Risk:** Hard to map to structured fields.
- **Expected Handling:** Convert to inferred tags where possible, else ask clarifying follow-up questions.

### EC-U8: Long free-text preference
- **Scenario:** Very long additional preferences paragraph.
- **Risk:** Prompt bloat and latency increase.
- **Expected Handling:** Summarize/extract key constraints before prompt construction.

## 3) Candidate Retrieval Edge Cases (Phase 4)

### EC-R1: Filter returns zero candidates
- **Scenario:** Strict filters eliminate all restaurants.
- **Risk:** Empty response, poor user experience.
- **Expected Handling:** Progressive relaxation strategy (rating -> cuisine strictness -> budget strictness) with transparent explanation.

### EC-R2: Filter returns too many candidates
- **Scenario:** Broad query returns thousands of records.
- **Risk:** High latency/cost when passing to LLM.
- **Expected Handling:** Use deterministic pre-ranking and cap to top-N before LLM call.

### EC-R3: Candidate bias toward popular areas
- **Scenario:** Ranking heuristic always favors high-density city zones.
- **Risk:** Poor diversity and user dissatisfaction.
- **Expected Handling:** Add diversity constraints (area spread, cuisine spread) in shortlist stage.

### EC-R4: Tied scores in deterministic ranking
- **Scenario:** Many restaurants have same composite score.
- **Risk:** Unstable order across identical requests.
- **Expected Handling:** Apply stable tie-breakers (rating count, normalized cost-fit, alphabetical fallback).

### EC-R5: Missing features in top-N candidates
- **Scenario:** Candidate has null cost or null cuisine.
- **Risk:** LLM explanations become incorrect or generic.
- **Expected Handling:** Exclude incomplete records or fill with safe defaults before prompt assembly.

## 4) LLM Recommendation Edge Cases (Phase 5)

### EC-L1: LLM timeout or API downtime
- **Scenario:** Model endpoint is slow/unreachable.
- **Risk:** Failed recommendation request.
- **Expected Handling:** Timebox requests, retry once, then fallback to retrieval-only ranking with templated explanations.

### EC-L2: Malformed structured output
- **Scenario:** LLM returns invalid JSON or misses required keys.
- **Risk:** UI/API response parsing failure.
- **Expected Handling:** Strict schema validator; re-prompt once with correction instruction; fallback if still invalid.

### EC-L3: Hallucinated restaurants
- **Scenario:** LLM recommends restaurants not in candidate list.
- **Risk:** Trust and factual correctness issues.
- **Expected Handling:** Post-validate recommendations against candidate IDs; drop unknown entities and regenerate/fallback.

### EC-L4: Generic explanations
- **Scenario:** LLM gives vague reasons not grounded in attributes.
- **Risk:** Low recommendation quality perception.
- **Expected Handling:** Prompt constraints requiring attribute citations (budget, rating, cuisine, location match).

### EC-L5: Prompt token overflow
- **Scenario:** Candidate payload + user preferences exceed token limit.
- **Risk:** Truncation and quality degradation.
- **Expected Handling:** Summarize candidates, cap fields, chunk or shrink top-N before sending to model.

### EC-L6: Unsafe or biased model output
- **Scenario:** Output includes discriminatory or inappropriate language.
- **Risk:** Safety/compliance issues.
- **Expected Handling:** Apply content moderation and replacement template; log incident for prompt refinement.

### EC-L7: Non-deterministic outputs for same input
- **Scenario:** Same query gives very different rankings frequently.
- **Risk:** Unstable user trust.
- **Expected Handling:** Lower randomness (temperature), preserve deterministic shortlist ordering, cache recent identical requests.

## 5) Response Presentation Edge Cases (Phase 6)

### EC-P1: Partial recommendation payload
- **Scenario:** One card missing rating/cost/explanation.
- **Risk:** Broken or inconsistent UI.
- **Expected Handling:** Show placeholder text (`Not available`) and keep page render resilient.

### EC-P2: Very long explanation text
- **Scenario:** LLM returns long paragraphs.
- **Risk:** Cluttered interface.
- **Expected Handling:** Truncate with "Read more" UI and maximum character limits.

### EC-P3: Unicode/encoding issues
- **Scenario:** Cuisine names contain special characters and render incorrectly.
- **Risk:** Display glitches.
- **Expected Handling:** Enforce UTF-8 encoding and sanitize response text before render.

### EC-P4: Duplicate items in final list
- **Scenario:** Same restaurant appears more than once after LLM formatting.
- **Risk:** Perceived low quality.
- **Expected Handling:** Final dedup pass on restaurant ID/name before display.

### EC-P5: Mobile layout overflow
- **Scenario:** Long restaurant names or explanation overflow card width.
- **Risk:** Poor usability on small screens.
- **Expected Handling:** Use responsive layout constraints and text wrapping rules.

## 6) Monitoring and Feedback Edge Cases (Phase 7)

### EC-M1: Metrics ingestion failure
- **Scenario:** Analytics endpoint goes down.
- **Risk:** Loss of observability.
- **Expected Handling:** Buffer events locally/queue and retry asynchronously.

### EC-M2: Feedback spam or abuse
- **Scenario:** Users submit repeated fake negative/positive feedback.
- **Risk:** Biased optimization decisions.
- **Expected Handling:** Rate limiting, deduplication, and anomaly detection on feedback events.

### EC-M3: Silent quality degradation
- **Scenario:** Latency is stable but relevance quality drops over weeks.
- **Risk:** Hard-to-detect product regression.
- **Expected Handling:** Track recommendation acceptance metrics and add weekly quality audits.

### EC-M4: Prompt update causes regression
- **Scenario:** New prompt decreases recommendation quality.
- **Risk:** Production degradation.
- **Expected Handling:** A/B test prompt versions and provide rollback switch.

## 7) Deployment and Operations Edge Cases (Phase 8)

### EC-O1: Missing environment variables
- **Scenario:** LLM API key or DB URL not configured.
- **Risk:** Runtime failures at startup.
- **Expected Handling:** Startup config validation and fail-fast with explicit missing-variable list.

### EC-O2: Third-party API rate limiting
- **Scenario:** LLM provider returns 429 responses.
- **Risk:** Intermittent failures and poor latency.
- **Expected Handling:** Exponential backoff, jitter, circuit breaker, and graceful fallback path.

### EC-O3: Traffic spikes during peak hours
- **Scenario:** Sudden increase in recommendation requests.
- **Risk:** Queue buildup and timeouts.
- **Expected Handling:** Autoscaling, request queueing, and response caching for repeated queries.

### EC-O4: Deployment rollback mismatch
- **Scenario:** App rollback uses old code with new schema assumptions.
- **Risk:** API and data contract mismatch.
- **Expected Handling:** Versioned contracts and backward-compatible schema migration strategy.

### EC-O5: Logging sensitive data
- **Scenario:** Raw user preferences or keys accidentally logged.
- **Risk:** Privacy and security violation.
- **Expected Handling:** Mask/redact sensitive values and run log-safety checks in CI.

## 8) End-to-End Cross-Phase Edge Cases

### EC-X1: No-data + strict user preferences + LLM timeout
- **Scenario:** Dataset is sparse in selected city and LLM call fails.
- **Risk:** User gets no recommendations.
- **Expected Handling:** Multi-layer fallback:
  1. Relax filters
  2. Switch to nearby city suggestion
  3. Use deterministic top picks with static explanation template

### EC-X2: Stale dataset + trendy user query
- **Scenario:** User asks for newly opened restaurants not in dataset.
- **Risk:** Recommendations appear outdated.
- **Expected Handling:** Communicate data freshness and suggest best available alternatives.

### EC-X3: High latency chain reaction
- **Scenario:** Slow DB query + large prompt + slow LLM response.
- **Risk:** End-to-end timeout.
- **Expected Handling:** Per-stage timeout budgets and failover to lightweight path.

### EC-X4: Inconsistent normalization across modules
- **Scenario:** Input normalization maps `North Indian` but dataset stores `North-Indian`.
- **Risk:** False no-match results.
- **Expected Handling:** Centralized taxonomy and shared normalization library across services.

## 9) Recommended Test Coverage Matrix

- **Unit tests:** Parsing, normalization, budget/rating validators, ranking tie-breakers.
- **Integration tests:** API -> retrieval -> prompt builder -> LLM validator -> response formatter.
- **Contract tests:** LLM output schema and fallback paths.
- **Data quality tests:** Required columns, null thresholds, duplicate thresholds.
- **Load tests:** Peak traffic behavior, queueing, timeout handling.
- **Chaos tests:** LLM outage, DB latency injection, metrics endpoint failure.

## 10) Definition of Done for Edge-Case Readiness

The system is edge-case ready when:
- Every critical edge case above has at least one automated test.
- Fallback responses remain user-meaningful (not generic errors).
- Monitoring captures failures in data, retrieval, and LLM stages.
- On-call runbook includes recovery steps for top operational failures.
