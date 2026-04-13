#!/usr/bin/env python3
import json, subprocess, sys, hashlib, datetime
from pathlib import Path

def run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def sha256_tree(root: Path):
    h = hashlib.sha256()
    for p in sorted(root.rglob("*")):
        if p.is_file():
            h.update(str(p.relative_to(root)).encode())
            h.update(b"\0")
            h.update(p.read_bytes())
            h.update(b"\0")
    return h.hexdigest()

def git_info():
    commit = run("git rev-parse --verify HEAD").stdout.strip()
    branch = run("git rev-parse --abbrev-ref HEAD").stdout.strip()
    return commit, branch

def ci_status():
    # simple heuristic: check .github/workflows last run via env or leave unknown
    return "unknown"

def build_status(connected_actors):
    repo = run("basename `git rev-parse --show-toplevel`").stdout.strip()
    commit, branch = git_info()
    tree_hash = sha256_tree(Path("."))
    st = {
        "repo": repo,
        "commit": commit,
        "branch": branch,
        "timestamp_utc": datetime.datetime.utcnow().isoformat()+"Z",
        "ci_status": ci_status(),
        "license": Path("LICENSE").read_text()[:200] if Path("LICENSE").exists() else None,
        "dco_ok": None,
        "integrity_hash": tree_hash,
        "connected_actors": connected_actors,
        "provenance": {"generated_by": "status.py"}
    }
    Path("status.json").write_text(json.dumps(st, indent=2))
    # sign with gpg (requires a key setup and gpg installed)
    sig = run("gpg --detach-sign --armor status.json")
    if sig.returncode != 0:
        print("GPG sign failed:", sig.stderr, file=sys.stderr)
        sys.exit(1)
    print("Wrote status.json and status.json.asc")

if __name__ == "__main__":
    # Accept connected actors as comma-separated CLI arg, e.g., "core,mirror1"
    actors = sys.argv[1].split(",") if len(sys.argv) > 1 else []
    build_status(actors)
