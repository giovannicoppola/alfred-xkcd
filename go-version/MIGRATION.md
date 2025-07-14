# Migration Guide: Python to Go

This guide helps you migrate from the Python-based XKCD Alfred workflow to the Go-based version.

## Overview

The Go version consolidates all Python scripts into a single binary (`xkcd-alfred`) that accepts different commands via command-line arguments. This provides better performance, easier deployment, and simplified maintenance.

## Migration Steps

### 1. Build the Go Binary

```bash
cd go-version
make deps  # Install dependencies
make build # Build the binary
```

### 2. Update Alfred Workflow Scripts

Replace each Python script call in your Alfred workflow with the corresponding Go command:

#### Script Filter Objects

| Original Python Call | New Go Command |
|---------------------|----------------|
| `python xkcd-query.py "{query}"` | `./xkcd-alfred query {query}` |
| `python xkcd-random.py` | `./xkcd-alfred random` |
| `python favsGrid.py` | `./xkcd-alfred favorites` |

#### Run Script Objects

| Original Python Call | New Go Command |
|---------------------|----------------|
| `python toggleFav.py "{query}"` | `./xkcd-alfred toggle-fav {query}` |
| `python fetchImage.py "{query}"` | `./xkcd-alfred fetch-image {query} $imageURL` |
| `python createTextView.py "{query}"` | `./xkcd-alfred text-view {query}` |
| `python createTextView_exRecents.py "{query}"` | `./xkcd-alfred text-view-path {query}` |
| `python forceUpdate.py` | `./xkcd-alfred force-update` |

### 3. Update File Paths

1. Copy the `xkcd-alfred` binary to your Alfred workflow directory
2. Remove the old Python files (optional, keep as backup initially)
3. Update any hardcoded paths in Alfred workflow objects

### 4. Environment Variables

The Go version uses the same environment variables as the Python version:
- `alfred_workflow_cache`
- `alfred_workflow_data`  
- `REFRESH_RATE`
- `imageURL`, `comicTitle`, `comicN`, `comicAlt`, `comicDate`, `imagePath` (for text views)

No changes needed to environment variable configuration.

### 5. Database Compatibility

The Go version uses the exact same SQLite database schema and file as the Python version. Your existing database will work without any migration needed.

## Detailed Alfred Workflow Updates

### Script Filter: Main Query

**Before:**
```bash
python xkcd-query.py "{query}"
```

**After:**
```bash
./xkcd-alfred query {query}
```

### Script Filter: Random Comic

**Before:**
```bash
python xkcd-random.py
```

**After:**
```bash
./xkcd-alfred random
```

### Script Filter: Favorites Grid

**Before:**
```bash
python favsGrid.py
```

**After:**
```bash
./xkcd-alfred favorites
```

### Run Script: Toggle Favorite

**Before:**
```bash
python toggleFav.py "{query}"
```

**After:**
```bash
./xkcd-alfred toggle-fav {query}
```

### Run Script: Fetch Image

**Before:**
```bash
python fetchImage.py "{query}"
```

**After:**
```bash
./xkcd-alfred fetch-image {query} $imageURL
```

Note: The Go version requires the image URL as a separate argument.

### Run Script: Create Text View

**Before:**
```bash
python createTextView.py "{query}"
```

**After:**
```bash
./xkcd-alfred text-view {query}
```

### Run Script: Create Text View from Path

**Before:**
```bash
python createTextView_exRecents.py "{query}"
```

**After:**
```bash
./xkcd-alfred text-view-path {query}
```

### Run Script: Force Update

**Before:**
```bash
python forceUpdate.py
```

**After:**
```bash
./xkcd-alfred force-update
```

## Testing the Migration

1. Build and test the Go binary:
   ```bash
   make build
   ./test.sh
   ```

2. Test individual commands:
   ```bash
   ./xkcd-alfred query python
   ./xkcd-alfred random
   ./xkcd-alfred favorites
   ```

3. Update one Alfred workflow object at a time and test functionality

4. Keep the Python version as backup until fully tested

## Benefits of Migration

### Performance Improvements
- **Faster startup**: No Python interpreter overhead
- **Lower memory usage**: Compiled binary vs interpreted scripts
- **Better concurrency**: Go's goroutines for parallel operations

### Operational Benefits
- **Single binary**: Easier deployment and distribution
- **No dependencies**: No need for Python environment or pip packages
- **Better error handling**: Improved logging and error messages
- **Cross-platform**: Easy to build for different architectures

### Development Benefits
- **Type safety**: Compile-time error checking
- **Better tooling**: Go's built-in tools for formatting, testing, etc.
- **Easier maintenance**: Single codebase vs multiple scripts

## Rollback Plan

If you need to rollback to the Python version:

1. Keep the original Python files as backup
2. Revert the Alfred workflow script commands to use Python
3. Ensure the Python environment and dependencies are still available

## Common Issues and Solutions

### Issue: Binary not found
**Solution:** Ensure the `xkcd-alfred` binary is in the correct path and has execute permissions

### Issue: Database not found
**Solution:** Run `./xkcd-alfred force-update` to initialize/update the database

### Issue: Environment variables not working
**Solution:** Verify Alfred workflow environment variables are set correctly

### Issue: Image caching not working
**Solution:** Check that cache directories have write permissions

## Support

If you encounter issues during migration:

1. Check the logs in Alfred's workflow debugger
2. Run commands manually in terminal to isolate issues
3. Verify file permissions and paths
4. Ensure environment variables are properly set

The Go version maintains full compatibility with the Python version's functionality while providing significant performance and operational improvements.
