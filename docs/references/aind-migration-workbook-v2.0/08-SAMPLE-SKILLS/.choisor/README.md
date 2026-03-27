# Choisor Configuration Directory

Choisor 2.0 - Multi-session task orchestrator for 5-stage migration workflows.

## Directory Structure

```
.choisor/
├── README.md           # This file
├── config.yaml         # Runtime configuration (sessions, daemon, current state)
├── project.yaml        # Project-level settings (domains, phase types)
├── workflow.yaml       # Workflow definition (stages, phases, skills)
├── daemon.pid          # Daemon process ID
├── instructions/       # Task instruction files for sessions
├── logs/
│   └── sessions/       # Session execution logs
├── sessions/
│   └── sessions.json   # Active session pool state
└── tasks/
    └── tasks.json      # Task list and states
```

## Configuration Files

### config.yaml

Runtime configuration for the orchestrator.

| Section | Key Settings |
|---------|--------------|
| `assignment` | `enabled`, `delay`, `stale_timeout` |
| `auto_commit` | `enabled`, `commit_on_completion` |
| `limit_monitor` | `ignore_limit` (prevent false positives) |
| `daemon` | `refresh_interval` (seconds) |
| `provider` | `anthropic` or `bedrock` |
| `claude_code` | `max_sessions`, `max_output_tokens`, `default_model` |
| `current` | `stage`, `phase` (current position) |
| `phase_gate` | `max_allowed_phase`, `auto_to_max` |
| `work_scope` | `enabled_domains` (domain filter) |

### project.yaml

Project-level domain and phase type configuration.

| Section | Purpose |
|---------|---------|
| `feature` | ID prefix, GAP suffix handling |
| `domain` | Skip domains, priority mapping |
| `phase_types` | Phase granularity per stage (system/domain/feature) |
| `paths` | Source/target directory paths |

**Phase Types:**

| Type | Description |
|------|-------------|
| `system` | One-time task (project-level) |
| `domain` | One task per domain |
| `feature` | One task per feature (parallelizable) |

### workflow.yaml

Full workflow definition with 5 stages.

| Stage | Phases | Description |
|-------|--------|-------------|
| 1. Discovery | 4 | Feature inventory, deep analysis |
| 2. Validation | 4 | Ground truth comparison |
| 3. Preparation | 5 | Architecture design |
| 4. Generation | 5 | Code generation, tests |
| 5. Assurance | 5 | Quality validation |

## Commands

```bash
# Status and scanning
/choisor status                    # Display current status
/choisor scan [--stage N]          # Scan and update tasks.json
/choisor sync                      # Sync task status with filesystem

# Task queries
/choisor query --status pending    # Filter by status
/choisor query --domain PA         # Filter by domain
/choisor query --stage 4           # Filter by stage
/choisor query --list --limit 20   # Show task list

# Manual control
/choisor manual-assign <feature>   # Assign specific feature
/choisor clean-restart <features>  # Reset features for rework

# Session control
/choisor stop                      # Stop first running session
/choisor stop --feature FEAT-CM-001
/choisor stop --session f4fe7c8a
/choisor stop --all                # Stop all sessions
```

## Phase Gate Control

All features must complete Phase N before proceeding to Phase N+1.

```
Phase 1 ──→ Phase 2 ──→ Phase 3 ──→ Phase 4 ──→ Phase 5
   │           │           │           │           │
   └──── All features complete each phase before next ────┘
```

## Current State

Current state is tracked in `config.yaml`:

```yaml
current:
  stage: "stage1"      # stage1 | stage2 | stage3 | stage4 | stage5
  phase: "phase3"      # Current phase in progress

phase_gate:
  max_allowed_phase: "phase4"  # Maximum phase allowed
  auto_to_max: true            # Auto-advance to max phase
```

## Related Files

- `.claude/skills/choisor/SKILL.md` - Full skill documentation
- `.claude/skills/common/inter-stage-contracts.yaml` - Stage contracts
- `CLAUDE.md` - Project instructions
