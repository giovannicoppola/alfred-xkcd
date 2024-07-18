#!/usr/bin/env python3


import json
import sqlite3
from config import MY_DATABASE, FAVS

def fetchComic(num):
    db = sqlite3.connect(MY_DATABASE)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    
    
    
    query = "SELECT * FROM xkcd WHERE num = {num}"
    cursor.execute(query)
    rs = cursor.fetchone()

    # read the favs file
    with open(FAVS) as f:
        favsJSON = json.load(f)

    


    myJSON = {
                "title": "Eyes and Horns",
                "subtitle": "Experimental \ud800\udd01 6 minutes \ud800\udd01 Chaerin Im",
                "icon": {
                    "path": "~/Library/Caches/com.runningwithcrayons.Alfred/Workflow Data/com.vitorgalvao.alfred.shortfilms/images/Eyes-and-horns-Chaerin-Im-01.jpg"
                },
                "mods": {
                    "alt": {
                        "subtitle": "Inspired by Picasso\u2019s \u2018Vollard Suite\u2019, the transformation of the over masculine Minotaur leads to the destruction of boundaries of sexes."
                    }
                },
                "quicklookurl": "https://www.shortoftheweek.com/2024/07/17/eyes-and-horns/",
                "match": "Eyes and Horns Experimental",
                "arg": "https://player.vimeo.com/video/985689913"
            }
    
    favsJSON['items'].append(myJSON)

    with open(FAVS, 'w') as f:
        json.dump(favsJSON, f, indent=4)

    




