#!/bin/bash

# Navigate to the Football_bot directory
cd /root/Football_bot

echo "=== Football Bot GitHub Push Script ==="
echo "Repository: https://github.com/alextrx818/claud4_final.git"
echo "Current directory: $(pwd)"
echo ""

# Check git status
echo "Checking git status..."
git status

echo ""
echo "Checking remote configuration..."
git remote -v

echo ""
echo "Checking current branch..."
git branch

echo ""
echo "Adding any untracked files..."
git add .

echo ""
echo "Committing any remaining changes..."
git commit -m "🚀 Final update: Complete 4-stage Football Bot pipeline with comprehensive documentation and production features" || echo "No changes to commit"

echo ""
echo "Fetching latest from remote..."
git fetch origin

echo ""
echo "Pushing to GitHub with force..."
git push origin master:main --force-with-lease

echo ""
echo "=== Push completed! ==="
echo "Check your repository at: https://github.com/alextrx818/claud4_final" 