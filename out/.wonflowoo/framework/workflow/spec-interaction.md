# Spec Interaction Guide

## Two-Tier Loading

- `_system.yml` — ALWAYS loaded. Holistic view.
- Individual specs — loaded ON DEMAND for relevant areas only.

## 4-Layer Model

- L1: Interfaces (any I/O — REST, gRPC, pubsub, WebSocket, scheduler, etc.)
- L2: Logic (step-by-step flows with error paths and edge cases)
- L3: Data (DB, cache, files, or stateless)
- L4: Dependencies (internal + external)

## Architecture docs ≠ Specs

- Architecture docs = intent, conventions, rationale (WHAT we planned)
- Specs = reality, actual implementation (WHAT exists)

## What Specs Do NOT Contain

- Exact code implementations, function signatures, variable names
- Exact SQL queries or line-by-line logic
- Test details or implementation minutiae
- Rationale or design decisions (that's in architecture docs)
- Aspirational features (that's in requirements + architecture docs)

## Cross-Module Flows

Cross-module flows (e.g., "user places order → payment → notification → inventory update") live in the **system spec** (`_system.yml`) under `cross_module_flows`.

Individual specs cover internal module logic. `_system.yml` captures inter-module interactions.

## Frontend Specs

Frontend modules also require specs when implemented/changed. Keep the same 4-layer model:
- Interface layer for UI/API boundaries
- Logic layer for state + interaction flows
- Data layer for local/remote data handling
- Dependency layer for internal/external dependencies

## Do NOT search the codebase (when specs exist)

On projects with specs, work from specs + arch docs. If you need to search code, the specs are incomplete — fix the specs.
