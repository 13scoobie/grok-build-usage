#!/usr/bin/env bash
# Quick installer for the grok-usage skill
# Works on macOS and Linux (any Unix-like with bash)

set -e

SKILL_NAME="grok-usage"
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/${SKILL_NAME}"
GROK_HOME="${GROK_HOME:-$HOME/.grok}"
DEST_DIR="$GROK_HOME/skills/${SKILL_NAME}"

if [ ! -d "$SOURCE_DIR" ]; then
  echo "Error: Could not find $SOURCE_DIR"
  exit 1
fi

# Basic python3 check (the script uses it)
if ! command -v python3 >/dev/null 2>&1; then
  echo "Warning: python3 not found in PATH. The direct script will need it."
  echo "The /grok-usage skill fast path (tail+grep) does not require Python."
fi

echo "Installing grok-usage skill to $DEST_DIR ..."
mkdir -p "$GROK_HOME/skills"
cp -r "$SOURCE_DIR" "$GROK_HOME/skills/"

echo ""
echo "✅ Installed!"
echo ""
echo "Next steps:"
echo "  1. Open (or restart) your grok TUI"
echo "  2. Type /grok-usage"
echo ""
echo "You can also use:"
echo "  /grok-usage --json"
echo "  /grok-usage --refresh"
echo ""
echo "The command will show up in the slash menu automatically."
echo ""
echo "Supports GROK_HOME env var for non-default locations."
