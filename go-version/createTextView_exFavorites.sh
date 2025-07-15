#!/bin/bash

# Wrapper script for text-view-path command for favorites (equivalent to createTextView_exFavorites.py)
# This script calls the Go binary with proper path resolution for favorites

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Path to the Go binary
BINARY="$SCRIPT_DIR/xkcd-alfred"

# Check if binary exists
if [ ! -f "$BINARY" ]; then
    echo "Error: xkcd-alfred binary not found at $BINARY" >&2
    echo "Please run build.sh first" >&2
    exit 1
fi

# Make sure binary is executable
chmod +x "$BINARY"

# Call the binary with text-view-path command and pass all arguments
# This works for both recents and favorites since text-view-path handles any image path
exec "$BINARY" text-view-path "$@" 