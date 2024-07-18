# Sunny ☀️   🌡️+87°F (feels +103°F, 63%) 🌬️↙4mph 🌔&m Wed Jul 17 19:24:22 2024
# W29Q3 – 199 ➡️ 166 – 67 ❇️ 297

import sqlite3
import json
import sys
from config import log


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
    # each dictionary should contain the title, author, and highText fields of the book
    
    # Split the string into individual search terms
    
    if not search_terms:
        query = "SELECT * FROM xkcd "
        params = []
    else:
        # Construct the SQL query
        query = "SELECT * FROM xkcd WHERE "
        conditions = []

        for term in search_terms:
            conditions.append(f"(alt LIKE ? OR title LIKE ?)")

        query += " AND ".join(conditions)

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
        result["items"].append({
            "title": f"{r['title']} ({myDate})",
            
            'subtitle': f"{myCounter}/{totCount} {r['alt']}",
            'valid': True,
            "quicklookurl": r['img'],
            
            "variables": {
                "imageURL": r['img'],
                "comicTitle": r['title'],
                "comicN": r['num'],
                "comicAlt": r['alt'],
                "comicDate": myDate,
            },
            
        

            
            'arg': f"https://xkcd.com/{r['num']}"
                }) 
        
    if MY_INPUT and not rs:
        result["items"].append({
            "title": "No matches found",
            "subtitle": "Try a different query",
            "arg": "",
            "icon": {
                "path": "icons/Warning.png"
                }
            
                })
        
    print (json.dumps(result))

queryItems('xkcd.sqlite', MY_INPUT)

# read a json file
with open('/Users/giovanni/Library/Caches/com.runningwithcrayons.Alfred/Workflow Data/com.vitorgalvao.alfred.shortfilms/list.json') as f:
    data = json.load(f)

# output the same file with pretty formatting
with open('/Users/giovanni/Library/Caches/com.runningwithcrayons.Alfred/Workflow Data/com.vitorgalvao.alfred.shortfilms/list_pretty.json', 'w') as f:
    json.dump(data, f, indent=4)