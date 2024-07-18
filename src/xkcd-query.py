# Sunny ☀️   🌡️+87°F (feels +103°F, 63%) 🌬️↙4mph 🌔&m Wed Jul 17 19:24:22 2024
# W29Q3 – 199 ➡️ 166 – 67 ❇️ 297

import sqlite3
import json
import sys
import datetime
import requests
from config import log, COMICSMAX, COMICSMAX_FILE, REFRESH_FLAG


MY_INPUT = sys.argv[1]


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

                # write to file the last number that worked, by replacing the existing COMICSMAX file
                
                
                break
        except requests.exceptions.RequestException as e:
            # Handle any exceptions that occur during the download
            log(f"An error occurred: {e}")
            break
    with open(f"newComics.json", 'w') as f:
        f.write(json.dumps(newComics, indent=2))
    update_database(newComics)
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    with open(COMICSMAX_FILE, 'w') as f:
        f.write(f"{myNewN}\n")
        f.write(f"{current_date}\n")
        


def update_database (newComics):
    # read the existing database
    db = sqlite3.connect('xkcd.sqlite')
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    
    # Add the new comics to the database
    for comic in newComics:
        cursor.execute("INSERT INTO xkcd (num, title, alt, img, year, month, day) VALUES (?, ?, ?, ?, ?, ?, ?)", (comic['num'], comic['title'], comic['alt'], comic['img'], comic['year'], comic['month'], comic['day']))
    
    # Commit the changes and close the connection
    db.commit()
    db.close()


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
        result["items"].append({
            "title": f"{r['title']} ({myDate})",
            
            'subtitle': f"{myCounter}/{totCount} {r['alt']}",
            'valid': True,
            "quicklookurl": r['img'],
            "mods": {
                "ctrl": {
                    "valid": True,
                    "arg": r['num'],
                    "subtitle": "⭐️ Add to favorites",
                    "variables": {
                        
                        "comicNum": r['num'],
                        "imageURL": r['img'],
                        "comicDate": myDate,
                    },

                }
              
            },
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






def main():
   
    if REFRESH_FLAG:
        checkUpdate(COMICSMAX)

    queryItems('xkcd.sqlite', MY_INPUT)

    # # read a json file
    # with open('/Users/giovanni/Library/Caches/com.runningwithcrayons.Alfred/Workflow Data/com.vitorgalvao.alfred.shortfilms/list.json') as f:
    #     data = json.load(f)

    # # output the same file with pretty formatting
    # with open('/Users/giovanni/Library/Caches/com.runningwithcrayons.Alfred/Workflow Data/com.vitorgalvao.alfred.shortfilms/list_pretty.json', 'w') as f:
    #     json.dump(data, f, indent=4)




if __name__ == '__main__':
    main()
