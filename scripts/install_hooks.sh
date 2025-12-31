#!/bin/sh
# Install git hooks

HOOK_DIR=".git/hooks"
SCRIPT_DIR="scripts"

if [ ! -d "$HOOK_DIR" ]; then
    echo "Error: .git directory not found. Are you in the root of the repo?"
    exit 1
fi

echo "Installing pre-commit hook..."
cp "$SCRIPT_DIR/pre-commit" "$HOOK_DIR/pre-commit"
chmod +x "$HOOK_DIR/pre-commit"

echo "Hooks installed successfully!"
