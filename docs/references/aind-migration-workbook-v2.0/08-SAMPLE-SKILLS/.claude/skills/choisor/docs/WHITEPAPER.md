# Choisor 2.0 - Task Orchestrator Whitepaper

**Version**: 2.0.0
**Last Updated**: January 2026
**Author**: Choisor Development Team

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Core Concepts](#2-core-concepts)
   - 2.1 [What is Choisor?](#21-what-is-choisor)
   - 2.2 [Key Terminology](#22-key-terminology)
   - 2.3 [Architecture Overview](#23-architecture-overview)
3. [5-Stage Migration Workflow](#3-5-stage-migration-workflow)
   - 3.1 [Stage Overview](#31-stage-overview)
   - 3.2 [Phase Types](#32-phase-types-systemdomainfeature)
   - 3.3 [Phase Gate Control](#33-phase-gate-control)
4. [Getting Started](#4-getting-started)
   - 4.1 [Prerequisites](#41-prerequisites)
   - 4.2 [Project Initialization](#42-project-initialization)
   - 4.3 [Directory Structure](#43-directory-structure)
5. [Configuration](#5-configuration)
   - 5.1 [config.yaml (Runtime Settings)](#51-configyaml-runtime-settings)
   - 5.2 [project.yaml (Project Properties)](#52-projectyaml-project-properties)
   - 5.3 [workflow.yaml (Workflow Definition)](#53-workflowyaml-workflow-definition)
6. [Commands Reference](#6-commands-reference)
   - 6.1 [Initialization Commands](#61-initialization-commands)
   - 6.2 [Status & Monitoring Commands](#62-status--monitoring-commands)
   - 6.3 [Task Management Commands](#63-task-management-commands)
   - 6.4 [Session Control Commands](#64-session-control-commands)
7. [Task Lifecycle](#7-task-lifecycle)
   - 7.1 [Task Generation](#71-task-generation)
   - 7.2 [Task States](#72-task-states)
   - 7.3 [Priority Algorithm](#73-priority-algorithm)
8. [Multi-Session Orchestration](#8-multi-session-orchestration)
   - 8.1 [Daemon Architecture](#81-daemon-architecture)
   - 8.2 [Session Pool Management](#82-session-pool-management)
   - 8.3 [Parallel Execution](#83-parallel-execution)
9. [Plugin Architecture](#9-plugin-architecture)
   - 9.1 [Plugin Types](#91-plugin-types)
   - 9.2 [Creating Custom Plugins](#92-creating-custom-plugins)
   - 9.3 [Default Plugins](#93-default-plugins)
10. [Validation System](#10-validation-system)
    - 10.1 [Stage Validators](#101-stage-validators)
    - 10.2 [Contract Validation](#102-contract-validation)
    - 10.3 [Quality Gates](#103-quality-gates)
11. [Best Practices](#11-best-practices)
    - 11.1 [Workflow Optimization](#111-workflow-optimization)
    - 11.2 [Error Handling](#112-error-handling)
    - 11.3 [Troubleshooting](#113-troubleshooting)
- [Appendix](#appendix)
  - [A. Configuration Reference](#a-configuration-reference)
  - [B. Command Quick Reference](#b-command-quick-reference)
  - [C. Glossary](#c-glossary)

---

## 1. Executive Summary

**Choisor 2.0** is a skill-centric task orchestrator designed for managing complex, multi-stage migration workflows. Originally developed for Spring MVC to Spring Boot migration projects, Choisor provides a comprehensive framework for orchestrating AI-assisted code transformation at enterprise scale.

### Key Capabilities

| Capability | Description |
|------------|-------------|
| **Dynamic Skill Discovery** | Auto-discovers skills from `.claude/skills/s{stage}-{phase}-*/SKILL.md` patterns |
| **Phase Gate Control** | Ensures all features complete Phase N before any proceeds to Phase N+1 |
| **Parallel Execution** | Native support for concurrent task execution (e.g., s4-03 + s4-04) |
| **Multi-Session Orchestration** | Manages up to 10 parallel Claude Code sessions |
| **Contract Validation** | Inter-stage data contract validation with severity-based reporting |
| **Plugin Architecture** | Extensible system for custom generators and validators |

### Target Use Cases

- **Legacy Code Migration**: Spring MVC → Spring Boot, iBatis → MyBatis
- **Large-Scale Refactoring**: Enterprise applications with 1000+ files
- **AI-Assisted Development**: Automated code generation with human oversight
- **Workflow Automation**: Multi-stage, dependency-aware task execution

### Design Principles

1. **QUERY-FIRST**: SQL preservation is paramount - 100% query compatibility
2. **Phase Gate Discipline**: Orderly progression prevents cascading errors
3. **Skill Alignment**: Tasks mapped 1:1 with discoverable skills
4. **Configuration over Code**: Workflow changes via YAML, not code modifications

---

## 2. Core Concepts

### 2.1 What is Choisor?

Choisor (pronounced "choi-sor") is an orchestration layer that sits between Claude Code sessions and complex migration workflows. It solves several critical challenges:

**Problem**: Large migration projects involve hundreds of features, each requiring multiple transformation phases. Manual coordination is error-prone and doesn't scale.

**Solution**: Choisor provides:
- Automated task discovery from filesystem structure
- Intelligent task prioritization and assignment
- Phase gate enforcement for workflow integrity
- Multi-session parallelization for throughput
- Validation checkpoints for quality assurance

```
┌─────────────────────────────────────────────────────────────┐
│                     Choisor Orchestrator                    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Phase     │  │   Task      │  │   Session   │         │
│  │   Gate      │  │   Queue     │  │   Pool      │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│         │               │                │                  │
│         └───────────────┼────────────────┘                  │
│                         ▼                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  Scheduler                           │   │
│  │    - 5-second polling interval                       │   │
│  │    - Priority-based task selection                   │   │
│  │    - Session assignment                              │   │
│  └─────────────────────────────────────────────────────┘   │
│                         │                                   │
│         ┌───────────────┼───────────────┐                  │
│         ▼               ▼               ▼                  │
│  ┌───────────┐   ┌───────────┐   ┌───────────┐            │
│  │ Session 1 │   │ Session 2 │   │ Session N │            │
│  │  (Opus)   │   │  (Opus)   │   │  (Opus)   │            │
│  └───────────┘   └───────────┘   └───────────┘            │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Key Terminology

| Term | Definition |
|------|------------|
| **Stage** | Major workflow phase (1-5): Discovery, Validation, Preparation, Generation, Assurance |
| **Phase** | Sub-phase within a stage (1-5), aligned with specific skills |
| **Skill** | Claude Code skill definition in `.claude/skills/s{N}-{NN}-*/SKILL.md` |
| **Task** | Atomic work unit combining stage, phase, skill, and feature |
| **Feature** | Business feature being migrated (e.g., FEAT-PA-001) |
| **Domain** | Functional domain grouping features (e.g., PA, CM, MM) |
| **Phase Gate** | Checkpoint ensuring all features complete Phase N before N+1 |
| **Session** | Claude Code execution context managed by Choisor |
| **Priority Tier** | Domain importance classification (P0-Foundation to P3-Supporting) |

### 2.3 Architecture Overview

Choisor employs a layered architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  /choisor   │  │   Status    │  │  Monitoring │         │
│  │  commands   │  │   Display   │  │    Tools    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│                    Core Engine Layer                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │    Phase    │  │   Priority  │  │    Skill    │         │
│  │    Gate     │  │   Engine    │  │   Registry  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│                    Daemon Layer                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Scheduler  │  │   Session   │  │   Parallel  │         │
│  │             │  │    Pool     │  │ Coordinator │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│                    Plugin Layer                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │    Task     │  │ Instruction │  │  Validator  │         │
│  │ Generators  │  │  Generators │  │   Plugins   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│                    Storage Layer                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  tasks.json │  │ sessions/   │  │ config.yaml │         │
│  │             │  │ sessions.json│  │ project.yaml│         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

**Key Components**:

1. **Phase Gate**: Enforces sequential phase progression across all features
2. **Priority Engine**: Calculates task execution order using weighted scoring
3. **Skill Registry**: Discovers and catalogs available skills dynamically
4. **Scheduler**: Polls for available tasks and assigns to sessions
5. **Session Pool**: Manages Claude Code session lifecycle
6. **Parallel Coordinator**: Orchestrates concurrent skill execution

---

## 3. 5-Stage Migration Workflow

### 3.1 Stage Overview

Choisor implements a structured 5-stage workflow for legacy code migration:

| Stage | Name | Phases | Purpose |
|-------|------|--------|---------|
| **1** | Discovery | 4 | Feature inventory, deep analysis, spec generation |
| **2** | Validation | 4 | Ground truth comparison, gap analysis |
| **3** | Preparation | 5 | Architecture design, dependency resolution |
| **4** | Generation | 5 | Code generation, test generation |
| **5** | Assurance | 5 | Quality validation, performance baseline |

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│  Stage  │───▶│  Stage  │───▶│  Stage  │───▶│  Stage  │───▶│  Stage  │
│    1    │    │    2    │    │    3    │    │    4    │    │    5    │
│Discovery│    │Validation│   │Preparation│   │Generation│   │Assurance│
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
     │              │              │              │              │
     ▼              ▼              ▼              ▼              ▼
  Feature       Ground         Architecture    Code &        Quality
  Inventory     Truth          Design          Tests         Gate
```

### Detailed Stage Breakdown

#### Stage 1: Discovery (s1-01 to s1-04)

| Phase | Skill | Type | Output |
|-------|-------|------|--------|
| 1 | s1-01-discovery-feature-inventory | domain | feature-inventory.yaml |
| 2 | s1-02-discovery-miplatform-protocol | domain | miplatform-protocol.yaml |
| 3 | s1-03-discovery-deep-analysis | feature | summary.yaml, main.yaml |
| 4 | s1-04-discovery-spec-generation | feature | main.yaml, api-specs/*.yaml |

#### Stage 2: Validation (s2-01 to s2-04)

| Phase | Skill | Type | Output |
|-------|-------|------|--------|
| 1 | s2-01-validation-source-inventory | domain | source-inventory.yaml |
| 2 | s2-02-validation-structural-comparison | domain | comparison-report.yaml |
| 3 | s2-03-validation-gap-analysis | feature | gap-analysis.yaml |
| 4 | s2-04-validation-spec-completion | feature | completion-report.yaml |

#### Stage 3: Preparation (s3-01 to s3-05)

| Phase | Skill | Type | Output |
|-------|-------|------|--------|
| 1 | s3-01-preparation-dependency-graph | system | dependency-graph.yaml |
| 2 | s3-02-preparation-interface-extraction | system | interface-specs.yaml |
| 3 | s3-03-preparation-technical-debt | system | tech-debt-report.yaml |
| 4 | s3-04-preparation-architecture-design | system | architecture.yaml |
| 5 | s3-05-preparation-generation-spec | system | generation-spec.yaml |

#### Stage 4: Generation (s4-01 to s4-05)

| Phase | Skill | Type | Output |
|-------|-------|------|--------|
| 1 | s4-01-generation-project-scaffold | system | Project structure |
| 2 | s4-02-generation-mini-pilot | system | Pilot validation |
| 3 | s4-03-generation-domain-batch | feature | Java/MyBatis code |
| 4 | s4-04-generation-test-generation | feature | Unit/integration tests |
| 5 | s4-05-generation-integration-build | system | Build validation |

#### Stage 5: Assurance (s5-01 to s5-05)

| Phase | Skill | Type | Output |
|-------|-------|------|--------|
| 1 | s5-01-assurance-structural-check | feature | Structural report |
| 2 | s5-02-assurance-functional-validation | feature | Functional report |
| 3 | s5-03-assurance-api-contract-test | feature | API test results |
| 4 | s5-04-assurance-performance-baseline | system | Performance metrics |
| 5 | s5-05-assurance-quality-gate | system | Quality decision |

### 3.2 Phase Types (system/domain/feature)

Each phase operates at one of three granularity levels:

| Type | Task Count | Description | Example |
|------|-----------|-------------|---------|
| **system** | 1 total | Project-wide operation | Project scaffold, quality gate |
| **domain** | 1 per domain | Domain-level aggregation | Feature inventory per domain |
| **feature** | 1 per feature | Feature-level parallelizable | Deep analysis per feature |

```
Phase Types Visualization:

system  ────────────────────────────────────────────────────▶
         [════════════════════════════════════════════════]
                              1 task

domain  ────────────────────────────────────────────────────▶
         [═══════════]  [═══════════]  [═══════════]
              PA             CM             MM
         (1 per domain)

feature ────────────────────────────────────────────────────▶
         [═][═][═][═][═][═][═][═][═][═][═][═][═][═][═][═]
          F1 F2 F3 F4 F5 F6 F7 F8 F9 ...
         (1 per feature - parallelizable)
```

**Configuration Example (project.yaml)**:

```yaml
phase_types:
  stage1:
    phase1: "domain"    # Feature Inventory
    phase2: "domain"    # Protocol Analysis
    phase3: "feature"   # Deep Analysis
    phase4: "feature"   # Spec Generation
  stage4:
    phase1: "system"    # Project Scaffold
    phase2: "system"    # Mini-pilot
    phase3: "feature"   # Domain Batch
    phase4: "feature"   # Test Generation
    phase5: "system"    # Integration Build
```

### 3.3 Phase Gate Control

Phase Gates ensure workflow integrity by enforcing sequential progression:

**Rule**: All features must complete Phase N before ANY feature can proceed to Phase N+1.

```
Phase Gate Visualization:

Phase 1 ─────────────────────────────────────────────────────
         [FEAT-PA-001 ✓] [FEAT-PA-002 ✓] [FEAT-CM-001 ✓]
         ════════════════ GATE PASSED ═══════════════════
                              │
                              ▼
Phase 2 ─────────────────────────────────────────────────────
         [FEAT-PA-001 ✓] [FEAT-PA-002 ⟳] [FEAT-CM-001 ✓]
         ════════════════ GATE BLOCKED ══════════════════
                    (PA-002 still in progress)
```

**Phase Gate Configuration**:

```yaml
# config.yaml
phase_gate:
  enabled: true           # Enable phase gate enforcement
  strict_mode: true       # Fail immediately on violation
  auto_to_max: true       # Auto-advance to max allowed phase
  max_allowed_phase: null # null = calculate dynamically
```

**Phase Gate Algorithm**:

```python
def get_max_allowed_phase(tasks):
    """Determine maximum allowed phase based on completion status."""
    for phase in reversed([1, 2, 3, 4, 5]):
        if is_phase_complete(phase, tasks):
            return min(phase + 1, 5)
    return 1  # Start with phase 1

def is_phase_complete(phase, tasks):
    """Check if all features have completed this phase."""
    feature_tasks = [t for t in tasks if t.type == "feature"]
    for feature_id in get_unique_features(feature_tasks):
        if not has_completed_phase(feature_id, phase, feature_tasks):
            return False
    return True
```

---

## 4. Getting Started

### 4.1 Prerequisites

Before using Choisor, ensure you have:

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.9+ | Required for daemon |
| Claude Code | Latest | CLI must be initialized |
| PyYAML | Any | For configuration parsing |
| Pydantic | 2.0+ | For schema validation |

**Verify Claude Code initialization**:

```bash
# Check if Claude Code is initialized
ls -la .claude/

# Expected output should include:
# - settings.json
# - skills/ directory
```

### 4.2 Project Initialization

Initialize Choisor using the `/choisor init` command:

```bash
# Interactive initialization
/choisor init

# Use specific template
/choisor init --template spring-migration

# Use project-specific preset
/choisor init --template hallain-tft

# Reinitialize existing project
/choisor init --force

# List available templates
/choisor init --list-templates
```

**Available Templates**:

| Template | Description |
|----------|-------------|
| `spring-migration` | Generic Spring MVC → Spring Boot migration |
| `hallain-tft` | Hallain TFT project with predefined domains |
| `custom` | Minimal configuration for custom projects |

**Init Options**:

| Option | Description | Example |
|--------|-------------|---------|
| `--template` | Use specific template | `--template spring-migration` |
| `--force` | Reinitialize existing | `--force` |
| `--name` | Set project name | `--name my-project` |
| `--source-base` | Legacy source directory | `--source-base legacy` |
| `--target-base` | Generated code directory | `--target-base generated` |
| `--java-package` | Java package path | `--java-package com/example` |

### 4.3 Directory Structure

After initialization, Choisor creates the following structure:

```
<project-root>/
├── .choisor/                      # Choisor configuration and state
│   ├── config.yaml                # Runtime configuration
│   ├── project.yaml               # Project properties
│   ├── workflow.yaml              # Workflow definition (optional)
│   ├── tasks/
│   │   └── tasks.json             # Task list and states
│   ├── sessions/
│   │   └── sessions.json          # Session pool state
│   ├── instructions/              # Active instruction files
│   ├── logs/                      # Session and task logs
│   │   └── instructions/          # Archived instructions
│   └── plugins/                   # Project-specific plugins
│       ├── generators/
│       └── validators/
│
├── .claude/                       # Claude Code configuration
│   └── skills/
│       ├── choisor/               # Choisor skill
│       ├── s1-01-discovery-*/     # Stage 1 Phase 1 skill
│       ├── s1-02-discovery-*/     # Stage 1 Phase 2 skill
│       └── ...                    # Other stage skills
│
└── work/
    └── specs/                     # Stage outputs
        ├── stage1-outputs/
        │   ├── phase1/{priority}/{domain}/
        │   ├── phase2/
        │   ├── phase3/{priority}/{domain}/{feature}/
        │   └── phase4/
        ├── stage2-outputs/
        ├── stage3-outputs/
        ├── stage4-outputs/
        └── stage5-outputs/
```

---

## 5. Configuration

Choisor uses a three-file configuration system:

| File | Purpose | Scope |
|------|---------|-------|
| `config.yaml` | Runtime/operational settings | Dynamic, frequently modified |
| `project.yaml` | Project properties | Static, project-specific |
| `workflow.yaml` | Workflow definition | Optional, for custom workflows |

### 5.1 config.yaml (Runtime Settings)

The `config.yaml` file contains runtime settings that can be modified during execution:

```yaml
# .choisor/config.yaml

# Assignment control
assignment:
  enabled: true         # true: normal assignment, false: stop new assignments
  delay: null           # Assignment delay in minutes (null = no delay)
  stale_timeout: 10     # Minutes before session is considered stale

# Auto-commit settings
auto_commit:
  enabled: true
  commit_on_completion: true

# Provider settings
provider: "anthropic"
default_model: "claude-opus-4-5-20251101"

# Claude Code session configuration
claude_code:
  max_sessions: 1
  max_output_tokens: 65536
  default_model: "claude-opus-4-5-20251101"

# Current workflow position (runtime state)
current:
  stage: "stage1"
  phase: "phase1"

# Phase Gate settings (runtime control)
phase_gate:
  max_allowed_phase: "phase4"   # Maximum phase allowed
  auto_to_max: true             # Auto-advance to max allowed

# Parallel execution settings
parallel:
  enabled: true
  pairs:
    - ["s4-03", "s4-04"]        # Code gen + test gen
  max_parallel_sessions: 10

# Path configurations
paths:
  skills_root: ".claude/skills"
  contracts_path: ".claude/skills/common/inter-stage-contracts.yaml"

# Work scope filtering (runtime filter)
work_scope:
  enabled_domains: null         # ["pa", "mm"] or null for all
  enabled_stages: null          # [1, 2, 3] or null for all

# Priority algorithm
priority:
  algorithm: "weighted_score"   # "weighted_score" | "fifo"
  weights:
    dependency_ready: 0.5
    priority_score: 0.3
    estimated_duration: 0.2
```

**Key Settings Explained**:

| Setting | Purpose | Common Adjustments |
|---------|---------|-------------------|
| `assignment.enabled` | Control task assignment | Set to `false` to pause |
| `assignment.delay` | Throttle assignments | Set to `5` for 5-min delay |
| `parallel.max_parallel_sessions` | Concurrent sessions | Reduce for resource limits |
| `work_scope.enabled_domains` | Focus on specific domains | `["PA", "CM"]` |

### 5.2 project.yaml (Project Properties)

The `project.yaml` file contains project-specific properties:

```yaml
# .choisor/project.yaml

name: "my-migration-project"
description: "Spring MVC to Spring Boot migration project"

# Feature identification patterns
feature:
  id_prefix: "FEAT-"           # Feature ID prefix
  gap_suffix: "GAP"            # Suffix for GAP features
  skip_gap_features: true      # Skip GAP features in generation

# Domain configuration
domain:
  skip_domains: []             # Domains to skip
  priority_map:                # Domain to priority tier mapping
    P0-Foundation: ["CM"]
    P1-Hub: ["PA"]
    P2-Core: ["MM", "QM"]
    P3-Supporting: ["RP"]

# Phase types by stage
phase_types:
  stage1:
    phase1: "domain"           # Feature Inventory
    phase2: "domain"           # Protocol Analysis
    phase3: "feature"          # Deep Analysis
    phase4: "feature"          # Spec Generation
  stage2:
    phase1: "domain"
    phase2: "domain"
    phase3: "feature"
    phase4: "feature"
  stage3:
    phase1: "system"
    phase2: "system"
    phase3: "system"
    phase4: "system"
    phase5: "system"
  stage4:
    phase1: "system"
    phase2: "system"
    phase3: "feature"
    phase4: "feature"
    phase5: "system"
  stage5:
    phase1: "feature"
    phase2: "feature"
    phase3: "feature"
    phase4: "system"
    phase5: "system"

# Path templates
paths:
  source_base: "hallain"                # Legacy source
  target_base: "next-hallain"           # Generated code
  java_src_path: "src/main/java"
  mapper_path: "src/main/resources/mapper"
  java_package: "com/hallain"
  specs_root: "work/specs"

# Stage definitions
stages:
  stage1:
    name: "Discovery"
    phases: ["phase1", "phase2", "phase3", "phase4"]
    skills:
      phase1: "s1-01-discovery-feature-inventory"
      phase2: "s1-02-discovery-miplatform-protocol"
      phase3: "s1-03-discovery-deep-analysis"
      phase4: "s1-04-discovery-spec-generation"
  # ... (other stages)

# Task source locations
task_sources:
  feature_inventory_base: "work/specs/stage1-outputs/phase1"
  feature_inventory_pattern: "work/specs/stage1-outputs/phase1/{priority}/{domain}/feature-inventory.yaml"
  stage1_specs: "work/specs/stage1-outputs/phase3"
  stage4_specs: "work/specs/stage1-outputs/phase3"
```

### 5.3 workflow.yaml (Workflow Definition)

The optional `workflow.yaml` enables custom workflow definitions:

```yaml
# .choisor/workflow.yaml

workflow:
  name: "hallain_tft"
  description: "Spring MVC to Spring Boot migration"

  # Skill discovery pattern
  skill_pattern: "s{stage}-{phase:02d}-*"
  skill_dir: ".claude/skills"

  stages:
    - id: "discovery"
      number: 1
      name: "Discovery"
      description: "Feature discovery and analysis"
      output_dir: "stage1-outputs"
      phases:
        - id: "feature-inventory"
          number: 1
          type: "domain"
          skill: "s1-01-discovery-feature-inventory"
          outputs:
            - "feature-inventory.yaml"
        - id: "miplatform-protocol"
          number: 2
          type: "domain"
          skill: "s1-02-discovery-miplatform-protocol"
          outputs:
            - "miplatform-protocol.yaml"
        - id: "deep-analysis"
          number: 3
          type: "feature"
          skill: "s1-03-discovery-deep-analysis"
          outputs:
            - "summary.yaml"
            - "main.yaml"
        - id: "spec-generation"
          number: 4
          type: "feature"
          skill: "s1-04-discovery-spec-generation"
          outputs:
            - "main.yaml"
            - "api-specs/*.yaml"

    - id: "generation"
      number: 4
      name: "Generation"
      parallel_pairs:
        - ["domain-batch", "test-generation"]
      phases:
        - id: "project-scaffold"
          number: 1
          type: "system"
          skill: "s4-01-generation-project-scaffold"
        - id: "domain-batch"
          number: 3
          type: "feature"
          skill: "s4-03-generation-domain-batch"
          generator: "generators.code_generation"   # Custom generator
        - id: "test-generation"
          number: 4
          type: "feature"
          skill: "s4-04-generation-test-generation"

  # Task source configuration
  task_sources:
    feature_inventory:
      path: "work/specs/stage1-outputs/phase1/{priority}/{domain}/feature-inventory.yaml"
      pattern: "work/specs/stage1-outputs/phase1/**/feature-inventory.yaml"
    specs:
      path: "work/specs/stage1-outputs/phase3/{priority}/{domain}/{feature}/"
```

---

## 6. Commands Reference

### 6.1 Initialization Commands

| Command | Description |
|---------|-------------|
| `/choisor init` | Initialize Choisor for a project |
| `/choisor init --template <name>` | Use specific template |
| `/choisor init --force` | Reinitialize existing project |
| `/choisor init --list-templates` | List available templates |

**Examples**:

```bash
# Standard initialization
/choisor init --template spring-migration

# With custom paths
/choisor init --template spring-migration \
  --name my-project \
  --source-base legacy \
  --target-base generated \
  --java-package com/example

# Reinitialize with force
/choisor init --force
```

### 6.2 Status & Monitoring Commands

| Command | Description |
|---------|-------------|
| `/choisor status` | Display current project status |
| `/choisor scan [--stage N]` | Scan for tasks and update tasks.json |
| `/choisor sync` | Synchronize task status with filesystem |
| `/choisor query [options]` | Query tasks with filters |

**Status Command Output**:

```
╔══════════════════════════════════════════════════════════════╗
║                    Choisor Status Report                     ║
╠══════════════════════════════════════════════════════════════╣
║ Project: hallain-tft                                         ║
║ Current Phase: 1.3 (Discovery - Deep Analysis)               ║
║ Phase Gate: Phase 3 allowed                                  ║
╠══════════════════════════════════════════════════════════════╣
║ Task Summary:                                                ║
║   Total: 156  Pending: 89  In Progress: 3  Completed: 64    ║
╠══════════════════════════════════════════════════════════════╣
║ Phase Progress:                                              ║
║   Phase 1: ████████████████████████ 100% (24/24)            ║
║   Phase 2: ████████████████████████ 100% (24/24)            ║
║   Phase 3: ████████████░░░░░░░░░░░░  52% (16/31)            ║
║   Phase 4: ░░░░░░░░░░░░░░░░░░░░░░░░   0% (0/31)             ║
╠══════════════════════════════════════════════════════════════╣
║ Active Sessions: 3/10                                        ║
║   Session f4fe7c8a: FEAT-PA-003 (s1-03)                     ║
║   Session 2b3c4d5e: FEAT-CM-001 (s1-03)                     ║
║   Session 9a8b7c6d: FEAT-MM-002 (s1-03)                     ║
╚══════════════════════════════════════════════════════════════╝
```

**Query Command Options**:

```bash
# Filter by status
/choisor query --status pending

# Filter by domain
/choisor query --domain PA

# Filter by stage and phase
/choisor query --stage 4 --phase 3

# List format with limit
/choisor query --list --limit 20

# JSON output
/choisor query --format json
```

### 6.3 Task Management Commands

| Command | Description |
|---------|-------------|
| `/choisor manual-assign <feature-id>` | Manually assign specific feature |
| `/choisor clean-restart <feature-ids>` | Reset features for rework |

**Manual Assignment**:

```bash
# Assign specific feature to next available session
/choisor manual-assign FEAT-PA-001

# Assign multiple features
/choisor manual-assign FEAT-PA-001 FEAT-PA-002
```

**Clean Restart**:

```bash
# Reset single feature
/choisor clean-restart FEAT-PA-001

# Reset multiple features
/choisor clean-restart FEAT-PA-001,FEAT-PA-002,FEAT-CM-001

# This will:
# 1. Reset task status to "pending"
# 2. Clear assigned_session
# 3. Delete existing output files
# 4. Archive instruction files
```

### 6.4 Session Control Commands

| Command | Description |
|---------|-------------|
| `/choisor stop` | Stop first running session |
| `/choisor stop --feature <id>` | Stop by feature ID |
| `/choisor stop --session <id>` | Stop by session ID |
| `/choisor stop --task <id>` | Stop by task ID |
| `/choisor stop --all` | Stop all running sessions |

**Examples**:

```bash
# Stop first running session
/choisor stop

# Stop session working on specific feature
/choisor stop --feature FEAT-CM-001

# Stop by session ID (prefix is OK)
/choisor stop --session f4fe7c8a

# Stop by task ID
/choisor stop --task s1-03-FEAT-CM-001

# Emergency stop all
/choisor stop --all
```

---

## 7. Task Lifecycle

### 7.1 Task Generation

Tasks are generated based on filesystem structure and configuration:

```
Task Generation Flow:

1. Scan filesystem for spec files
   └─▶ work/specs/stage1-outputs/phase3/{priority}/{domain}/{feature}/

2. Filter by project config
   └─▶ Skip GAP features (if configured)
   └─▶ Filter by enabled_domains
   └─▶ Filter by enabled_stages

3. Create Task objects
   └─▶ Extract feature_id from path
   └─▶ Determine domain from path
   └─▶ Set skill_id from stage/phase
   └─▶ Calculate priority from domain tier

4. Persist to tasks.json
   └─▶ .choisor/tasks/tasks.json
```

**Task Object Structure**:

```python
@dataclass
class Task:
    id: str                        # e.g., "s1-03-FEAT-PA-001"
    stage: int                     # 1-5
    phase: int                     # 1-5
    skill_id: str                  # e.g., "s1-03"
    feature_id: str                # e.g., "FEAT-PA-001"
    domain: str                    # e.g., "PA"
    status: TaskStatus             # pending, assigned, in_progress, etc.
    title: str                     # Human-readable title
    priority: int                  # 1-10 (higher = more important)
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]       # Additional context
    assigned_session: Optional[str]
    dependencies: List[str]        # Dependent task IDs
    estimated_duration: Optional[int]  # Minutes
```

### 7.2 Task States

Tasks progress through the following states:

```
Task State Machine:

  ┌─────────────────────────────────────────────────────────┐
  │                                                         │
  │                      ┌──────────┐                       │
  │                      │ PENDING  │◄───────────────┐      │
  │                      └────┬─────┘                │      │
  │                           │                      │      │
  │                    assign │                reset │      │
  │                           ▼                      │      │
  │                      ┌──────────┐                │      │
  │                      │ ASSIGNED │────────────────┘      │
  │                      └────┬─────┘     (timeout)         │
  │                           │                             │
  │                    start  │                             │
  │                           ▼                             │
  │                    ┌────────────┐                       │
  │                    │IN_PROGRESS │                       │
  │                    └─────┬──────┘                       │
  │                          │                              │
  │          ┌───────────────┼───────────────┐              │
  │          │               │               │              │
  │          ▼               ▼               ▼              │
  │     ┌─────────┐     ┌────────┐     ┌────────┐          │
  │     │COMPLETED│     │ FAILED │     │  SKIP  │          │
  │     └─────────┘     └────────┘     └────────┘          │
  │          │               │               │              │
  │          └───────────────┴───────────────┘              │
  │                          │                              │
  │                   Terminal States                       │
  └─────────────────────────────────────────────────────────┘
```

| State | Description | Transitions |
|-------|-------------|-------------|
| **PENDING** | Task awaiting assignment | → ASSIGNED |
| **ASSIGNED** | Task assigned to session | → IN_PROGRESS, → PENDING (timeout) |
| **IN_PROGRESS** | Task being executed | → COMPLETED, → FAILED, → SKIP |
| **COMPLETED** | Task finished successfully | Terminal |
| **FAILED** | Task failed with error | Terminal (can be reset) |
| **SKIP** | Task skipped (e.g., empty folder) | Terminal |

### 7.3 Priority Algorithm

Choisor uses a weighted scoring algorithm to prioritize tasks:

```
Score = (dependency_ready × 0.4) + (priority_score × 0.4) + (duration_score × 0.2)
```

**Component Breakdown**:

| Component | Weight | Calculation |
|-----------|--------|-------------|
| `dependency_ready` | 0.4 | 1.0 if all dependencies complete, 0.0 otherwise |
| `priority_score` | 0.4 | Task priority (1-10) normalized to 0.0-1.0 |
| `duration_score` | 0.2 | `1.0 - min(estimated_duration/120, 1.0)` |

**Priority Configuration**:

```yaml
# config.yaml
priority:
  algorithm: "weighted_score"  # or "fifo"
  weights:
    dependency_ready: 0.5
    priority_score: 0.3
    estimated_duration: 0.2
```

**Domain Priority Mapping**:

Tasks inherit priority from their domain's tier:

| Tier | Priority Score | Domains (Example) |
|------|---------------|-------------------|
| P0-Foundation | 10 | CM (Common) |
| P1-Hub | 8 | PA (Production) |
| P2-Core | 6 | MM, QM |
| P3-Supporting | 4 | RP |

---

## 8. Multi-Session Orchestration

### 8.1 Daemon Architecture

The Choisor daemon manages the scheduling loop:

```
Daemon Architecture:

┌─────────────────────────────────────────────────────────────┐
│                      Choisor Daemon                          │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                    Scheduler                           │  │
│  │                                                        │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │              Schedule Tick (5s)                  │  │  │
│  │  │                                                  │  │  │
│  │  │  1. Reload config (if changed)                   │  │  │
│  │  │  2. Check stale sessions                        │  │  │
│  │  │  3. Check running sessions for completion       │  │  │
│  │  │  4. Process completed sessions                  │  │  │
│  │  │  5. Trim excess sessions                        │  │  │
│  │  │  6. Check assignment delay                      │  │  │
│  │  │  7. Get available sessions                      │  │  │
│  │  │  8. Create new session if needed               │  │  │
│  │  │  9. Assign task to session                     │  │  │
│  │  │  10. Check parallel opportunities              │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
│                           │                                  │
│                           ▼                                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                   Session Pool                         │  │
│  │                                                        │  │
│  │    Session States:                                     │  │
│  │    IDLE → ASSIGNED → RUNNING → COMPLETED              │  │
│  │      ↑                           │                     │  │
│  │      └───────── release ─────────┘                     │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

**Starting the Daemon**:

```bash
# In a separate terminal
python -m choisor.daemon.main
```

**Daemon Configuration**:

```yaml
# config.yaml
daemon:
  refresh_interval: 10  # seconds (5-300)

assignment:
  enabled: true
  delay: null           # minutes
  stale_timeout: 10     # minutes
```

### 8.2 Session Pool Management

The Session Pool manages Claude Code session lifecycle:

```python
class SessionState(Enum):
    IDLE = "idle"           # Ready for task
    ASSIGNED = "assigned"   # Task assigned, launching
    RUNNING = "running"     # Actively executing
    COMPLETED = "completed" # Task done, awaiting release
    FAILED = "failed"       # Error occurred
    TERMINATED = "terminated"  # Manually stopped
```

**Session Lifecycle**:

```
Session Lifecycle:

1. CREATE (create_session)
   └─▶ Session enters IDLE state
   └─▶ Assigned UUID
   └─▶ Saved to sessions.json

2. ASSIGN (assign_task)
   └─▶ State: IDLE → ASSIGNED
   └─▶ Task ID recorded
   └─▶ Instruction file written
   └─▶ Claude process launched
   └─▶ State: ASSIGNED → RUNNING

3. EXECUTE (managed by Claude)
   └─▶ Process executes instruction
   └─▶ Outputs written to filesystem
   └─▶ Process completes

4. COMPLETE (check_session_status)
   └─▶ State: RUNNING → COMPLETED
   └─▶ Scheduler notified

5. RELEASE (release_session)
   └─▶ Task added to history
   └─▶ State: COMPLETED → IDLE
   └─▶ Ready for next task
```

**Session Pool Statistics**:

```python
def get_stats() -> Dict[str, int]:
    return {
        "idle": 2,
        "assigned": 1,
        "running": 5,
        "completed": 0,
        "failed": 0,
        "terminated": 0,
        "total": 8,
    }
```

### 8.3 Parallel Execution

Choisor supports parallel execution for specific skill pairs:

```
Parallel Execution (s4-03 + s4-04):

Feature: FEAT-PA-001
┌────────────────────────────────────────────────────────────┐
│                                                            │
│  Session A                    Session B                    │
│  ┌──────────────────────┐    ┌──────────────────────┐     │
│  │ s4-03: Domain Batch  │    │ s4-04: Test Gen     │     │
│  │ (Code Generation)    │    │ (Test Generation)    │     │
│  └──────────┬───────────┘    └──────────┬───────────┘     │
│             │                           │                  │
│             └───────────┬───────────────┘                  │
│                         │                                  │
│                         ▼                                  │
│             ┌───────────────────────┐                     │
│             │   Both Complete       │                     │
│             │   FEAT-PA-001 Done    │                     │
│             └───────────────────────┘                     │
└────────────────────────────────────────────────────────────┘
```

**Configuration**:

```yaml
# config.yaml
parallel:
  enabled: true
  pairs:
    - ["s4-03", "s4-04"]   # Code gen + test gen
  max_parallel_sessions: 10
```

**Parallel Coordinator Logic**:

```python
class ParallelCoordinator:
    def can_run_parallel_by_skill_id(self, skill_id: str) -> bool:
        """Check if skill can run in parallel with another."""
        for pair in self.parallel_pairs:
            if skill_id in pair:
                return True
        return False

    def get_parallel_skill_id(self, skill_id: str) -> Optional[str]:
        """Get the parallel skill for a given skill."""
        for pair in self.parallel_pairs:
            if skill_id == pair[0]:
                return pair[1]
            if skill_id == pair[1]:
                return pair[0]
        return None
```

---

## 9. Plugin Architecture

### 9.1 Plugin Types

Choisor supports three types of plugins:

| Plugin Type | Purpose | Interface |
|-------------|---------|-----------|
| **TaskGeneratorPlugin** | Custom task generation | `generate(project_root, config, workflow, registry, project_config) → List[Task]` |
| **InstructionGeneratorPlugin** | Custom instruction generation | `generate(task, config, workflow, project_config) → str` |
| **ValidatorPlugin** | Custom output validation | `validate(task, output_path, workflow) → ValidationResult` |

### 9.2 Creating Custom Plugins

**Directory Structure**:

```
.choisor/plugins/
├── __init__.py
├── generators/
│   ├── __init__.py
│   └── custom_generator.py
└── validators/
    ├── __init__.py
    └── custom_validator.py
```

**Task Generator Plugin Example**:

```python
# .choisor/plugins/generators/code_generation.py

from choisor.plugins.base import TaskGeneratorPlugin
from choisor.core import Task

class CodeGenerationTaskGenerator(TaskGeneratorPlugin):
    """Custom task generator for Stage 4 code generation."""

    @property
    def stage_id(self) -> str:
        return "generation"

    def generate(
        self,
        project_root,
        config,
        workflow,
        registry,
        project_config,
    ) -> list[Task]:
        tasks = []

        # Custom logic for code generation tasks
        specs_path = project_root / "work/specs/stage1-outputs/phase3"

        for feature_dir in self._scan_features(specs_path):
            # Skip GAP features
            if project_config.feature.skip_gap_features:
                if project_config.feature.gap_suffix in feature_dir.name:
                    continue

            complexity = self._calculate_complexity(feature_dir)

            task = Task(
                id=f"{feature_dir.name}-codegen",
                stage=workflow.get_stage("generation").number,
                phase=3,
                skill_id="s4-03",
                feature_id=feature_dir.name,
                # ... rest of task creation
            )
            tasks.append(task)

        return tasks
```

**Validator Plugin Example**:

```python
# .choisor/plugins/validators/code_validator.py

from choisor.plugins.base import ValidatorPlugin
from choisor.generators.validators.base import ValidationResult

class CodeValidator(ValidatorPlugin):
    """Custom validator for generated code."""

    @property
    def stage_id(self) -> str:
        return "generation"

    def validate(self, task, output_path, workflow) -> ValidationResult:
        result = ValidationResult(passed=True)

        # Check Java files exist
        java_files = list(output_path.glob("**/*.java"))
        if not java_files:
            result.add_error("No Java files generated")

        # Check mapper files exist
        mapper_files = list(output_path.glob("**/*.xml"))
        if not mapper_files:
            result.add_warning("No mapper XML files found")

        # Check for compilation errors (basic syntax check)
        for java_file in java_files:
            if not self._check_syntax(java_file):
                result.add_error(f"Syntax error in {java_file.name}")

        return result
```

### 9.3 Default Plugins

Choisor provides default plugins that work with workflow.yaml:

**DefaultTaskGeneratorPlugin**:

```python
class DefaultTaskGeneratorPlugin(TaskGeneratorPlugin):
    """Default task generator that works from workflow.yaml."""

    def generate(self, ...) -> list[Task]:
        stage = self._workflow.get_stage(self._stage_id)
        tasks = []

        for phase in stage.phases:
            phase_type = phase.type  # "system", "domain", or "feature"

            if phase_type == "system":
                # One task total
                tasks.append(self._create_system_task(phase))
            elif phase_type == "domain":
                # One task per domain
                for domain in self._get_domains():
                    tasks.append(self._create_domain_task(phase, domain))
            else:  # feature
                # One task per feature
                for feature in self._get_features():
                    tasks.append(self._create_feature_task(phase, feature))

        return tasks
```

**Plugin Loading**:

```python
class PluginLoader:
    """Loads plugins from project directory."""

    def load(self) -> PluginRegistry:
        registry = PluginRegistry()

        if not self.plugins_dir.exists():
            return registry

        # Add plugins dir to Python path
        sys.path.insert(0, str(self.plugins_dir))

        # Load generator plugins
        for plugin_file in (self.plugins_dir / "generators").glob("*.py"):
            self._load_generator_plugin(plugin_file, registry)

        # Load validator plugins
        for plugin_file in (self.plugins_dir / "validators").glob("*.py"):
            self._load_validator_plugin(plugin_file, registry)

        return registry
```

---

## 10. Validation System

### 10.1 Stage Validators

Stage validators verify output integrity:

```python
class StageValidator(ABC):
    """Abstract base class for stage output validators."""

    @abstractmethod
    def get_stage(self) -> int:
        """Return stage number this validator handles."""
        pass

    @abstractmethod
    def validate(
        self,
        task: Task,
        output_path: Path,
        config: ChoisorConfig
    ) -> ValidationResult:
        """Validate stage output."""
        pass
```

**ValidationResult Structure**:

```python
@dataclass
class ValidationResult:
    passed: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    def add_error(self, message: str) -> None:
        self.errors.append(message)
        self.passed = False

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    @classmethod
    def success(cls, details=None) -> "ValidationResult":
        return cls(passed=True, details=details or {})

    @classmethod
    def failure(cls, errors: list[str], details=None) -> "ValidationResult":
        return cls(passed=False, errors=errors, details=details or {})
```

### 10.2 Contract Validation

Contract validation ensures inter-stage data integrity:

**Contract Violation Severities**:

| Severity | Description | Action |
|----------|-------------|--------|
| **CRITICAL** | Blocking violation | Immediate stop, regeneration required |
| **MAJOR** | Significant issue | Warning, manual review needed |
| **MINOR** | Minor inconsistency | Log and continue |

**Validation Rules**:

| Rule | Description |
|------|-------------|
| `output_exists` | Output file/directory must exist |
| `yaml_syntax` | Valid YAML format |
| `not_empty` | File must have content |
| `metadata_required` | Required metadata fields present |
| `timestamp_format` | ISO8601 format for timestamps |
| `summary_count_match` | Summary counts match actual data |
| `url_lowercase` | URLs should be lowercase |
| `url_trailing_slash` | No trailing slashes |
| `url_extension` | No extensions (.mi, .do, .action) |

**ContractValidator Usage**:

```python
validator = ContractValidator(contracts_path)
validator.load_contracts()

# Validate stage output
violations = validator.validate_stage_output(
    stage=1,
    phase=4,
    output_path=Path("work/specs/stage1-outputs/phase4/FEAT-PA-001")
)

# Check for blocking violations
if validator.has_blocking_violations(violations):
    raise ValidationError("Critical violations found")

# Get summary
summary = validator.get_violations_summary(violations)
# {"CRITICAL": 0, "MAJOR": 2, "MINOR": 5}
```

**URL Normalization**:

```python
def normalize_url(url: str) -> str:
    """Normalize URL according to contract rules."""
    if not url:
        return url

    # Step 1: Lowercase
    normalized = url.lower()

    # Step 2: Remove trailing slash
    normalized = normalized.rstrip("/")

    # Step 3: Remove extensions
    for ext in [".mi", ".do", ".action"]:
        if normalized.endswith(ext):
            normalized = normalized[:-len(ext)]
            break

    return normalized
```

### 10.3 Quality Gates

Quality gates enforce workflow progression criteria:

```
Quality Gate Criteria:

┌─────────────────────────────────────────────────────────────┐
│                    Stage Completion Gate                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Coverage Requirements:                                      │
│  ├─ Feature Coverage  ≥ 99%                                 │
│  ├─ Endpoint Coverage ≥ 95%                                 │
│  └─ SQL Coverage      = 100%                                │
│                                                             │
│  Violation Thresholds:                                      │
│  ├─ CRITICAL          = 0                                   │
│  ├─ MAJOR             ≤ 5 (with justification)              │
│  └─ MINOR             ≤ 20                                  │
│                                                             │
│  Phase Gate Status:                                         │
│  └─ All features must complete current phase                │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  Result: PASS / FAIL / CONDITIONAL                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 11. Best Practices

### 11.1 Workflow Optimization

**Domain Prioritization**:

```yaml
# project.yaml - Optimize domain processing order
domain:
  priority_map:
    P0-Foundation: ["CM"]       # Process first - shared components
    P1-Hub: ["PA"]              # High-value features
    P2-Core: ["MM", "QM"]       # Core business logic
    P3-Supporting: ["RP"]       # Lower priority
```

**Parallel Session Tuning**:

| Scenario | Recommended Sessions | Rationale |
|----------|---------------------|-----------|
| Local dev machine | 1-3 | Resource constraints |
| CI/CD pipeline | 3-5 | Balanced throughput |
| Dedicated server | 5-10 | Maximum parallelism |

**Phase Gate Strategy**:

```yaml
# config.yaml - Phase gate tuning
phase_gate:
  enabled: true
  strict_mode: true        # Fail immediately on violation
  auto_to_max: true        # Don't wait for manual advancement
  max_allowed_phase: null  # Let system calculate
```

### 11.2 Error Handling

**Stale Session Recovery**:

Choisor automatically recovers stale sessions:

```
Stale Session Detection:

1. Session inactive > stale_timeout (default: 10 min)
2. Scheduler detects stale state
3. Task reset to PENDING
4. Session released to IDLE
5. Task eligible for reassignment
```

**Configuration**:

```yaml
assignment:
  stale_timeout: 10  # Minutes before stale detection
```

**Task Failure Handling**:

```bash
# Manual reset for failed task
/choisor clean-restart FEAT-PA-001

# Check failure reason
/choisor query --status failed --list
```

### 11.3 Troubleshooting

**Common Issues**:

| Issue | Symptom | Solution |
|-------|---------|----------|
| Tasks not assigning | Status shows pending but no progress | Check `assignment.enabled: true` |
| Phase gate blocked | "Gate blocked" in status | Complete pending tasks in current phase |
| Session timeout | Sessions going stale | Increase `stale_timeout` |
| No tasks found | Scan returns 0 tasks | Check spec file structure |
| Parallel not working | Only one task at a time | Verify `parallel.enabled: true` |

**Diagnostic Commands**:

```bash
# Check current status
/choisor status

# Verify task scan
/choisor scan --stage 1

# Query specific domain
/choisor query --domain PA --list

# Check session states
# View .choisor/sessions/sessions.json
```

**Log Analysis**:

```bash
# Daemon logs location
.choisor/logs/

# Archived instructions
.choisor/logs/instructions/

# Task history in tasks.json
.choisor/tasks/tasks.json
```

---

## Appendix

### A. Configuration Reference

#### config.yaml (Complete Reference)

```yaml
# Assignment Control
assignment:
  enabled: bool          # Enable/disable task assignment (default: true)
  delay: int | null      # Assignment delay in minutes (default: null)
  stale_timeout: int     # Stale session timeout in minutes (default: 10)

# Auto-commit
auto_commit:
  enabled: bool          # Enable auto-commit (default: true)
  commit_on_completion: bool  # Commit after each phase (default: true)

# Provider
provider: str            # LLM provider (default: "anthropic")
default_model: str       # Model ID (default: "claude-opus-4-5-20251101")

# Claude Code
claude_code:
  max_sessions: int      # Max concurrent sessions (default: 1)
  max_output_tokens: int # Output token limit (default: 65536)
  default_model: str     # Default model for sessions

# Current Position
current:
  stage: str             # Current stage (e.g., "stage1")
  phase: str             # Current phase (e.g., "phase1")

# Phase Gate
phase_gate:
  max_allowed_phase: str | null  # Max phase (null = auto)
  auto_to_max: bool      # Auto-advance (default: true)
  enabled: bool          # Enable phase gates (default: true)
  strict_mode: bool      # Fail on violation (default: true)

# Parallel Execution
parallel:
  enabled: bool          # Enable parallel (default: true)
  pairs: list[list[str]] # Skill pairs (default: [["s4-03", "s4-04"]])
  max_parallel_sessions: int  # Max parallel (default: 10)

# Paths
paths:
  skills_root: str       # Skills directory (default: ".claude/skills")
  contracts_path: str    # Contracts file path

# Work Scope
work_scope:
  enabled_domains: list[str] | null  # Filter domains (null = all)
  enabled_stages: list[int] | null   # Filter stages (null = all)

# Priority
priority:
  algorithm: str         # "weighted_score" | "fifo"
  weights:
    dependency_ready: float   # Weight for dependency (default: 0.5)
    priority_score: float     # Weight for priority (default: 0.3)
    estimated_duration: float # Weight for duration (default: 0.2)
```

#### project.yaml (Complete Reference)

```yaml
# Project Identity
name: str                # Project name (REQUIRED)
description: str         # Project description

# Feature Patterns
feature:
  id_prefix: str         # Feature ID prefix (default: "FEAT-")
  gap_suffix: str        # GAP feature suffix (default: "GAP")
  skip_gap_features: bool  # Skip GAP features (default: true)

# Domain Configuration
domain:
  skip_domains: list[str]  # Domains to skip
  priority_map:
    P0-Foundation: list[str]
    P1-Hub: list[str]
    P2-Core: list[str]
    P3-Supporting: list[str]

# Phase Types
phase_types:
  stage1:
    phase1: str  # "system" | "domain" | "feature"
    phase2: str
    phase3: str
    phase4: str
  # ... (stages 2-5)

# Paths
paths:
  source_base: str       # Legacy source directory (REQUIRED)
  target_base: str       # Generated code directory (REQUIRED)
  java_src_path: str     # Java source path (default: "src/main/java")
  mapper_path: str       # Mapper path (default: "src/main/resources/mapper")
  java_package: str      # Java package (REQUIRED)
  specs_root: str        # Specs root (default: "work/specs")

# Stage Definitions
stages:
  stage1:
    name: str
    phases: list[str]
    skills:
      phase1: str
      phase2: str
      # ...

# Task Sources
task_sources:
  feature_inventory_base: str
  feature_inventory_pattern: str
  stage1_specs: str
  stage4_specs: str
```

### B. Command Quick Reference

| Command | Description |
|---------|-------------|
| `/choisor init` | Initialize project |
| `/choisor init --template <name>` | Use template |
| `/choisor init --force` | Reinitialize |
| `/choisor init --list-templates` | List templates |
| `/choisor status` | Show status |
| `/choisor scan [--stage N]` | Scan for tasks |
| `/choisor sync` | Sync task status |
| `/choisor query [options]` | Query tasks |
| `/choisor manual-assign <id>` | Assign feature |
| `/choisor clean-restart <ids>` | Reset features |
| `/choisor stop` | Stop first session |
| `/choisor stop --feature <id>` | Stop by feature |
| `/choisor stop --session <id>` | Stop by session |
| `/choisor stop --all` | Stop all sessions |

**Query Options**:

| Option | Description |
|--------|-------------|
| `--status <status>` | Filter by status |
| `--domain <code>` | Filter by domain |
| `--stage <number>` | Filter by stage |
| `--phase <number>` | Filter by phase |
| `--list` | Show task list |
| `--limit <n>` | Limit results |
| `--format json` | JSON output |

### C. Glossary

| Term | Definition |
|------|------------|
| **Choisor** | Task orchestrator for multi-stage migration workflows |
| **Stage** | Major workflow phase (1-5) |
| **Phase** | Sub-phase within a stage (1-5) |
| **Skill** | Claude Code skill definition (.claude/skills/s{N}-{NN}-*/) |
| **Task** | Atomic work unit (stage + phase + feature) |
| **Feature** | Business feature being migrated |
| **Domain** | Functional domain grouping features |
| **Phase Gate** | Checkpoint ensuring sequential phase completion |
| **Session** | Claude Code execution context |
| **Session Pool** | Manager for multiple concurrent sessions |
| **Scheduler** | Component that assigns tasks to sessions |
| **Priority Tier** | Domain importance classification (P0-P3) |
| **Contract** | Inter-stage data format specification |
| **Validator** | Component that verifies output integrity |
| **Plugin** | Extensible component for custom logic |
| **QUERY-FIRST** | Design principle prioritizing SQL preservation |
| **GAP Feature** | Feature marked for gap analysis (skipped in generation) |
| **Stale Session** | Session inactive beyond timeout threshold |

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2026-01 | Initial release |

---

*This document is part of the Choisor 2.0 project. For the latest updates, see the project repository.*
