# Makefile for XKCD Alfred Workflow (Go Version)

BINARY_NAME=xkcd-alfred
MAIN_FILE=main.go

# Default target
.PHONY: all
all: build

# Build the binary
.PHONY: build
build:
	go build -o $(BINARY_NAME) $(MAIN_FILE)

# Install dependencies
.PHONY: deps
deps:
	go mod tidy
	go mod download

# Clean build artifacts
.PHONY: clean
clean:
	rm -f $(BINARY_NAME)
	rm -f $(BINARY_NAME)-*

# Build for different architectures
.PHONY: build-intel
build-intel:
	GOOS=darwin GOARCH=amd64 go build -o $(BINARY_NAME)-intel $(MAIN_FILE)

.PHONY: build-arm64
build-arm64:
	GOOS=darwin GOARCH=arm64 go build -o $(BINARY_NAME)-arm64 $(MAIN_FILE)

# Create universal binary (requires both intel and arm64 builds)
.PHONY: build-universal
build-universal: build-intel build-arm64
	lipo -create -output $(BINARY_NAME)-universal $(BINARY_NAME)-intel $(BINARY_NAME)-arm64

# Run tests (if any are added later)
.PHONY: test
test:
	go test -v ./...

# Format code
.PHONY: fmt
fmt:
	go fmt ./...

# Run linter
.PHONY: lint
lint:
	golangci-lint run

# Show help
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  build          - Build the binary for current architecture"
	@echo "  build-intel    - Build for Intel Macs (amd64)"
	@echo "  build-arm64    - Build for Apple Silicon Macs (arm64)"
	@echo "  build-universal- Create universal binary (Intel + ARM64)"
	@echo "  deps           - Install/update dependencies"
	@echo "  clean          - Remove build artifacts"
	@echo "  test           - Run tests"
	@echo "  fmt            - Format code"
	@echo "  lint           - Run linter"
	@echo "  help           - Show this help message"

# Installation target (copy to Alfred workflow directory)
.PHONY: install
install: build
	@echo "To install in Alfred workflow, copy $(BINARY_NAME) to your workflow directory"
	@echo "Example: cp $(BINARY_NAME) ~/Library/Application\\ Support/Alfred/Alfred.alfredpreferences/workflows/[your-workflow-id]/"
