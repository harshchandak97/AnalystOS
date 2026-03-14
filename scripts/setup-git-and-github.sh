#!/usr/bin/env bash
# Run this after accepting the Xcode license: sudo xcodebuild -license
set -e
cd "$(dirname "$0")/.."

echo "Initializing git..."
git init

echo "Adding files..."
git add README.md .gitignore scripts/

echo "Creating initial commit..."
git commit -m "Initial commit: Add README and .gitignore"

echo ""
echo "Done. To link to GitHub:"
echo "  1. Create a new repository on GitHub named 'AnalystOS' (or your choice)."
echo "  2. Run: git remote add origin https://github.com/YOUR_USERNAME/AnalystOS.git"
echo "  3. Run: git branch -M main && git push -u origin main"
echo ""
echo "Or with SSH: git remote add origin git@github.com:YOUR_USERNAME/AnalystOS.git"
