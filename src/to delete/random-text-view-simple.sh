#!/bin/bash

# Simple Random Text View Script (for use within Alfred workflow)
# This script assumes alfred_workflow_data is already set by Alfred
# Set the Alfred workflow data path if not already set (for testing outside Alfred)
if [ -z "$alfred_workflow_data" ]; then
    export alfred_workflow_data="$HOME/Library/Application Support/Alfred/Workflow Data/giovanni.xkcd"
fi

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
XKCD_BINARY="$SCRIPT_DIR/xkcd-alfred"

# Check if the binary exists
if [ ! -f "$XKCD_BINARY" ]; then
    echo "Error: xkcd-alfred binary not found at $XKCD_BINARY"
    echo "Please run ./build.sh ../src first to compile the binary"
    exit 1
fi

# Get a random comic and parse the JSON to extract comic number and other details
RANDOM_OUTPUT=$("$XKCD_BINARY" random)

# Check if the random command was successful
if [ $? -ne 0 ]; then
    echo "Error: Failed to get random comic"
    exit 1
fi

# Extract the comic number from the JSON output using jq or sed/grep
# First try with jq if available, otherwise fall back to sed
if command -v jq >/dev/null 2>&1; then
    COMIC_NUM=$(echo "$RANDOM_OUTPUT" | jq -r '.items[0].arg')
    IMAGE_URL=$(echo "$RANDOM_OUTPUT" | jq -r '.items[0].variables.imageURL')
    COMIC_TITLE=$(echo "$RANDOM_OUTPUT" | jq -r '.items[0].variables.comicTitle')
    COMIC_ALT=$(echo "$RANDOM_OUTPUT" | jq -r '.items[0].variables.comicAlt')
    COMIC_DATE=$(echo "$RANDOM_OUTPUT" | jq -r '.items[0].variables.comicDate')
    IMAGE_PATH=$(echo "$RANDOM_OUTPUT" | jq -r '.items[0].variables.imagePath')
    TOGGLE_FAV=$(echo "$RANDOM_OUTPUT" | jq -r '.items[0].variables.toggleFav')
    IS_FAVORITE=$(echo "$RANDOM_OUTPUT" | jq -r '.items[0].variables.isFavorite')
else
    # Fallback to sed/grep parsing (less reliable but works without jq)
    COMIC_NUM=$(echo "$RANDOM_OUTPUT" | grep -o '"arg":"[0-9]*"' | head -1 | sed 's/"arg":"\([0-9]*\)"/\1/')
    IMAGE_URL=$(echo "$RANDOM_OUTPUT" | grep -o '"imageURL":"[^"]*"' | head -1 | sed 's/"imageURL":"\([^"]*\)"/\1/')
    COMIC_TITLE=$(echo "$RANDOM_OUTPUT" | grep -o '"comicTitle":"[^"]*"' | head -1 | sed 's/"comicTitle":"\([^"]*\)"/\1/')
    COMIC_ALT=$(echo "$RANDOM_OUTPUT" | grep -o '"comicAlt":"[^"]*"' | head -1 | sed 's/"comicAlt":"\([^"]*\)"/\1/')
    COMIC_DATE=$(echo "$RANDOM_OUTPUT" | grep -o '"comicDate":"[^"]*"' | head -1 | sed 's/"comicDate":"\([^"]*\)"/\1/')
    IMAGE_PATH=$(echo "$RANDOM_OUTPUT" | grep -o '"imagePath":"[^"]*"' | head -1 | sed 's/"imagePath":"\([^"]*\)"/\1/')
    TOGGLE_FAV=$(echo "$RANDOM_OUTPUT" | grep -o '"toggleFav":"[^"]*"' | head -1 | sed 's/"toggleFav":"\([^"]*\)"/\1/')
    IS_FAVORITE=$(echo "$RANDOM_OUTPUT" | grep -o '"isFavorite":[^,}]*' | head -1 | sed 's/"isFavorite":\([^,}]*\)/\1/')
fi

# Check if we successfully extracted the comic number
if [ -z "$COMIC_NUM" ]; then
    echo "Error: Could not extract comic number from random output"
    echo "Random output was: $RANDOM_OUTPUT"
    exit 1
fi

# Set environment variables for the text-view command
export comicTitle="$COMIC_TITLE"
export imageURL="$IMAGE_URL"
export comicN="$COMIC_NUM"
export comicAlt="$COMIC_ALT"
export comicDate="$COMIC_DATE"
export imagePath="$IMAGE_PATH"
# Convert boolean to the format expected by the Go code
if [ "$IS_FAVORITE" = "true" ]; then
    export isFavorite="1"
else
    export isFavorite=""
fi

# Run the text-view command with the comic number
"$XKCD_BINARY" text-view "$COMIC_NUM"
