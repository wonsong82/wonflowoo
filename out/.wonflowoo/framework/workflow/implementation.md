# Phase 5: Implementation Monitoring

## Goal

Track progress across waves, ensure specs are current, close out the project.

## Per-Wave Checklist

1. All tasks in wave dispatched (one developer per task, parallel)
2. All developer plans reviewed and approved
3. All implementations complete with acceptance criteria met
4. `spec-updater` spawned for EACH completed task (MANDATORY — no exceptions)
5. All spec updates verified (correct specs updated, _system.yml current)
6. Wave marked complete in plan doc
7. **Draft updated with per-task implementation notes** — for EACH completed task, record in the draft's Implementation section: task ID, completion status, deviations from plan, issues encountered, spec file paths. This is NOT optional — the draft is the session recovery mechanism.

## Spec Updates Are NON-NEGOTIABLE

After EVERY implementation task:
1. Developer reports completion with a **change manifest** (files created/modified, endpoints, data touched)
2. Orchestrator spawns `spec-updater` with: change manifest + task file + source paths + existing specs + _system.yml
3. `spec-updater` determines which specs to update, writes updates, reports back
4. Orchestrator verifies spec updates were made before marking task complete

If spec-updater reports no updates needed → verify this is correct (e.g., pure refactor with no behavior change). Otherwise, investigate.

**Developers do NOT update specs directly.** They provide the change manifest. The `spec-updater` has the macro view to route changes to the correct feature specs.

## Spec Update Per Case

- **Greenfield** — spec-updater creates new spec files from change manifest
- **Add Feature** — spec-updater updates existing specs, creates new ones for new modules
- **Refactoring** — spec-updater regenerates affected specs to reflect structural changes
- **Bug Fix** — spec-updater updates spec if the fix changes behavior (logic flows, error paths)
- **Migration** — spec-updater regenerates specs for migrated modules

## Verification wave (final)

- Plan compliance: does implementation match what was planned?
- Scope fidelity: did we build what was asked, nothing more, nothing less?
- Spec accuracy: do specs reflect what was actually built?
- Run /spec-validate for bidirectional coverage check

### Optional: High-Accuracy Review (Large/Enterprise)

For Large or Enterprise complexity, spawn `architecture-consultant` for a holistic review:
- Load: _system.yml + all specs + architecture docs + requirements + plan
- Goal: Check implementation matches requirements, identify spec drift, cross-cutting concerns
- Output: Review report
- Address critical findings before marking project complete

## Failure Handling

- Developer fails acceptance criteria → re-dispatch with specific failures noted
- Spec generation skipped → REJECT completion, send developer back to generate specs
- Build/test failures after implementation → re-dispatch developer to fix (use session continuation)
- Cross-wave integration issues → may need to revise earlier task's code; dispatch developer for the affected task
- 3 consecutive failures on same task → STOP, document attempts, escalate to human

## Completion

1. All task files marked `completed`
2. All specs generated and validated
3. System spec current
4. Draft marked `Status: done`
5. Present completion summary to human

---

## Wisdom Accumulation

After implementation, review for learnings:
- New pattern → update conventions.yml
- Non-obvious decision → create ADR
- Spec gap → improve spec conventions
- Architecture drift → update arch docs

## Testing Strategy

Testing is embedded in the framework, not a separate concern:

- **Task acceptance criteria** include test expectations (e.g., "unit tests for all service methods", "integration test for login flow")
- **Quality gates** require tests to pass ("all existing tests pass" is a clearance check)
- **Specs do NOT track test coverage** — that's a code-level concern, not an orchestrator-level concern
- **Test conventions** live in `conventions.yml` (test framework, file patterns, coverage minimums)

The framework says "tests must exist and pass." HOW to test is defined by the project's conventions.

## Bootstrap + Skills Reminder

If code exists without `.wonflowoo/workspace` specs → use `/bootstrap` skill. Do NOT run the normal lifecycle on an uninitialized codebase.

- `/bootstrap` — 8-step pipeline for existing codebases
- `/spec-generate` — AI-assisted spec generation from code (MANDATORY after every task)
- `/spec-validate` — bidirectional validation (forward + backward coverage)
