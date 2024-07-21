# Sunny ☀️   🌡️+87°F (feels +103°F, 63%) 🌬️↙4mph 🌔&m Wed Jul 17 19:24:22 2024
# W29Q3 – 199 ➡️ 166 – 67 ❇️ 297

import sqlite3
import json
import sys

from time import time
import requests
from config import log, COMICSMAX, REFRESH_FLAG, MY_DATABASE, CACHE_FOLDER_RECENTS, checkUpdate


MY_INPUT = sys.argv[1]





def queryItems(database, myInput):
    db = sqlite3.connect(database)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    
    myCounter = 0
    
    # split the input into search substrings 
    search_terms = myInput.split()
    # search for all the substrings in the input across 2 text fields (title, alt) in the table
    # return the results as a list of dictionaries
    
    
    if not search_terms:
        query = "SELECT * FROM xkcd ORDER BY NUM DESC"
        params = []
    else:
        # Construct the SQL query
        query = "SELECT * FROM xkcd WHERE "
        conditions = []

        for term in search_terms:
            conditions.append(f"(alt LIKE ? OR title LIKE ?)")

        query += " AND ".join(conditions)
        query += " ORDER BY NUM DESC"

        # Prepare the list of parameters for the placeholders in the SQL query
        params = []
        for term in search_terms:
            params.append(f"%{term}%")
            params.append(f"%{term}%")

    # Execute the query
    cursor.execute(query, params)
    rs = cursor.fetchall()
    
    
    totCount = len(rs)
    

    result = {"items": []}

    for r in rs:
        myCounter += 1
        myDate = f"{r['year']}-{r['month']}-{r['day']}"
        if r['is_favorite']:
            myFav = "❤️"
            toggleFav = "Remove from favorites 🫤"  
        else:
            myFav = ""
            toggleFav = "⭐️ Add to favorites"  

        if r['is_read']:
            myRead = ""
            
        else:
            myRead = "•"
            


        comicsNum = r['num']
        
        
        result["items"].append({
            "title": f"{r['title']} ({myDate}) {myFav}{myRead}",
            
            'subtitle': f"{myCounter:,}/{totCount:,} {r['alt']}",
            'valid': True,
            "quicklookurl": r['img'],
            "mods": {
                "ctrl": {
                    "valid": True,
                    "arg": comicsNum,
                    "subtitle": toggleFav,
                    "variables": {
                        "currQuery": MY_INPUT,
                        "imageURL": r['img'],
                        "comicDate": myDate,
                    },

                },
              "shift": {
                    "valid": True,
                    "arg": comicsNum,
                    "subtitle": "copy to clipboard 📋️",
                 
                },
                "cmd": {
                    "valid": True,
                    "arg": f"https://xkcd.com/{r['num']}",
                    "subtitle": "open on xkcd.com 🌐",
                    
                },
                "alt": {
                    "valid": True,
                    "arg": f"https://www.explainxkcd.com/wiki/index.php/{r['num']}",
                    "subtitle": "open on explainxkcd.com 🌐",
                    
                        }
            },


            "variables": {
                "imageURL": r['img'],
                "comicTitle": r['title'],
                "comicN": r['num'],
                "comicAlt": r['alt'],
                "comicDate": myDate,
                "imagePath": f"{CACHE_FOLDER_RECENTS}{comicsNum}.png"
            },
            
        

            
            'arg': comicsNum
                }) 
        
    if MY_INPUT and not rs:
        result["items"].append({
            "title": "No comics found 🫥",
            "subtitle": "Try a different query!",
            "arg": "",
            "icon": {
                "path": "icons/Warning.png"
                }
            
                })
        
    print (json.dumps(result))






def main():
    main_start_time = time()
    if REFRESH_FLAG:
        log ("checking for updates")
        checkUpdate(COMICSMAX)

    queryItems(MY_DATABASE, MY_INPUT)
    main_timeElapsed = time() - main_start_time
    log(f"\nscript duration (main query): {round (main_timeElapsed,3)} seconds")

    # 0.06 seconds without refreshing, 0.11 seconds with refreshing (but no new comics)




if __name__ == '__main__':
    main()
