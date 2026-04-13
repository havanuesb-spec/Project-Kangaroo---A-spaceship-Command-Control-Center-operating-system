#!/usr/bin/env bash
set -e
USER="${1:-$(git config user.name)}"
if [ -z "$USER" ]; then echo "user required"; exit 1; fi
TOKEN=$(curl -s -X POST -H "Content-Type: application/json" -d "{\"user\":\"$USER\"}" http://localhost:4000/enter | jq -r .token)
echo "$TOKEN" > .edit_token
# enable commit hook that adds Signed-off-by and records action
mkdir -p .githooks
cat > .githooks/commit-msg <<'HOOK'
#!/bin/sh
tokfile=".edit_token"
if [ ! -f "$tokfile" ]; then
  echo "Not in edit mode. Use enter-edit-mode.sh"
  exit 1
fi
token=$(cat "$tokfile")
# append token info to commit message for audit linking (short)
echo "" >> "$1"
echo "Edit-Session-Token: ${token:0:16}" >> "$1"
HOOK
chmod +x .githooks/commit-msg
git config core.hooksPath .githooks
echo "Entered edit mode; token saved to .edit_token"
