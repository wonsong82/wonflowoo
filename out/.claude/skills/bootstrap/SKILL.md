---
name: bootstrap
description: "Use when adopting WonfloWoo on an existing codebase with no .wonflowoo/workspace directory. Runs the 8-step bootstrap pipeline to generate specs and architecture docs."
disable-model-invocation: true
allowed-tools: Read, Write, Bash, Grep, Glob
---

# Skill: Bootstrap Pipeline (Case 3)
Use when a running codebase has no spec system yet.

## Objective
Create feature-grouped specs and `_system.yml` without full-codebase context in one step.

## Pipeline
1. Quick Scan
2. Fan-Out Per-File Analysis
3. Summarize Metadata
4. AI Feature Grouping
5. Feature Spec Generation
6. Incremental `_system.yml`
7. Validation Pass
8. Human Review

## Principles
- Separate factual extraction from opinionated grouping.
- Keep outputs traceable to source files.
- Optimize orchestrator loading (`_system.yml` first, feature specs on demand).
- **NEVER accumulate sub-agent results in orchestrator context.** Sub-agents WRITE to files. Orchestrator reads file paths. This is how the pipeline scales to any project size.

## Working Directory

All intermediate artifacts go in `.wonflowoo/workspace/.bootstrap/` — a temporary working directory cleaned up after Step 8.

```
.wonflowoo/workspace/.bootstrap/
├── analysis/          # Step 2: per-file/batch YAML analyses
├── summaries/         # Step 3: compressed metadata
└── groups.yml         # Step 4: feature groupings
```

## Data Flow Between Steps (CRITICAL)

```
Step 1 (orchestrator)  → significant file list in memory (small)
           ↓
Step 2 (investigators) → WRITE to .wonflowoo/workspace/.bootstrap/analysis/{batch}.yml
           ↓ orchestrator receives: "done, wrote to {path}" (NOT the content)
Step 3 (compressors)   → READ from analysis/, WRITE to .wonflowoo/workspace/.bootstrap/summaries/{partition}.yml
           ↓ orchestrator receives: "done, wrote to {path}" (NOT the content)
Step 4 (orchestrator or grouping agent) → READ from summaries/, WRITE .wonflowoo/workspace/.bootstrap/groups.yml
           ↓
Step 5 (spec agents)   → READ from analysis/ (only their feature's files) + groups.yml → WRITE .wonflowoo/workspace/specs/
           ↓
Step 6 (system agent)  → READ each spec summary → WRITE .wonflowoo/workspace/specs/_system.yml incrementally
           ↓
Step 7 (validator)     → READ _system.yml + specs → report gaps
           ↓
Step 8 (orchestrator)  → Present to human → clean up .wonflowoo/workspace/.bootstrap/
```

The orchestrator stays lean (<30K tokens) regardless of project size. It coordinates via file paths, never via result contents.

## Inputs
- Source tree
- Project configs (`package.json`, `go.mod`, `pyproject.toml`, `build.gradle`, etc.)

## Required Outputs
- `.wonflowoo/workspace/specs/{feature}.yml`
- `.wonflowoo/workspace/specs/_system.yml`
- `.wonflowoo/workspace/architecture/tech-stack.yml`, `conventions.yml`, `dependencies.yml`, `system-design.md`

## Step 0: Framework Adoption + Pre-Flight (Orchestrator)

Bootstrap is the entry point for adopting WonfloWoo on an existing project. Before the analysis pipeline starts, set up the framework and handle any colliding files.

### 0a. Detect and migrate colliding files

Check for existing files/directories that collide with WonfloWoo framework paths. For EACH collision, rename to `{name}.migrated.{ext}` (or `{name}.migrated/` for directories):

| Check | If exists | Migrate to |
|---|---|---|
| `AGENTS.md` (root) | Back up — contains project conventions | `AGENTS.migrated.md` |
| `CLAUDE.md` (root) | Back up — contains project conventions | `CLAUDE.migrated.md` |
| `AGENTS.md` in subdirs (e.g., `backend/`, `frontend/`) | Back up each one | `{dir}/AGENTS.migrated.md` |
| `.wonflowoo/workspace/` directory | Back up — may have stale specs | `.wonflowoo.migrated/` |
| `.claude/` directory | Back up — may have existing agent configs | `.claude.migrated/` |

Migrated files are valuable context — reference them during spec generation.

### 0b. Install framework files

After migrations are complete:
1. Copy WonfloWoo `AGENTS.md` (or `CLAUDE.md`) to project root
2. Create `.wonflowoo/` directory structure: `framework/` + `workspace/`
3. Copy `.claude/skills/` (bootstrap, spec-generate, spec-validate) if on Claude Code
4. Copy `.opencode/oh-my-opencode.jsonc` if on OmO

### 0c. Pre-flight checks

1. **Inventory migrated files** — list all `*.migrated.*` files found; these inform spec generation
2. **Check for existing documentation** (README, docs/, wiki, etc.)
   - Any existing project docs inform spec generation — treat as read-only references
   - Don't modify them; use them as additional context alongside code analysis
3. **Verify .wonflowoo/workspace directory is ready** (framework files present, no conflicting specs)
4. **Create working directory**: `mkdir -p .wonflowoo/workspace/.bootstrap/analysis .wonflowoo/workspace/.bootstrap/summaries`

## Step 1: Quick Scan (Orchestrator)
Perform a shallow shape scan.

Inspect:
- Directory tree and file counts by area
- Language/framework/runtime signals
- Source roots and depth
- Significant source files (exclude generated/config/tests/type-only files)

Identify:
- Scale estimate
- Stack profile
- Significant file list for fan-out
- Partitioning strategy (batch size based on scale)

Output MUST be structured YAML (not markdown tables or prose):
```yaml
quick_scan:
  scale_estimate: { files: <int>, loc_estimate: <int>, depth: <int> }
  stack_signals: [<signal>, <signal>]
  source_roots: [<path>, <path>]
  significant_files: [<path>, <path>]
```

Partitioning guidance:
- Small (<50 files): skip fan-out, one agent reads all
- Medium (50-500 files): batch into 5-15 groups by module/directory affinity
- Large (500-2,000 files): batch into 15-30 groups, consider hierarchical grouping

## Step 2: Fan-Out (Per-File Analysis)

Partitioning:
- Group files by directory/module affinity (files in the same package go together)
- Target 20-60 files per batch for medium projects
- Keep each investigator independent

Each investigator:
1. Reads assigned source files
2. Produces 4-layer per-file YAML analysis
3. **WRITES output to `.wonflowoo/workspace/.bootstrap/analysis/{batch-name}.yml`** — one file per batch

Investigator prompt must include:
- The file list to analyze
- The output path to write to
- Instruction to WRITE the YAML file, then report back with ONLY: "Wrote analysis to {path}, {N} files analyzed"

Per-file analysis format:
```yaml
file_analysis:
  file: <path>
  interfaces: [...]
  logic: {...}
  data: {...}
  dependencies: {...}
```

**CRITICAL: Do NOT collect investigator output via background_output(). The investigator writes to a file. The orchestrator only receives confirmation + file path.**

## Step 3: Summarize (Metadata Extraction)

Compression agents:
1. **READ from** `.wonflowoo/workspace/.bootstrap/analysis/{batch}.yml`
2. Compress each per-file analysis into ~10-line grouping metadata
3. **WRITE to** `.wonflowoo/workspace/.bootstrap/summaries/{partition-name}.yml`
4. Report back with ONLY: "Wrote summaries to {path}, {N} files compressed"

Required summary fields per file:
```yaml
- file: src/services/auth.service.ts
  imports: [src/repositories/user.repo.ts, bcrypt, jsonwebtoken]
  exports: [AuthService]
  interfaces: [none-internal-service]
  data_touched: [users(read), refresh_tokens(read/write), redis:rate_limit(read/write)]
  domain_signals: [auth, login, token, jwt]
```

Rules:
- Factual only
- One summary per analyzed file
- Zero omissions

**CRITICAL: Do NOT collect compression output via background_output(). Same file-based pattern as Step 2.**

## Step 4: AI Feature Grouping

Now the orchestrator (or a spawned grouping agent) reads ONLY the compressed summaries:
1. **READ** all files in `.wonflowoo/workspace/.bootstrap/summaries/`
2. Group files into features using: naming patterns, import adjacency, shared data, domain keywords
3. **WRITE** `.wonflowoo/workspace/.bootstrap/groups.yml`

This is the first time the orchestrator (or grouping agent) sees cross-file data — but it's compact summaries (~10 lines/file), not raw analyses.

Output format:
```yaml
feature_groups:
  auth:
    files: [src/routes/auth.routes.ts, src/services/auth.service.ts, src/middleware/auth.middleware.ts]
  order-processing:
    files: [src/routes/order.routes.ts, src/services/order.service.ts, src/repositories/order.repo.ts]
```

Quality checks:
- Avoid giant catch-all groups (>30 files)
- Avoid excessive non-trivial single-file groups
- Keep inter-group coupling understandable
- Target 10-25 feature groups for medium projects

## Step 5: Feature Spec Generation
Generate one final feature spec per group from relevant per-file analyses.

Execution model:
- One generator agent per feature (parallel)
- Each agent reads ONLY:
  - `.wonflowoo/workspace/.bootstrap/groups.yml` (to know which files belong to their feature)
  - Relevant entries from `.wonflowoo/workspace/.bootstrap/analysis/` (only their feature's files)
  - Existing project docs or migrated files if relevant
- Each agent **WRITES** directly to `.wonflowoo/workspace/specs/{feature-name}.yml`

Each feature spec must contain:
- L1 `interfaces`
- L2 `logic` (trigger + steps + key error/security)
- L3 `data`
- L4 `dependencies`
- Top-level `source_paths`
- Every interface entry and every flow entry must include `file:` pointing to the source file

## Step 6: System Spec + Architecture Docs (DELEGATED — not orchestrator)

**CRITICAL: By this point the orchestrator has high context from managing Steps 0-5. Steps 6-7 MUST be delegated to fresh sub-agents that start with clean context.**

Spawn a `system-builder` sub-agent with instructions to:

1. Read ALL spec files from `.wonflowoo/workspace/specs/` (the 4-layer feature specs just generated)
2. Read `.wonflowoo/workspace/.bootstrap/groups.yml` (feature groupings with file lists)
3. Read the quick scan results from Step 1 (stack signals, source roots)
4. Build `_system.yml` incrementally — one feature at a time:
   - `modules[]` summary
   - `dependency_graph`
   - `data_ownership`
   - `data_relationships`
   - `cross_module_flows`
5. Also generate architecture docs:
   - `.wonflowoo/workspace/architecture/tech-stack.yml` — from detected stack
   - `.wonflowoo/workspace/architecture/conventions.yml` — from patterns observed in specs
   - `.wonflowoo/workspace/architecture/dependencies.yml` — from external package usage across specs
   - `.wonflowoo/workspace/architecture/system-design.md` — narrative with Mermaid diagrams
6. Write all files to disk. Report back with ONLY file paths written.

The sub-agent starts fresh (~5K context) and reads specs from disk. It never inherits the orchestrator's 150K+ conversation.

## Step 7: Validation Pass (DELEGATED)

Spawn a `validator` sub-agent with instructions to:

1. Read `_system.yml`
2. Read all feature specs from `.wonflowoo/workspace/specs/`
3. Read the significant file list from Step 1

Check:
- All significant files accounted for (compare file list vs all `source_paths` in specs)
- Backward check: any orphan files not in any feature?
- Dependency graph references resolve
- Data ownership/relationships complete
- Feature sizes sensible
- Major cross-module flows captured

If gaps:
- Classify (`missing_file`, `dangling_dependency`, `data_gap`, `grouping_issue`)
- Patch affected feature specs and `_system.yml`
- Report findings to orchestrator

## Step 8: Human Review
Present:
- Feature grouping map
- `_system.yml` overview
- Representative feature specs
- Generated architecture companion docs

Clearance checklist:
- [ ] Grouping matches team mental model
- [ ] Tech stack is correctly identified
- [ ] Data relationships are accurate
- [ ] No major features/files are missing
- [ ] Conventions match real team practice
- [ ] Cross-module flows capture the key business processes

Apply corrections, rerun validation, then mark bootstrap complete.

After human approval:
1. Clean up `.wonflowoo/workspace/.bootstrap/` (delete the temporary working directory)
2. Project operates as Case 2 — all future implementation uses `/spec-generate` to keep specs current

## Scaling Behavior
| Size/Profile | Strategy |
|---|---|
| Small (<50 files) | Compressed process: one capable agent can analyze all files directly; still run validation and human review |
| Medium (50-500 files) | Full 8-step pipeline with batched parallel fan-out (5-15 batches) |
| Large (500-2,000 files) | Full pipeline plus hierarchical grouping (package first, feature second) |
| Monorepo | Run pipeline per package/workspace; connect outputs via system-level dependencies |

## Completion Criteria
- Every significant source file appears in feature specs
- `_system.yml` is complete/consistent with no unresolved validation blockers
- `.wonflowoo/workspace/.bootstrap/` cleaned up
- Human clearance checklist is approved
