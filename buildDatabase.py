# Sunny ☀️   🌡️+79°F (feels +82°F, 65%) 🌬️↘6mph 🌔&m Wed Jul 17 06:21:21 2024
# W29Q3 – 199 ➡️ 166 – 67 ❇️ 297


"""
A script to build an xkcd database by using the json interface
current count as of today: 2,958
"""

import requests
from time import time, sleep
import sqlite3
import json
import sys

MY_INPUT = sys.argv[1]


def create_XKCD_DB(myData):
	conn = sqlite3.connect('xkcd.sqlite')
	c = conn.cursor()
	
	sql_drop = "DROP TABLE IF EXISTS xkcd"
	sql_create = """CREATE TABLE xkcd (
		ID INTEGER PRIMARY KEY AUTOINCREMENT,        
		 
		month INT,
		num INT,
		link TEXT,
		
		year INTEGER,
		news TEXT,
		safe_title TEXT,

		transcript TEXT,
		alt TEXT,
		img TEXT,
		
		title TEXT,
		day INT
		
		)
		"""
	
	c.execute(sql_drop)
	c.execute(sql_create)
	
	for myComic in myData:
		
		c.execute('INSERT INTO xkcd (month, num, link, year, news, safe_title, transcript, alt, img, title, day) VALUES (?,?,?,   ?,?,?,   ?,?,?, ?,?)', 
			(myComic['month'], 
			myComic['num'],
			myComic['link'],
			
			myComic['year'],
			myComic['news'],
			myComic['safe_title'],

			myComic['transcript'],
			myComic['alt'],
			myComic['img'],
	
			myComic['title'],
			myComic['day']
		))
	

	
	conn.commit()
	conn.close()

def insert_xkcd_data():
	conn = sqlite3.connect('xkcd.sqlite')
	c = conn.cursor()
	for xkcd in xkcd_list:
		c.execute('''INSERT INTO XKCD (TITLE, IMG, ALT, LINK)
					 VALUES (?, ?, ?, ?)''', (xkcd['title'], xkcd['img'], xkcd['alt'], xkcd['link']))
	conn.commit()
	conn.close()
    


def getJSONdata(start, end):
        

    currentURL = 'https://xkcd.com/info.0.json'
    baseURL = f"https://xkcd.com/xxxx/info.0.json"

    toDo = start-end 
    xkcd_list = []
    myCounter = 0
    failedURLs = []
    for i in range(start, end, -1):
        # Wait 
        sleep(0.2)
        url = f"https://xkcd.com/{i}/info.0.json"
        myCounter += 1
        response = requests.get(url)

        if response.status_code == 200:
            json_data = response.json()
            xkcd_list.append(json_data)
            print(f"Retrieved data for {json_data['title']}: {myCounter}/{toDo} ({myCounter/toDo*100:.0f}%)")

        else:
            print(f"Failed to retrieve data: {response.status_code}")
            failedURLs.append(url)

    # save the list to a json file
    with open('xkcd.json', 'w') as f:
        f.write(json.dumps(xkcd_list, indent=2))
    
    #write the failed URLs to a file
    with open('failedURLs.txt', 'w') as f:
        for url in failedURLs:
            f.write(url + '\n')

def refreshReadwise_Reader_Database (rebuildDays=0):
	
	
	
	#retrieving all the images
	select_statement = "SELECT user_book_id, cover_image_url FROM highlights"
	
	c.execute(select_statement)

	rs = c.fetchall()
	
	for rec in rs:
		if rec[1]:
			ICON_PATH = f'{IMAGE_FOLDER}{rec[0]}.jpg'
			if not os.path.exists(ICON_PATH):
				log ("retrieving image" + ICON_PATH)
				try:
					urllib.request.urlretrieve(rec[1], ICON_PATH)
				except urllib.error.URLError as e:
				    # If an exception occurs, print an error message and delete the file if it exists
					log(f"Failed to download file: {e.reason}")
					ICON_PATH = f'{IMAGE_FOLDER}{rec[0]}.jpg'
					src = 'icons/supplementals.png'
					shutil.copy(src, ICON_PATH)

		else:
			ICON_PATH = f'{IMAGE_FOLDER}{rec[0]}.jpg'
			src = 'icons/supplementals.png'
			shutil.copy(src, ICON_PATH)

	
	
	
def queryItems(database, myInput):
    db = sqlite3.connect(database)
    db.row_factory = sqlite3.Row
    myCounter = 0
    types = [k for k, v in my_checks.items() if v == '1']
    myTypes = ','.join('?'*len(types))

    # getting list of tags from the database
    tag_statement = "SELECT name FROM tags"
    tag_rows = db.execute(tag_statement).fetchall()
    tagList = [row[0] for row in tag_rows]
    tagList = ['#' + s for s in tagList]

    #initializing JSON output
    result = {"items": [], "variables":{}}
    mySearchInput = myInput.strip()

    # extracting any full tags from current input, adding them to the sql query
    fullTags = re.findall('#[^ ]+ ', myInput)
    fullTags = [s.strip() for s in fullTags]
    
    tag_sql = ""
    for currTag  in fullTags:
        if currTag.strip() in tagList: #if it is a real tag
            mySearchInput = re.sub(currTag, '', mySearchInput).strip()
            currTag = currTag[1:].strip()
            tag_sql = f"{tag_sql} AND highTags LIKE '%{currTag}%'"
        

    # check if the user is trying to enter a tag
    MYMATCH = re.search(r'(?:^| )#[^ ]*$', myInput)
    if (MYMATCH !=None):
        
        MYFLAG = MYMATCH.group(0).lstrip(' ')
        mySearchInput = re.sub(MYFLAG,'',myInput)
        myInput = re.sub(MYFLAG,'',myInput)
        
        mySubset = [i for i in tagList if MYFLAG in i]
        
        # adding a complete tag if the user selects it from the list
        if mySubset:
            for thislabel in mySubset:
                result["items"].append({
                "title": thislabel,
                "subtitle": myInput,
                "arg": myInput+thislabel+" ",
                "icon": {
                        "path": f"icons/label.png"
                    }
                })
        else:
            result["items"].append({
            "title": "no labels matching",
            "subtitle": "try another query?",
            "arg": " ",
            "icon": {
                    "path": f"icons/Warning.png"
                }
            })
            
    
    else:

        
        
        keywords = mySearchInput.split()
        if len(keywords) > 1:
            conditions = []
            conditions2 = []
            for keyword in keywords:
                if SEARCH_SCOPE == "Text":
                    conditions.append(f"(highText LIKE '%{keyword}%')")
                    conditions_str = " AND ".join(conditions)
            
        
                elif SEARCH_SCOPE == "Book":
                    conditions.append(f"(title LIKE '%{keyword}%')")
                    conditions_str = " AND ".join(conditions)
            
                elif SEARCH_SCOPE == "Both":
                    conditions.append(f"(highText LIKE '%{keyword}%')")
                    conditions1_str = " AND ".join(conditions)
                    conditions2.append(f"(title LIKE '%{keyword}%')")
                    conditions2_str = " AND ".join(conditions2)
                    conditions_str = f'({conditions1_str}) OR ({conditions2_str})' 
            
                    
        else: 
            if SEARCH_SCOPE == "Text":
                conditions_str = f"(highText LIKE '%{mySearchInput}%')"
                    
    
            elif SEARCH_SCOPE == "Book":
                conditions_str = f"(title LIKE '%{mySearchInput}%')"
                
            elif SEARCH_SCOPE == "Both":
                conditions_str = f"(highText LIKE '%{mySearchInput}%' or title LIKE '%{mySearchInput}%')"
    
    
        sql = f"SELECT * FROM highlights WHERE {conditions_str} and category IN ({myTypes}) {tag_sql}"
        log (sql)
        
        rs = db.execute(sql, types).fetchall()
        totCount = len(rs)


        for r in rs:
            myCounter += 1
            myURL = r['high_readwise_url']
            myURLall = r['readwise_url']
            myTags = ''
            if r['highTags'] != "[]":
                myTags = json.loads (r['highTags'].replace("'", '"'))
                myTags = ",".join ([x['name'] for x in myTags])
                myTags = f"🏷️ {myTags}"
                if r['high_is_favorite'] == 1:
                    myTags = myTags+'❤️'
        
            if r['highURL']:
                sourceURLstring = f"open source URL"
            else:
                sourceURLstring = "no source URL"
            myQuickLook = f"{IMAGE_H_FOLDER}{r['highID']}.jpg"
            result["items"].append({
                "title": r['highText'],
                
                'subtitle': f"{myCounter}/{totCount} {r['title']}-{r['author']} {myTags}",
                'valid': True,
                "quicklookurl": myQuickLook,
                'variables': {
                    "fullOutput": f"{r['highText']}\n\n{r['author']}: {r['title']}",
                    "myURL": myURL,
                    "myStatus": 'completed',
                    "myURLall": myURLall
                },
                 "mods": {
    
    
                    "command": {
                        "valid": 'true',
                        "subtitle": f"{sourceURLstring}",
                        "arg": r['highURL']
                    }},
                "icon": {
                    "path": f"{IMAGE_FOLDER}{r['user_book_id']}.jpg"
                },
                'arg': ''
                    }) 
            
        if MYINPUT and not rs:
            result["items"].append({
                "title": "No matches in your library",
                "subtitle": "Try a different query",
                "arg": "",
                "icon": {
                    "path": "icons/Warning.png"
                    }
                
                    })
        
    print (json.dumps(result))

# readJSONdata
def readJSONdata():
	with open('xkcd.json', 'r') as f:
		xkcd_list = json.load(f)
	return xkcd_list

      


def main():
	main_start_time = time()
	# getJSONdata (2958,0)
	myData = readJSONdata()
	
	create_XKCD_DB(myData)
	main_timeElapsed = time() - main_start_time
	print (f"\nscript duration: {round (main_timeElapsed,3)} seconds")




if __name__ == "__main__":
    main()


