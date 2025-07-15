import sys
import os
import datetime
import zipfile
import urllib.request
import sqlite3

# Add your desired path to PYTHONPATH
sys.path.append(os.path.join(os.getcwd(), 'lib'))
import requests



def checkDatabase(data_folder):
    
    DB_ZIPPED = 'xkcd.sqlite.zip'
    
    if os.path.exists(DB_ZIPPED):  # there is a zipped database: distribution version
        log ("found distribution database, extracting")
        with zipfile.ZipFile(DB_ZIPPED, "r") as zip_ref:
            zip_ref.extractall(data_folder)
        os.remove (DB_ZIPPED)
    





CACHE_FOLDER = os.getenv('alfred_workflow_cache')
CACHE_FOLDER_RECENTS = CACHE_FOLDER+"/images/recents/"
CACHE_FOLDER_FAVS = CACHE_FOLDER+"/images/favs/"
COMICSMAX_FILE = CACHE_FOLDER+"/comicsMax.txt"
REFRESH_RATE = int(os.path.expanduser(os.getenv('REFRESH_RATE', '')))

DATA_FOLDER = os.getenv('alfred_workflow_data')

if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)
    checkDatabase(DATA_FOLDER)
if not os.path.exists(CACHE_FOLDER):
    os.makedirs(CACHE_FOLDER)
if not os.path.exists(CACHE_FOLDER_RECENTS):
    os.makedirs(CACHE_FOLDER_RECENTS)
if not os.path.exists(CACHE_FOLDER_FAVS):
    os.makedirs(CACHE_FOLDER_FAVS)


MY_DATABASE = f'{DATA_FOLDER}/xkcd.sqlite'


def log(s, *args):
    if args:
        s = s % args
    print(s, file=sys.stderr)


if not os.path.exists(COMICSMAX_FILE):
    COMICSMAX = 2962
    REFRESH_FLAG = True
else:
    # check if the database needs to be refreshed
    
    # Step 2: Read the file
    with open(COMICSMAX_FILE, "r") as file:
        lines = file.readlines()
        COMICSMAX = int(lines[0].strip())
        file_date = datetime.datetime.strptime(lines[1].strip(), "%Y-%m-%d").date()

        # Step 3: Get the current date
        current_date = datetime.date.today()

        # Step 4: Calculate the difference in days
        date_difference = (current_date - file_date).days

        # Step 5: Check if the date difference is more than x days
        if date_difference >= REFRESH_RATE:
            REFRESH_FLAG = True
        else:
            REFRESH_FLAG = False


def fetchComicsPath(num, myURL, mode='recent'):
    if mode == 'favs':
        COMICS_PATH = f"{CACHE_FOLDER_FAVS}{num}.png"
    else:
        COMICS_PATH = f"{CACHE_FOLDER_RECENTS}{num}.png"
    
    if not os.path.exists(COMICS_PATH):
        log ("retrieving image: " + COMICS_PATH)
        try:
            urllib.request.urlretrieve(myURL, COMICS_PATH)
        except urllib.error.URLError as e:
                log("Error retrieving image: ", e.reason)  # Log the specific error reason
    return COMICS_PATH



def toggle_read(num_value, db_path=MY_DATABASE):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    

    # Retrieve the current value of is_favorite
    cursor.execute("SELECT is_read, num FROM xkcd WHERE num = ?", (num_value,))
    current_value = cursor.fetchone()
    
    
    # Check if the record was found
    if current_value is None:
        log(f"No record found with num = {num_value}")
        return
    
    
    # Toggle the value of is_favorite
    new_value = not bool(current_value[0])

    # Update the value in the database
    cursor.execute("UPDATE xkcd SET is_read = ? WHERE num = ?", (new_value, num_value))
    conn.commit()

    # Close the connection
    conn.close()

def checkUpdate(myNewN):
    # read the highest comic number from the COMICSMAX variable
    #try on the website if there is a new comic with a number higher than the highest in the database
    #if so, update the database and the COMICSMAX variable

    newComics = []
    
    while True:
        # Construct the file URL
        file_url = f"https://xkcd.com/{myNewN}/info.0.json"
        
        try:
            # Attempt to download the file
            response = requests.get(file_url)
            
            # Check if the download was successful
            if response.status_code == 200:
                # Save the file
                json_data = response.json()
                newComics.append(json_data)
                log(f"Downloaded {myNewN}.json")
                
                # Increment the variable
                myNewN += 1
            else:
                # If the status code is not 200, break the loop
                log(f"Failed to download file{myNewN}.json")

                break
        except requests.exceptions.RequestException as e:
            # Handle any exceptions that occur during the download
            log(f"An error occurred: {e}")
            break
    
    #with open(f"{CACHE_FOLDER}/newComics.json", 'w') as f:
    #    f.write(json.dumps(newComics, indent=2))
    
    # update the database with the new comics
    update_database(newComics) 
    
    
    # write to file the last number that worked, by replacing the existing COMICSMAX file
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    with open(COMICSMAX_FILE, 'w') as f:
        f.write(f"{myNewN}\n")
        f.write(f"{current_date}\n")





def update_database (newComics):
    # read the existing database
    db = sqlite3.connect(MY_DATABASE)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    
    # Add the new comics to the database
    for comic in newComics:
        cursor.execute("INSERT INTO xkcd (num, title, alt, img, year, month, day) VALUES (?, ?, ?, ?, ?, ?, ?)", (comic['num'], comic['title'], comic['alt'], comic['img'], comic['year'], comic['month'], comic['day']))
    
    # Commit the changes and close the connection
    db.commit()
    db.close()
