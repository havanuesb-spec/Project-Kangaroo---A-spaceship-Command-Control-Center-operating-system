#!/usr/bin/env bash
set -e
if [ ! -f .edit_token ]; then echo "Not in edit mode"; exit 1; fi
TOKEN=$(cat .edit_token)
curl -s -X POST -H "Content-Type: application/json" -d "{\"token\":\"$TOKEN\"}" http://localhost:4000/exit
rm -f .edit_token
git config --unset core.hooksPath || true
echo "Exited edit mode; hooks disabled"
