#!/bin/bash
set -e

CLAUDE_DIR="$HOME/.claude/projects"
CWD_HASH=$(echo "$PWD" | sed 's|/|-|g')

SESSION_ID="$1"
if [ -z "$SESSION_ID" ]; then
  LATEST=$(find "$CLAUDE_DIR/$CWD_HASH" -name "*.jsonl" -type f 2>/dev/null | xargs ls -t 2>/dev/null | head -1)
  if [ -z "$LATEST" ]; then
    LATEST=$(find "$CLAUDE_DIR" -name "*.jsonl" -type f 2>/dev/null | xargs ls -t 2>/dev/null | head -1)
  fi
  if [ -z "$LATEST" ]; then
    echo "No session ID provided and no sessions found."
    echo "Usage: $0 [session-id]"
    exit 1
  fi
  SESSION_ID=$(basename "$LATEST" .jsonl)
  echo "Auto-detected session: $SESSION_ID"
  echo ""
fi

if [ ! -d "$CLAUDE_DIR" ]; then
  echo "Error: ~/.claude/projects/ not found. Is Claude Code installed?"
  exit 1
fi

JSONL_FILE=$(find "$CLAUDE_DIR" -name "${SESSION_ID}*.jsonl" 2>/dev/null | head -1)

if [ -z "$JSONL_FILE" ]; then
  JSONL_FILE=$(find "$CLAUDE_DIR" -name "*.jsonl" -exec grep -l "$SESSION_ID" {} \; 2>/dev/null | head -1)
fi

if [ -z "$JSONL_FILE" ]; then
  echo "Error: Session $SESSION_ID not found in ~/.claude/projects/"
  echo "Available sessions:"
  find "$CLAUDE_DIR" -name "*.jsonl" -exec basename {} .jsonl \; 2>/dev/null | tail -10
  exit 1
fi

node -e "
const fs = require('fs');
const lines = fs.readFileSync('$JSONL_FILE', 'utf8').trim().split('\n');
const entries = lines.map(l => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);

let msgCount = 0;
let steps = [];
let totalInput = 0;
let totalOutput = 0;

for (const entry of entries) {
  if (entry.type === 'assistant' && entry.message?.usage) {
    msgCount++;
    const u = entry.message.usage;
    const input = (u.input_tokens || 0) + (u.cache_read_input_tokens || 0) + (u.cache_creation_input_tokens || 0);
    const output = u.output_tokens || 0;
    const total = input + output;
    steps.push(total);
    totalInput += input;
    totalOutput += output;
  }
}

console.log('=== ORCHESTRATOR ===');
console.log('Session:', '$SESSION_ID');
console.log('File:', '$JSONL_FILE');
console.log('Messages:', msgCount);
console.log('Steps:', steps.length);
if (steps.length > 0) {
  console.log('Context: ' + Math.min(...steps).toLocaleString() + ' → ' + Math.max(...steps).toLocaleString() + ' tokens (per-turn)');
  console.log('Total input: ' + totalInput.toLocaleString() + ' tokens');
  console.log('Total output: ' + totalOutput.toLocaleString() + ' tokens');
}
console.log();

console.log('Sub-agents found: N/A (Claude Code sub-agents are isolated — no session linking)');
console.log();

console.log('=== SUMMARY ===');
const maxTurn = steps.length > 0 ? Math.max(...steps) : 0;
const flag = maxTurn > 150000 ? ' ⚠️  HIGH' : maxTurn > 100000 ? ' ⚠️  ELEVATED' : ' ✅ OK';
console.log('Max per-turn context: ' + maxTurn.toLocaleString() + flag);
console.log('Note: Claude Code reports per-API-call tokens, not cumulative context like OmO.');
console.log('Total tokens used: ' + (totalInput + totalOutput).toLocaleString());
"
