#!/usr/bin/env bash
set -e
if [ ! -f .edit_token ]; then echo "enter edit mode first"; exit 1; fi
TOKEN=$(cat .edit_token)
HARV_URL="${HARV_URL:-http://localhost:5000}"
OP="$1"
shift
curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "{\"op\":\"$OP\",\"args\":$(jq -nc --argjson a '[]' '$a')}" "$HARV_URL/run" | jq
