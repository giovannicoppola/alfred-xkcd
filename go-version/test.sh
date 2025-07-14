#!/bin/bash

# Test script for XKCD Alfred Workflow (Go Version)
# This script tests the basic functionality of the Go implementation

set -e

BINARY="./xkcd-alfred"
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "🧪 Testing XKCD Alfred Workflow (Go Version)"
echo "============================================"

# Check if binary exists
if [ ! -f "$BINARY" ]; then
    echo -e "${RED}❌ Binary not found. Please run 'make build' first.${NC}"
    exit 1
fi

# Test 1: Help command
echo "📋 Test 1: Help command"
if $BINARY 2>&1 | grep -q "Usage:"; then
    echo -e "${GREEN}✅ Help command works${NC}"
else
    echo -e "${RED}❌ Help command failed${NC}"
    exit 1
fi

# Test 2: Query without arguments (should list all comics)
echo "📋 Test 2: Query without arguments"
if $BINARY query 2>/dev/null | jq -e '.items' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Query command works${NC}"
else
    echo -e "${RED}❌ Query command failed or JSON is invalid${NC}"
    # Still continue as database might not be initialized
fi

# Test 3: Query with search term
echo "📋 Test 3: Query with search term"
if $BINARY query python 2>/dev/null | jq -e '.items' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Query with search term works${NC}"
else
    echo -e "${RED}❌ Query with search term failed${NC}"
fi

# Test 4: Random comic
echo "📋 Test 4: Random comic"
if $BINARY random 2>/dev/null | jq -e '.items' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Random comic command works${NC}"
else
    echo -e "${RED}❌ Random comic command failed${NC}"
fi

# Test 5: Favorites
echo "📋 Test 5: Favorites"
if $BINARY favorites 2>/dev/null | jq -e '.items' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Favorites command works${NC}"
else
    echo -e "${RED}❌ Favorites command failed${NC}"
fi

# Test 6: Force update
echo "📋 Test 6: Force update"
if $BINARY force-update 2>/dev/null | jq -e '.items[0].title' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Force update command works${NC}"
else
    echo -e "${RED}❌ Force update command failed${NC}"
fi

# Test 7: Invalid command
echo "📋 Test 7: Invalid command"
if $BINARY invalid-command 2>&1 | grep -q "Unknown command"; then
    echo -e "${GREEN}✅ Error handling works${NC}"
else
    echo -e "${RED}❌ Error handling failed${NC}"
fi

echo ""
echo "🎉 All basic tests completed!"
echo ""
echo "📝 Note: Some tests may show failures if the database is not initialized."
echo "   Run '$BINARY force-update' to initialize the database."
echo ""
echo "🚀 To use with Alfred, replace Python script calls with:"
echo "   python xkcd-query.py \"{query}\" → $BINARY query {query}"
echo "   python xkcd-random.py → $BINARY random"
echo "   python favsGrid.py → $BINARY favorites"
echo "   etc."
