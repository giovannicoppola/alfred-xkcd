# Sunny ☀️   🌡️+87°F (feels +103°F, 63%) 🌬️↙4mph 🌔&m Wed Jul 17 19:24:22 2024
# W29Q3 – 199 ➡️ 166 – 67 ❇️ 297

import sqlite3
import json
from time import time
import random
from config import log, COMICSMAX, REFRESH_FLAG, MY_DATABASE, CACHE_FOLDER_RECENTS, checkUpdate, update_database



def randomUnread(database):
    db = sqlite3.connect(database)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    
    # Query to get all num ids where is_read is not 1
    query = "SELECT num FROM xkcd WHERE is_read != 1 OR is_read IS NULL"
    cursor.execute(query)

    # Fetch all results
    results = cursor.fetchall()

    # Create a list of num ids
    num_ids = [row[0] for row in results]
    log(f"Number of unread comics: {len(num_ids)}")
    unreadN = len(num_ids)
    # Choose a random num id from the list
    random_num = random.choice(num_ids)
    return random_num, unreadN

def fetchRandom(database, num, unreads):
    db = sqlite3.connect(MY_DATABASE)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
	
    query = f"SELECT * FROM xkcd WHERE NUM = {num}"
    cursor.execute(query)
    r = cursor.fetchone()

    

    result = {"items": []}

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
        "title": f"{r['title']} (#{comicsNum} {myDate}) {myFav}{myRead} [unread: {unreads:,}]",
        
        'subtitle': f"{r['alt']}",
        'valid': True,
        "quicklookurl": r['img'],
        "mods": {
            "ctrl": {
                "valid": True,
                "arg": comicsNum,
                "subtitle": toggleFav,
                "variables": {
                    
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
        
    
        
    print (json.dumps(result))






def main():
    main_start_time = time()
    if REFRESH_FLAG:
        log ("checking for updates")
        checkUpdate(COMICSMAX)

    myNum, unreadN = randomUnread(MY_DATABASE)
    fetchRandom(MY_DATABASE, myNum, unreadN)
    main_timeElapsed = time() - main_start_time
    log(f"\nscript duration (random): {round (main_timeElapsed,3)} seconds")

    




if __name__ == '__main__':
    main()
