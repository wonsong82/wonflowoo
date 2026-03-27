---
name: spec-generate
description: "Use after implementation to generate or update specs from actual code. AI-assisted: reads code, produces 4-layer YAML spec draft for developer review."
allowed-tools: Read, Write, Grep, Glob
---

# Skill: Spec Generation/Update After Implementation
Use this after coding is complete to keep specs aligned to actual code.

## Core Rule
Specs are post-implementation artifacts.
- Include implemented reality.
- Exclude planned/aspirational behavior.
- Treat spec updates as acceptance criteria.

All 4 layers (`interfaces`, `logic`, `data`, `dependencies`) are REQUIRED in every spec. No layer can be omitted — if a module has no data, use `data: { stateless: true }`.

## When to Run
- After implementation + verification
- Before task closure
- After refactors/migrations/boundary changes
- Any time runtime behavior changes

## Inputs
- Changed/created runtime source files
- Existing feature spec (if updating)
- `.wonflowoo/workspace/specs/_system.yml`
- Architecture docs for naming/convention context

## Required Read Scope
Read the actual changed runtime files:
- Routes/controllers/handlers
- Services/use-cases/domain logic
- Repositories/models/ORM code
- Migrations/schema files
- Workers/jobs/subscribers/publishers
- Integration adapters/clients

Do not generate specs from issue text/commit messages alone.

---

## Procedure

## 1) Determine target spec file
Choose one path:
- New feature -> create `.wonflowoo/workspace/specs/{feature}.yml`
- Existing feature -> update in place
- Boundary shift -> split/merge/reassign and update references

Naming rules:
- Kebab-case
- Stable unit identity (feature/domain/module/page/package)
- Not time-indexed

## 2) Build `source_paths`
Populate top-level `source_paths` from files represented by the spec.

Include behavior-defining files. Exclude generated/temp/test-only files unless needed to explain runtime behavior.

Example:
```yaml
source_paths:
  - src/routes/auth.routes.ts
  - src/services/auth.service.ts
  - src/repositories/refresh-token.repository.ts
```

## 3) Produce L1 Interfaces from interface code
Extract all I/O surfaces from routes/events/jobs/outbound clients.

For each interface include:
- `type`
- `direction`
- Interface detail (endpoint/topic/job/call)
- `file:` anchor

Example:
```yaml
interfaces:
  - type: rest
    direction: inbound
    file: src/routes/auth.routes.ts
    endpoints:
      - path: /api/auth/login
        method: POST
  - type: pubsub
    direction: outbound
    file: src/services/auth.service.ts
    topics:
      - name: user.login.success
```

## 4) Produce L2 Logic from service/domain code
Capture step-by-step behavior in flows.

Per flow capture:
- Flow name
- `trigger`
- Ordered `steps`
- `error_handling` subsection where applicable
- `security` subsection where applicable
- `file:` anchor

Structure:
```yaml
logic:
  flows:
    <flow_name>:
      file: src/path/to/file.ts
      trigger: <event/request>
      steps:
        - ...
      error_handling:
        - ...
      security:
        - ...
```

Write at behavioral level, not line-by-line code narration.

## 5) Produce L3 Data from ORM/migrations/repositories
Capture actual state interactions:
- Stores used (DB/cache/files)
- Tables/collections/keys touched
- Significant columns/fields/relationships
- `stateless: true` when no persistence

Stateless example:
```yaml
data: { stateless: true }
```

Represent actual read/write behavior, not only declared schema.

## 6) Produce L4 Dependencies from imports + runtime calls
Capture:
- Internal dependencies (`depends_on`, `depended_by` if known)
- External packages/services + usage purpose

Infer from imports and concrete runtime integration points.

## 7) Assemble/update feature spec
Required shape:
```yaml
name: <feature-name>
description: <purpose>
source_paths: [...]
interfaces: [...]
logic: {...}
data: {...}
dependencies: {...}
```

Mandatory traceability:
- Top-level `source_paths`
- `file:` fields for interfaces/flows/services where applicable

---

## Update `_system.yml`
After feature spec update, align system spec.

Update:
- `modules[]` summary
- `dependency_graph`
- `data_ownership`
- `data_relationships`
- `cross_module_flows` for changed multi-module behavior

### New feature
- Add module entry.

### Existing feature update
- Refresh module summary and relationships.

### Split/merge cases
- Reassign `source_paths`, remove old entries, and add new module entries.

System spec update rule: if new feature -> add module entry. If updating existing -> refresh summary and relationships. If splitting/merging -> reassign `source_paths`, remove old entries, add new ones.

---

## Developer Review Checklist
- [ ] Every changed runtime file appears in a spec `source_paths`
- [ ] Every spec interface exists in code
- [ ] Logic flows reflect real behavior and key error paths
- [ ] Data layer matches actual reads/writes
- [ ] Dependencies match real imports/integrations
- [ ] `_system.yml` updated for module/dependency/data changes
- [ ] Naming consistent across feature spec and `_system.yml`

## Commit Guidance
Commit implementation and spec updates together:
- Code changes
- Updated/created `.wonflowoo/workspace/specs/{feature}.yml`
- Updated `.wonflowoo/workspace/specs/_system.yml`

Do not defer spec updates to a follow-up commit.

After generating/updating specs, run `/spec-validate` to ensure bidirectional coverage before task closure.

## Completion Criteria
- Feature spec reflects current implemented behavior
- `_system.yml` reflects current system relationships
- Review checklist passes with no known drift
