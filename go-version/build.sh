#!/bin/bash

# Check if required arguments are provided
if [ $# -lt 1 ]; then
    echo "Error: Output directory is required"
    echo "Usage: $0 <output_directory>"
    echo "Example: $0 ./bin"
    exit 1
fi

APP_NAME="xkcd-alfred"
OUTPUT_DIR="$1"

# Install dependencies first
echo "Installing dependencies..."
go mod tidy
go mod download

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Clean up any existing binaries
rm -f "${OUTPUT_DIR}/${APP_NAME}" "${OUTPUT_DIR}/${APP_NAME}_x86_64" "${OUTPUT_DIR}/${APP_NAME}_arm64"

echo "Compiling for x86_64..."
CGO_ENABLED=1 GOARCH=amd64 GOOS=darwin go build -o "${OUTPUT_DIR}/${APP_NAME}_x86_64" . || {
    echo "Error: Failed to compile for x86_64"
    exit 1
}

echo "Compiling for arm64..."
CGO_ENABLED=1 GOARCH=arm64 GOOS=darwin go build -o "${OUTPUT_DIR}/${APP_NAME}_arm64" . || {
    echo "Error: Failed to compile for arm64"
    exit 1
}

echo "Creating universal binary..."
lipo -create -output "${OUTPUT_DIR}/${APP_NAME}" "${OUTPUT_DIR}/${APP_NAME}_x86_64" "${OUTPUT_DIR}/${APP_NAME}_arm64" || {
    echo "Error: Failed to create universal binary"
    exit 1
}

# Clean up intermediate files
rm -f "${OUTPUT_DIR}/${APP_NAME}_x86_64" "${OUTPUT_DIR}/${APP_NAME}_arm64"

echo "Done! Universal binary created: ${OUTPUT_DIR}/${APP_NAME}"
lipo -info "${OUTPUT_DIR}/${APP_NAME}"
