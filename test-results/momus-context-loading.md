# Test Result: Momus Context Loading (Built-in Agent Role Routing)

**Test date:** 2026-03-28  
**Platform:** OmO (OpenCode) via opencode run  
**Session:** ses_2cdeb2ec3ffeBtJGng5jOn5ztx  
**Duration:** ~2 min  
**Result:** PASS — momus follows Role Routing and loads framework context  

---

## What This Test Validates

Whether OmO's built-in momus agent (used for plan-reviewer role) follows the AGENTS.md Role Routing and loads the tech-lead context files — specifically `.wonflowoo/framework/agent-guides/tech-leads.md` and `.wonflowoo/workspace/specs/_system.yml`.

This matters because momus has its own built-in system prompt. The question was: does it also respect project-level AGENTS.md instructions?

---

## Test Setup

Created a minimal test environment with:
- WonfloWoo AGENTS.md (with Role Routing)
- `.wonflowoo/framework/agent-guides/tech-leads.md`
- `.wonflowoo/workspace/specs/_system.yml` with distinctive fake content:
  - Module: `unicorn-launcher` ("Launches magical unicorns into orbit using rainbow fuel")
  - Module: `dragon-tamer` ("Tames wild dragons using AI-powered lullabies")
  - Cross-module flow: `launch_sequence`

The orchestrator dispatched `task(subagent_type="momus")` with `Role: plan-reviewer` in the prompt, asking the agent to report what it loaded.

---

## Results

| Check | Result |
|---|---|
| Read AGENTS.md? | ✅ Read both test-level and project-level |
| Role Routing → Tech Lead section? | ✅ Correctly identified plan-reviewer → Sub-Agent: Tech Lead |
| Loaded tech-leads.md? | ✅ `.wonflowoo/framework/agent-guides/tech-leads.md` |
| Loaded _system.yml? | ✅ `.wonflowoo/workspace/specs/_system.yml` |
| Found unicorn-launcher module? | ✅ |
| Found dragon-tamer module? | ✅ |
| Found launch_sequence flow? | ✅ |
| Guessed anything? | ✅ No — all answers backed by file reads |

---

## Key Finding

**Built-in OmO agents DO follow AGENTS.md Role Routing** when run from a directory with the framework installed. The earlier failed test (which concluded momus ignores AGENTS.md) was run from the project root which had no framework files — not a valid test environment.

---

## Summary

| Checks | Pass | Gaps |
|---|---|---|
| 8 | 8 | 0 |

**Zero gaps. Momus loads tech-lead context via Role Routing.**
