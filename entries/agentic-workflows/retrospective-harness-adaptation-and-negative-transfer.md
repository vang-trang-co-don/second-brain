# Retrospective Harness Adaptation & Negative Transfer: Evaluating Agent Self-Evolution

> **One-liner:** Self-evolving agent harnesses often inject speculative rules that increase task latency by up to 198% or trigger false regression panics; harness changes require closed-loop recurrence tracking and proactive pruning.

---

## Metadata
- **Source:** arXiv:2610.34938 ("How Do Coding-Agent Harnesses Self-Evolve? An Empirical Study of Retrospective Adaptation"), Heidelberg University (Sebastian Baltes et al.), Matt Pocock (@mattpocockuk)
- **Author/Creator:** Sebastian Baltes, Matt Pocock
- **Captured Date:** 2026-10-14
- **Tags:** `#agentic-workflow` `#harness-engineering` `#retrospective` `#negative-transfer` `#self-evolution` `#pruning`
- **Category:** `agentic-workflows`

---

## 1. The Core Idea: The Illusion of Self-Evolution

Agent harnesses that modify their own instructions (via skills like `/retro` or prompt self-reflection) suffer from three systemic failure modes:

1. **Prior-Driven Pollution:** When prompted to reflect, agents suggest generic textbook best practices (e.g., adding linters, pre-commit hooks) even when their absence had zero impact on the task. In empirical testing, 18 out of 19 prior-driven proposals were lint mandates injected regardless of session trace evidence.
2. **The Incomplete List Trap (False Regression Panic):** If a retrospective records a list of known failing tests to ignore, and a subsequent task hits an unlisted pre-existing failure, the agent assumes its own edits caused the breakage. In Sphinx benchmarks, this caused 4 out of 5 adapted sessions to trigger expensive baseline rebuilds that unadapted runs never ran.
3. **The Harness Tax:** Instructions accumulate linearly. Even when an instruction prevented a bad command, bundled secondary rules (e.g., "always run full CI lint before finishing") inflated median session runtimes from 88s to 156s (+77%) and 82s to 245s (+198%) with zero net gain in task resolution rates.

**Core Axiom:** Harness self-evolution requires an evaluation and pruning loop. Writing a rule into `AGENTS.md` or a skill file is an unverified hypothesis until downstream tasks prove the rule reduced recurrence without adding unrelated overhead.

---

## 2. Key Mechanisms & Patterns

### A. Proposal Taxonomy
- **Experience-Driven:** The proposal links to an exact failed tool call or shell error in the session transcript (e.g., calling `pytest` when only `bin/test` exists).
- **Prior-Driven:** The proposal comes from general training priors (e.g., "every repo must have pre-commit hooks"). These must be blocked or isolated to explicit linter tooling, not added to runtime agent prompts.
- **Weak:** General advice without a concrete mechanism ("be more careful when editing docstrings"). These should be dropped immediately.

### B. Closed-Loop Adaptation Lifecycle
An adaptation cannot be permanent upon creation. It moves through a lifecycle:
1. `Candidate`: Proposed from an observed failure.
2. `Canary`: Active in a subset of sessions; records whether the targeted failure occurred.
3. `Effective`: The targeted failure occurred and recurrence dropped to zero without increasing session duration beyond the threshold (+15%).
4. `Negative Transfer`: The adaptation caused extra tool calls on unrelated tasks or increased latency without resolving new tasks. Automatically flagged for removal.
5. `Pruned`: Deleted from the context window.

---

## 3. Real-World Production Failures (Baltes et al. Findings)

1. **SymPy Test Command vs. Lint Tax:**
   - *Fix applied:* Added `bin/test` guidance to `CLAUDE.md` to stop failed `pytest` invocations, but bundled "run CI lint checks before finishing".
   - *Outcome:* Eliminated failed `pytest` runs (5/5 to 0/5), but doubled median execution time (88s to 156s). Success rate did not change.
2. **Sphinx Known-Failures Incomplete Specification:**
   - *Fix applied:* Injected a file listing 2 known test failures, instructing the agent that any failure outside this list is a regression.
   - *Outcome:* On subsequent tasks, environment drift introduced a third legacy failure. The agent spent 245s running baseline comparison builds to fix an issue that was already broken before its first edit.
3. **Astropy Leap-Second Drift:**
   - *Fix applied:* Custom plugin to patch leap-second cache plus a comparison script.
   - *Outcome:* Downstream tasks failed due to NumPy deprecations, which the custom script misclassified as novel bugs.

---

## 4. Reconstructability Blueprint: Closed-Loop Retro Engine

### A. Tracking Schema (PostgreSQL / SQLite)

```sql
CREATE TABLE IF NOT EXISTS harness_adaptations (
    id VARCHAR(64) PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    trigger_error_type VARCHAR(128) NOT NULL,
    target_scope VARCHAR(128) NOT NULL, -- e.g., "repo:sympy", "tool:bash"
    proposal_type VARCHAR(32) NOT NULL, -- 'experience_driven', 'prior_driven'
    mechanism_type VARCHAR(32) NOT NULL, -- 'context_prompt', 'hook', 'known_failures'
    file_path VARCHAR(255) NOT NULL,
    injected_content TEXT NOT NULL,
    status VARCHAR(32) DEFAULT 'canary' -- 'canary', 'verified', 'flagged_overhead', 'pruned'
);

CREATE TABLE IF NOT EXISTS adaptation_session_traces (
    session_id VARCHAR(64) PRIMARY KEY,
    adaptation_id VARCHAR(64) NOT NULL REFERENCES harness_adaptations(id) ON DELETE CASCADE,
    task_category VARCHAR(64) NOT NULL,
    target_problem_encountered BOOLEAN NOT NULL,
    adaptation_consulted BOOLEAN NOT NULL,
    target_action_occurred BOOLEAN NOT NULL,
    duration_seconds INTEGER NOT NULL,
    token_usage_total INTEGER NOT NULL,
    unrelated_baseline_runs INTEGER DEFAULT 0,
    task_success BOOLEAN NOT NULL
);

CREATE INDEX idx_trace_adaptation ON adaptation_session_traces(adaptation_id, status);
```

### B. Verification & Auto-Pruning Engine (Go)

```go
package retro

import (
	"context"
	"database/sql"
	"fmt"
)

type AdaptationStatus string

const (
	StatusCanary          AdaptationStatus = "canary"
	StatusVerified        AdaptationStatus = "verified"
	StatusFlaggedOverhead AdaptationStatus = "flagged_overhead"
	StatusPruned          AdaptationStatus = "pruned"
)

type EvaluationResult struct {
	AdaptationID       string
	SampleCount        int
	RecurrenceRate     float64
	MedianLatencyDelta float64
	FalseAlarmRuns     int
	Recommendation     AdaptationStatus
}

func EvaluateAdaptation(ctx context.Context, db *sql.DB, adaptationID string, baselineMedianSec float64) (*EvaluationResult, error) {
	row := db.QueryRowContext(ctx, `
		SELECT 
			COUNT(*),
			COALESCE(AVG(CASE WHEN target_action_occurred THEN 1.0 ELSE 0.0 END), 0.0),
			COALESCE(SUM(unrelated_baseline_runs), 0),
			COALESCE(AVG(duration_seconds), 0.0)
		FROM adaptation_session_traces
		WHERE adaptation_id = $1 AND target_problem_encountered = TRUE
	`, adaptationID)

	var samples, falseAlarms int
	var recurrence, avgDuration float64
	if err := row.Scan(&samples, &recurrence, &falseAlarms, &avgDuration); err != nil {
		return nil, err
	}

	result := &EvaluationResult{
		AdaptationID:       adaptationID,
		SampleCount:        samples,
		RecurrenceRate:     recurrence,
		FalseAlarmRuns:     falseAlarms,
		MedianLatencyDelta: avgDuration - baselineMedianSec,
		Recommendation:     StatusCanary,
	}

	if samples < 5 {
		return result, nil // Insufficient statistical power
	}

	// 1. If it induces false alarm verification runs on unrelated tasks -> prune immediately
	if falseAlarms > 0 {
		result.Recommendation = StatusPruned
		return result, nil
	}

	// 2. If recurrence did not decrease (< 50% reduction) -> flagged
	if recurrence > 0.5 {
		result.Recommendation = StatusFlaggedOverhead
		return result, nil
	}

	// 3. If recurrence was eliminated but latency increased by > 30% -> flagged for instruction bloat
	if baselineMedianSec > 0 && (avgDuration-baselineMedianSec)/baselineMedianSec > 0.30 {
		result.Recommendation = StatusFlaggedOverhead
		return result, nil
	}

	result.Recommendation = StatusVerified
	return result, nil
}
```

---

## 5. Concrete Rules for Second Brain & Agent Memory

1. **No Speculative Universal Tiers:** Do not mandate DDL schemas or API contracts for topics that do not involve databases or network services. Prior-driven templates waste token budget and dilute search density.
2. **Negative Transfer Audit:** Any rule or template that causes an agent to generate hallucinated stub files or run redundant checks must be deleted.
3. **Decouple Invariants from Guidance:** Invariants belong in strict lint/compiler rules. Advisory instructions belong in modular on-demand reference notes, not persistent system prompts.
4. **Pruning Cadence:** Conduct a periodic sweep of repository rules. If a note or rule has not prevented an error or guided an implementation within 30 days, archive or delete it.
