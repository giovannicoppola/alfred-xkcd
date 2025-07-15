#!/usr/bin/env python3


import json

import sqlite3
from time import time

from config import MY_DATABASE, log, fetchComicsPath, REFRESH_FLAG, COMICSMAX, checkUpdate



def fetchFavs():
    
    
    db = sqlite3.connect(MY_DATABASE)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    
    
    
    query = f"SELECT * FROM xkcd WHERE is_favorite = 1"
    cursor.execute(query)
    rs = cursor.fetchall()
    
    favsJSON = {"items": []}
    
    for r in rs:
        
        COMICS_PATH = fetchComicsPath(r['num'], r['img'],'favs')
        myDate = f"{r['year']}-{r['month']}-{r['day']}"

        myJSON = {
                    "title": r['title'],
                    "subtitle": r['alt'],
                    "icon": {
                        "path": COMICS_PATH
                    },
                    "mods": {
                        "ctrl": {
                            "subtitle": "remove from favorites",
                            "arg": r['num']
                        },
                        "shift": {
                            "subtitle": "copy to clipboard 📋️",
                            "arg": COMICS_PATH
                        },
                         "cmd": {
                            "arg": f"https://xkcd.com/{r['num']}",
                            "subtitle": "open on xkcd.com 🌐",
                        },
                        "alt": {
                    "valid": True,
                    "arg": f"https://www.explainxkcd.com/wiki/index.php/{r['num']}",
                    "subtitle": "open on explainxkcd.com 🌐",
                    
                        }
                    },
                    "quicklookurl": r['img'],
                    "match": f"{r['title']} {r['alt']}",
                    "arg": r['num'],
                     "variables": {
                "imageURL": r['img'],
                "comicTitle": r['title'],
                "comicN": r['num'],
                "comicAlt": r['alt'],
                "comicDate": myDate,
                "imagePath": COMICS_PATH
            },
                }
    
        favsJSON['items'].append(myJSON)
        
    if not rs:
        favsJSON["items"].append({
            "title": "No favorites here 🫤",
            "subtitle": "Add some!",
            "arg": "",
            "icon": {
                "path": "icons/broken-heart.png"
                }
            
                })

    
    print (json.dumps(favsJSON)) 

def main():
    main_start_time = time()
    if REFRESH_FLAG:
        log ("checking for updates")
        checkUpdate(COMICSMAX)

    fetchFavs()

    main_timeElapsed = time() - main_start_time
    log(f"\nscript duration (favsGrid): {round (main_timeElapsed,3)} seconds")



if __name__ == "__main__":
    main()



