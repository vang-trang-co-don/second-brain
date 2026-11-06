# Second Brain & pstack Integration Todo List

## Session Pickup Steps
- [x] 1. Read the project checkpoint / transcript fallback (completed: inspected `~/.pi/agent/sessions/--home-dungcq-projects--/2026-11-05T12-50-24-090Z_01a1abc2-aada-76d2-8d1e-a8c56fcbbc7e.jsonl`).
- [x] 2. Reconstruct operational state (completed: Grounding, 3-Candidate Arena, and Phase C Synthesis were formulated; implementation was left pending when Pi returned empty messages).
- [x] 3. Diff done vs pending (completed: Resume point is implementing Candidate 3 - JIT Aspect-Sliced Memory Lever).
- [x] 4. Verify inherited claims against original goal on the real artifact (completed: verified `entries/` has 14 markdown files matching the structured template).
- [x] 5. Route remaining work to matching playbook (routed to: Feature playbook).

## Feature Playbook Steps
- [x] 1. `how` over the affected subsystem (skip: covered by Phase A Grounding in inherited session).
- [x] 2. `architect` for parallel design exploration (skip: covered by 3-Candidate Arena in inherited session).
- [x] 3. Write the throughput checkpoint as four todo items:
  - [x] Blocking first steps: Verify entry parsing and define manifest schema.
  - [x] Independent workstreams: Slicing engine, manifest generator, CLI query/check subcommands, skill definition.
  - [x] Shared mutable state: `MANIFEST.json` generated from entries; keep single source of truth.
  - [x] Smallest safe decomposition: Single owner for tool and manifest to guarantee contract consistency.
- [x] 4. Implement code and tools:
  - [x] 4.1. Create `scripts/brain` (CLI tool supporting `query`, `list`, `sync-manifest`, `check`).
  - [x] 4.2. Generate `/home/dungcq/projects/second-brain/MANIFEST.json` for all 14 entries with keywords, triggers, and core invariants.
  - [x] 4.3. Update `/home/dungcq/.agents/skills/second-brain/SKILL.md` to integrate `brain query` with pstack skills (`/architect`, `/tdd`, `/thermos`, `/reflect`).
  - [x] 4.4. Update second-brain README and docs to document the CLI lever.
- [x] 5. Verify on matching surface:
  - [x] 5.1. Execute `brain check` across all 14 entries.
  - [x] 5.2. Test aspect slicing (`invariants`, `mechanisms`, `cases`, `schema`, `probes`) across multiple domains (`fnb-pos`, `fnb-restaurant-p2p`, `b2b-saas-ui-ux`, etc.).
  - [x] 5.3. Test search and triggers (`pos`, `tạm tính`, `vietqr`, `p2p`).
  - [x] 5.4. Verify automated manifest sync idempotency.
- [x] 6. Sequence into clean commit(s) (commit ceb8202).
- [x] 7. If contested, interrogate (skip: n/a, design consensus reached in synthesis).
- [x] 8. Final verification and report.
