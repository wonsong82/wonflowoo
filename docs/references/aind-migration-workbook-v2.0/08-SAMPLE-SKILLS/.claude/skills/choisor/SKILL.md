---
name: choisor
description: Multi-session task orchestrator for managing complex project workflows with Phase Gate control (project)
version: 2.0.0
---

# Choisor 2.0 - Task Orchestrator

A skill-centric task orchestrator for 5-stage migration workflows.

## Overview

Choisor 2.0 manages:
- **Skill-aligned Phase Gates**: Integer phases (1-5) aligned with skills
- **Dynamic Skill Discovery**: Auto-discovers skills from `.claude/skills/s{stage}-{phase}-*/SKILL.md`
- **Parallel Execution**: Native support for s4-03 + s4-04 parallel code/test generation
- **Task Prioritization**: Weighted score algorithm for optimal task ordering
- **Multi-session Orchestration**: Up to 10 parallel Claude Code sessions
- **Contract Validation**: Inter-stage data contract validation

## Commands

### User Commands

- `/choisor init [options]` - Initialize Choisor for a new project
- `/choisor status` - Display current project status, phase progress
- `/choisor scan [--stage N]` - Scan for tasks and update tasks.json
- `/choisor sync` - Synchronize task status with filesystem outputs
- `/choisor query [options]` - Query tasks with filters
- `/choisor manual-assign <feature-id>` - Manually assign specific feature
- `/choisor clean-restart <feature-ids>` - Reset features for rework
- `/choisor stop [options]` - Stop running session and release task

### Init Options

```bash
/choisor init                                    # Interactive initialization
/choisor init --template spring-migration        # Use specific template
/choisor init --template hallain-tft             # Hallain TFT preset
/choisor init --force                            # Reinitialize existing
/choisor init --list-templates                   # Show available templates
/choisor init --name my-project                  # Set project name
/choisor init --source-base legacy               # Set source directory
/choisor init --target-base generated            # Set target directory
/choisor init --java-package com/example         # Set Java package
```

**Templates:**
- `spring-migration` - Spring MVC to Spring Boot migration (default)
- `custom` - Minimal configuration for custom projects
- `hallain-tft` - Hallain TFT specific configuration

### Stop Options

```bash
/choisor stop                          # Stop first running session
/choisor stop --feature FEAT-CM-001    # Stop by feature ID
/choisor stop --session f4fe7c8a       # Stop by session ID (prefix OK)
/choisor stop --task s1-03-FEAT-CM-001 # Stop by task ID
/choisor stop --all                    # Stop all running sessions
```

### Query Options

```bash
/choisor query --status pending        # Filter by status
/choisor query --domain PA             # Filter by domain
/choisor query --stage 4               # Filter by stage
/choisor query --phase 3               # Filter by phase
/choisor query --list --limit 20       # Show task list
/choisor query --format json           # Output format
```

### Daemon Commands (internal)

- `/choisor assign-next` - Select and assign next task
- `/choisor process-completion` - Process task completion

## 5-Stage Workflow

| Stage | Name | Skills | Description |
|-------|------|--------|-------------|
| 1 | Discovery | s1-01 to s1-04 | Feature inventory, deep analysis |
| 2 | Validation | s2-01 to s2-04 | Ground truth comparison |
| 3 | Preparation | s3-01 to s3-05 | Architecture design |
| 4 | Generation | s4-01 to s4-05 | Code generation, tests |
| 5 | Assurance | s5-01 to s5-05 | Quality validation |

## Phase Gate Control

All features must complete Phase N before any feature can proceed to Phase N+1.

```
Phase 1 ──→ Phase 2 ──→ Phase 3 ──→ Phase 4 ──→ Phase 5
   │           │           │           │           │
   └──── All features complete each phase before next ────┘
```

## Parallel Execution

Choisor supports parallel execution for specific skill pairs:

- **s4-03** (domain-batch generation) + **s4-04** (test generation)

When s4-03 completes for a feature, s4-04 can run in parallel for the same feature.

## Configuration

Configuration is stored in `.choisor/config.yaml`:

```yaml
# Current position
current_stage: 1
current_phase: 1

# Phase gate settings
phase_gate:
  enabled: true
  strict_mode: true
  auto_to_max: true

# Parallel execution
parallel:
  enabled: true
  pairs:
    - ["s4-03", "s4-04"]
  max_parallel_sessions: 10

# Work scope filtering
work_scope:
  enabled_domains: null  # null = all domains
  enabled_stages: null   # null = all stages

# Paths
paths:
  skills_root: ".claude/skills"
  specs_root: "work/specs"
  contracts_path: ".claude/skills/common/inter-stage-contracts.yaml"
```

## Project Structure

```
<project-root>/
├── .choisor/
│   ├── config.yaml           # Configuration
│   ├── tasks/
│   │   └── tasks.json        # Task list and states
│   ├── sessions/
│   │   └── sessions.json     # Session pool state
│   ├── instructions/         # Instruction files
│   └── logs/                 # Session logs
└── .claude/skills/
    ├── choisor/              # This skill
    └── s{N}-{NN}-*/          # Stage skills
```

## Priority Algorithm

Tasks are prioritized using weighted scoring:

```
Score = (dependency_ready × 0.4) + (priority × 0.4) + (duration × 0.2)
```

- **dependency_ready**: 1.0 if dependencies complete, 0.0 otherwise
- **priority**: Task priority (1-10) normalized to 0-1
- **duration**: Shorter tasks preferred (inverse of estimated time)

## Usage

```bash
# Initialize Choisor for a new project
/choisor init --template spring-migration    # Initialize with template
/choisor init --list-templates               # Show available templates

# In Claude Code session
/choisor status                              # Check status
/choisor scan --stage 1                      # Scan Stage 1 tasks
/choisor query --status pending --list       # View pending tasks
/choisor manual-assign FEAT-PA-001           # Assign specific feature
/choisor stop --feature FEAT-PA-001          # Stop session working on feature
/choisor stop --all                          # Stop all running sessions

# Start daemon (separate terminal)
python -m choisor.daemon.main
```

## Key Changes from v1.0 (choisor_old)

| Feature | v1.0 (choisor_old) | v2.0 |
|---------|-------------------|------|
| Phase naming | String ("phase1") | Integer (1-5) |
| Skill discovery | Manual config | Dynamic glob |
| Parallel support | Manual | Native s4-03+s4-04 |
| Config | Dict-based | Pydantic schema |
| Task model | Dict | Dataclass |

## See Also

- `CLAUDE.md` - Project instructions
- `.claude/skills/common/inter-stage-contracts.yaml` - Stage contracts
