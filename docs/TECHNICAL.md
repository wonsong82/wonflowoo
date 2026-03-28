# WonfloWoo — Technical Details

How the framework concept is realized in concrete deliverables.

This document focuses on:
- platform mechanics (OmO + Claude Code)
- agent/skill loading behavior
- format and naming decisions
- context window budgeting
- bootstrap and spec-generation implementation details
- tested operational findings from real runs

---

## 1. Directory Architecture

WonfloWoo uses three directories: platform-specific directories (`.claude/`, `.opencode/`) auto-discovered by each platform, and a shared WonfloWoo directory (`.wonflowoo/`) split into framework + workspace.

| Directory | Purpose | Typical Contents | Shared Across Platforms? |
|---|---|---|---|
| `.claude/` | Platform-specific: Claude Code agent definitions + shared skills | `agents/*.md` (Claude-only), `skills/*/SKILL.md` (shared) | Skills: yes. Agents: Claude-only |
| `.opencode/` | Platform-specific: OmO plugin configuration | `oh-my-opencode.jsonc` | OmO-only |
| `.wonflowoo/` | Cross-platform shared files with framework/workspace split | Framework: `framework/workflow/`, `framework/agent-guides/`, `framework/schemas/`, `framework/examples/`. Workspace: `workspace/config.yml`, `workspace/specs/`, `workspace/architecture/`, `workspace/drafts/`, `workspace/plans/`, `workspace/tasks/`, `workspace/requirements/` | Yes |

### Why this split exists

1. **Platform directories are auto-discovered**
   - `.claude/` is auto-discovered by Claude Code (agents, skills).
   - `.opencode/` is auto-discovered by OmO (plugin config).
   - These exist because the platforms require them at specific paths.

2. **`.wonflowoo/` uses a framework/workspace split**
   - **Framework operating files** (`framework/workflow/`, `framework/agent-guides/`, `framework/schemas/`, `framework/examples/`) — copied during framework adoption, rarely change. These tell agents HOW to work.
   - **Project knowledge artifacts** (`workspace/specs/`, `workspace/architecture/`, `workspace/drafts/`, `workspace/plans/`, `workspace/tasks/`, `workspace/requirements/`, `workspace/config.yml`) — generated during work, change continuously. These capture WHAT the project is.
   - Both live under `.wonflowoo/` because both are cross-platform and project-scoped.

3. **Cross-platform portability**
   - `.wonflowoo/` is fully shared — both OmO and Claude Code read the same specs, architecture, workflows, and agent-guides.
   - `.claude/agents/` is Claude-only but references shared `.wonflowoo/framework/agent-guides/`.
   - OmO dispatches WonfloWoo roles using built-in specialists (`oracle`, `librarian`, `explore`) plus `sisyphus` for tech-lead roles (`architect`, `gap-analyst`, `task-writer`, `plan-reviewer`, `spec-updater`) with Role Routing in AGENTS.md.

### Updated structure (deliverable state)

```text
project-root/
│
│ # ── Platform-specific directories (auto-loaded by each platform) ──────────
│
├── AGENTS.md                        # OmO operating manual — auto-loaded by OpenCode for ALL agents
├── CLAUDE.md                        # Claude Code operating manual — auto-loaded for main session only
│
├── .claude/                         # Claude Code platform directory (auto-discovered)
│   ├── skills/                      # Slash commands — shared across platforms (OmO also reads this)
│   │   ├── bootstrap/SKILL.md       #   /bootstrap — adopt WonfloWoo on existing codebase
│   │   ├── spec-generate/SKILL.md   #   /spec-generate — AI-assisted spec creation
│   │   ├── spec-validate/SKILL.md   #   /spec-validate — spec quality checks
│   │   └── token-usage/SKILL.md     #   /token-usage — track context usage across orchestrator/sub-agents
│   └── agents/                      # Claude Code sub-agent definitions (OmO uses built-in agents instead)
│       ├── tech-lead.md             #   Slim wrapper → loads .wonflowoo/framework/agent-guides/tech-leads.md
│       ├── sr-dev.md                #   Slim wrapper → loads .wonflowoo/framework/agent-guides/developers.md (backend)
│       ├── jr-dev.md                #   Slim wrapper → loads .wonflowoo/framework/agent-guides/developers.md
│       ├── quick-dev.md             #   Slim wrapper → loads .wonflowoo/framework/agent-guides/developers.md
│       ├── frontend-dev.md          #   Slim wrapper → loads .wonflowoo/framework/agent-guides/developers.md (frontend)
│       ├── spec-updater.md          #   Slim wrapper → loads .wonflowoo/framework/agent-guides/spec-updater.md
│       ├── plan-reviewer.md         #   Claude-only wrapper (OmO dispatches plan-reviewer via sisyphus)
│       ├── architecture-consultant.md  # Claude-only (OmO uses built-in oracle agent)
│       ├── librarian.md             #   Claude-only (OmO uses built-in librarian agent)
│       └── explorer.md              #   Claude-only (OmO uses built-in explore agent)
│
├── .opencode/                       # OmO platform directory
│   └── oh-my-opencode.jsonc         #   Plugin config (agent models, categories, features)
│
│ # ── WonfloWoo directory (.wonflowoo/) ─────────────────────────────────────
│ #    Split into framework (copied) and workspace (generated).
│
└── .wonflowoo/
    │
    │ # Framework operating files (copied during adoption, rarely change)
    │
    ├── framework/
    │   ├── schemas/                 # Reference YAML schemas for validation
    │   │   ├── config.schema.yml
    │   │   ├── spec.schema.yml
    │   │   ├── system-spec.schema.yml
    │   │   ├── task-file.schema.yml
    │   │   ├── draft.template.md
    │   │   └── plan.template.md
    │   ├── workflow/                # Phase playbooks — loaded by orchestrator on phase entry
    │   │   ├── discovery.md
    │   │   ├── architecture.md
    │   │   ├── planning.md
    │   │   ├── delegation.md
    │   │   ├── implementation.md
    │   │   └── spec-interaction.md
    │   ├── agent-guides/            # Sub-agent instructions — shared across platforms
    │   │   ├── tech-leads.md        #   Spec system context, what to load (tech-lead roles)
    │   │   ├── developers.md        #   Workflow, conventions, change manifest (developer roles)
    │   │   ├── task-writer.md       #   Expands plan briefs into self-contained task instruction files
    │   │   ├── plan-reviewer.md     #   5-check review + approve/reject criteria for developer plans
    │   │   └── spec-updater.md      #   Routing logic for updating specs (spec-updater role)
    │   └── examples/                # Reference implementation (read-only)
    │       └── inventory-system/    #   Complete example with all artifact types
    │
    │ # Project knowledge artifacts (generated during work, change continuously)
    │
    └── workspace/
        ├── config.yml               # Project identity + settings (name, description, auto_proceed)
        ├── architecture/            # Design intent — written during Architecture phase
        │   ├── tech-stack.yml
        │   ├── conventions.yml
        │   ├── dependencies.yml     #   Only if external service integrations exist
        │   ├── system-design.md     #   Narrative with Mermaid diagrams
        │   └── decisions/           #   ADRs for non-obvious decisions (on-demand loaded)
        │       └── 001-*.md
        ├── specs/                   # Implementation reality — updated after every task
        │   ├── _system.yml          #   System-level view (always loaded by orchestrator + tech leads)
        │   └── {feature}.yml        #   Per-feature 4-layer specs (lazy loaded)
        ├── requirements/            # Confirmed requirements — written during Discovery
        │   └── {id}-{name}.md
        ├── drafts/                  # Living memory — orchestrator's persistent state
        │   └── {id}-{name}.md
        ├── plans/                   # Task breakdown — written during Planning
        │   └── {id}-{name}.md
        └── tasks/                   # Task files + developer plans — written during Delegation
            ├── {task-id}-{origin}.{task-name}.yml       # Self-contained task instruction
            └── {task-id}-{origin}.{task-name}.plan.md   # Developer's implementation plan
```

---

## 2. Platform Mechanics

### 2.1 Skill Discovery

Skill discovery remains stable and cross-platform compatible.

#### Claude Code
- Discovers `.claude/skills/<name>/SKILL.md`.
- Skills become slash commands (`/bootstrap`, `/spec-generate`, `/spec-validate`).
- Progressive loading behavior: metadata first, full body when invoked.

#### OmO (OpenCode)
- Scans multiple skill directories in priority order.
- `.claude/skills/` is recognized natively and remains the preferred shared location.
- Skills can be explicitly loaded in delegated runs (for example through `load_skills=[...]`).

#### Practical implication
Keeping skills in `.claude/skills/` gives one shared artifact set across platforms.

### 2.2 Agent Definitions (NEW)

#### Claude Code agent definitions

Claude agents are files at:

```text
.claude/agents/<name>.md
```

Each file uses YAML frontmatter. Deliverables currently use:
- `name`
- `description`
- `model`
- `tools`
- `skills` (present where relevant)

Example pattern (current — slim wrappers referencing shared guides):

```yaml
---
name: sr-dev
description: "Senior developer for complex multi-file implementation..."
model: opus
tools: Read, Write, Edit, Bash, Glob, Grep
---

Load `.wonflowoo/framework/agent-guides/developers.md` and follow it. Refer to the Backend focus areas section.
```

Invocation model:
- Main agent delegates with `@agent-name` (for example, `@sr-dev`, `@plan-reviewer`).
- Developers do NOT update specs — they provide change manifests. `@spec-updater` handles spec updates.

In current deliverables, Claude agent files are intentionally slim wrappers; detailed role behavior is centralized in shared `.wonflowoo/framework/agent-guides/` docs to avoid duplicating instructions across platforms.

#### OmO agent model

OmO has two practical delegation families:

1. **Built-in named specialist agents** via `subagent_type`
    - `oracle`
    - `momus`
    - `librarian`
    - `explore`
    - `sisyphus` (reasoning-heavy tech-lead work)

2. **Category-routed Sisyphus-Junior** via `category`
    - `deep` (sr-dev)
    - `unspecified-low` (jr-dev)
    - `quick` (quick-dev)
    - `visual-engineering` (frontend-dev)

**Role Routing:** On OmO, ALL agents (including sub-agents) auto-load `AGENTS.md`. The file includes a Role Routing section at the top that directs sub-agents to skip orchestrator instructions and load their role-specific guide from `.wonflowoo/framework/agent-guides/`. The dispatch prompt must include `Role: {role-name}` as the first line.

Invocation model:
- `task(subagent_type="oracle", ...)`
- `task(subagent_type="librarian", ...)`
- `task(subagent_type="sisyphus", ...)`
- `task(category="deep", ...)`

### 2.3 Sub-Agent Spawning Limitation (NEW)

Both platforms currently enforce **flat delegation**.

#### OmO
- `task()` is blocked for spawned Sisyphus-Junior sub-agents (BLOCKED_TOOLS limitation).
- Only the main session can spawn additional sub-agents.
- **Hard 50 descendant limit per root session** (`background_task.maxDescendants=50`). After 50 sub-agent spawns, no more can be created. Requires starting a new session to reset.

#### Claude Code
- Delegation from within delegated sub-agents is blocked.
- Only the top-level main tech lead session can continue fan-out delegation.
- **No hard sub-agent count limit.** The practical constraint is context window exhaustion, not a count ceiling. Long-running sessions with many delegations are limited by token budget, not a descendant counter.

#### Design implication for WonfloWoo

WonfloWoo keeps the conceptual hierarchy (main tech lead → developer/consultant reviewers), but execution is implemented as:

- **flat spawn authority** (main session only)
- **file-mediated handoffs** (`.wonflowoo/workspace/tasks/*.yml`, `.wonflowoo/workspace/tasks/*.plan.md`, plan documents)

So the workflow behaves hierarchically, while runtime spawning remains non-nested.

### 2.4 `SKILL.md` Format

Skill file format remains valid and unchanged in principle.

```markdown
---
name: bootstrap
description: "Use when adopting WonfloWoo on an existing codebase..."
disable-model-invocation: true
allowed-tools: Read, Write, Bash, Grep, Glob
---

# Skill body
...instructions...
```

Common frontmatter fields:

| Field | Required | Purpose |
|---|---|---|
| `name` | Yes | Skill ID; generally matches directory name |
| `description` | Yes | Discovery + intent matching |
| `disable-model-invocation` | No | Force explicit user invocation |
| `allowed-tools` | No | Restrict tool surface |
| `context: fork` | No | Isolated execution mode (platform-specific) |
| `model` | No | Model override (platform-specific) |
| `agent` | No | Agent hint/pinning (platform-specific) |
| `compatibility` | No | Cross-platform compatibility metadata |

---

## 3. Cross-Platform Agent Mapping (NEW)

WonfloWoo role intent is stable; execution differs by platform primitives.

| Role | OmO | Claude Code |
|---|---|---|
| `architect` | `task(subagent_type="sisyphus")` | `@tech-lead` |
| `architecture-consultant` (read-only) | `task(subagent_type="oracle")` | `@architecture-consultant` |
| `gap-analyst` | `task(subagent_type="sisyphus")` | `@tech-lead` |
| `task-writer` | `task(subagent_type="sisyphus")` | `@task-writer` |
| `plan-reviewer` | `task(subagent_type="sisyphus")` | `@plan-reviewer` |
| `spec-updater` | `task(subagent_type="sisyphus")` | `@spec-updater` |
| `librarian` | `task(subagent_type="librarian")` | `@librarian` |
| `explorer` | `task(subagent_type="explore")` | `@explorer` |
| `sr-dev` | `task(category="deep")` | `@sr-dev` |
| `jr-dev` | `task(category="unspecified-low")` | `@jr-dev` |
| `quick-dev` | `task(category="quick")` | `@quick-dev` |
| `frontend-dev` | `task(category="visual-engineering")` | `@frontend-dev` |

### Interpretation notes

1. **`subagent_type` in OmO**
   - Spawns a built-in specialist agent with specialized internal prompting.

2. **`category` in OmO**
   - Spawns Sisyphus-Junior and routes model selection by category.

3. **`@agent` in Claude Code**
    - Delegates to an isolated sub-agent defined in `.claude/agents/*.md`.

### Dispatch lookup enforcement

- Workflow docs should name role intent (for example, "Spawn `plan-reviewer`").
- The orchestrator must resolve that role via the mapping table before dispatch (`plan-reviewer` → `task(subagent_type="sisyphus")` on OmO).
- **CRITICAL:** Never pass role names as `subagent_type` values.
- OmO dispatch prompts must include `Role: {role-name}` as the first line.

---

## 4. Tool Parity Gaps (NEW)

| Capability | OmO | Claude Code | Gap |
|---|---|---|---|
| Context7 (library docs) | Built-in MCP | NOT available by default | Can configure as MCP in `.mcp.json` |
| grep_app (GitHub code search) | Built-in MCP | NOT available by default | Can configure as MCP |
| Web search (Exa/Tavily) | Built-in MCP | NOT available by default | Can configure as MCP |
| GitHub CLI (`gh`) | Available via Bash | Available via Bash | No gap |
| WebFetch | Available | Available | No gap |
| AST-grep | Available | Available | No gap |

### Operational note

OmO bundles Context7, grep_app, and websearch MCPs as first-class capabilities.

Claude Code can reach parity by explicitly wiring these MCPs in `.mcp.json`. Until that configuration exists, Claude-side research agents degrade gracefully to:
- `WebFetch`
- `gh` via Bash
- direct repository/document traversal

### Action item for full Claude librarian parity

Configure these MCPs in project `.mcp.json`:
1. Context7
2. grep_app
3. websearch

---

## 5. Category → Model Routing (UPDATED)

The framework now treats category/model mapping as **platform-native**, not `config.yml`-defined.

### OmO
- Categories are native runtime concepts.
- Routing is configured in OmO runtime settings (`.opencode/oh-my-openagent.jsonc`), not in `.wonflowoo/workspace/config.yml`.
- The old custom `plan-review` category was removed from `.opencode/oh-my-opencode.jsonc`; plan review now routes by role (`plan-reviewer`) via `task(subagent_type="sisyphus")`.

### Claude Code
- No category router in `.wonflowoo/workspace/config.yml`.
- Model selection is per-agent in `.claude/agents/*.md` frontmatter (`model: opus`, `model: sonnet`, etc.).

### Framework-level contract

WonfloWoo references **categories and roles by name**.
Each platform resolves that reference using its own native mechanism.

---

## 6. `config.yml` (UPDATED)

Current config shape:

```yaml
project:
  name: ""
  description: ""
spec_organization:
  unit_term: ""       # e.g., "module", "service", "package"
  boundary: ""        # e.g., "service-layer", "api-boundary"
auto_proceed: false
```

### Semantics

- `project.name`: filled during Architecture phase.
- `project.description`: filled during Architecture phase.
- `spec_organization.unit_term`: organizational unit from architecture (e.g., `module` for modular monolith).
- `spec_organization.boundary`: how units are separated (e.g., `service-layer` for layered arch).
- `auto_proceed`: controls phase gate behavior.
  - `false` (default): stop and require human approval at each gate.
  - `true`: automatically continue through gates.

### Removed fields

1. **`category_routing`**
   - removed from framework config because routing is platform-native.

---

## 7. Task ID Scheme (NEW/UPDATED)

WonfloWoo now uses **independent 5-digit sequences per artifact type**.

### Core rule

- Requirements: `{id}-{name}` with its own sequence (`00001`, `00002`, ...)
- Drafts: `{id}-{name}` with its own sequence (`00001`, `00002`, ...)
- Plans: `{id}-{name}` with its own sequence (`00001`, `00002`, ...)
- Tasks: `{task-id}-{origin}.{task-name}` with its own sequence (`00001`, `00002`, ...)

### Examples

```text
.wonflowoo/workspace/plans/00001-inventory-system.md

.wonflowoo/workspace/tasks/00001-inventory-system.setup-auth.yml
.wonflowoo/workspace/tasks/00001-inventory-system.setup-auth.plan.md
.wonflowoo/workspace/tasks/00002-inventory-system.create-user-roles.yml
.wonflowoo/workspace/tasks/00002-inventory-system.create-user-roles.plan.md
.wonflowoo/workspace/tasks/00003-bugfix.checkout-null.yml
.wonflowoo/workspace/tasks/00004-adhoc.update-readme.yml
```

### Linkage model

- Each task includes `plan_ref` (for example `plan_ref: "00001-inventory-system"`).
- Plan document lists task IDs for execution tracking.

`origin` semantics:
- plan-derived tasks: plan name (`inventory-system`)
- bug fix tasks: `bugfix`
- ad-hoc tasks: `adhoc`

### Stability by artifact type

- Requirements, drafts, and plans use `{id}-{name}` within their own per-type sequences.
- Specs remain non-numbered semantic names (`auth.yml`, `order-processing.yml`, `_system.yml`).

---

## 8. Core Technical Decisions (Retained + Updated)

### 8.1 File Format Decisions

#### YAML for structured artifacts

Used for:
- specs (`.wonflowoo/workspace/specs/*.yml`)
- architecture structure docs (`tech-stack.yml`, `conventions.yml`, `dependencies.yml`)
- tasks (`.wonflowoo/workspace/tasks/*.yml`)
- config (`.wonflowoo/workspace/config.yml`)
- system spec (`.wonflowoo/workspace/specs/_system.yml`)

Why YAML:
- human-readable
- machine-parseable
- multiline-friendly
- comment-capable
- good diff ergonomics

#### Markdown for narrative artifacts

Used for:
- requirements
- drafts
- plans
- task implementation plans (`*.plan.md`)
- system design narratives
- ADRs

Why Markdown:
- readable by humans and agents
- good for iterative editing
- native repository rendering
- diagram embedding support

#### Mermaid for all diagrams

All architecture/flow diagrams in markdown are Mermaid.

Why:
- text-native and versionable
- diffable
- no external design file dependency

### 8.2 File Naming Convention

#### General naming
- kebab-case for semantic names
- 5-digit zero-padded numeric IDs where IDs are required

#### Current patterns

```text
.wonflowoo/workspace/requirements/{id}-{name}.md
.wonflowoo/workspace/drafts/{id}-{name}.md
.wonflowoo/workspace/plans/{id}-{name}.md

.wonflowoo/workspace/tasks/{task-id}-{origin}.{task-name}.yml
.wonflowoo/workspace/tasks/{task-id}-{origin}.{task-name}.plan.md

.wonflowoo/workspace/specs/{feature}.yml
.wonflowoo/workspace/specs/_system.yml
```

#### Task origin segment
- planned task: `{task-id}-{plan-name}.{task-name}`
- bugfix task: `{task-id}-bugfix.{task-name}`
- ad-hoc task: `{task-id}-adhoc.{task-name}`

### 8.3 Context Window Budget Calculations

The design assumption is that no one agent should need whole-codebase context.

#### Main tech lead baseline

| Context block | Typical size |
|---|---|
| AGENTS.md / CLAUDE.md (slim core) | ~130-160 lines (OmO `AGENTS.md` currently ~8KB with Role Routing + sub-agent sections) |
| `.wonflowoo/framework/workflow/{phase}.md` (lazy per phase) | ~65-161 lines |
| `.wonflowoo/workspace/config.yml` | ~10-20 lines |
| architecture docs | ~200-500 lines |
| `_system.yml` | ~100-500 lines |
| active draft | ~50-150 lines |
| accumulated conversation | variable |
| relevant feature specs (lazy) | ~100-400 lines/spec |

Typical working range remains well below modern high-context limits when lazy loading is respected: slim core always loaded, phase workflow loaded only on phase entry, and detailed specs loaded on demand.

#### Spawned tech lead baseline

Same file context, but without long conversation history.
This keeps the delegated agent’s effective budget focused on the assigned job.

#### Developer baseline

| Context block | Typical size |
|---|---|
| task file | ~50-120 lines |
| referenced arch docs | ~100-250 lines |
| referenced specs | ~200-700 lines |
| touched source files | variable |

The task artifact acts as a compact context contract.

#### Bootstrap heavy step budget

| Step | Context profile |
|---|---|
| Quick scan | tree + config signals |
| Fan-out per-file | tiny isolated per-agent file slices |
| Metadata summarize | compact per-file summaries |
| AI grouping | all summaries in one pass (heaviest step) |
| Feature spec generation | per-feature analysis packets |
| Incremental `_system.yml` | current system + one feature summary |
| Validation pass | complete generated outputs |

Large codebases can use hierarchical grouping (package/domain first, then feature).

### 8.4 Two-Tier Spec Architecture Rationale

#### Problem

If every task loaded every detailed feature spec, context would bloat rapidly and reduce model effectiveness.

#### Solution

1. **`_system.yml` (always loaded)**
   - compressed map of modules, dependencies, ownership, cross-module relationships

2. **feature specs (lazy loaded)**
   - full detail for only touched domains

This mirrors real architecture cognition:
- start from system map
- zoom into relevant modules only

### 8.5 Bootstrap Pipeline Technical Detail (UPDATED)

Bootstrap is a **9-step pipeline** (Step 0 + Steps 1-8) with file-based delivery between steps.

#### Step 0 — Framework adoption + pre-flight
- detect colliding files (existing AGENTS.md, .wonflowoo/, .claude/) → migrate to `*.migrated.md` / `.wonflowoo.migrated/`
- install framework files (AGENTS.md, .wonflowoo/framework/{schemas,workflow,agent-guides}, .wonflowoo/workspace/config.yml, skills)
- create working directory: `.wonflowoo/workspace/.bootstrap/analysis/`, `.wonflowoo/workspace/.bootstrap/summaries/`
- inventory migrated files and existing docs as context sources

#### File-based data flow (CRITICAL for scalability)
Sub-agents write results to `.wonflowoo/workspace/.bootstrap/` files — NOT back into orchestrator context via `background_output()`. The orchestrator coordinates via file paths only, keeping context lean regardless of project size.

```
Step 2 → writes to .wonflowoo/workspace/.bootstrap/analysis/{batch}.yml
Step 3 → reads analysis/, writes to .wonflowoo/workspace/.bootstrap/summaries/{partition}.yml
Step 4 → reads summaries/, writes .wonflowoo/workspace/.bootstrap/groups.yml
Step 5 → reads analysis/ (per feature), writes .wonflowoo/workspace/specs/{feature}.yml
Steps 6-7 → delegated to fresh sub-agents (orchestrator context is high by this point)
Step 8 → cleanup: delete .wonflowoo/workspace/.bootstrap/
```

#### Step 1 — Quick scan
- detect stack/runtime signals
- identify source roots
- produce significant file list

#### Step 2 — Fan-out per-file analysis
- one investigator per significant file (or tiny coupled bundle)
- produce per-file 4-layer extraction envelope

#### Step 3 — Metadata summarize
- compress each per-file analysis into grouping metadata:
  - imports/exports
  - interfaces
  - data touched
  - domain signals

#### Step 4 — AI feature grouping
- cluster summaries into feature groups using:
  - naming cues
  - import/call adjacency
  - data overlap
  - domain keywords

#### Step 5 — Feature spec generation
- one generator per feature group
- output feature-level 4-layer spec
- include `source_paths`
- include per-flow/per-interface `file:` references

#### Step 6 — Incremental `_system.yml` generation (DELEGATED to fresh sub-agent)
- merge feature summaries into `_system.yml` one-by-one
- update:
  - `modules`
  - `dependency_graph`
  - `data_ownership`
  - `data_relationships`
  - `cross_module_flows`
- also derive architecture companion docs:
  - `tech-stack.yml`
  - `conventions.yml`
  - `dependencies.yml`
  - `system-design.md`

#### Step 7 — Validation pass (DELEGATED to fresh sub-agent)
- backward coverage check (all significant files represented)
- resolve dangling dependencies and data gaps
- patch and revalidate until blockers cleared

#### Step 8 — Human review
- confirm grouping map fits team mental model
- confirm stack/conventions/data relationship correctness
- verify no major feature/file omission

### Why this design works

- keeps low-level extraction factual and traceable
- isolates opinionated grouping to a single stage
- preserves scalability via parallel fan-out + incremental merge

### 8.6 Spec Generation Technical Detail

Spec maintenance is mandatory and AI-assisted.

#### Post-implementation spec loop

1. Developer completes code changes.
2. Developer reports a structured change manifest (files changed, interfaces, data touched).
3. Orchestrator spawns `spec-updater` with change manifest + task file + source paths + existing specs + `_system.yml`.
4. `spec-updater` updates affected feature specs in 4-layer form.
5. `spec-updater` updates `_system.yml` when cross-module topology changed.
6. Orchestrator verifies updates before marking task complete.

#### Why mandatory

Without immediate spec updates:
- orchestrator context quality decays
- future task planning drifts from reality
- code-search dependency increases (anti-goal)

#### Validation model

Three tiers:
1. structural (schema/required fields)
2. content consistency (references, dependency names, identifiers)
3. coverage metrics (forward + backward confidence)

### 8.7 Architecture Docs vs Specs

| Dimension | Architecture docs | Specs |
|---|---|---|
| Timing | Architecture phase | After implementation / updates |
| Nature | Intent + rationale | Implemented reality |
| Typical content | stack choices, conventions, high-level design, ADRs | interfaces, logic flows, data behavior, dependencies |

#### Boundary principle

- Architecture docs explain **how and why to build**.
- Specs explain **what currently exists**.

#### ADR loading policy

ADRs are usually on-demand, not always-loaded.
This prevents historical rationale from consuming routine execution context.

### 8.8 Draft as External Memory

Drafts are persistent working memory for long-lived orchestration.

They provide:
1. re-entry continuity after interrupted sessions
2. context hygiene for delegated agents
3. durable process trace

#### Re-entry logic

| Detected state | Meaning | Action |
|---|---|---|
| active draft exists | in-progress lifecycle | resume draft phase |
| active plan exists (no active draft) | implementation execution period | continue plan tracking |
| none | idle | wait for new work |

Drafts are not deleted; completion is represented via status updates.

### 8.9 Multi-Repo

Each repo is self-contained with its own `.wonflowoo/` space.

Cross-repo coupling is represented in system/spec references (for example external dependencies/contracts), not by a shared global `.wonflowoo/` database.

This keeps ownership boundaries clean and supports independent release cadence.

### 8.10 Versioning

Artifacts are versioned in Git alongside source changes.

`framework_version` in specs indicates expected schema/framework format generation era.

No external metadata store is required; repository history is the source of truth.

---

## 9. Testing Findings (NEW)

Real framework testing surfaced several operating truths that now inform this technical model.

### 9.1 `opencode run` is NOT viable for sub-agent-heavy workflows

`opencode run` single-turn mode has a timing issue: pending sub-agents aren't in the children list when the completion check fires. The main session exits before sub-agents start or complete.

`opencode run -c` (continue) helps for multi-turn but has the same sub-agent timing issue per turn.

**For full lifecycle testing, use interactive mode via tmux.** The server stays alive, sub-agents complete naturally, and system notifications trigger the orchestrator's next turn.

### 9.2 Orchestrator compaction is handled by the draft system

The orchestrator's context grows linearly with conversation turns (~25-30K per wave). For projects with 5+ waves, the orchestrator will hit context limits and the platform will compact.

This is NOT a problem because the **draft system** is the orchestrator's persistent memory — not conversation history. After compaction, the orchestrator re-reads the draft and picks up where it left off (re-entry logic). All decisions, task statuses, and progress are on disk in .wonflowoo/workspace/ files.

**Sub-agent context is the real scaling concern.** Each sub-agent starts fresh with clean context. In testing, sub-agents stayed under 65K tokens. If a sub-agent exceeds 100K, it's a red flag.

### 9.3 Phase gates depend on strong imperative wording

Phase gate behavior was more reliable when instructions were explicit and forceful, e.g.:

```text
>>> PHASE GATE: STOP <<<
```

Declarative soft language produced more accidental auto-advance behavior.

### 9.4 Sub-agent spawning is flat on both platforms

Confirmed in practice:
- OmO spawned agents cannot invoke `task()`.
- Claude delegated agents cannot further delegate via `@agent`.

Therefore orchestration must always route through the main tech lead.

### 9.5 “Research before asking” works when explicit

Discovery quality improved when rules explicitly required:
- external/domain research first
- then human interview

This reduced generic questioning and improved requirement suggestion quality.

### 9.6 Clearance checklists require explicit “show the checklist” language

Checklist compliance became reliable only when instructions mandated visible checklist output before advancing.

Implicit checklist expectations were frequently skipped in practice.

---

## Closing Summary

The current deliverable state is now:

1. Unified cross-platform skill artifacts (`.claude/skills/`).
2. Shared agent-guides (`.wonflowoo/framework/agent-guides/`) — platform-agnostic role instructions.
3. Claude agent definitions as slim wrappers referencing shared guides (`.claude/agents/`).
4. OmO AGENTS.md with Role Routing — sub-agents self-route to correct section.
5. Platform-native delegation/routing strategy (not config-routed).
6. Flat-spawn orchestration with file-based hierarchical workflow.
7. Dedicated `spec-updater` agent — developers provide change manifests, spec-updater routes to correct specs.
8. Three-step protocol (plan → review → implement) enforced in delegation.
9. Bootstrap with file-based delivery pattern — scales to 500+ file projects.
10. Slim config contract and separated task ID sequencing.
11. Tested and validated across greenfield, add-feature, and bootstrap cases.
