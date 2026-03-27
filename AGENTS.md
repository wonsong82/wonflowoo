# AGENTS.md — WonfloWoo (One Flow)

## What This Project Is

**WonfloWoo (One Flow)** — a universal **AI-aided development workflow** specification that works across **all** project shapes:

| Dimension | Range |
|---|---|
| Scale | Tiny side project ↔ Enterprise (100+ microservice repos) |
| Repo structure | Single repo ↔ Multi-repo ↔ Monorepo |
| Team size | Solo developer ↔ 30+ collaborators |
| Maturity | Greenfield ↔ Legacy brownfield |

The goal: **one AI-assisted workflow system that adapts to any of these combinations** — not a lowest-common-denominator compromise, but a system that scales its ceremony and structure to match the context. The AI agent should be able to onboard itself, understand the project's shape, and work effectively regardless of the environment it drops into.

## Why It Matters

AI coding agents today have no standard way to understand and operate within a project. Every project reinvents its own onboarding — or has none, leaving agents to guess. This project defines a universal specification so an AI agent can drop into *any* project and know how to navigate, contribute, and follow the right conventions.

## Project Structure

```
20260318-agentsmd/
├── AGENTS.md                  # This file — project instructions
├── README.md                  # WonfloWoo summary / pitch
├── docs/                      # Design documents
│   ├── CONCEPT.md             # Full WonfloWoo specification
│   ├── TECHNICAL.md           # Platform mechanics, context budgets, implementation details
│   ├── TODO.md                # Pending enhancements
│   └── references/            # Source materials (OmO, Choisor, analysis)
│       └── oh-my-openagent/   # OmO plugin source code — use this for agent behavior reference
├── out/                       # Deliverables — what gets copied into adopting projects
│   ├── AGENTS.md              # OmO/OpenCode agent instructions
│   ├── CLAUDE.md              # Claude Code agent instructions
│   ├── .claude/               # Claude Code agents + skills
│   │   ├── agents/            # Agent configs (tech-lead, sr-dev, jr-dev, etc.)
│   │   └── skills/            # Framework skills (bootstrap, spec-generate, spec-validate)
│   ├── .opencode/             # OmO plugin config
│   └── .wonflowoo/            # Framework + workspace directory
│       ├── framework/          # Copied during adoption (workflow, agent-guides, schemas)
│       └── workspace/          # Generated during work (config, specs, architecture, tasks, etc.)
├── test-results/              # Extracted test results (committed)
│   ├── greenfield-v1.md
│   ├── greenfield-v2.md
│   ├── greenfield-v3.md
│   ├── greenfield-v4.md
│   ├── bootstrap.md
│   └── add-feature.md
└── tests/                     # E2E test environments (gitignored — local only)
```

**IMPORTANT:** When looking up OmO agent behavior (Sisyphus, Momus, Oracle, etc.), check `docs/references/oh-my-openagent/src/agents/` for actual source code. Do NOT guess — read the source.

## Status

**Phase: v1 Complete** — Specification, deliverables, schemas, examples, and skills all produced. Ready for real-project validation.

## How to Test the Framework

### Testing Strategy

Tests live in `tests/`. Each test is a self-contained folder with framework deliverables copied in + generated artifacts from the test run.

**Principles:**
- Each test folder is created by copying deliverables from `out/`, then running the framework against it
- Test folders are kept for review — do NOT delete until user confirms
- Use **cheap/fast models** for generating sample projects (when test needs existing source code)
- For full lifecycle testing, use **tmux interactive mode** (see Testing Notes below)

### CLI Quick Reference

```bash
# Claude Code (non-interactive, skip permissions for testing)
cd tests/{test-folder}/
claude -p "{test prompt}" --model sonnet --dangerously-skip-permissions

# OmO — single turn (new session each time — sub-agent results may not persist)
cd tests/{test-folder}/
opencode run "{test prompt}"

# OmO — multi-turn using SAME session (preserves sub-agent state + context)
cd tests/{test-folder}/
opencode run "{first prompt}"                    # creates a session
opencode run -c "{second prompt}"                # continues LAST session
opencode run -s {session-id} "{second prompt}"   # continues SPECIFIC session

# OmO — interactive (best for full lifecycle testing)
cd tests/{test-folder}/
opencode
```

### Testing Notes (Learned from Practice)

**`opencode run` is NOT viable for sub-agent-heavy lifecycle tests:**
- `opencode run` single-turn mode has a timing issue: pending sub-agents aren't in the children list when the completion check fires. The main session exits before sub-agents start or complete.
- `opencode run -c` (continue) helps for multi-turn but still has the same sub-agent timing issue per turn.
- **For full lifecycle testing (Discovery → Implementation), use interactive mode via tmux:**

```bash
# Start opencode in tmux (stays alive, sub-agents work properly)
tmux new-session -d -s test-session -c /path/to/tests/case-name
tmux send-keys -t test-session "opencode" Enter
# Wait for TUI to start (~5s)
tmux send-keys -t test-session "your prompt here" Enter
# Note: may need an extra Enter to submit (TUI quirk)
tmux send-keys -t test-session Enter
# Monitor via capture-pane
tmux capture-pane -t test-session -p
# Export session for full conversation
opencode export {session-id}
```

**Why tmux is required:** Interactive mode keeps the server alive. When sub-agents complete, the system sends `<system-reminder>` notifications that trigger the main agent's next turn. This is the natural flow — `opencode run` artificially truncates it.

**`opencode run` single-turn is fine for:**
- Simple tests with no sub-agents (skill loading, context detection)
- Quick validation prompts

**`opencode run` single-turn is NOT fine for:**
- Any test involving developer sub-agents writing code
- Architecture phase (spawns architect specialist)
- Delegation + Implementation (spawns tech leads + developers)

**Sub-agent spawning limitation (both platforms):**
- Sub-agents (Sisyphus-Junior on OmO, @agents on Claude Code) CANNOT spawn further sub-agents. `task()` is blocked for sub-agents.
- Only the main session can call `task()` / delegate to `@agent`. All spawning is flat — main orchestrator dispatches everything.
- The framework concept (tech lead → developer) is preserved via files: developer writes .plan.md → main spawns tech lead to review → main spawns developer to implement.

**Session continuation for multi-phase testing:**
```bash
# Phase 1
opencode run "I want to build a task management app..."
# Phase 2 (continue same session — agent has all prior context)
opencode run -c "Yes proceed to architecture."
# Phase 3
opencode run -c "Architecture approved. Proceed."
```

**Why tmux is required:** Interactive mode keeps the server alive. When sub-agents complete, the system sends `<system-reminder>` notifications that trigger the main agent's next turn. This is the natural flow — `opencode run` artificially truncates it.

### What to Validate

| Test | Expected Result |
|---|---|
| Fresh session, no specs | Agent detects uninitialized state, asks greenfield vs bootstrap |
| Greenfield prompt | Agent creates draft, starts Discovery interview |
| Bootstrap prompt | Agent invokes /bootstrap skill, follows 8-step pipeline |
| Add feature (initialized) | Agent loads _system.yml + relevant specs, starts Discovery |
| /bootstrap command | Skill discovered and loaded on both platforms |
| /spec-generate command | Skill discovered and loaded on both platforms |
| /spec-validate command | Skill discovered and loaded on both platforms |
| Draft persistence | After interrupting a session, new session finds and resumes from draft |

### How to Run an E2E Case Test

When the user says "run greenfield test" (or any of the 6 cases), follow this procedure:

**Step 1: Set up test environment**
```bash
# Create test folder
mkdir -p tests/{case-name}/.wonflowoo/framework tests/{case-name}/.wonflowoo/workspace tests/{case-name}/.claude tests/{case-name}/.opencode

# Copy framework deliverables
cp out/AGENTS.md tests/{case-name}/AGENTS.md
cp -r out/.claude/skills tests/{case-name}/.claude/skills
cp -r out/.claude/agents tests/{case-name}/.claude/agents
cp -r out/.wonflowoo/framework/* tests/{case-name}/.wonflowoo/framework/
cp out/.opencode/oh-my-opencode.jsonc tests/{case-name}/.opencode/oh-my-opencode.jsonc
```

For cases that need existing source code (bootstrap, add-feature, bugfix, refactoring, migration):
- Generate a small sample project using a **quick/cheap model** (task with category="quick")
- For bootstrap: source code only, no .wonflowoo/ specs
- For add-feature: source code + copy example specs from `out/.wonflowoo/framework/examples/inventory-system/`
- For bugfix/refactoring/migration: same as add-feature (needs initialized .wonflowoo/workspace/)

**Step 2: Run the test**

Best approach: use `opencode` in tmux (interactive mode). See Testing Notes above.

```bash
cd tests/{case-name}

# Start opencode in tmux
tmux new-session -d -s test -c $(pwd)
tmux send-keys -t test "opencode" Enter
# Wait for TUI (~5s), then send prompt
tmux send-keys -t test "{human request}" Enter
tmux send-keys -t test Enter
```

**Human prompts per case (use these, no coaching):**

| Case | Initial prompt |
|---|---|
| **Greenfield** | "I want to build a task management app. Users can create projects, add tasks, assign to team members, set due dates, mark done. Simple dashboard for overdue tasks and progress. About 5 users." |
| **Add Feature** | "I want to add a comments feature to tasks. Users should be able to add comments, see comment history, and get notified when someone comments on their task." |
| **Bootstrap** | "Set up the AI workflow for this existing project." |
| **Bug Fix** | "Users are getting 500 errors when they try to mark tasks as complete." |
| **Refactoring** | "The task service is getting too big. Split it into separate concerns — task CRUD, assignment logic, and notification logic." |
| **Migration** | "Migrate the backend from Express to Fastify." |

**Step 3: Validate against CONCEPT.md (DYNAMIC — not a static checklist)**

Your source of truth is `docs/CONCEPT.md`. Do NOT validate from memory or a hardcoded list.

For each phase the test enters:
1. Read the relevant section of `docs/CONCEPT.md` (e.g., "Phase 1: Discovery" for Discovery)
2. Read the relevant case flow (e.g., "Case 1: Start Fresh (Greenfield)")
3. Extract EVERY requirement, step, clearance item, output specification, and rule from the spec
4. Compare against what the agent actually did and what files were actually generated
5. Report: PASS (matches spec) or GAP (spec says X, agent did Y or didn't do it)

**What to check per phase (derived from CONCEPT.md at test time):**
- Every step listed in the phase — was it performed?
- Every clearance checklist item — was it checked and shown?
- Phase gate — did the agent STOP and wait?
- Output files — do they exist at the correct paths with correct naming convention?
- Output content — does it match the spec's description? (e.g., requirements doc should NOT contain tech stack)
- Specialist spawning — was it done where the spec says it's required?
- File naming convention — do task IDs, plan refs, status fields match the spec?

**Step 4: Check generated files**

```bash
# What was generated?
find tests/{case-name}/.wonflowoo -type f | sort

# Read and compare each artifact against CONCEPT.md's specified format
```

For each generated file, read it and check:
- Does it follow the schema in `out/.wonflowoo/framework/schemas/`?
- Does it match the format described in CONCEPT.md?
- Are all required fields present?
- Does naming follow the convention in CONCEPT.md's "File Naming Convention" section?

**Step 5: Record results (MANDATORY for every test)**

Every test MUST produce a `GAP_ANALYSIS.md` in the test folder — even if there are zero gaps. This is the test deliverable.

```
tests/{case-name}/GAP_ANALYSIS.md
```

Required structure:
1. **Header** — test date, platform, session ID, app/project, duration, result
2. **What this test validates** — list the specific features/changes being tested
3. **Phase-by-phase results** — table per phase with check # / requirement / result
4. **New feature validation** (if testing new features) — table with feature / status / evidence
5. **Gap details** (if any):
   ```
   ### GAP-{phase}-{number}: {title}
   **CONCEPT.md says:** {exact quote or reference with line/section}
   **What happened:** {what the agent actually did}
   **Severity:** CRITICAL / MEDIUM / LOW
   ```
6. **Scalability check** — for EVERY test, record:
   - Orchestrator context progression (min → max tokens, growth rate per wave)
   - Sub-agent context usage (min/max per role)
   - Flag if any sub-agent exceeded 100K or needed compaction
   - Flag if orchestrator compacted and verify draft-based re-entry worked
   - Note: sub-agent context issues are real scaling problems. Orchestrator compaction is expected and handled by the draft system.
7. **Summary table**:
   ```
   | Phase | Checks | Pass | Gaps |
   |---|---|---|---|
   | Discovery | N | N | N |
   | ... |
   | TOTAL | N | N | N |
   ```

Keep test folder for review — do NOT clean up until the user confirms.
```
