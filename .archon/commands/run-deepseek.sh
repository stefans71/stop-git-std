#!/bin/bash
# DeepSeek V3.2 agent runner for FrontierBoard-Archon integration
# Generic wrapper — project files are passed via inbox, not hardcoded paths
set -euo pipefail

AGENT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTBOX="$AGENT_DIR/outbox"
API_KEY="${DEEPSEEK_API_KEY:?DEEPSEEK_API_KEY not set}"
MODEL="${DEEPSEEK_MODEL:-deepseek-chat}"
API_URL="https://api.deepseek.com/chat/completions"
TMPDIR=$(mktemp -d)
trap 'rm -rf $TMPDIR' EXIT

# Build system prompt from agent identity
cat "$AGENT_DIR/CLAUDE.md" > "$TMPDIR/system.txt"

# Build user prompt from inbox files
# context.md and brief.md are required; additional files are optional
cat > "$TMPDIR/user.txt" << 'SECTION'
## Context
SECTION
cat "$AGENT_DIR/inbox/context.md" >> "$TMPDIR/user.txt"

cat >> "$TMPDIR/user.txt" << 'SECTION'

## Brief
SECTION
cat "$AGENT_DIR/inbox/brief.md" >> "$TMPDIR/user.txt"

# Append any additional inbox files (round2-brief.md, consolidation.md, etc.)
for EXTRA in "$AGENT_DIR/inbox/"*.md; do
  BASENAME=$(basename "$EXTRA")
  case "$BASENAME" in
    context.md|brief.md) continue ;;  # already included
    *)
      cat >> "$TMPDIR/user.txt" << SECTION

## $BASENAME
SECTION
      cat "$EXTRA" >> "$TMPDIR/user.txt"
      ;;
  esac
done

echo "Prompt assembled: $(wc -c < "$TMPDIR/user.txt") bytes"

# Build JSON payload using bun
bun -e "
const fs = require('fs');
const system = fs.readFileSync('$TMPDIR/system.txt', 'utf8');
const user = fs.readFileSync('$TMPDIR/user.txt', 'utf8');
const payload = {
  model: '$MODEL',
  messages: [
    { role: 'system', content: system },
    { role: 'user', content: user }
  ],
  max_tokens: 8192,
  temperature: 0.3
};
fs.writeFileSync('$TMPDIR/payload.json', JSON.stringify(payload));
console.log('Payload written:', Math.round(fs.statSync('$TMPDIR/payload.json').size / 1024) + 'KB');
"

echo "Calling DeepSeek API ($MODEL)..."
curl -s -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d @"$TMPDIR/payload.json" > "$TMPDIR/response.json"

# Extract the response content
bun -e "
const fs = require('fs');
const data = JSON.parse(fs.readFileSync('$TMPDIR/response.json', 'utf8'));
if (data.choices && data.choices[0]) {
  fs.writeFileSync('$OUTBOX/report.md', data.choices[0].message.content);
  console.log('Report written (' + data.choices[0].message.content.split('\n').length + ' lines)');
  if (data.usage) console.log('Tokens:', JSON.stringify(data.usage));
} else if (data.error) {
  console.error('API Error:', JSON.stringify(data.error));
  process.exit(1);
} else {
  console.error('Unexpected response:', JSON.stringify(data).substring(0,500));
  process.exit(1);
}
"
