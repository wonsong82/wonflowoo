# Phase 1: Discovery (Cases 1-2 Only)

## Goal

Capture and confirm WHAT we're building. Business requirements only. NO tech decisions.

## Inputs to Load

1. `.wonflowoo/workspace/drafts/{id}-{name}.md` (active draft)
2. `.wonflowoo/workspace/specs/_system.yml` (for existing projects)
3. Relevant existing specs (add-feature only)

## Steps

**Step 1 — Research before asking.**
BEFORE asking the human ANY questions, fire librarian research:
- "What are typical features and requirements for {type of system}?"
- "What are best practices and standard capabilities for {domain}?"
Use findings to ask INFORMED questions, not generic ones.

**Step 2 — Interview the human.**
Ask about BUSINESS REQUIREMENTS ONLY:
- What the system does (features, workflows)
- Who uses it (roles, personas, access levels)
- What it integrates with (external systems, data sources)
- Scope boundaries (what's IN, what's OUT)
- Constraints (timeline, compliance, scale)

DO NOT ask about:
- Tech stack (language, framework, database)
- Deployment (cloud, containers, hosting)
- Infrastructure (CI/CD, monitoring)
- Any HOW questions — those belong in Architecture

If the human volunteers tech preferences, note them in the draft. Do NOT put them in the requirements doc.

**Step 3 — After each exchange, suggest standard requirements.**
"Systems like this typically also need X, Y, Z. Do you want these?"

**Step 4 — After each exchange, run clearance check.**

```
DISCOVERY CLEARANCE:
□ Core objective clearly defined?
□ Scope boundaries established (IN / OUT)?
□ User roles / personas identified?
□ Key data entities identified?
□ Integration points with external systems identified?
□ Tech preferences or constraints captured? (greenfield only)
□ Impact on existing system understood? (add feature only)
□ Affected modules / specs identified? (add feature only)
□ No critical ambiguities remaining?
```

Show the checklist with status. If ANY item is unchecked → ask the specific question.

**Step 5 — When ALL items pass: write requirements doc.**
Output: `.wonflowoo/workspace/requirements/{id}-{name}.md` — confirmed scope, features, constraints, acceptance criteria. NO tech stack.
Requirements doc header must include: `Status: pending_approval | approved | amended`.

## Failure Handling

- Librarian returns nothing useful → re-research with more specific query or different angle
- Human gives contradictory requirements → surface the contradiction explicitly, ask to resolve
- Clearance items keep failing after 2 rounds → present what's unclear and ask human to fill the gaps directly
- 3 consecutive failures → STOP, document what's blocking, escalate to human

## Phase Gate

If `auto_proceed` is false (default): STOP. Present summary to human. Wait for explicit confirmation. DO NOT auto-advance.
If `auto_proceed` is true: Log the summary to draft, proceed automatically.
When human confirms requirements, update requirements status to `approved`.
