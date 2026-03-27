# /init-deep vs Specs System — Analysis

Comparing OmO's `/init-deep` hierarchical AGENTS.md system with our framework's specs system.

## What Each System Is

### `/init-deep` (OmO)

A **context injection system**. Generates hierarchical `AGENTS.md` files at multiple directory levels — telegraphic, convention-focused, auto-injected when an agent reads files in that directory. Breadcrumbs scattered through the codebase so any agent landing anywhere knows the local rules.

Generated from static analysis: file counts, LSP symbols, configs, directory structure. Scored by complexity — not every directory gets one. Child never repeats parent.

### Our Specs

A **compressed codebase representation for the orchestrator's mental model**. YAML files that capture what actually exists: module structure, data model, API surface, feature inventory, dependency graph. The tech lead's mental map of the whole system, externalized.

Generated from code behavior and semantics — post-implementation, updated after every code change.

## What `/init-deep` Root AGENTS.md Actually Contains

| Section | What it captures | Orchestrator planning value |
|---|---|---|
| OVERVIEW | 1-2 sentences, core stack | Minimal — too compressed |
| STRUCTURE | Directory tree with non-obvious purposes | Navigation — WHERE things are, not WHAT they do |
| WHERE TO LOOK | Task → location mapping | Navigation — "auth stuff is in src/auth" |
| CODE MAP | Symbols, types, locations, reference counts (from LSP) | Structural centrality — "UserService is referenced 47 times" |
| CONVENTIONS | Deviations from standard only | Style guidance — how to write, not what exists |
| ANTI-PATTERNS | What's forbidden | Guardrails — what NOT to do |
| COMMANDS | dev/test/build | Operational |

CODE MAP is the closest to "understanding the system" — symbol names, types, file locations, reference counts from LSP. Gives **structural centrality** (what's important by reference count) and **physical layout** (where things live).

## What `/init-deep` Does NOT Give an Orchestrator

- **Semantic knowledge** — "UserService handles registration, login, profile management, uses bcrypt for passwords, and the user table has 12 columns with a soft-delete pattern"
- **Logical dependency flow** — "The order service calls user service for billing info, then calls notification service for receipts"
- **Actual API surface** — "The API has 23 endpoints, all using this auth middleware, all returning this error shape"
- **Data model relationships** — "The payments table has a foreign key to orders, which has a foreign key to users, with cascade delete"

`/init-deep` tells you "there's a thing called UserService at this location that 47 other things reference." It doesn't tell you what UserService does, what data it touches, or how it connects to OrderService at a business logic level.

## Does `/init-deep` Help the Orchestrator Plan?

**No.** It's a structural index optimized for developer navigation — "I just landed in this directory, what are the local rules?" It saves context by being telegraphic and hierarchical (child never repeats parent), but it's saving context on the wrong information for planning. An orchestrator needs semantic understanding of the system, not a directory guide.

## Capability Comparison

| Planning Need | `/init-deep` | Our Specs |
|---|---|---|
| "Where is the auth code?" | ✅ WHERE TO LOOK table | ✅ module structure |
| "What does the auth module do?" | ❌ | ✅ feature inventory, logic summary |
| "What tables does auth touch?" | ❌ | ✅ data model with relationships |
| "What endpoints exist?" | ❌ | ✅ API surface |
| "If I add payments, what does it integrate with?" | ❌ | ✅ dependency graph + feature flow |
| "What conventions should I follow here?" | ✅ CONVENTIONS section | ✅ conventions.yml |
| "What's forbidden in this directory?" | ✅ ANTI-PATTERNS | ❌ (not per-directory) |
| "How do I orient myself in this module?" | ✅ (primary purpose) | ❌ (not its job) |

## Key Differences

| Dimension | `/init-deep` | Our Specs |
|---|---|---|
| **Purpose** | Help any agent orient itself in a directory | Help the orchestrator understand the whole system without reading all code |
| **Audience** | Every agent, every session | Primarily the orchestrator; developers load relevant slices |
| **Scope** | Per-directory (local context) | Per-system (global picture) |
| **Content type** | Conventions, anti-patterns, structure, gotchas | Actual state — modules, data model, APIs, features, dependencies |
| **Format** | Markdown (telegraphic prose) | YAML (structured, machine-parsable) |
| **Generated from** | Static analysis (file counts, LSP symbols, configs) | Code behavior and semantics (what it does, not just what it looks like) |
| **When created** | On demand, can be regenerated anytime | Post-implementation, updated after every code change |
| **Relationship to code** | Describes conventions and structure around the code | Describes what the code actually does |
| **Core question answered** | "How should I write code here?" | "What already exists and how does it connect?" |

## Conclusion

They're **complementary layers**, not competitors. `/init-deep` is developer-facing (local orientation). Specs are orchestrator-facing (system understanding). If you had to pick one for orchestrator-level planning, specs win by a mile — but the best system has both.

Our framework should consider whether per-directory convention injection (like `/init-deep`) adds value on top of our architecture docs (`conventions.yml`) + specs. The open question: does `conventions.yml` already cover what `/init-deep` does for developers, or is there value in the hierarchical, per-directory, auto-injected format?
