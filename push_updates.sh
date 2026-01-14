#!/usr/bin/env bash
set -euo pipefail

SRC="/home/slygentleman/Desktop/ai_wire_v2"
REPO="/home/slygentleman/Desktop/ai-wire-repo"

cd "$REPO"

# Copy freshly generated JSON into the repo
cp "$SRC/data.json" "$REPO/data.json"
cp "$SRC/benchmarks.json" "$REPO/benchmarks.json"

# Commit only if there are changes
git add data.json benchmarks.json

if git diff --cached --quiet; then
  echo "[OK] No changes to publish."
  exit 0
fi

git commit -m "Daily update $(date -u +%F)"
git push origin main

echo "[OK] Published updates to GitHub Pages."
