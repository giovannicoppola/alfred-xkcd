#!/usr/bin/env python3


import json
import os
import sqlite3
import urllib.request
from config import MY_DATABASE, FAVS, CACHE_FOLDER_IMAGES, log

myNum = os.path.expanduser(os.getenv('comicNum', ''))
myURL=os.path.expanduser(os.getenv('imageURL', ''))

log (f"mynum = {myNum}")
def fetchComic(num):
    
    # read the favs file
    with open(FAVS) as f:
        favsJSON = json.load(f)
        
    
    db = sqlite3.connect(MY_DATABASE)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    
    
    
    query = f"SELECT * FROM xkcd WHERE num = {num}"
    cursor.execute(query)
    rs = cursor.fetchall()
    

    for r in rs:
        COMICS_PATH = f"{CACHE_FOLDER_IMAGES}{r['num']}.png"
        if not os.path.exists(COMICS_PATH):
            log ("retrieving image" + COMICS_PATH)
            try:
                urllib.request.urlretrieve(myURL, COMICS_PATH)
            except urllib.error.URLError as e:
                log("Error retrieving image:", e.reason)  # Log the specific error reason

    

        myJSON = {
                    "title": r['title'],
                    "subtitle": r['alt'],
                    "icon": {
                        "path": COMICS_PATH
                    },
                    "mods": {
                        "alt": {
                            "subtitle": "test"
                        }
                    },
                    "quicklookurl": r['img'],
                    "match": f"{r['title']} {r['alt']}",
                    "arg": COMICS_PATH
                }
    
    favsJSON['items'].append(myJSON)

    with open(FAVS, 'w') as f:
        json.dump(favsJSON, f, indent=4)

    print (json.dumps(favsJSON)) 

if myNum:
    fetchComic(myNum)
else:
    # read the favs file
    with open(FAVS) as f:
        favsJSON = json.load(f)
    
    print (json.dumps(favsJSON))




