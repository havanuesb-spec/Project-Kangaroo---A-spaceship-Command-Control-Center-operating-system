#!/usr/bin/env bash
set -e
HARV_URL="${HARV_URL:-http://localhost:5000}"
USER="${1:-$(git config user.name)}"
if [ -z "$USER" ]; then echo "provide user"; exit 1; fi
resp=$(curl -s -X POST -H "Content-Type: application/json" -d "{\"user\":\"$USER\"}" "$HARV_URL/enter")
token=$(echo "$resp" | jq -r .token)
if [ "$token" = "null" ] || [ -z "$token" ]; then echo "enter failed"; echo "$resp"; exit 1; fi
echo "$token" > .edit_token
# enable local hooks
mkdir -p .githooks
cat > .githooks/commit-msg <<'HOOK'
#!/bin/sh
tokfile=".edit_token"
if [ ! -f "$tokfile" ]; then
  echo "Not in edit mode. Use enter-edit-mode.sh"
  exit 1
fi
token=$(cat "$tokfile")
echo "" >> "$1"
echo "Edit-Session-Token: ${token:0:16}" >> "$1"
HOOK
chmod +x .githooks/commit-msg
git config core.hooksPath .githooks
echo "Entered edit mode; token saved"
