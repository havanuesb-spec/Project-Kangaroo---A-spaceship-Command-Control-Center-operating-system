#!/usr/bin/env bash
set -e
AUDIT="${1:-./audit.log}"
DIGEST=$(sha256sum "$AUDIT" | awk '{print $1}')
echo "{\"audit_file\":\"$AUDIT\",\"sha256\":\"$DIGEST\",\"ts\":\"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\"}" > audit_digest.json
gpg --armor --detach-sign --output audit_digest.json.asc audit_digest.json
echo "wrote audit_digest.json and audit_digest.json.asc"
