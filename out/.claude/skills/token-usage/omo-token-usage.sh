#!/bin/bash
set -e

SESSION_ID="$1"
if [ -z "$SESSION_ID" ]; then
  SESSION_ID=$(opencode session list 2>/dev/null | awk 'NR==3 {print $1}')
  if [ -z "$SESSION_ID" ]; then
    echo "No session ID provided and no sessions found."
    echo "Usage: $0 [session-id]"
    exit 1
  fi
  echo "Auto-detected session: $SESSION_ID"
  echo ""
fi

TMP=$(mktemp -d)
trap "rm -rf $TMP" EXIT

opencode export "$SESSION_ID" 2>/dev/null > "$TMP/main.json"

node -e "
const fs = require('fs');
const data = JSON.parse(fs.readFileSync('$TMP/main.json', 'utf8'));
const msgs = data.messages || [];

const steps = [];
for (const msg of msgs) {
  for (const p of msg.parts || []) {
    if (p.type === 'step-finish' && p.tokens) {
      steps.push(p.tokens.total || 0);
    }
  }
}

console.log('=== ORCHESTRATOR ===');
console.log('Session:', '$SESSION_ID');
console.log('Messages:', msgs.length);
console.log('Steps:', steps.length);
if (steps.length > 0) {
  console.log('Context: ' + Math.min(...steps).toLocaleString() + ' → ' + Math.max(...steps).toLocaleString() + ' tokens');
  console.log('Growth: ' + Math.round(Math.max(...steps) / Math.min(...steps)) + 'x');
}
console.log();

const subSessions = new Set();
for (const msg of msgs) {
  for (const p of msg.parts || []) {
    const s = JSON.stringify(p);
    const m = s.match(/ses_[a-zA-Z0-9]+/g);
    if (m) m.forEach(id => subSessions.add(id));
  }
}
subSessions.delete('$SESSION_ID');
fs.writeFileSync('$TMP/subs.txt', Array.from(subSessions).join('\n'));
console.log('Sub-agents found:', subSessions.size);
console.log();
"

if [ -s "$TMP/subs.txt" ]; then
  echo "=== SUB-AGENTS ==="
  echo ""
  printf "%-55s %6s %8s %8s\n" "TITLE" "STEPS" "MIN" "MAX"
  printf "%-55s %6s %8s %8s\n" "-----" "-----" "---" "---"

  while IFS= read -r sid; do
    opencode export "$sid" 2>/dev/null > "$TMP/sub.json" || continue
    node -e "
const fs = require('fs');
const data = JSON.parse(fs.readFileSync('$TMP/sub.json', 'utf8'));
const msgs = data.messages || [];
let max = 0, min = Infinity, steps = 0;
for (const msg of msgs) {
  for (const p of msg.parts || []) {
    if (p.type === 'step-finish' && p.tokens) {
      const t = p.tokens.total || 0;
      if (t > max) max = t;
      if (t < min && t > 0) min = t;
      steps++;
    }
  }
}
const title = (data.info?.title || '$sid').substring(0, 55);
if (min === Infinity) min = 0;
console.log(title.padEnd(55) + ' ' + String(steps).padStart(6) + ' ' + String(min.toLocaleString()).padStart(8) + ' ' + String(max.toLocaleString()).padStart(8));
" 2>/dev/null
  done < "$TMP/subs.txt"
  echo ""
fi

echo "=== SUMMARY ==="
node -e "
const fs = require('fs');
const data = JSON.parse(fs.readFileSync('$TMP/main.json', 'utf8'));
const msgs = data.messages || [];
let maxOrch = 0;
for (const msg of msgs) {
  for (const p of msg.parts || []) {
    if (p.type === 'step-finish' && p.tokens) {
      const t = p.tokens.total || 0;
      if (t > maxOrch) maxOrch = t;
    }
  }
}
const flag = maxOrch > 150000 ? ' ⚠️  HIGH' : maxOrch > 100000 ? ' ⚠️  ELEVATED' : ' ✅ OK';
console.log('Max orchestrator context: ' + maxOrch.toLocaleString() + flag);
console.log('Compaction risk: ' + (maxOrch > 150000 ? 'HIGH — draft re-entry will be needed' : maxOrch > 100000 ? 'MODERATE — may compact on longer sessions' : 'LOW'));
"
