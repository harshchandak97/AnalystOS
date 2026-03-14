#!/usr/bin/env bash
# Push AnalystOS to GitHub. Run from project root.
# If you see an Xcode license error, run first: sudo xcodebuild -license
set -e
cd "$(dirname "$0")/.."

REMOTE="https://github.com/harshchandak97/AnalystOS.git"

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "Initializing git..."
  git init
fi

echo "Adding files..."
git add -A
git status

if git diff --cached --quiet 2>/dev/null && git rev-parse HEAD >/dev/null 2>&1; then
  echo "Nothing new to commit."
else
  echo "Creating commit..."
  git commit -m "Initial commit: AnalystOS hackathon scaffold (Streamlit + src modules + sample data)" || true
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  echo "Adding remote origin..."
  git remote add origin "$REMOTE"
fi

echo "Setting branch to main and pushing..."
git branch -M main
git push -u origin main

echo "Done. Repo is at: $REMOTE"
