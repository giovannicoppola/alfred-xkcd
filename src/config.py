import sys
import os
import datetime

CACHE_FOLDER = os.getenv('alfred_workflow_cache')
CACHE_FOLDER_IMAGES = CACHE_FOLDER+"/images/"
COMICSMAX_FILE = CACHE_FOLDER+"/comicsMax.txt"

if not os.path.exists(CACHE_FOLDER):
    os.makedirs(CACHE_FOLDER)
if not os.path.exists(CACHE_FOLDER_IMAGES):
    os.makedirs(CACHE_FOLDER_IMAGES)

MY_DATABASE = 'xkcd.sqlite'
FAVS = 'xkcd_Favs.json'

def log(s, *args):
    if args:
        s = s % args
    print(s, file=sys.stderr)


if not os.path.exists(COMICSMAX_FILE):
    COMICSMAX = 2959
    REFRESH_FLAG = True
else:
    # check if the database needs to be refreshed
    x = 0  # Example: 10 days

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
        if date_difference >= x:
            REFRESH_FLAG = True
        else:
            REFRESH_FLAG = False



"""
import os
import sys
import zipfile

WF_DATA = os.getenv('alfred_workflow_data')
INDEX_DB = WF_DATA + '/index.db'



UStotPop = 329484123



if not os.path.exists(WF_DATA):
    os.makedirs(WF_DATA)


def log(s, *args):
    if args:
        s = s % args
    print(s, file=sys.stderr)


def logF(log_message, file_name):
    with open(file_name, "a") as f:
        f.write(log_message + "\n")





def checkDatabase():
    
    DB_ZIPPED = 'index.db.zip'
    
    if os.path.exists(DB_ZIPPED):  # there is a zipped database: distribution version
        log ("found distribution database, extracting")
        with zipfile.ZipFile(DB_ZIPPED, "r") as zip_ref:
            zip_ref.extractall(WF_DATA)
        os.remove (DB_ZIPPED)
    elif os.path.exists('index.db'):  # there is a new version, possibly rebuilt via script: replace the version in DATA
        os.rename('index.db', INDEX_DB)




checkDatabase()



"""