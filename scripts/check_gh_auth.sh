#!/bin/bash

# Check GitHub CLI authentication using GH_TOKEN

set -e  # Exit on error

# Check if GH_TOKEN is set
if [ -z "${GH_TOKEN:-}" ]; then
    echo "Error: GH_TOKEN environment variable is not set."
    echo "Set it with: export GH_TOKEN=<your_github_token>"
    exit 1
fi

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "Error: gh CLI is not installed."
    echo "Install from: https://cli.github.com/"
    exit 1
fi

# Export token for gh CLI to pick up
export GH_TOKEN

echo "Checking GitHub CLI authentication..."
if gh auth status 2>&1; then
    echo "GitHub CLI authentication successful."
else
    echo "Error: GitHub CLI authentication failed."
    echo "Ensure GH_TOKEN is a valid GitHub personal access token."
    exit 1
fi
