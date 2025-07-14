#!/bin/bash

# Deployment script for XKCD Alfred Workflow (Go Version)
# This script helps deploy the Go binary and wrapper scripts to Alfred

set -e

ALFRED_WORKFLOW_DIR="$1"

if [ -z "$ALFRED_WORKFLOW_DIR" ]; then
    echo "Usage: $0 <alfred_workflow_directory>"
    echo ""
    echo "Example:"
    echo "  $0 ~/Library/Application\ Support/Alfred/Alfred.alfredpreferences/workflows/giovanni.xkcd"
    echo ""
    echo "Your workflow directory seems to be:"
    echo "  /Users/giovanni.coppola/Library/CloudStorage/OneDrive-RegeneronPharmaceuticals,Inc/SyncApps/Alfred/Alfred.alfredpreferences/workflows/giovanni.xkcd"
    exit 1
fi

if [ ! -d "$ALFRED_WORKFLOW_DIR" ]; then
    echo "Error: Alfred workflow directory does not exist: $ALFRED_WORKFLOW_DIR"
    exit 1
fi

echo "🚀 Deploying XKCD Alfred Workflow (Go Version)"
echo "=============================================="
echo "Target directory: $ALFRED_WORKFLOW_DIR"
echo ""

# Check if binary exists
if [ ! -f "./xkcd-alfred" ]; then
    echo "❌ Binary not found. Please run build.sh first:"
    echo "   ./build.sh ."
    exit 1
fi

# Copy binary
echo "📦 Copying binary..."
cp "./xkcd-alfred" "$ALFRED_WORKFLOW_DIR/"
chmod +x "$ALFRED_WORKFLOW_DIR/xkcd-alfred"

# Copy wrapper scripts
echo "📦 Copying wrapper scripts..."
cp ./*.sh "$ALFRED_WORKFLOW_DIR/"

# Make sure all scripts are executable
chmod +x "$ALFRED_WORKFLOW_DIR"/*.sh

# Copy icons if they exist
if [ -d "./icons" ]; then
    echo "📦 Copying icons..."
    cp -r "./icons" "$ALFRED_WORKFLOW_DIR/"
fi

echo ""
echo "✅ Deployment completed!"
echo ""
echo "📝 Next steps in Alfred:"
echo "1. Update your Script Filters to use the new wrapper scripts:"
echo ""
echo "   Old Python scripts → New Go wrapper scripts:"
echo "   python xkcd-query.py \"{query}\" → ./xkcd-query.sh \"{query}\""
echo "   python xkcd-random.py → ./xkcd-random.sh"
echo "   python favsGrid.py → ./favorites.sh"
echo "   python toggleFav.py {query} → ./toggle-fav.sh {query}"
echo "   python fetchImage.py {query} → ./fetch-image.sh {query}"
echo "   python createTextView.py {query} → ./text-view.sh {query}"
echo "   python createTextView_exRecents.py {query} → ./text-view-path.sh {query}"
echo "   python forceUpdate.py → ./force-update.sh"
echo ""
echo "2. Remove the old Python files if desired"
echo "3. Test the workflow in Alfred"
echo ""
echo "🎉 Your Go-based XKCD workflow is ready!"
