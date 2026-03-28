---
name: token-usage
description: "Extract token usage per session and sub-agents. Detects platform (OmO or Claude Code) and runs the appropriate tool."
allowed-tools: Read, Bash, Glob
---

# Skill: Token Usage Analysis

Extracts per-turn token usage for a session and all its sub-agents. Useful after tests to check context growth and scalability.

## Usage

```
/token-usage [session-id]
```

If no session ID is provided, detect the current session:
- **OmO**: run `opencode session list` and use the most recent session ID
- **Claude Code**: find the most recently modified `.jsonl` in `~/.claude/projects/` for the current working directory

## Platform Detection

Detect which platform is running, then use the correct tool:

- If `opencode` CLI is available → run `.claude/skills/token-usage/omo-token-usage.sh <session-id>`
- If `~/.claude/projects/` exists → run `.claude/skills/token-usage/claude-token-usage.sh <session-id>`
- If neither → report error

## Output

Both tools produce the same output format:

```
=== ORCHESTRATOR ===
Session: <id>
Messages: N
Steps: N
Context: min → max tokens
Growth: Nx

=== SUB-AGENTS ===
TITLE                                 STEPS    MIN      MAX
...

=== SUMMARY ===
Max orchestrator context: N ✅ OK / ⚠️ ELEVATED / ⚠️ HIGH
Compaction risk: LOW / MODERATE / HIGH
```
