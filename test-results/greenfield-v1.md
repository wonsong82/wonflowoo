# Gap Analysis: Greenfield Test (Case 1) — Full Lifecycle

**Test date:** 2026-03-25  
**Platform:** OmO (OpenCode) interactive mode via tmux  
**Model:** Claude Opus 4.6 (Sisyphus Ultraworker)  
**Session:** ses_2d878a834ffeTrrY8UWhNRLn4Q  
**Phases tested:** Discovery, Architecture, Planning, Delegation, Implementation (partial — Waves 0-2 complete, Wave 3 in progress when stopped)  
**Duration:** ~1h 45m (8:24 PM → 10:09 PM)  
**Test stopped at:** Wave 3 (comments + activity log) in progress. Waves 4-5 not reached.

---

## Test Methodology

1. Copied framework deliverables from `out/` into `test/temp/greenfield/`
2. Started `opencode` in tmux (interactive mode) — required for sub-agent persistence
3. Sent greenfield prompt: "I want to build a task management app..."
4. Answered agent questions as a human would (natural, non-coaching prompts)
5. Approved phase gates to advance through all phases
6. Validated each phase against CONCEPT.md sections, not from memory
7. Stopped during Implementation (Wave 3) due to time — sufficient data collected

**Key finding: Sub-agents work correctly in interactive mode.** `opencode run` single-turn mode cannot sustain sub-agent lifecycles.

---

## Timeline

| Time | Event | Duration |
|---|---|---|
| 8:24 PM | Session start, greenfield prompt | — |
| 8:26 PM | Librarian research complete | 2 min |
| 8:34 PM | Discovery complete, requirements approved | 10 min |
| 8:41 PM | Architecture librarian research complete | 7 min |
| 8:50 PM | Architecture specialist complete (8m 24s) | 9 min |
| 8:52 PM | Architecture approved | 2 min |
| 8:55 PM | Gap analysis specialist complete | 3 min |
| 9:01 PM | Planning complete, plan approved | 6 min |
| 9:15 PM | All 9 task files generated | 14 min |
| 9:16 PM | Wave 0 Task 00002 developer dispatched | — |
| 9:19 PM | 00002 developer plan ready (3 min) | 3 min |
| 9:37 PM | 00002 implementation complete (17 min) | 17 min |
| 9:40 PM | Wave 0 Task 00003 developer dispatched | — |
| 10:01 PM | 00003 auth implementation complete (21 min) | 21 min |
| 10:04 PM | Wave 1 Tasks 00004+00005 dispatched (parallel) | — |
| ~10:20 PM | Wave 1 complete | ~16 min |
| ~10:25 PM | Wave 2 Task 00006 dispatched | — |
| ~10:45 PM | Wave 2 complete (with one fix cycle) | ~20 min |
| ~10:47 PM | Wave 3 Task 00007 dispatched | — |
| ~10:50 PM | **Test stopped** | — |

**Total Discovery→Planning: ~37 min. Per-task implementation: ~17-21 min.**

---

## Phase 1: Discovery

| # | Check | Result | Notes |
|---|---|---|---|
| D1 | Complexity classified | ✅ PASS | Identified greenfield, medium+ complexity |
| D2 | Librarian fired before questions | ✅ PASS | "Research task management app features" |
| D3 | Draft created and updated | ✅ PASS | Correct path, updated across phases |
| D4 | Business-only interview | ✅ PASS | No tech questions in Discovery |
| D5 | Standard requirements suggested | ✅ PASS | Activity log, search, archiving, etc. |
| D6 | Clearance check (7 greenfield items) | ⚠️ GAP | **GAP-D-1**: Missing "Tech preferences captured?" |
| D7 | Requirements doc path | ✅ PASS | `.ai/requirements/00001-task-management.md` |
| D8 | Status: pending_approval → approved | ✅ PASS | Correct transitions |
| D9 | Phase gate respected | ✅ PASS | Stopped, waited for approval |
| D10 | No tech in requirements | ✅ PASS | Zero tech references |

### GAP-D-1: Discovery Clearance Missing Greenfield-Only Item
**CONCEPT.md line 514:** `□ Tech preferences or constraints captured? (greenfield only)`  
**What happened:** 6/7 items shown. Tech prefs captured later (Architecture start), stored in draft correctly.  
**Root cause:** AGENTS.md omits this item.  
**Severity:** LOW

---

## Phase 2: Architecture

| # | Check | Result | Notes |
|---|---|---|---|
| A1 | Full architecture scope | ✅ PASS | All docs designed from scratch |
| A2 | Librarian research fired | ✅ PASS | 2 librarians (Prisma + Next.js patterns) |
| A3 | Specialist consulted | ✅ PASS | Ultrabrain architect, 8m 24s, wrote 8 files |
| A4 | tech-stack.yml | ✅ PASS | 119 lines, comprehensive |
| A5 | conventions.yml | ✅ PASS | Present and detailed |
| A6 | system-design.md + Mermaid | ✅ PASS | 6 Mermaid diagrams |
| A7 | ADRs for non-obvious decisions | ✅ PASS | 4 ADRs created |
| A8 | dependencies.yml skipped | ✅ PASS | Correctly — no external services |
| A9 | config.yml updated | ⚠️ GAP | **GAP-A-1**: Missing spec_organization fields |
| A10 | Clearance check (8 items) | ⚠️ GAP | **GAP-A-2**: Missing "Human aligned?" |
| A11 | Phase gate respected | ✅ PASS | Stopped, waited for approval |

### GAP-A-1: config.yml Missing spec_organization Fields
**AGENTS.md says:** Set `spec_organization.unit_term` and `spec_organization.boundary` from architecture decisions.  
**What happened:** Only `project.name` and `project.description` set. Architecture chose "modular monolith" but `unit_term: module` and `boundary: service-layer` not populated.  
**Severity:** MEDIUM — Affects spec generation downstream.

### GAP-A-2: Architecture Clearance Missing "Human Aligned" Item
**CONCEPT.md line 578:** `□ Human aligned — no fundamental disagreements?`  
**What happened:** 7/8 items shown. Human DID approve via phase gate.  
**Root cause:** AGENTS.md omits this item.  
**Severity:** LOW

---

## Phase 3: Planning

| # | Check | Result | Notes |
|---|---|---|---|
| P1 | Gap analysis by specialist | ✅ PASS | Deep agent, found 4 critical gaps |
| P2 | Critical gaps → human | ✅ PASS | All 4 presented, answered before planning |
| P3 | Dependency-ordered waves | ✅ PASS | 6 waves, correct ordering |
| P4 | Greenfield wave pattern | ✅ PASS | Foundation → Core → Dependent → Verification |
| P5 | Task detail level | ✅ PASS | Description, acceptance criteria, guardrails, category, deps |
| P6 | Gap classification (critical/minor/ambiguous) | ✅ PASS | 4 critical, 7 minor/ambiguous |
| P7 | Present and confirm | ✅ PASS | Summary with feature→task mapping |
| P8 | Clearance check (8 items) | ⚠️ GAP | **GAP-P-1**: Missing 2 items |
| P9 | Plan doc format | ✅ PASS | Status, Task IDs, gaps, waves, per-task status |
| P10 | Phase gate respected | ✅ PASS | Stopped, asked for approval |

### GAP-P-1: Planning Clearance Missing Items
**CONCEPT.md lines 693-695:** Missing `□ Each task scoped to feature-level?` and `□ Plan reviewed and confirmed by human?`  
**Root cause:** AGENTS.md has 6/8 items.  
**Severity:** LOW — Both conditions satisfied, just not displayed.

---

## Phase 4: Delegation

### What CONCEPT.md Requires (lines 769-1001)

| # | Requirement | Source |
|---|---|---|
| DEL1 | Generate task instruction files (self-contained YAML) | lines 773-880 |
| DEL2 | Task file includes: task, wave, status, category, context, brief, refs, must_do, must_not_do, acceptance_criteria, depends_on, blocks | lines 787-878 |
| DEL3 | One developer per task | line 988 |
| DEL4 | Developer writes .plan.md BEFORE coding | lines 892-920 |
| DEL5 | Plan persisted as companion file: `{task-id}.{task-name}.plan.md` | lines 922-936 |
| DEL6 | Mandatory alignment check: orchestrator reviews plan before implementation | lines 938-975 |
| DEL7 | Task status tracking: pending → in_progress → completed | lines 979-990 |
| DEL8 | Wave progression: all tasks complete → next wave unblocked | line 990 |
| DEL9 | Failure handling: re-dispatch or escalate | lines 994-1001 |

### Results

| # | Check | Result | Notes |
|---|---|---|---|
| DEL1 | Task files generated | ✅ PASS | All 9 `.yml` files in `.ai/tasks/` |
| DEL2 | Task file structure | ✅ PASS | All required fields present (see auth-system.yml: task, wave, status, category, context, brief, architecture_refs, spec_refs, adr_refs, must_do, must_not_do, acceptance_criteria, depends_on, blocks) |
| DEL3 | One developer per task | ✅ PASS | Each task dispatched to its own sub-agent |
| DEL4 | Developer writes .plan.md first | ⚠️ GAP | **GAP-DEL-1**: Two-step vs one-step dispatch |
| DEL5 | Plan persisted as companion file | ✅ PASS | All completed tasks have `.plan.md` files (6 plan files for 6 completed tasks) |
| DEL6 | Mandatory alignment check | ⚠️ GAP | **GAP-DEL-2**: Alignment loop partially skipped |
| DEL7 | Task status tracking | ✅ PASS | Status updated in `.yml` files (verified: 00003.auth-system.yml shows `status: completed`) |
| DEL8 | Wave progression | ✅ PASS | Wave 0 → Wave 1 → Wave 2 → Wave 3 in correct order |
| DEL9 | Failure handling | ✅ PASS | Task 00006 had TS error, agent sent developer back to fix (session continuation) |

### GAP-DEL-1: Combined Plan+Implement Dispatch (Two-Step Collapsed to One)

**CONCEPT.md says (lines 892-966):** Developer planning is a DISTINCT step:
1. Developer dispatched → writes `.plan.md` → STOPS
2. Orchestrator reviews plan
3. If approved → developer dispatched again to implement
4. If rejected → developer revises plan

**What happened:**
- Task 00002: ✅ Correctly two-step (plan dispatched separately, reviewed by main agent, then implementation dispatched)
- Tasks 00003-00006: ❌ Combined into single dispatch ("plan → implement in one dispatch"). Agent noted: "going straight to plan + implement cycle"

**Impact:** The alignment loop was skipped for tasks 00003+. Plans were still written to `.plan.md` files, but the orchestrator reviewed them AFTER implementation rather than before.

**Why this matters per CONCEPT.md (lines 938-975):** The alignment loop catches spec drift, ambiguous instructions, architecture conflicts, and missing context BEFORE code is written. Skipping it means issues are found in verification rather than prevented.

**Severity:** HIGH — This is a core framework mechanism being bypassed. The two-step process is explicitly described as "mandatory alignment check."

### GAP-DEL-2: Alignment Loop Partially Skipped

**CONCEPT.md says (line 940):** "Before a developer writes any code, there is a **mandatory alignment check**."

**What happened:**
- Task 00002: ✅ Plan reviewed before implementation. Agent even caught an issue (Comment.author onDelete missing) and sent a fix instruction.
- Tasks 00003+: ❌ Plan+implement combined. No pre-implementation review.

**Root cause:** The agent optimized for speed, collapsing the two-step process into one. The AGENTS.md instructions say "developer writes .plan.md → STOP → report plan → review → then implement" but the agent deviated after the first task.

**Severity:** HIGH (same root cause as GAP-DEL-1)

---

## Phase 5: Implementation (Partial — Waves 0-2)

### What CONCEPT.md Requires (lines 1005-1062)

| # | Requirement | Source |
|---|---|---|
| IMP1 | Developers follow architecture docs and conventions | line 1013 |
| IMP2 | Verify against acceptance criteria from task file | line 1014 |
| IMP3 | Generate/update specs after implementation | lines 1015, 1030-1040 |
| IMP4 | Orchestrator validates before marking complete | lines 1022-1027 |
| IMP5 | Wave progression: all complete → next wave | line 1026 |
| IMP6 | Draft updated with progress | line 1028 |
| IMP7 | Verification wave (final) | lines 1042-1051 |

### Results (Waves 0-2 only — test stopped during Wave 3)

| # | Check | Result | Notes |
|---|---|---|---|
| IMP1 | Follows conventions | ✅ PASS | Folder structure matches conventions.yml, service/repository pattern followed |
| IMP2 | Acceptance criteria verified | ✅ PASS | Orchestrator explicitly verified each task (e.g., "TS clean, Prisma valid, folder structure correct") |
| IMP3 | Specs generated | ✅ PASS | 6 specs created: _system.yml, project-scaffolding.yml, auth.yml, users.yml, project-management.yml, task-management.yml |
| IMP4 | Orchestrator validates | ✅ PASS | Each task verified before marking complete |
| IMP5 | Wave progression | ✅ PASS | Correct wave ordering observed |
| IMP6 | Draft updated | ⚠️ GAP | **GAP-IMP-1**: Draft not fully updated during implementation |
| IMP7 | Verification wave | ⏭️ N/A | Test stopped before Wave 5 |

### GAP-IMP-1: Draft Not Fully Updated During Implementation

**CONCEPT.md says (line 1028):** Orchestrator "updates draft — records implementation progress, issues encountered, deviations from plan"

**What happened:** Draft's Implementation section shows:
```
### Implementation
- Completed tasks:
- Validation outcomes:
- Spec updates applied:
```
All empty. The draft's Phase field correctly reads `delegation` but the Implementation section was never populated despite 6 tasks completing.

**Severity:** MEDIUM — Draft should be the living record of progress. Missing implementation notes means session recovery would lack progress details.

---

## Task File Quality

Sampled `00003.auth-system.yml` (118 lines):

| CONCEPT.md Field | Present? | Quality |
|---|---|---|
| task (description) | ✅ | Clear, specific |
| wave | ✅ | Correct (0) |
| status | ✅ | Tracked (completed) |
| category | ✅ | Correct (deep) |
| context | ✅ | **Excellent** — 36 lines, includes auth flow, error envelope, route groups, user model fields |
| brief | ✅ | **Excellent** — 27 lines, step-by-step what to build |
| architecture_refs | ✅ | 3 refs |
| spec_refs | ✅ | Empty (correct — no prior specs for greenfield first tasks) |
| adr_refs | ✅ | 1 ref (001-auth-strategy.md) |
| must_do | ✅ | 11 items, specific |
| must_not_do | ✅ | 6 items, specific |
| acceptance_criteria | ✅ | 11 items, verifiable |
| plan_ref | ✅ | "00001-task-management" |
| depends_on | ✅ | [00002.project-scaffolding] |
| blocks | ✅ | [00004, 00005] |

**Task file quality is HIGH.** Self-contained, detailed context inline, all fields present. Matches CONCEPT.md example closely.

---

## Developer Plan Quality

Sampled `00003.auth-system.plan.md` (78 lines):

| CONCEPT.md Required Element | Present? |
|---|---|
| Files to create/modify | ✅ (separate lists) |
| Implementation approach | ✅ (7 execution steps) |
| Order of operations | ✅ (numbered sequence) |
| Edge cases and error handling | ✅ (risks/mitigations section) |
| How each acceptance criterion will be met | ✅ (explicit mapping section) |

**Developer plan quality is HIGH.** Matches CONCEPT.md requirements for developer planning output.

---

## Spec Generation

| Spec File | Generated After Task | 4-Layer? | source_paths? |
|---|---|---|---|
| _system.yml | 00002 | N/A (system spec) | N/A |
| project-scaffolding.yml | 00002 | ✅ | ✅ |
| auth.yml | 00003 | ✅ | ✅ (12 paths) |
| users.yml | 00004 | ✅ | ✅ |
| project-management.yml | 00005 | ✅ | ✅ |
| task-management.yml | 00006 | ✅ | ✅ |

**6 specs generated for 6 completed tasks.** Each task produced specs. Sampled auth.yml: includes interfaces (REST endpoints, routes, middleware, server-actions), source_paths, and structured data. Follows the spec schema pattern.

---

## File Naming & Structure

| Check | Result |
|---|---|
| Requirements: `{id}-{name}.md` | ✅ `00001-task-management.md` |
| Drafts: same `{id}-{name}` | ✅ `00001-task-management.md` |
| Plans: same `{id}-{name}` | ✅ `00001-task-management.md` |
| Task files: `{task-id}.{task-name}.yml` | ✅ `00002.project-scaffolding.yml` etc. |
| Developer plans: `{task-id}.{task-name}.plan.md` | ✅ `00002.project-scaffolding.plan.md` etc. |
| ADRs: 3-digit sequential | ✅ `001-auth-strategy.md` through `004-...` |
| Specs: kebab-case, not numbered | ✅ `auth.yml`, `users.yml`, etc. |
| System spec: `_system.yml` | ✅ Present |
| Kebab-case everywhere | ✅ |
| Global 5-digit IDs | ✅ |

---

## Source Code (69 files at test stop)

| Layer | Files | Correct Structure? |
|---|---|---|
| App routes (auth) | login, change-password | ✅ `(auth)/` group |
| App routes (dashboard) | dashboard, projects, users, task detail | ✅ `(dashboard)/` group |
| API routes | auth catch-all, notifications/stream | ✅ Reserved per tech-stack.yml |
| Components/UI | 10 shadcn/ui components | ✅ `components/ui/` |
| Components/Features | projects (7), tasks (8), users (3) | ✅ `components/features/` |
| Server/Actions | auth, project, task, user | ✅ `server/actions/` |
| Server/Services | project, task, user | ✅ `server/services/` |
| Server/Repositories | project, task, user | ✅ `server/repositories/` |
| Validations | auth, project, task, user | ✅ `lib/validations/` |
| Types | index.ts, next-auth.d.ts | ✅ `types/` |
| Auth | auth.config.ts, auth.ts, middleware.ts | ✅ Split config per ADR-001 |
| Prisma | schema, migration, seed | ✅ |

**Folder structure matches conventions.yml exactly.** Service → Repository → Actions layering followed.

---

## Summary

| Phase | Total Checks | Pass | Gaps | Critical |
|---|---|---|---|---|
| Discovery | 10 | 9 | 1 | 0 |
| Architecture | 11 | 9 | 2 | 0 |
| Planning | 10 | 9 | 1 | 0 |
| Delegation | 9 | 7 | 2 | 0 |
| Implementation (partial) | 6 | 5 | 1 | 0 |
| Task Files | 15 | 15 | 0 | 0 |
| Developer Plans | 5 | 5 | 0 | 0 |
| Spec Generation | 6 | 6 | 0 | 0 |
| File Naming | 10 | 10 | 0 | 0 |
| Source Structure | 12 | 12 | 0 | 0 |
| **TOTAL** | **94** | **87** | **7** | **0** |

---

## All Gaps (sorted by severity)

| Gap ID | Severity | Phase | Summary | Root Cause | Fix Location |
|---|---|---|---|---|---|
| GAP-DEL-1 | HIGH | Delegation | Plan+Implement combined into single dispatch after Task 00002. Two-step alignment loop collapsed. | Agent speed optimization. AGENTS.md says two-step but doesn't enforce strongly enough. | `out/AGENTS.md` Phase 4 — strengthen mandatory language |
| GAP-DEL-2 | HIGH | Delegation | Mandatory alignment check skipped for tasks 00003-00006. Plans reviewed post-implementation. | Same root cause as DEL-1 | Same fix as DEL-1 |
| GAP-A-1 | MEDIUM | Architecture | config.yml missing `spec_organization.unit_term` and `spec_organization.boundary` | Agent didn't populate these fields despite AGENTS.md instruction | `out/AGENTS.md` — make spec_organization fields more prominent |
| GAP-IMP-1 | MEDIUM | Implementation | Draft Implementation section not populated despite 6 tasks completing | Agent updated draft for phase transitions but not per-task progress | `out/AGENTS.md` — add explicit instruction to update draft per completed task |
| GAP-D-1 | LOW | Discovery | Clearance missing "Tech preferences captured?" (greenfield only) | AGENTS.md has 6/7 clearance items | `out/AGENTS.md` Phase 1 clearance |
| GAP-A-2 | LOW | Architecture | Clearance missing "Human aligned?" | AGENTS.md has 7/8 clearance items | `out/AGENTS.md` Phase 2 clearance |
| GAP-P-1 | LOW | Planning | Clearance missing "Feature-level scoping?" and "Plan confirmed by human?" | AGENTS.md has 6/8 clearance items | `out/AGENTS.md` Phase 3 clearance |

---

## Key Observations

1. **The framework works.** End-to-end from greenfield prompt to 69 source files + 6 specs + full architecture + task files. The agent correctly followed Discovery → Architecture → Planning → Delegation → Implementation with proper phase gates.

2. **Sub-agents are fully functional in interactive mode.** Architecture specialist wrote 8 files. Developer agents wrote source code + specs. Librarians returned research. All via tmux interactive mode.

3. **The two highest gaps (DEL-1, DEL-2) share one root cause**: the agent collapsed the plan-then-implement two-step into a single dispatch for speed. The AGENTS.md instruction exists but isn't enforced strongly enough. Fix: stronger "NEVER" language + explicit two-step protocol.

4. **All LOW gaps are clearance checklist mismatches** between AGENTS.md and CONCEPT.md. Simple fix: update AGENTS.md clearance lists.

5. **Task file quality is excellent.** 118-line self-contained technical user stories with inline context, detailed acceptance criteria, explicit guardrails. This matches the CONCEPT.md vision precisely.

6. **Spec generation works.** Every completed task produced specs. The 4-layer model and source_paths are present. System spec exists.

7. **Implementation takes ~17-21 min per task.** For a greenfield 9-task project, full implementation would take ~2.5-3 hours. This is the main practical bottleneck.

8. **`opencode run` (single-turn) is NOT viable for lifecycle testing.** Only interactive mode via tmux works for sub-agent-heavy workflows.
