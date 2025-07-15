package main

import (
	"archive/zip"
	"database/sql"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"math/rand"
	"net/http"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strconv"
	"strings"
	"time"

	_ "github.com/mattn/go-sqlite3"
)

// Configuration constants and global variables
var (
	CACHE_FOLDER         string
	CACHE_FOLDER_RECENTS string
	CACHE_FOLDER_FAVS    string
	COMICSMAX_FILE       string
	DATA_FOLDER          string
	MY_DATABASE          string
	REFRESH_RATE         int
	COMICSMAX            int
	REFRESH_FLAG         bool
)

// Comic represents an XKCD comic
type Comic struct {
	Num        int    `json:"num"`
	Title      string `json:"title"`
	Alt        string `json:"alt"`
	Img        string `json:"img"`
	Year       string `json:"year"`
	Month      string `json:"month"`
	Day        string `json:"day"`
	IsFavorite bool   `db:"is_favorite"`
	IsRead     bool   `db:"is_read"`
}

// AlfredItem represents an item in Alfred's JSON output
type AlfredItem struct {
	Title        string                 `json:"title"`
	Subtitle     string                 `json:"subtitle"`
	Valid        bool                   `json:"valid"`
	Arg          string                 `json:"arg"`
	Icon         map[string]string      `json:"icon,omitempty"`
	QuickLookURL string                 `json:"quicklookurl,omitempty"`
	Variables    map[string]interface{} `json:"variables,omitempty"`
	Mods         map[string]interface{} `json:"mods,omitempty"`
	Match        string                 `json:"match,omitempty"`
}

// AlfredOutput represents Alfred's JSON response format
type AlfredOutput struct {
	Items []AlfredItem `json:"items"`
}

// TextViewOutput represents the text view JSON response
type TextViewOutput struct {
	Variables map[string]string      `json:"variables"`
	Response  string                 `json:"response"`
	Footer    string                 `json:"footer"`
	Behaviour map[string]interface{} `json:"behaviour"`
	Arg       string                 `json:"arg"`
}

func init() {
	// Initialize configuration
	CACHE_FOLDER = os.Getenv("alfred_workflow_cache")
	if CACHE_FOLDER == "" {
		CACHE_FOLDER = "/tmp/alfred-xkcd-cache"
	}

	CACHE_FOLDER_RECENTS = filepath.Join(CACHE_FOLDER, "images", "recents")
	CACHE_FOLDER_FAVS = filepath.Join(CACHE_FOLDER, "images", "favs")
	COMICSMAX_FILE = filepath.Join(CACHE_FOLDER, "comicsMax.txt")

	DATA_FOLDER = os.Getenv("alfred_workflow_data")
	if DATA_FOLDER == "" {
		DATA_FOLDER = "/tmp/alfred-xkcd-data"
	}

	MY_DATABASE = filepath.Join(DATA_FOLDER, "xkcd.sqlite")

	refreshRateStr := os.Getenv("REFRESH_RATE")
	if refreshRateStr == "" {
		REFRESH_RATE = 7 // Default to 7 days
	} else {
		var err error
		REFRESH_RATE, err = strconv.Atoi(refreshRateStr)
		if err != nil {
			REFRESH_RATE = 7
		}
	}

	// Create directories
	os.MkdirAll(DATA_FOLDER, 0755)
	os.MkdirAll(CACHE_FOLDER, 0755)
	os.MkdirAll(CACHE_FOLDER_RECENTS, 0755)
	os.MkdirAll(CACHE_FOLDER_FAVS, 0755)

	// Check database
	checkDatabase()

	// Check refresh flag
	checkRefreshFlag()
}

func logMessage(msg string) {
	fmt.Fprintf(os.Stderr, "%s\n", msg)
}

// formatNumberWithCommas formats an integer with thousand separators
func formatNumberWithCommas(n int) string {
	if n < 1000 {
		return fmt.Sprintf("%d", n)
	}

	// Convert to string and add commas every 3 digits from the right
	str := fmt.Sprintf("%d", n)
	length := len(str)
	result := ""

	for i, digit := range str {
		if i > 0 && (length-i)%3 == 0 {
			result += ","
		}
		result += string(digit)
	}

	return result
}

func checkDatabase() {
	dbZipped := "xkcd.sqlite.zip"

	// Check if the zip file exists
	if _, err := os.Stat(dbZipped); err != nil {
		return // No zip file to extract
	}

	// Check if database already exists in data folder
	if _, err := os.Stat(MY_DATABASE); err == nil {
		logMessage("Database already exists in data folder, skipping extraction of xkcd.sqlite.zip")
		return
	}

	// Database doesn't exist, extract the zip file
	logMessage("Found distribution database, extracting")
	err := extractZip(dbZipped, DATA_FOLDER)
	if err != nil {
		logMessage(fmt.Sprintf("Error extracting database: %v", err))
		// Still try to remove the zip file even if extraction failed
		os.Remove(dbZipped)
		return
	}

	// Remove the zip file after successful extraction
	err = os.Remove(dbZipped)
	if err != nil {
		logMessage(fmt.Sprintf("Warning: could not remove zip file: %v", err))
	} else {
		logMessage("Successfully removed xkcd.sqlite.zip after extraction")
	}
}

func extractZip(src, dest string) error {
	r, err := zip.OpenReader(src)
	if err != nil {
		return err
	}
	defer r.Close()

	for _, f := range r.File {
		rc, err := f.Open()
		if err != nil {
			return err
		}
		defer rc.Close()

		path := filepath.Join(dest, f.Name)
		if f.FileInfo().IsDir() {
			os.MkdirAll(path, f.FileInfo().Mode())
			continue
		}

		os.MkdirAll(filepath.Dir(path), 0755)
		outFile, err := os.OpenFile(path, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, f.FileInfo().Mode())
		if err != nil {
			return err
		}

		_, err = io.Copy(outFile, rc)
		outFile.Close()
		if err != nil {
			return err
		}
	}
	return nil
}

func checkRefreshFlag() {
	if _, err := os.Stat(COMICSMAX_FILE); os.IsNotExist(err) {
		COMICSMAX = 3116
		REFRESH_FLAG = true
		return
	}

	data, err := os.ReadFile(COMICSMAX_FILE)
	if err != nil {
		COMICSMAX = 3116
		REFRESH_FLAG = true
		return
	}

	lines := strings.Split(string(data), "\n")
	if len(lines) < 2 {
		COMICSMAX = 3116
		REFRESH_FLAG = true
		return
	}

	COMICSMAX, err = strconv.Atoi(strings.TrimSpace(lines[0]))
	if err != nil {
		COMICSMAX = 3116
		REFRESH_FLAG = true
		return
	}

	fileDate, err := time.Parse("2006-01-02", strings.TrimSpace(lines[1]))
	if err != nil {
		REFRESH_FLAG = true
		return
	}

	daysDiff := int(time.Since(fileDate).Hours() / 24)
	REFRESH_FLAG = daysDiff >= REFRESH_RATE
}

func fetchComicsPath(num int, imgURL, mode string) string {
	var comicsPath string
	if mode == "favs" {
		comicsPath = filepath.Join(CACHE_FOLDER_FAVS, fmt.Sprintf("%d.png", num))
	} else {
		comicsPath = filepath.Join(CACHE_FOLDER_RECENTS, fmt.Sprintf("%d.png", num))
	}

	if _, err := os.Stat(comicsPath); os.IsNotExist(err) {
		logMessage(fmt.Sprintf("Retrieving image: %s", comicsPath))
		downloadImage(imgURL, comicsPath)
	}

	return comicsPath
}

func downloadImage(url, filepath string) error {
	resp, err := http.Get(url)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	out, err := os.Create(filepath)
	if err != nil {
		return err
	}
	defer out.Close()

	_, err = io.Copy(out, resp.Body)
	return err
}

func openDB() (*sql.DB, error) {
	db, err := sql.Open("sqlite3", MY_DATABASE)
	if err != nil {
		return nil, err
	}

	// Create the table if it doesn't exist
	createTableSQL := `
	CREATE TABLE IF NOT EXISTS xkcd (
		num INTEGER PRIMARY KEY,
		title TEXT,
		alt TEXT,
		img TEXT,
		year TEXT,
		month TEXT,
		day TEXT,
		safe_title TEXT,
		transcript TEXT,
		link TEXT,
		news TEXT,
		is_favorite BOOLEAN DEFAULT 0,
		is_read BOOLEAN DEFAULT 0
	);`

	_, err = db.Exec(createTableSQL)
	if err != nil {
		db.Close()
		return nil, fmt.Errorf("error creating table: %v", err)
	}

	return db, nil
}

func toggleFavorite(num int) (string, error) {
	db, err := openDB()
	if err != nil {
		return "", err
	}
	defer db.Close()

	var isFav sql.NullBool
	var img string
	err = db.QueryRow("SELECT is_favorite, img FROM xkcd WHERE num = ?", num).Scan(&isFav, &img)
	if err != nil {
		return "", err
	}

	// Handle NULL values - treat NULL as false
	isFavorite := isFav.Valid && isFav.Bool

	var exitMessage string
	if isFavorite {
		// Remove from favorites
		favPath := filepath.Join(CACHE_FOLDER_FAVS, fmt.Sprintf("%d.png", num))
		os.Remove(favPath)
		exitMessage = "Removed from favorites 💔"
	} else {
		// Add to favorites and mark as read
		fetchComicsPath(num, img, "favs")
		markAsRead(num) // Mark as read when adding to favorites
		exitMessage = "Added to favorites ❤️"
	}

	_, err = db.Exec("UPDATE xkcd SET is_favorite = ? WHERE num = ?", !isFavorite, num)
	if err != nil {
		return "", err
	}

	return exitMessage, nil
}

func markAsRead(num int) error {
	db, err := openDB()
	if err != nil {
		return err
	}
	defer db.Close()

	_, err = db.Exec("UPDATE xkcd SET is_read = ? WHERE num = ?", true, num)
	return err
}

func toggleRead(num int) error {
	db, err := openDB()
	if err != nil {
		return err
	}
	defer db.Close()

	var isReadNull sql.NullBool
	err = db.QueryRow("SELECT is_read FROM xkcd WHERE num = ?", num).Scan(&isReadNull)
	if err != nil {
		return err
	}

	// Handle NULL values - treat NULL as false (unread)
	isRead := isReadNull.Valid && isReadNull.Bool

	_, err = db.Exec("UPDATE xkcd SET is_read = ? WHERE num = ?", !isRead, num)
	return err
}

func checkUpdate(startNum int) error {
	var newComics []Comic
	currentNum := startNum

	for {
		url := fmt.Sprintf("https://xkcd.com/%d/info.0.json", currentNum)
		resp, err := http.Get(url)
		if err != nil {
			break
		}

		if resp.StatusCode != 200 {
			resp.Body.Close()
			break
		}

		var comic Comic
		if err := json.NewDecoder(resp.Body).Decode(&comic); err != nil {
			resp.Body.Close()
			break
		}
		resp.Body.Close()

		newComics = append(newComics, comic)
		logMessage(fmt.Sprintf("Downloaded %d.json", currentNum))
		currentNum++
	}

	if len(newComics) > 0 {
		updateDatabase(newComics)
	}

	// Update COMICSMAX file
	currentDate := time.Now().Format("2006-01-02")
	content := fmt.Sprintf("%d\n%s\n", currentNum, currentDate)
	return os.WriteFile(COMICSMAX_FILE, []byte(content), 0644)
}

func updateDatabase(newComics []Comic) error {
	db, err := openDB()
	if err != nil {
		return err
	}
	defer db.Close()

	for _, comic := range newComics {
		_, err := db.Exec(
			"INSERT INTO xkcd (num, title, alt, img, year, month, day, safe_title, transcript, link, news, is_favorite, is_read) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
			comic.Num, comic.Title, comic.Alt, comic.Img, comic.Year, comic.Month, comic.Day,
			comic.Title, "", "", "", 0, 0,
		)
		if err != nil {
			logMessage(fmt.Sprintf("Error inserting comic %d: %v", comic.Num, err))
		}
	}
	return nil
}

func queryComics(input string) error {
	start := time.Now()

	if REFRESH_FLAG {
		logMessage("Checking for updates")
		checkUpdate(COMICSMAX)
	}

	db, err := openDB()
	if err != nil {
		return err
	}
	defer db.Close()

	var rows *sql.Rows
	searchTerms := strings.Fields(input)

	if len(searchTerms) == 0 {
		rows, err = db.Query("SELECT num, title, alt, img, year, month, day, is_favorite, is_read FROM xkcd ORDER BY num DESC")
	} else {
		var conditions []string
		var params []interface{}

		for _, term := range searchTerms {
			if _, err := strconv.Atoi(term); err == nil {
				conditions = append(conditions, "(alt LIKE ? OR title LIKE ? OR num = ?)")
				params = append(params, "%"+term+"%", "%"+term+"%", term)
			} else {
				conditions = append(conditions, "(alt LIKE ? OR title LIKE ?)")
				params = append(params, "%"+term+"%", "%"+term+"%")
			}
		}

		query := "SELECT num, title, alt, img, year, month, day, is_favorite, is_read FROM xkcd WHERE " +
			strings.Join(conditions, " AND ") + " ORDER BY num DESC"
		rows, err = db.Query(query, params...)
	}

	if err != nil {
		return err
	}
	defer rows.Close()

	var comics []Comic
	for rows.Next() {
		var comic Comic
		var isFav, isRead sql.NullBool
		err := rows.Scan(&comic.Num, &comic.Title, &comic.Alt, &comic.Img,
			&comic.Year, &comic.Month, &comic.Day, &isFav, &isRead)
		if err != nil {
			continue
		}
		comic.IsFavorite = isFav.Bool
		comic.IsRead = isRead.Bool
		comics = append(comics, comic)
	}

	output := AlfredOutput{Items: []AlfredItem{}}

	for i, comic := range comics {
		date := fmt.Sprintf("%s-%s-%s", comic.Year, comic.Month, comic.Day)

		var fav, read string
		var toggleFavText string

		if comic.IsFavorite {
			fav = "❤️"
			toggleFavText = "💔 Remove from favorites"
		} else {
			fav = ""
			toggleFavText = "❤️ Add to favorites"
		}

		if comic.IsRead {
			read = ""
		} else {
			read = "•"
		}

		imagePath := filepath.Join(CACHE_FOLDER_RECENTS, fmt.Sprintf("%d.png", comic.Num))

		item := AlfredItem{
			Title:        fmt.Sprintf("%s (#%d %s) %s%s", comic.Title, comic.Num, date, fav, read),
			Subtitle:     fmt.Sprintf("%s/%s %s", formatNumberWithCommas(i+1), formatNumberWithCommas(len(comics)), comic.Alt),
			Valid:        true,
			Arg:          strconv.Itoa(comic.Num),
			QuickLookURL: comic.Img,
			Variables: map[string]interface{}{
				"imageURL":   comic.Img,
				"comicTitle": comic.Title,
				"comicN":     comic.Num,
				"comicAlt":   comic.Alt,
				"comicDate":  date,
				"imagePath":  imagePath,
				"toggleFav":  toggleFavText,
				"isFavorite": comic.IsFavorite,
			},
			Mods: map[string]interface{}{
				"ctrl": map[string]interface{}{
					"valid":    true,
					"arg":      comic.Num,
					"subtitle": toggleFavText,
					"variables": map[string]interface{}{
						"currQuery": input,
						"imageURL":  comic.Img,
						"comicDate": date,
						"comicN":    comic.Num,
					},
				},
				"shift": map[string]interface{}{
					"valid":    true,
					"arg":      comic.Num,
					"subtitle": "copy to clipboard 📋️",
				},
				"cmd": map[string]interface{}{
					"valid":    true,
					"arg":      fmt.Sprintf("https://xkcd.com/%d", comic.Num),
					"subtitle": "open on xkcd.com 🌐",
				},
				"alt": map[string]interface{}{
					"valid":    true,
					"arg":      fmt.Sprintf("https://www.explainxkcd.com/wiki/index.php/%d", comic.Num),
					"subtitle": "open on explainxkcd.com 🌐",
				},
			},
		}
		output.Items = append(output.Items, item)
	}

	if input != "" && len(comics) == 0 {
		output.Items = append(output.Items, AlfredItem{
			Title:    "No comics found 🫥",
			Subtitle: "Try a different query!",
			Arg:      "",
			Icon:     map[string]string{"path": "icons/Warning.png"},
		})
	}

	jsonOutput, _ := json.Marshal(output)
	fmt.Print(string(jsonOutput))

	elapsed := time.Since(start)
	logMessage(fmt.Sprintf("\nScript duration (main query): %.3f seconds", elapsed.Seconds()))

	return nil
}

func randomComic() error {
	start := time.Now()

	if REFRESH_FLAG {
		logMessage("Checking for updates")
		checkUpdate(COMICSMAX)
	}

	db, err := openDB()
	if err != nil {
		return err
	}
	defer db.Close()

	// Get all unread comics
	rows, err := db.Query("SELECT num FROM xkcd WHERE is_read != 1 OR is_read IS NULL")
	if err != nil {
		return err
	}
	defer rows.Close()

	var unreadNums []int
	for rows.Next() {
		var num int
		rows.Scan(&num)
		unreadNums = append(unreadNums, num)
	}

	if len(unreadNums) == 0 {
		fmt.Print(`{"items":[{"title":"All comics read!","subtitle":"Great job!","arg":""}]}`)
		return nil
	}

	// Pick random comic
	randomNum := unreadNums[rand.Intn(len(unreadNums))]

	// Fetch the comic details
	var comic Comic
	var isFav, isRead sql.NullBool
	err = db.QueryRow("SELECT num, title, alt, img, year, month, day, is_favorite, is_read FROM xkcd WHERE num = ?", randomNum).
		Scan(&comic.Num, &comic.Title, &comic.Alt, &comic.Img, &comic.Year, &comic.Month, &comic.Day, &isFav, &isRead)
	if err != nil {
		return err
	}

	comic.IsFavorite = isFav.Bool
	comic.IsRead = isRead.Bool

	date := fmt.Sprintf("%s-%s-%s", comic.Year, comic.Month, comic.Day)

	var fav, read string
	var toggleFavText string

	if comic.IsFavorite {
		fav = "❤️"
		toggleFavText = "💔 Remove from favorites"
	} else {
		fav = ""
		toggleFavText = "❤️ Add to favorites"
	}

	if comic.IsRead {
		read = ""
	} else {
		read = "•"
	}

	imagePath := filepath.Join(CACHE_FOLDER_RECENTS, fmt.Sprintf("%d.png", comic.Num))

	output := AlfredOutput{
		Items: []AlfredItem{
			{
				Title:        fmt.Sprintf("%s (#%d %s) %s%s [unread: %s]", comic.Title, comic.Num, date, fav, read, formatNumberWithCommas(len(unreadNums))),
				Subtitle:     comic.Alt,
				Valid:        true,
				Arg:          strconv.Itoa(comic.Num),
				QuickLookURL: comic.Img,
				Variables: map[string]interface{}{
					"imageURL":   comic.Img,
					"comicTitle": comic.Title,
					"comicN":     comic.Num,
					"comicAlt":   comic.Alt,
					"comicDate":  date,
					"imagePath":  imagePath,
					"toggleFav":  toggleFavText,
					"isFavorite": comic.IsFavorite,
				},
				Mods: map[string]interface{}{
					"ctrl": map[string]interface{}{
						"valid":    true,
						"arg":      comic.Num,
						"subtitle": toggleFavText,
						"variables": map[string]interface{}{
							"imageURL":  comic.Img,
							"comicDate": date,
						},
					},
					"shift": map[string]interface{}{
						"valid":    true,
						"arg":      comic.Num,
						"subtitle": "copy to clipboard 📋️",
					},
					"cmd": map[string]interface{}{
						"valid":    true,
						"arg":      fmt.Sprintf("https://xkcd.com/%d", comic.Num),
						"subtitle": "open on xkcd.com 🌐",
					},
					"alt": map[string]interface{}{
						"valid":    true,
						"arg":      fmt.Sprintf("https://www.explainxkcd.com/wiki/index.php/%d", comic.Num),
						"subtitle": "open on explainxkcd.com 🌐",
					},
				},
			},
		},
	}

	jsonOutput, _ := json.Marshal(output)
	fmt.Print(string(jsonOutput))

	elapsed := time.Since(start)
	logMessage(fmt.Sprintf("\nScript duration (random): %.3f seconds", elapsed.Seconds()))

	return nil
}

func favoriteGrid() error {
	start := time.Now()

	if REFRESH_FLAG {
		logMessage("Checking for updates")
		checkUpdate(COMICSMAX)
	}

	db, err := openDB()
	if err != nil {
		return err
	}
	defer db.Close()

	rows, err := db.Query("SELECT num, title, alt, img, year, month, day FROM xkcd WHERE is_favorite = 1")
	if err != nil {
		return err
	}
	defer rows.Close()

	output := AlfredOutput{Items: []AlfredItem{}}

	for rows.Next() {
		var comic Comic
		rows.Scan(&comic.Num, &comic.Title, &comic.Alt, &comic.Img, &comic.Year, &comic.Month, &comic.Day)

		// Since this is favoriteGrid, we know all items are favorites
		comic.IsFavorite = true

		comicsPath := fetchComicsPath(comic.Num, comic.Img, "favs")
		date := fmt.Sprintf("%s-%s-%s", comic.Year, comic.Month, comic.Day)

		// Since all items in favorites grid are favorites, we can hardcode the toggle text
		toggleFavText := "💔 Remove from favorites"

		item := AlfredItem{
			Title:        comic.Title,
			Valid:        true,
			Subtitle:     comic.Alt,
			Arg:          strconv.Itoa(comic.Num),
			Icon:         map[string]string{"path": comicsPath},
			QuickLookURL: comic.Img,
			Match:        fmt.Sprintf("%s %s", comic.Title, comic.Alt),
			Variables: map[string]interface{}{
				"imageURL":   comic.Img,
				"comicTitle": comic.Title,
				"comicN":     comic.Num,
				"comicAlt":   comic.Alt,
				"comicDate":  date,
				"imagePath":  comicsPath,
				"toggleFav":  toggleFavText,
			},
			Mods: map[string]interface{}{
				"ctrl": map[string]interface{}{
					"subtitle": "💔 remove from favorites",
					"arg":      comic.Num,
				},
				"shift": map[string]interface{}{
					"subtitle": "copy to clipboard 📋️",
					"arg":      comicsPath,
				},
				"cmd": map[string]interface{}{
					"arg":      fmt.Sprintf("https://xkcd.com/%d", comic.Num),
					"subtitle": "open on xkcd.com 🌐",
				},
				"alt": map[string]interface{}{
					"valid":    true,
					"arg":      fmt.Sprintf("https://www.explainxkcd.com/wiki/index.php/%d", comic.Num),
					"subtitle": "open on explainxkcd.com 🌐",
				},
			},
		}
		output.Items = append(output.Items, item)
	}

	if len(output.Items) == 0 {
		output.Items = append(output.Items, AlfredItem{
			Title:    "No favorites here 🫤",
			Subtitle: "Add some!",
			Arg:      "",
			Icon:     map[string]string{"path": "icons/broken-heart.png"},
		})
	}

	jsonOutput, _ := json.Marshal(output)
	fmt.Print(string(jsonOutput))

	elapsed := time.Since(start)
	logMessage(fmt.Sprintf("\nScript duration (favsGrid): %.3f seconds", elapsed.Seconds()))

	return nil
}

func recentGrid() error {
	start := time.Now()

	if REFRESH_FLAG {
		logMessage("Checking for updates")
		checkUpdate(COMICSMAX)
	}

	logMessage(fmt.Sprintf("Reading from recents path: %s", CACHE_FOLDER_RECENTS))

	files, err := os.ReadDir(CACHE_FOLDER_RECENTS)
	if err != nil {
		logMessage(fmt.Sprintf("Error reading directory: %v", err))
		return fmt.Errorf("failed to read recents directory: %v", err)
	}

	logMessage(fmt.Sprintf("Found %d files in recents directory", len(files)))

	// Sort files by modification time (most recent first)
	sort.Slice(files, func(i, j int) bool {
		infoI, errI := files[i].Info()
		infoJ, errJ := files[j].Info()
		if errI != nil || errJ != nil {
			return false // Keep original order if we can't get file info
		}
		return infoI.ModTime().After(infoJ.ModTime())
	})

	// Open database to get comic details
	db, err := openDB()
	if err != nil {
		return err
	}
	defer db.Close()

	output := AlfredOutput{Items: []AlfredItem{}}

	// Process each image file in the recents folder
	for i, file := range files {
		if file.IsDir() || !strings.HasSuffix(file.Name(), ".png") {
			logMessage(fmt.Sprintf("Skipping file: %s (is dir: %v)", file.Name(), file.IsDir()))
			continue
		}

		// Extract comic number from filename (e.g., "123.png" -> 123)
		filename := file.Name()
		comicNumStr := strings.TrimSuffix(filename, ".png")
		comicNum, err := strconv.Atoi(comicNumStr)
		if err != nil {
			logMessage(fmt.Sprintf("Skipping file with non-numeric name: %s", filename))
			continue // Skip files that don't have numeric names
		}

		// logMessage(fmt.Sprintf("Processing comic number: %d", comicNum))

		// Get comic details from database
		var comic Comic
		var isFav sql.NullBool
		err = db.QueryRow("SELECT num, title, alt, img, year, month, day, is_favorite FROM xkcd WHERE num = ?", comicNum).Scan(
			&comic.Num, &comic.Title, &comic.Alt, &comic.Img, &comic.Year, &comic.Month, &comic.Day, &isFav)
		if err != nil {
			// If comic not found in database, create a basic entry with the comic number
			logMessage(fmt.Sprintf("Comic %d not found in database, creating basic entry", comicNum))
			comic = Comic{
				Num:   comicNum,
				Title: fmt.Sprintf("XKCD #%d", comicNum),
				Alt:   "Comic not yet in database",
				Img:   fmt.Sprintf("https://imgs.xkcd.com/comics/%d.png", comicNum),
				Year:  "Unknown",
				Month: "Unknown",
				Day:   "Unknown",
			}
			comic.IsFavorite = false // Default to not favorite for missing comics
		} else {
			comic.IsFavorite = isFav.Valid && isFav.Bool
		}

		comicsPath := filepath.Join(CACHE_FOLDER_RECENTS, filename)
		date := fmt.Sprintf("%s-%s-%s", comic.Year, comic.Month, comic.Day)

		// Set toggle favorite text based on current status
		var toggleFavText string
		var titleWithFavorite string
		if comic.IsFavorite {
			toggleFavText = "💔 Remove from favorites"
			titleWithFavorite = comic.Title + " ❤️"
		} else {
			toggleFavText = "❤️ Add to favorites"
			titleWithFavorite = comic.Title
		}

		item := AlfredItem{
			Title:        titleWithFavorite,
			Subtitle:     comic.Alt,
			Valid:        true,
			Arg:          strconv.Itoa(comic.Num),
			Icon:         map[string]string{"path": comicsPath},
			QuickLookURL: comic.Img,
			Match:        fmt.Sprintf("%s %s", comic.Title, comic.Alt),
			Variables: map[string]interface{}{
				"imageURL":   comic.Img,
				"comicTitle": comic.Title,
				"comicN":     comic.Num,
				"comicAlt":   comic.Alt,
				"comicDate":  date,
				"imagePath":  comicsPath,
				"position":   i + 1, // Add position for reference
				"toggleFav":  toggleFavText,
				"crumble":    "recentGrid",
			},
			Mods: map[string]interface{}{
				"ctrl": map[string]interface{}{
					"subtitle": toggleFavText,
					"arg":      comic.Num,
				},
				"shift": map[string]interface{}{
					"subtitle": "copy to clipboard 📋️",
					"arg":      comicsPath,
				},
				"cmd": map[string]interface{}{
					"arg":      fmt.Sprintf("https://xkcd.com/%d", comic.Num),
					"subtitle": "open on xkcd.com 🌐",
				},
				"alt": map[string]interface{}{
					"valid":    true,
					"arg":      fmt.Sprintf("https://www.explainxkcd.com/wiki/index.php/%d", comic.Num),
					"subtitle": "open on explainxkcd.com 🌐",
				},
			},
		}
		output.Items = append(output.Items, item)
	}

	logMessage(fmt.Sprintf("Created %d items for output", len(output.Items)))

	if len(output.Items) == 0 {
		output.Items = append(output.Items, AlfredItem{
			Title:    "No recent comics here 🫤",
			Subtitle: "View some comics first!",
			Arg:      "",
			Icon:     map[string]string{"path": "icons/broken-heart.png"},
		})
	}

	jsonOutput, _ := json.Marshal(output)
	fmt.Print(string(jsonOutput))

	logMessage(fmt.Sprintf("Recent grid completed in: %s", time.Since(start)))
	return nil
}

func fetchImage(arg string) error {
	start := time.Now()

	var num int
	var imageURL string
	var err error

	// Check if argument is a URL or a number
	if strings.HasPrefix(arg, "http") {
		// Argument is a URL, extract comic number from it
		imageURL = arg
		// Extract number from URL like: https://imgs.xkcd.com/comics/global_ranking.png
		// We need to get the comic number from environment or database
		comicN := os.Getenv("comicN")
		if comicN == "" {
			return fmt.Errorf("when passing URL as argument, comicN environment variable must be set")
		}
		num, err = strconv.Atoi(comicN)
		if err != nil {
			return fmt.Errorf("invalid comicN environment variable: %v", err)
		}
	} else {
		// Argument is a comic number
		num, err = strconv.Atoi(arg)
		if err != nil {
			return fmt.Errorf("invalid comic number: %v", err)
		}
		// Get image URL from environment variable
		imageURL = os.Getenv("imageURL")
		if imageURL == "" {
			return fmt.Errorf("imageURL environment variable not set")
		}
	}

	comicsPath := fetchComicsPath(num, imageURL, "recent")
	fmt.Print(comicsPath)

	elapsed := time.Since(start)
	logMessage(fmt.Sprintf("\nScript duration (fetchImage): %.3f seconds", elapsed.Seconds()))

	return nil
}

func createTextView(numStr string) error {
	start := time.Now()

	// Get environment variables first
	comicTitle := os.Getenv("comicTitle")
	imageURL := os.Getenv("imageURL")
	comicN := os.Getenv("comicN")
	comicAlt := os.Getenv("comicAlt")
	comicDate := os.Getenv("comicDate")
	imagePath := os.Getenv("imagePath")
	isFavoriteStr := os.Getenv("isFavorite")

	// Use comicN from environment variable if available, otherwise try to parse argument
	var num int
	var err error

	if comicN != "" {
		num, err = strconv.Atoi(comicN)
		if err != nil {
			return fmt.Errorf("invalid comic number in comicN environment variable: %s", comicN)
		}
		logMessage(fmt.Sprintf("Using comic number from environment: %d", num))
	} else {
		num, err = strconv.Atoi(numStr)
		if err != nil {
			return fmt.Errorf("could not parse comic number from input '%s'", numStr)
		}
		logMessage(fmt.Sprintf("Using comic number from argument: %d", num))
	}

	// Fetch image and mark as read
	fetchComicsPath(num, imageURL, "recent")
	markAsRead(num)

	// Check if comic is a favorite from environment variable or database fallback
	var isFavorite bool
	if isFavoriteStr != "" {
		// Use environment variable if available (from main query)
		isFavorite = isFavoriteStr == "true"
	} else {
		// Fallback to database query if environment variable not available
		db, err := openDB()
		if err != nil {
			return err
		}
		defer db.Close()

		var isFav sql.NullBool
		err = db.QueryRow("SELECT is_favorite FROM xkcd WHERE num = ?", num).Scan(&isFav)
		if err != nil {
			// If there's an error, just continue without the emoji
			logMessage(fmt.Sprintf("Warning: could not check favorite status for comic %d: %v", num, err))
			isFavorite = false
		} else {
			isFavorite = isFav.Valid && isFav.Bool
		}
		logMessage(fmt.Sprintf("Using favorite status from database: %t", isFavorite))
	}

	// Add ❤️ emoji to footer if it's a favorite
	footer := fmt.Sprintf("#%s %s", comicN, comicDate)
	var toggleFavText string
	if isFavorite {
		footer = footer + " ❤️"
		toggleFavText = "💔 Remove from favorites"
	} else {
		toggleFavText = "❤️ Add to favorites"
	}
	output := TextViewOutput{
		Variables: map[string]string{
			"comicPath": imagePath,
			"toggleFav": toggleFavText,
		},
		Response: fmt.Sprintf("# %s \n![](%s) \n%s", comicTitle, imageURL, comicAlt),
		Footer:   footer,
		Arg:      strconv.Itoa(num), // Add comic number as arg for toggle favorites
		Behaviour: map[string]interface{}{
			"response":   "append",
			"scroll":     "end",
			"inputfield": "select",
		},
	}

	jsonOutput, _ := json.Marshal(output)
	fmt.Print(string(jsonOutput))

	elapsed := time.Since(start)
	logMessage(fmt.Sprintf("\nScript duration (create textView): %.3f seconds", elapsed.Seconds()))

	return nil
}

func createTextViewFromPath(imagePath string) error {
	start := time.Now()

	// Extract number from path
	re := regexp.MustCompile(`/(\d+)\.png$`)
	matches := re.FindStringSubmatch(imagePath)
	if len(matches) < 2 {
		return fmt.Errorf("could not extract number from path")
	}

	num, err := strconv.Atoi(matches[1])
	if err != nil {
		return err
	}

	logMessage(fmt.Sprintf("number: %d", num))

	// Fetch comic from database
	db, err := openDB()
	if err != nil {
		return err
	}
	defer db.Close()

	var comic Comic
	var isFav sql.NullBool
	err = db.QueryRow("SELECT num, title, alt, img, year, month, day, is_favorite FROM xkcd WHERE num = ?", num).
		Scan(&comic.Num, &comic.Title, &comic.Alt, &comic.Img, &comic.Year, &comic.Month, &comic.Day, &isFav)
	if err != nil {
		return err
	}

	date := fmt.Sprintf("%s-%s-%s", comic.Year, comic.Month, comic.Day)

	// Add ❤️ emoji to footer if it's a favorite
	footer := fmt.Sprintf("#%d %s", comic.Num, date)
	toggleFavText := "❤️ Add to favorites"
	if isFav.Valid && isFav.Bool {
		footer = footer + " ❤️"
		toggleFavText = "💔 Remove from favorites"
	}

	output := TextViewOutput{
		Variables: map[string]string{
			"comicPath": imagePath,
			"toggleFav": toggleFavText,
		},
		Response: fmt.Sprintf("# %s \n![](%s) \n%s", comic.Title, comic.Img, comic.Alt),
		Footer:   footer,
		Arg:      strconv.Itoa(comic.Num), // Add comic number as arg for toggle favorites
		Behaviour: map[string]interface{}{
			"response":   "append",
			"scroll":     "end",
			"inputfield": "select",
		},
	}

	jsonOutput, _ := json.Marshal(output)
	fmt.Print(string(jsonOutput))

	elapsed := time.Since(start)
	logMessage(fmt.Sprintf("\nScript duration (textView recent): %.3f seconds", elapsed.Seconds()))

	return nil
}

func forceUpdate() error {
	logMessage("Checking for updates")
	checkUpdate(COMICSMAX)
	logMessage("Done 👍")

	result := AlfredOutput{
		Items: []AlfredItem{
			{
				Title:    "Done!",
				Subtitle: "ready to search xkcd now",
				Arg:      "",
				Icon:     map[string]string{"path": "icons/done.png"},
			},
		},
	}

	jsonOutput, _ := json.Marshal(result)
	fmt.Print(string(jsonOutput))

	return nil
}

func initializeDatabase() error {
	db, err := sql.Open("sqlite3", MY_DATABASE)
	if err != nil {
		return err
	}
	defer db.Close()

	// Create the xkcd table if it doesn't exist
	createTableSQL := `
	CREATE TABLE IF NOT EXISTS xkcd (
		num INTEGER PRIMARY KEY,
		title TEXT,
		alt TEXT,
		img TEXT,
		year TEXT,
		month TEXT,
		day TEXT,
		is_favorite BOOLEAN DEFAULT 0,
		is_read BOOLEAN DEFAULT 0
	);`

	_, err = db.Exec(createTableSQL)
	if err != nil {
		return fmt.Errorf("error creating table: %v", err)
	}

	logMessage("Database table initialized")
	return nil
}

func main() {
	if len(os.Args) < 2 {
		fmt.Fprintf(os.Stderr, "Usage: %s <command> [args...]\n", os.Args[0])
		fmt.Fprintf(os.Stderr, "Commands:\n")
		fmt.Fprintf(os.Stderr, "  query <search_terms>     - Search for comics\n")
		fmt.Fprintf(os.Stderr, "  random                   - Get random unread comic\n")
		fmt.Fprintf(os.Stderr, "  favorites                - Show favorites grid\n")
		fmt.Fprintf(os.Stderr, "  recents                   - Show recents grid\n")
		fmt.Fprintf(os.Stderr, "  toggle-fav <num>         - Toggle favorite status\n")
		fmt.Fprintf(os.Stderr, "  fetch-image <num> <url>  - Fetch comic image\n")
		fmt.Fprintf(os.Stderr, "  text-view <num>          - Create text view\n")
		fmt.Fprintf(os.Stderr, "  text-view-path <path>    - Create text view from image path\n")
		fmt.Fprintf(os.Stderr, "  force-update             - Force database update\n")
		os.Exit(1)
	}

	command := os.Args[1]

	rand.Seed(time.Now().UnixNano())

	switch command {
	case "query":
		var input string
		if len(os.Args) > 2 {
			input = strings.Join(os.Args[2:], " ")
		}
		if err := queryComics(input); err != nil {
			log.Fatal(err)
		}
	case "random":
		if err := randomComic(); err != nil {
			log.Fatal(err)
		}
	case "favorites":
		if err := favoriteGrid(); err != nil {
			log.Fatal(err)
		}
	case "recents":
		if err := recentGrid(); err != nil {
			log.Fatal(err)
		}
	case "toggle-fav":
		if len(os.Args) < 3 {
			log.Fatal("Usage: toggle-fav <comic_number>")
		}
		num, err := strconv.Atoi(os.Args[2])
		if err != nil {
			log.Fatal(err)
		}
		message, err := toggleFavorite(num)
		if err != nil {
			log.Fatal(err)
		}
		fmt.Print(message)
	case "fetch-image":
		if len(os.Args) < 3 {
			log.Fatal("Usage: fetch-image <comic_number>")
		}
		if err := fetchImage(os.Args[2]); err != nil {
			log.Fatal(err)
		}
	case "text-view":
		if len(os.Args) < 3 {
			log.Fatal("Usage: text-view <comic_number>")
		}
		if err := createTextView(os.Args[2]); err != nil {
			log.Fatal(err)
		}
	case "text-view-path":
		if len(os.Args) < 3 {
			log.Fatal("Usage: text-view-path <image_path>")
		}
		if err := createTextViewFromPath(os.Args[2]); err != nil {
			log.Fatal(err)
		}
	case "force-update":
		if err := forceUpdate(); err != nil {
			log.Fatal(err)
		}
	default:
		fmt.Fprintf(os.Stderr, "Unknown command: %s\n", command)
		os.Exit(1)
	}
}
