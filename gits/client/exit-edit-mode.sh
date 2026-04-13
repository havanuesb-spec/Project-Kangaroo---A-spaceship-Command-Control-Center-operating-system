#!/usr/bin/env bash
set -e
HARV_URL="${HARV_URL:-http://localhost:5000}"
if [ ! -f .edit_token ]; then echo "not in edit mode"; exit 1; fi
TOKEN=$(cat .edit_token)
curl -s -X POST -H "Content-Type: application/json" -d "{\"token\":\"$TOKEN\"}" "$HARV_URL/exit" >/dev/null
rm -f .edit_token
git config --unset core.hooksPath || true
echo "Exited edit mode"
