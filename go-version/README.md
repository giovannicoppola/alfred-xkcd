# XKCD Alfred Workflow - Go Version

This is a Go implementation of the XKCD Alfred workflow, converted from the original Python scripts. The entire functionality has been consolidated into a single `main.go` file that accepts different commands via command line arguments.

## Features

- **Search Comics**: Search through XKCD comics by title, alt text, or comic number
- **Random Comic**: Get a random unread comic
- **Favorites Management**: Add/remove comics from favorites and view favorites grid
- **Image Caching**: Download and cache comic images locally
- **Text View Creation**: Create formatted text views of comics for Alfred
- **Database Updates**: Automatically check for new comics and update the SQLite database
- **Read Status**: Mark comics as read/unread

## Installation

1. Make sure you have Go installed (version 1.21 or later)
2. Navigate to the go-version directory:
   ```bash
   cd go-version
   ```
3. Install dependencies:
   ```bash
   go mod tidy
   ```
4. Build the executable:
   ```bash
   go build -o xkcd-alfred main.go
   ```

## Usage

The compiled binary accepts various commands:

### Available Commands

1. **Query/Search Comics**:
   ```bash
   ./xkcd-alfred query [search terms]
   ./xkcd-alfred query python
   ./xkcd-alfred query 353
   ./xkcd-alfred query          # List all comics
   ```

2. **Random Comic**:
   ```bash
   ./xkcd-alfred random
   ```

3. **Favorites Management**:
   ```bash
   ./xkcd-alfred favorites      # Show favorites grid
   ./xkcd-alfred toggle-fav 353 # Toggle favorite status for comic 353
   ```

4. **Image Operations**:
   ```bash
   ./xkcd-alfred fetch-image 353 https://imgs.xkcd.com/comics/python.png
   ```

5. **Text Views**:
   ```bash
   ./xkcd-alfred text-view 353
   ./xkcd-alfred text-view-path /path/to/image/353.png
   ```

6. **Database Update**:
   ```bash
   ./xkcd-alfred force-update
   ```

## Environment Variables

The application uses the same environment variables as the Python version:

- `alfred_workflow_cache`: Cache directory for images and temporary files
- `alfred_workflow_data`: Data directory for the SQLite database
- `REFRESH_RATE`: Number of days between automatic database updates (default: 7)

For text view creation, these environment variables are used:
- `comicTitle`: Comic title
- `imageURL`: Comic image URL
- `comicN`: Comic number
- `comicAlt`: Comic alt text
- `comicDate`: Comic date
- `imagePath`: Local image path

## Differences from Python Version

1. **Single Binary**: All functionality is consolidated into one executable
2. **Command-based**: Uses command line arguments instead of separate script files
3. **Better Performance**: Go's compiled nature provides faster execution
4. **Memory Efficiency**: More efficient memory usage compared to Python
5. **Dependency Management**: Uses Go modules instead of pip requirements

## Mapping from Python Scripts

| Python Script | Go Command |
|---------------|------------|
| `xkcd-query.py` | `./xkcd-alfred query [terms]` |
| `xkcd-random.py` | `./xkcd-alfred random` |
| `favsGrid.py` | `./xkcd-alfred favorites` |
| `toggleFav.py` | `./xkcd-alfred toggle-fav <num>` |
| `fetchImage.py` | `./xkcd-alfred fetch-image <num> <url>` |
| `createTextView.py` | `./xkcd-alfred text-view <num>` |
| `createTextView_exRecents.py` | `./xkcd-alfred text-view-path <path>` |
| `forceUpdate.py` | `./xkcd-alfred force-update` |

## Alfred Integration

To integrate with Alfred, you would replace the Python script calls in your Alfred workflow with calls to the Go binary:

Instead of:
```bash
python xkcd-query.py "{query}"
```

Use:
```bash
./xkcd-alfred query {query}
```

## Dependencies

- `github.com/mattn/go-sqlite3` - SQLite driver for Go

## Building for Distribution

To build a distributable binary:

```bash
# For macOS (Intel)
GOOS=darwin GOARCH=amd64 go build -o xkcd-alfred-intel main.go

# For macOS (Apple Silicon)
GOOS=darwin GOARCH=arm64 go build -o xkcd-alfred-arm64 main.go

# Universal binary (requires lipo tool)
lipo -create -output xkcd-alfred-universal xkcd-alfred-intel xkcd-alfred-arm64
```

## Performance

The Go version provides significant performance improvements:
- Faster startup times (no interpreter overhead)
- Lower memory usage
- Better concurrency handling
- Faster JSON processing

## Database Schema

The application expects the same SQLite database schema as the Python version:

```sql
CREATE TABLE xkcd (
    num INTEGER PRIMARY KEY,
    title TEXT,
    alt TEXT,
    img TEXT,
    year TEXT,
    month TEXT,
    day TEXT,
    is_favorite BOOLEAN DEFAULT 0,
    is_read BOOLEAN DEFAULT 0
);
```

## Error Handling

The Go version includes improved error handling and logging. Errors are written to stderr, while Alfred JSON output goes to stdout, ensuring clean separation of concerns.
