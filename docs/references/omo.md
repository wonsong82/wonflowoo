# Oh My OpenCode (OmO) — Reference Analysis

How OmO approaches AI-driven development, and what's relevant to our universal framework.

## What It Is

An OpenCode (Claude Code fork) plugin that turns a single AI agent into a coordinated multi-agent development team. 1268 TypeScript files, 160k LOC. Multi-model orchestration across Claude, GPT, Gemini, Kimi, GLM.

## Core Philosophy (from Manifesto)

- **Human intervention = failure signal.** If the human has to babysit the agent, the system failed. Like autonomous driving — taking the wheel means the car couldn't handle it.
- **Indistinguishable code.** Output should be indistinguishable from a senior engineer's work. No AI slop, no cleanup needed.
- **Token cost is acceptable if productivity gains are real.** Parallel agents, thorough verification, accumulated knowledge — worth the tokens.
- **Minimize human cognitive load.** Human provides intent. Agent handles everything else.
- **Predictable, continuous, delegatable.** Like a compiler: markdown in, working code out. Survives interruptions. Self-correcting.

## Agent Architecture

### Three Layers

```
PLANNING LAYER (Human + AI)
  Prometheus (Planner) — interviews user, creates detailed plans
  Metis (Consultant) — catches gaps Prometheus missed
  Momus (Reviewer) — ruthless validation: OKAY or REJECT

EXECUTION LAYER (Conductor)
  Atlas (Conductor) — reads plan, delegates tasks, accumulates wisdom, verifies
  Sisyphus (Orchestrator) — main agent for direct interaction, delegates via categories

WORKER LAYER (Specialists)
  Sisyphus-Junior — category-spawned executor (cannot re-delegate)
  Oracle — read-only architecture consultant (GPT-5.4)
  Explore — fast codebase grep (cheap models)
  Librarian — documentation/OSS search (Gemini Flash)
```

### Agent Roles Mapped to Our Model

| OmO Agent | Our Framework Analog | Notes |
|---|---|---|
| Prometheus | Orchestrator in Discovery phase | Interview-based requirements extraction |
| Metis | Quality gate on Discovery | Gap analysis before planning |
| Momus | Quality gate on Planning | Validates plans meet clarity/verification thresholds |
| Atlas | Orchestrator in Delegation phase | Conductor that coordinates but doesn't code |
| Sisyphus | Orchestrator (general) | Main agent, full lifecycle |
| Sisyphus-Junior | Developer (subagent) | Focused executor, cannot delegate further |
| Oracle | Specialist consultant | Architecture advice, debugging |
| Explore | Research tool (internal) | Codebase pattern discovery |
| Librarian | Research tool (external) | Docs, OSS, web search |

## Category System (How Work Gets Routed)

Instead of picking models by name, work is routed by **semantic category**. Category → model mapping is automatic.

| Category | Default Model | Domain |
|---|---|---|
| `visual-engineering` | Gemini 3.1 Pro | Frontend, UI/UX |
| `ultrabrain` | GPT-5.4 (xhigh) | Hard logic, architecture |
| `deep` | GPT-5.3 Codex | Autonomous problem-solving |
| `artistry` | Gemini 3.1 Pro (high) | Creative tasks |
| `quick` | GPT-5.4 Mini | Trivial changes |
| `unspecified-low` | Claude Sonnet 4.6 | Low-effort misc |
| `unspecified-high` | Claude Opus 4.6 (max) | High-effort misc |
| `writing` | Gemini 3 Flash | Documentation, prose |

**Key insight**: The orchestrator describes INTENT (what kind of work), not implementation (which model). This decouples task description from model selection.

## Skills System

Skills inject specialized knowledge + tools into agents:
- **Prompt injection** — domain-specific instructions prepended to system prompt
- **Embedded MCPs** — skills carry their own MCP servers, spun up on-demand
- **Category + Skill combos** — e.g., `visual-engineering` + `frontend-ui-ux` + `playwright`

Built-in: `git-master`, `playwright`, `frontend-ui-ux`, `dev-browser`

Custom skills via `SKILL.md` files in `.opencode/skills/` or `~/.config/opencode/skills/`.

## Context Management

### Hierarchical AGENTS.md (`/init-deep`)

Auto-generates AGENTS.md files at multiple directory levels:

```
project/
├── AGENTS.md              ← project-wide (50-150 lines)
├── src/
│   ├── AGENTS.md          ← src-specific (30-80 lines)
│   └── components/
│       └── AGENTS.md      ← component-specific
```

- **Scoring system** determines which dirs warrant AGENTS.md (file count, subdir count, symbol density, reference centrality)
- **Child never repeats parent** — only directory-specific deviations
- **Auto-injected** when agent reads files in that directory
- **Quality gates**: telegraphic style, no generic advice, no obvious info

### Wisdom Accumulation

After each delegated task, the orchestrator:
1. Extracts learnings from subagent's response
2. Categorizes into: Conventions, Successes, Failures, Gotchas, Commands
3. Passes forward to ALL subsequent subagents

Stored in `.sisyphus/notepads/{plan-name}/`:
- `learnings.md`, `decisions.md`, `issues.md`, `verification.md`, `problems.md`

### Session Continuity

- `boulder.json` tracks active plan, session IDs, progress
- `/start-work` resumes from last checkpoint
- `/handoff` creates structured context summary for new sessions

## Enforcement Mechanisms

| Mechanism | Purpose |
|---|---|
| Todo Continuation Enforcer | Yanks idle agents back to work — "you have incomplete todos" |
| Ralph Loop / ULW Loop | Self-referential loop until DONE signal detected |
| Comment Checker | Strips AI slop from comments |
| Write File Guard | Prevents overwriting without reading first |
| Prometheus MD-Only | Planner can only write markdown (no code) |
| Tool Restrictions | Oracle/Librarian/Explore are read-only — cannot write or delegate |
| Sisyphus-Junior Restrictions | Cannot re-delegate (blocked from task tool) |

## Workflow Modes

### Ultrawork (`ulw`) — "Just Do It"
Human provides intent. Agent figures out everything. Keeps going until done. No planning phase.

### Prometheus → Atlas — "Precise Orchestration"
1. Prometheus interviews human, creates plan in `.sisyphus/plans/`
2. Metis gap-analyzes the plan
3. Momus validates (OKAY/REJECT loop)
4. `/start-work` → Atlas executes plan, delegating to Junior agents
5. Wisdom accumulates across tasks

## Planning System (Prometheus — Deep Dive)

Prometheus is OmO's dedicated planning agent. It's a 3-phase system: Interview → Plan Generation → Optional High Accuracy Review.

### Phase 1: Interview Mode

Prometheus classifies the user's intent FIRST, then adapts its interview depth:

| Intent Type | Strategy | Interview Depth |
|---|---|---|
| Trivial/Simple | Fast turnaround | "I see X, should I also do Y?" → propose action |
| Build from Scratch | Discovery focus | Research codebase FIRST, then ask informed questions |
| Refactoring | Safety focus | Map impact scope + test coverage, then ask about constraints |
| Mid-sized Task | Boundary focus | Define exact outputs, explicit exclusions, guardrails |
| Collaborative | Dialogue focus | Explore together, incremental clarity |
| Architecture | Strategic focus | Consult Oracle (expensive model), research best practices |
| Research | Investigation focus | Parallel probes, synthesis, exit criteria |

**Key behaviors:**

- **Research before asking**: For build-from-scratch, fires explore/librarian agents BEFORE asking the user anything. Results in informed questions like "I found your app uses Next.js 14 with App Router. Do you want to extend the existing session pattern, or use NextAuth?" — not generic "what framework do you want?"
- **Draft as working memory**: Writes `.sisyphus/drafts/{name}.md` and updates after EVERY exchange. Records: requirements, decisions, research findings, open questions, scope boundaries. This is the agent's external memory — prevents context loss in long conversations.
- **Clearance checklist** after every turn: Core objective clear? Scope boundaries? No ambiguities? Tech approach decided? Test strategy? If ALL YES → auto-transition to plan generation. If any NO → ask the specific unclear question.
- **Test infrastructure assessment** (mandatory): Detects if tests exist in the project, asks user to decide TDD / tests-after / none. This decision affects the entire plan structure.
- **Never passive**: Every turn ends with either a specific question, a draft update + next question, or auto-transition to planning. Never "let me know if you have questions."

### Phase 2: Plan Generation

Triggered automatically (clearance check passes) or explicitly ("create the work plan"):

**Step 1 — Metis consultation (mandatory)**: Before generating the plan, summons Metis (gap analysis agent) with full context: user's goal, key discussion points, research findings. Metis identifies: questions not asked, guardrails needed, scope creep areas, unvalidated assumptions, missing acceptance criteria, unaddressed edge cases.

**Step 2 — Generate plan**: Writes to `.sisyphus/plans/{name}.md`. Includes:
- TL;DR (summary, deliverables, estimated effort, parallel execution info, critical path)
- Context (original request, interview summary, research findings, Metis review)
- Work Objectives (core objective, concrete deliverables, definition of done, must have, must NOT have)
- Verification Strategy (test decision, QA policy — zero human intervention, all agent-executed)
- Execution Strategy — **parallel execution waves**:
  - Wave 1: Foundation + scaffolding (start immediately)
  - Wave 2: Core modules (max parallel, after Wave 1)
  - Wave 3: Integration + UI (after Wave 2)
  - Wave FINAL: 4 parallel review agents — all must approve, then human gives final okay
- Each task includes: what to do, must NOT do, recommended agent category + skills (with justification), parallelization info (wave, blocks, blocked by), exhaustive references (pattern/API/test/external — with WHY each matters), acceptance criteria (agent-executable only), QA scenarios (exact tool + exact steps + exact assertions + evidence path)

**Step 3 — Self-review**: Classify gaps:
- **Critical** (requires user decision) → placeholder in plan, ask specific question with options
- **Minor** (can self-resolve) → fix silently, note in summary
- **Ambiguous** (has reasonable default) → apply default, disclose in summary

**Step 4 — Present summary**: Key decisions made, scope IN/OUT, guardrails applied, auto-resolved items, defaults applied, decisions needed (if any).

### Phase 3: High Accuracy Mode (Optional Momus Review Loop)

If user opts in, the plan enters a **Momus review loop**:

```
while (true) {
  result = submit plan to Momus
  if result === "OKAY" → break
  else → fix ALL issues, resubmit (no maximum retries, no shortcuts)
}
```

Momus only says "OKAY" when:
- 100% of file references are verified as real
- ≥80% of tasks have clear reference sources
- ≥90% of tasks have concrete acceptance criteria
- Zero tasks require unvalidated business logic assumptions
- Zero critical red flags

**Rules**: No excuses, fix EVERY issue (not just some), keep looping until "OKAY" or user explicitly cancels. Quality is non-negotiable when high accuracy is requested.

### Planning Constraints (Prometheus Identity)

- **Planner, never implementer**: Even if user says "just do it", Prometheus refuses to write code. Plans only.
- **Markdown-only file access**: Can only create/edit `.md` files. Enforced by system hook.
- **Single plan mandate**: No matter how large the task, everything goes into ONE plan. 50+ TODOs is fine. Split plans cause lost context and forgotten requirements.
- **Maximum parallelism**: Plans must maximize parallel execution. Target 5-8 tasks per wave. Fewer than 3 per wave (except final) = under-splitting. One task = one module/concern = 1-3 files.

### What's Relevant to Our Framework from Planning

- **Intent classification → adaptive interview depth**: Don't interview the same way for a typo fix as for a new feature. Scale ceremony to task complexity.
- **Research before asking**: Investigate the codebase first, then ask informed questions. Results in much better requirements.
- **Draft as external memory**: For long planning sessions, persist decisions to a file so nothing gets lost.
- **Clearance checklist**: A concrete gate for "are we ready to plan?" — prevents premature planning on incomplete requirements.
- **Gap classification (Critical/Minor/Ambiguous)**: Not all gaps need user input. Self-resolve what you can, disclose defaults, only escalate what you must.
- **Parallel execution waves with dependency tracking**: Tasks grouped by dependency layer, maximizing throughput.
- **QA scenarios as part of the plan**: Each task comes with exact verification steps — not "test it works" but specific selectors, data, assertions, evidence paths.
- **Final verification wave**: Multiple independent reviewers check different dimensions (compliance, quality, QA, scope fidelity) in parallel.
- **Optional high-accuracy review loop**: For high-stakes work, a separate reviewer validates the plan itself before execution begins.

---

## What's Relevant to Our Framework

### Directly applicable:
- **Hierarchical AGENTS.md** — context at multiple directory levels, auto-injected
- **Category system** — semantic task routing decoupled from model selection
- **Skills system** — injectable domain knowledge + tools
- **Wisdom accumulation** — learnings persist and propagate across tasks
- **Enforcement hooks** — agents stay on task, produce quality output
- **Session continuity** — work survives interruptions, resumes from checkpoints
- **Planning validation loop** — Metis + Momus catch gaps before implementation

### Needs adaptation for universality:
- **Tight coupling to OpenCode/Claude Code** — our framework must be harness-agnostic
- **Model-specific defaults** — our framework shouldn't assume which models exist
- **Plugin architecture** — OmO is a plugin; our framework is a specification, not code
- **Scoring thresholds for init-deep** — tuned for TypeScript projects; needs generalization
- **Agent restrictions via tool blocking** — implementation-specific; our framework needs conceptual equivalents

### Key gaps OmO doesn't address (that we should):
- **Multi-repo orchestration** — OmO operates within a single repo
- **Team coordination** — no model for multiple human developers + agents
- **Bootstrapping** — no standard process for generating specs from an existing codebase
- **Language/framework agnosticism** — AGENTS.md format is implicit, not specified
- **Spec system** — OmO uses hierarchical AGENTS.md but doesn't have the structured YAML spec layer from our ai-service draft

---

*Analyzed from: `references/oh-my-openagent/` — docs, agents, features, manifesto, orchestration guide, prometheus (interview-mode, plan-generation, high-accuracy-mode, identity-constraints, plan-template, system-prompt).*
